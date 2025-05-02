import pygame
from pygame import display, event, font, image, mouse, mixer
import sys
from os.path import abspath, dirname, join
from random import choice, randint
from game_objects import LEVEL_PATTERNS, IMAGES, SOUNDS
from game_objects import create_aliens, single_save_score, create_block_pattern, alien_shoot, mute_all, play_music_for_level, load_controls_from_settings, open_settings_menu
from game_objects import load_volume, update_sound_volumes, apply_vhs_effect, load_vhs_mode
from game_objects import Player, Alien, Extra, Explosion, Block, Laser
import json

# --- Rutas ---
BASE_PATH = abspath(dirname(__file__))  # Ruta base del proyecto
IMAGE_PATH = join(BASE_PATH, 'images/')  # Carpeta de imágenes
FONT_PATH = join(BASE_PATH, 'fonts/')    # Carpeta de fuentes
AUDIO_PATH = join(BASE_PATH, 'audio/')   # Carpeta de audios
SETTINGS_PATH = join(BASE_PATH, 'settings.json')

# --- Colores ---
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

# --- Inicialización de Pygame ---
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)  # Oculta el cursor del mouse

ship_cursor = image.load(join(IMAGE_PATH, 'ship.png')).convert_alpha()
ship_cursor = pygame.transform.rotate(ship_cursor, 45)
ship_cursor = pygame.transform.scale(ship_cursor, (40, 40))

TITLE_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 64)
BUTTON_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 40)
FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 24)
SMALL_FONT = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 20)

# Configuración de pantalla completa
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders - Single Player")

# Cargar y ajustar imagen de fondo
background_image = image.load(join(IMAGE_PATH, 'background.jpg')).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Reloj para controlar los FPS
CLOCK = pygame.time.Clock()

# --- Cargar configuración desde settings.json ---
with open(SETTINGS_PATH, 'r') as f:
    SETTINGS = json.load(f)

# --- Función para pedir el nombre del jugador ---
def get_player_name():
    input_active = True
    name = ''
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 32, 300, 64)
    color_active = pygame.Color('lightskyblue3')
    base_font = pygame.font.Font(join(FONT_PATH, 'space_invaders.ttf'), 32)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10 and event.unicode.isalnum():
                    name += event.unicode

        # Dibujar pantalla de ingreso de nombre
        SCREEN.blit(background_image, (0, 0))
        prompt = base_font.render("Ingresa tu nombre:", True, WHITE)
        text_surface = base_font.render(name, True, WHITE)
        SCREEN.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        SCREEN.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
        VHS_MODE = load_vhs_mode()
        if VHS_MODE:
            apply_vhs_effect(SCREEN)
        pygame.draw.rect(SCREEN, color_active, input_rect, 2)
        pygame.display.flip()
        CLOCK.tick(60)


# --- Función para manejar colisiones ---
def handle_collisions(player, aliens, enemy_lasers, blocks, extra_group, explosions, sounds, name):
    for laser in player.lasers:
        if pygame.sprite.spritecollide(laser, blocks, True):
            laser.kill()
        aliens_hit = pygame.sprite.spritecollide(laser, aliens, True)
        if aliens_hit:
            for alien in aliens_hit:
                laser.kill()
                player.score += alien.value
                explosions.add(Explosion(alien.rect.centerx, alien.rect.centery, alien.color))
                sounds['invaderkilled'].play()
        extras_hit = pygame.sprite.spritecollide(laser, extra_group, True)
        if extras_hit:
            for extra in extras_hit:
                player.score += 50
                laser.kill()
                sounds['mysterykilled'].play()
                explosion = Explosion(extra.rect.centerx, extra.rect.centery, 'extra')
                explosions.add(explosion)

    for laser in enemy_lasers:
        if pygame.sprite.spritecollide(laser, blocks, True):
            laser.kill()
        if pygame.sprite.spritecollide(player, enemy_lasers, True):
            laser.kill()
            player.lives -= 1
            sounds['shipexplosion'].play()
            player.image = player.hit_image
            player.hit_timer = pygame.time.get_ticks()

            if player.lives <= 0:
                # --- GAME OVER ---
                single_save_score(name, player.score)
                VHS_MODE = load_vhs_mode()
                mute_all()
                SOUNDS['game_over'].play(-1)

                game_over_start = pygame.time.get_ticks()
                while pygame.time.get_ticks() - game_over_start < 5000:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                    SCREEN.blit(background_image, (0, 0))
                    game_over_text = FONT.render("GAME OVER", True, RED)
                    score_text = FONT.render(f'Score: {player.score}', True, WHITE)
                    SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                                 SCREEN_HEIGHT // 2 - 50))
                    SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                             SCREEN_HEIGHT // 2 + 10))

                    if VHS_MODE:
                        apply_vhs_effect(SCREEN)

                    pygame.display.update()
                    pygame.time.delay(16)
                SOUNDS['game_over'].stop()
                import main_menu
                main_menu.main()
                return


# --- Función de menú de pausa ---
def pause_menu(player, name):
    selected = 0
    options = ['Reanudar', 'Volver al Menu', 'Configuracion', 'Salir del Juego']
    base_font = pygame.font.Font(join(FONT_PATH, 'space_invaders.ttf'), 32)
    paused = True

    while paused:
        SCREEN.blit(background_image, (0, 0))
        title_text = base_font.render('PAUSA', True, WHITE)
        SCREEN.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        VHS_MODE = load_vhs_mode()
        if VHS_MODE:
            apply_vhs_effect(SCREEN)

        for i, option in enumerate(options):
            color = GREEN if i == selected else WHITE
            option_text = base_font.render(option, True, color)
            SCREEN.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50 + i * 60))

        pygame.display.update()
        CLOCK.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    selected_option = options[selected]
                    if selected_option == 'Reanudar':
                        paused = False
                    elif selected_option == 'Volver al Menu':
                        single_save_score(name, player.score)
                        VHS_MODE = load_vhs_mode()
                        mute_all()
                        SOUNDS['game_over'].play(-1)

                        game_over_start = pygame.time.get_ticks()
                        while pygame.time.get_ticks() - game_over_start < 5000:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()

                            SCREEN.blit(background_image, (0, 0))
                            game_over_text = FONT.render("GAME OVER", True, RED)
                            score_text = FONT.render(f'Score: {player.score}', True, WHITE)
                            SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                            SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

                            if VHS_MODE:
                                apply_vhs_effect(SCREEN)

                            pygame.display.update()
                            pygame.time.delay(16)

                        SOUNDS['game_over'].stop()
                        import main_menu
                        main_menu.main()

                    elif selected_option == 'Configuracion':
                        open_settings_menu(player_names=["Jugador 1"])
                    elif selected_option == 'Salir del Juego':
                        single_save_score(name, player.score)
                        pygame.quit()
                        sys.exit()


# --- Loop principal del juego Single Player ---
def main():
    # Iniciar volumen y controles al comienzo
    volume_level = load_volume()
    pygame.mixer.music.set_volume(volume_level)
    update_sound_volumes(volume_level)
    
    new_volume = load_volume()
    if new_volume != volume_level:
        volume_level = new_volume
        pygame.mixer.music.set_volume(volume_level)
        update_sound_volumes(volume_level)
    
    VHS_MODE = load_vhs_mode()

    controls_p1, controls_p2 = load_controls_from_settings()

    SOUNDS['transition_music'].play(-1)
    name = get_player_name()
    SOUNDS['transition_music'].stop()
    play_music_for_level(1)

    player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20), SCREEN_WIDTH, 6, SCREEN_HEIGHT, controls_p1, player_id=1)
    player_group = pygame.sprite.GroupSingle(player)
    player.lives = 3
    player.score = 0

    explosions = pygame.sprite.Group()
    current_level = 0
    aliens = create_aliens(LEVEL_PATTERNS[current_level])

    blocks = pygame.sprite.Group()
    for i in range(4):
        x_offset = SCREEN_WIDTH // 5 * (i + 1) - 40
        blocks_pattern = create_block_pattern(x_offset, SCREEN_HEIGHT - 150, 6, GREEN)
        blocks.add(*blocks_pattern)

    direction = 1
    extra_group = pygame.sprite.Group()
    extra_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(extra_timer, randint(8000, 12000))

    enemy_lasers = pygame.sprite.Group()
    enemy_shoot_timer = pygame.USEREVENT + 2
    pygame.time.set_timer(enemy_shoot_timer, 800)

    running = True
    while running:
        VHS_MODE = load_vhs_mode()
        # --- Actualización dinámica de volumen y controles ---
        new_volume = load_volume()
        if new_volume != volume_level:
            volume_level = new_volume
            pygame.mixer.music.set_volume(volume_level)
            update_sound_volumes(volume_level)

        new_controls_p1, new_controls_p2 = load_controls_from_settings()
        if new_controls_p1 != controls_p1:
            controls_p1 = new_controls_p1
            player.controls = controls_p1  # Actualizar controles del jugador
            
        SCREEN.blit(background_image, (0, 0))
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pause_menu(player, name)
            
            elif e.type == extra_timer:
                side = choice(['left', 'right'])
                extra_group.add(Extra(side, SCREEN_WIDTH))
                SOUNDS['mysteryentered'].play()
            elif e.type == enemy_shoot_timer and aliens:
                alien_shoot(aliens, enemy_lasers, SCREEN_HEIGHT, SOUNDS['shoot2'])

        aliens.update(direction)
        
        # Aliens destruyen bloques si los tocan
        for alien in aliens:
            pygame.sprite.spritecollide(alien, blocks, True)
        
        for alien in aliens:
            if alien.rect.right >= SCREEN_WIDTH or alien.rect.left <= 0:
                direction *= -1
                for a in aliens:
                    a.rect.y += 10

                # Verificar si algún alien ha llegado demasiado abajo
                for a in aliens:
                    if a.rect.bottom >= SCREEN_HEIGHT - 80:
                        game_over_text = FONT.render("GAME OVER", True, RED)
                        score_text = FONT.render(f'Score: {player.score}', True, WHITE)
                        single_save_score(name, player.score)
                        mute_all()
                        SOUNDS['game_over'].play(-1)

                        # Mostrar pantalla de Game Over por 5 segundos con efecto VHS si está activo
                        start_time = pygame.time.get_ticks()
                        while pygame.time.get_ticks() - start_time < 5000:
                            SCREEN.blit(background_image, (0, 0))
                            SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                            SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                            if VHS_MODE:
                                apply_vhs_effect(SCREEN)
                            pygame.display.update()
                            CLOCK.tick(60)

                        SOUNDS['game_over'].stop()
                        import main_menu
                        main_menu.main()
                        return
                break


        player_group.update()
        extra_group.update()
        enemy_lasers.update()

        handle_collisions(player, aliens, enemy_lasers, blocks, extra_group, explosions, SOUNDS, name)

        if not aliens:
            current_level += 1
            if current_level >= len(LEVEL_PATTERNS):
                win_text = FONT.render("¡VICTORIA!", True, GREEN)
                score_text = FONT.render(f'Score: {player.score}', True, WHITE)
                single_save_score(name, player.score)
                mute_all()
                SOUNDS['victory'].play()
                
                start_time = pygame.time.get_ticks()
                while pygame.time.get_ticks() - start_time < 5000:
                    SCREEN.blit(background_image, (0, 0))
                    SCREEN.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                    SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                    if VHS_MODE:
                        apply_vhs_effect(SCREEN)
                    pygame.display.update()
                    CLOCK.tick(60)

                SOUNDS['victory'].stop()
                import main_menu
                main_menu.main()
                return
            else:
                play_music_for_level(current_level + 1)
                aliens = create_aliens(LEVEL_PATTERNS[current_level])
                direction = 1
                player.lasers.empty()
                enemy_lasers.empty()
                pygame.time.wait(1000)

        player_group.draw(SCREEN)
        player.lasers.draw(SCREEN)
        aliens.draw(SCREEN)
        blocks.draw(SCREEN)
        extra_group.draw(SCREEN)
        enemy_lasers.draw(SCREEN)
        explosions.update()
        explosions.draw(SCREEN)

        for i in range(player.lives):
            SCREEN.blit(IMAGES['ship'], (SCREEN_WIDTH - (i + 1) * 60 - 10, 10))

        score_text = FONT.render(f'Score: {player.score}', True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        level_text = FONT.render(f'Nivel: {current_level + 1}', True, WHITE)
        SCREEN.blit(level_text, (10, 40))

        if VHS_MODE:
            apply_vhs_effect(SCREEN)

        pygame.display.update()
        CLOCK.tick(60)

def run_game():
    main()

if __name__ == "__main__":
    main()