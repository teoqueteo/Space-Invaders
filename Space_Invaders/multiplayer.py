import pygame
from pygame import display, event, font, image, mouse, mixer
import sys
from os.path import abspath, dirname, join
from random import choice, randint
from game_objects import LEVEL_PATTERNS, IMAGES, SOUNDS
from game_objects import create_aliens, multi_save_score, create_block_pattern, alien_shoot, mute_all, play_music_for_level, load_controls_from_settings, open_settings_menu
from game_objects import load_volume, update_sound_volumes, apply_vhs_effect, load_vhs_mode
from game_objects import Player, Alien, Extra, Explosion, Block, Laser
import json


# --- Paths ---
BASE_PATH = abspath(dirname(__file__))
IMAGE_PATH = join(BASE_PATH, 'images/')
FONT_PATH = join(BASE_PATH, 'fonts/')
AUDIO_PATH = join(BASE_PATH, 'audio/')
SETTINGS_PATH = join(BASE_PATH, 'settings.json')

# --- Colores ---
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)


# --- Initialize ---
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)  # Oculta el puntero

# Pantalla completa con dimensiones adaptativas
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders - Multiplayer")

# Cargar y ajustar imagen de fondo
background_image = image.load(join(IMAGE_PATH, 'background.jpg')).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Reloj para controlar los FPS
CLOCK = pygame.time.Clock()


ship_cursor = image.load(join(IMAGE_PATH, 'ship.png')).convert_alpha()
ship_cursor = pygame.transform.rotate(ship_cursor, 45)
ship_cursor = pygame.transform.scale(ship_cursor, (40, 40))


TITLE_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 64)
BUTTON_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 40)
FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 24)
SMALL_FONT = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 20)

# --- Cargar configuración desde settings.json ---
with open(SETTINGS_PATH, 'r') as f:
    SETTINGS = json.load(f)

# --- Get player name ---
def get_player_name(player_num):
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
                if event.key == pygame.K_RETURN:
                    if name:
                        return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isalnum():
                        name += event.unicode

        SCREEN.blit(background_image, (0, 0))
        prompt = base_font.render(f"Jugador {player_num}, Ingresa tu nombre:", True, WHITE)
        text_surface = base_font.render(name, True, WHITE)
        SCREEN.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        SCREEN.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
        VHS_MODE = load_vhs_mode()
        if VHS_MODE:
            apply_vhs_effect(SCREEN)
        pygame.draw.rect(SCREEN, color_active, input_rect, 2)
        pygame.display.flip()
        CLOCK.tick(60)

# --- Handle collisions ---
def handle_collisions(player1, player2, aliens, enemy_lasers, blocks, extra_group, explosions, sounds, player1_name, player2_name):
    # Solo las colisiones con jugadores vivos
    if player1.is_alive:
        for laser in player1.lasers:
            if pygame.sprite.spritecollide(laser, blocks, True):
                laser.kill()
            # Con aliens
            aliens_hit = pygame.sprite.spritecollide(laser, aliens, True)
            if aliens_hit:
                for alien in aliens_hit:
                    laser.kill()
                    player1.score += alien.value  # Sumar puntos dependiendo del tipo de alien
                    explosion = Explosion(alien.rect.centerx, alien.rect.centery, alien.color)
                    explosions.add(explosion)
                    sounds['invaderkilled'].play()

            # Con nave misteriosa
            extras_hit = pygame.sprite.spritecollide(laser, extra_group, True)
            if extras_hit:
                for extra in extras_hit:
                    player1.score += 50  # Mystery ship suma 50 puntos
                    laser.kill()
                    sounds['mysterykilled'].play()
                    explosion = Explosion(extra.rect.centerx, extra.rect.centery, 'extra')
                    explosions.add(explosion)

    if player2.is_alive:
        for laser in player2.lasers:
            if pygame.sprite.spritecollide(laser, blocks, True):
                laser.kill()
            # Con aliens
            aliens_hit = pygame.sprite.spritecollide(laser, aliens, True)
            if aliens_hit:
                for alien in aliens_hit:
                    laser.kill()
                    player2.score += alien.value  # Sumar puntos dependiendo del tipo de alien
                    explosion = Explosion(alien.rect.centerx, alien.rect.centery, alien.color)
                    explosions.add(explosion)
                    sounds['invaderkilled'].play()

            # Con nave misteriosa
            extras_hit = pygame.sprite.spritecollide(laser, extra_group, True)
            if extras_hit:
                for extra in extras_hit:
                    player2.score += 50  # Mystery ship suma 50 puntos
                    laser.kill()
                    sounds['mysterykilled'].play()
                    explosion = Explosion(extra.rect.centerx, extra.rect.centery, 'extra')
                    explosions.add(explosion)

    # --- Colisiones +de láser enemigo --- (igual que antes para ambos jugadores)
    for laser in enemy_lasers:
        # Con barreras (las balas enemigas destruyen las barreras)
        if pygame.sprite.spritecollide(laser, blocks, True):
            laser.kill()

        # Con jugadores vivos
        if player1.is_alive and pygame.sprite.spritecollide(player1, enemy_lasers, True):
            laser.kill()
            player1.lives -= 1
            SOUNDS['shipexplosion'].play()
            player1.image = player1.hit_image
            player1.hit_timer = pygame.time.get_ticks()
            if player1.lives <= 0:
                player1.die()  # Llamamos al método para hacer morir al jugador

        if player2.is_alive and pygame.sprite.spritecollide(player2, enemy_lasers, True):
            laser.kill()
            player2.lives -= 1
            SOUNDS['shipexplosion'].play()
            player2.image = player2.hit_image
            player2.hit_timer = pygame.time.get_ticks()
            if player2.lives <= 0:
                player2.die()  # Llamamos al método para hacer morir al jugador


    # --- GAME OVER si ambos jugadores están muertos ---
    if not player1.is_alive and not player2.is_alive:
        total_score = player1.score + player2.score
        multi_save_score(f"{player1_name} y {player2_name}", total_score)
        VHS_MODE = load_vhs_mode()
        mute_all()
        SOUNDS['game_over'].play(-1)

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < 5000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            SCREEN.blit(background_image, (0, 0))
            game_over_text = FONT.render("GAME OVER", True, RED)
            score_p1_text = FONT.render(f'{player1_name}: {player1.score}', True, WHITE)
            score_p2_text = FONT.render(f'{player2_name}: {player2.score}', True, WHITE)
            score_total_text = FONT.render(f'Total: {total_score}', True, GREEN)
            SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            SCREEN.blit(score_p1_text, (SCREEN_WIDTH // 2 - score_p1_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            SCREEN.blit(score_p2_text, (SCREEN_WIDTH // 2 - score_p2_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            SCREEN.blit(score_total_text, (SCREEN_WIDTH // 2 - score_total_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            if VHS_MODE:
                apply_vhs_effect(SCREEN)
                        
            pygame.display.update()
            CLOCK.tick(60)
        SOUNDS['game_over'].stop()
        import main_menu
        main_menu.main()
        return

# --- Pause menu ---
def pause_menu(player1_name, player2_name, player1, player2):
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
            SCREEN.blit(option_text,
                        (SCREEN_WIDTH // 2 - option_text.get_width() // 2,
                         SCREEN_HEIGHT // 2 - 50 + i * 60))

        pygame.display.update()
        CLOCK.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif ev.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif ev.key == pygame.K_RETURN:
                    selected_option = options[selected]
                    if selected_option == 'Reanudar':
                        paused = False
                    elif selected_option == 'Volver al Menu':
                        total_score = player1.score + player2.score
                        multi_save_score(f"{player1_name} y {player2_name}", total_score)
                        VHS_MODE = load_vhs_mode()
                        mute_all()
                        SOUNDS['game_over'].play(-1)

                        start_time = pygame.time.get_ticks()
                        while pygame.time.get_ticks() - start_time < 5000:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()

                            SCREEN.blit(background_image, (0, 0))
                            game_over_text = FONT.render("GAME OVER", True, RED)
                            score_p1_text = FONT.render(f'{player1_name}: {player1.score}', True, WHITE)
                            score_p2_text = FONT.render(f'{player2_name}: {player2.score}', True, WHITE)
                            score_total_text = FONT.render(f'Total: {total_score}', True, GREEN)
                            SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
                            SCREEN.blit(score_p1_text, (SCREEN_WIDTH // 2 - score_p1_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                            SCREEN.blit(score_p2_text, (SCREEN_WIDTH // 2 - score_p2_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                            SCREEN.blit(score_total_text, (SCREEN_WIDTH // 2 - score_total_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
                            if VHS_MODE:
                                apply_vhs_effect(SCREEN)
                        
                            pygame.display.update()
                            CLOCK.tick(60)
                        SOUNDS['game_over'].stop()
                        import main_menu
                        main_menu.main()
                        return
                    
                    elif selected_option == 'Configuracion':
                        open_settings_menu(player_names=[player1_name, player2_name])
                    elif selected_option == 'Salir del Juego':
                        multi_save_score(f"{player1_name} y {player2_name}",
                                         player1.score + player2.score)
                        pygame.quit()
                        sys.exit()


# --- Loop principal del juego Multiplayer ---
def main():
    # --- Inicialización de volumen y controles ---
    volume_level = load_volume()
    pygame.mixer.music.set_volume(volume_level)
    update_sound_volumes(volume_level)
    VHS_MODE = load_vhs_mode()

    controls_p1, controls_p2 = load_controls_from_settings()

    # --- Pedir nombres ---
    SOUNDS['transition_music'].play(-1)
    player1_name = get_player_name(1)
    player2_name = get_player_name(2)
    SOUNDS['transition_music'].stop()

    play_music_for_level(1)

    # --- Crear jugadores ---
    player1 = Player((200, 580), SCREEN_WIDTH, 5, SCREEN_HEIGHT, controls_p1, player_id=1)
    player2 = Player((600, 580), SCREEN_WIDTH, 5, SCREEN_HEIGHT, controls_p2, player_id=2)
    player_group = pygame.sprite.Group(player1, player2)

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
        # — Volumen dinámico —
        new_vol = load_volume()
        if new_vol != volume_level:
            volume_level = new_vol
            pygame.mixer.music.set_volume(volume_level)
            update_sound_volumes(volume_level)

        # — Controles dinámicos —
        new_c1, new_c2 = load_controls_from_settings()
        if new_c1 != controls_p1:
            controls_p1 = new_c1
            player1.controls = controls_p1
        if new_c2 != controls_p2:
            controls_p2 = new_c2
            player2.controls = controls_p2

        SCREEN.blit(background_image, (0, 0))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pause_menu(player1_name, player2_name, player1, player2)
            
            elif e.type == extra_timer:
                side = choice(['left', 'right'])
                extra_group.add(Extra(side, SCREEN_WIDTH))
                SOUNDS['mysteryentered'].play()
            elif e.type == enemy_shoot_timer and aliens:
                alien_shoot(aliens, enemy_lasers, SCREEN_HEIGHT, SOUNDS['shoot2'])

        # Movimiento de los aliens
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
                        total_score = player1.score + player2.score
                        multi_save_score(f"{player1_name} y {player2_name}", total_score)
                        VHS_MODE = load_vhs_mode()
                        mute_all()
                        SOUNDS['game_over'].play(-1)

                        start_time = pygame.time.get_ticks()
                        while pygame.time.get_ticks() - start_time < 5000:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()

                            SCREEN.blit(background_image, (0, 0))
                            game_over_text = FONT.render("GAME OVER", True, RED)
                            score_p1_text = FONT.render(f'{player1_name}: {player1.score}', True, WHITE)
                            score_p2_text = FONT.render(f'{player2_name}: {player2.score}', True, WHITE)
                            score_total_text = FONT.render(f'Total: {total_score}', True, GREEN)
                            SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
                            SCREEN.blit(score_p1_text, (SCREEN_WIDTH // 2 - score_p1_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                            SCREEN.blit(score_p2_text, (SCREEN_WIDTH // 2 - score_p2_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                            SCREEN.blit(score_total_text, (SCREEN_WIDTH // 2 - score_total_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
                            if VHS_MODE:
                                apply_vhs_effect(SCREEN)
                        
                            pygame.display.update()
                            CLOCK.tick(60)
                        SOUNDS['game_over'].stop()
                        import main_menu
                        main_menu.main()
                        return
                break

        # Actualización de los grupos
        player_group.update()
        extra_group.update()
        enemy_lasers.update()

        # Manejo de las colisiones
        handle_collisions(player1, player2, aliens, enemy_lasers, blocks, extra_group, explosions, SOUNDS, player1_name, player2_name)


        # Verificar si pasamos de nivel
        if not aliens:
            current_level += 1
            if current_level >= len(LEVEL_PATTERNS):
                total_score = player1.score + player2.score
                multi_save_score(f"{player1_name} y {player2_name}", total_score)
                VHS_MODE = load_vhs_mode()
                mute_all()
                SOUNDS['victory'].play()

                start_time = pygame.time.get_ticks()
                while pygame.time.get_ticks() - start_time < 5000:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                    SCREEN.blit(background_image, (0, 0))
                    victory_text = FONT.render("¡VICTORIA!", True, GREEN)
                    score_p1_text = FONT.render(f'{player1_name}: {player1.score}', True, WHITE)
                    score_p2_text = FONT.render(f'{player2_name}: {player2.score}', True, WHITE)
                    score_total_text = FONT.render(f'Total: {total_score}', True, GREEN)

                    SCREEN.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
                    SCREEN.blit(score_p1_text, (SCREEN_WIDTH // 2 - score_p1_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                    SCREEN.blit(score_p2_text, (SCREEN_WIDTH // 2 - score_p2_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                    SCREEN.blit(score_total_text, (SCREEN_WIDTH // 2 - score_total_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

                    if VHS_MODE:
                        apply_vhs_effect(SCREEN)

                    pygame.display.update()
                    CLOCK.tick(60)

                SOUNDS['victory'].stop()
                import main_menu
                main_menu.main()
                return
            else:
                # Cargar el siguiente nivel
                play_music_for_level(current_level + 1)
                aliens = create_aliens(LEVEL_PATTERNS[current_level])
                direction = 1
                player1.lasers.empty()
                player2.lasers.empty()
                enemy_lasers.empty()
                pygame.time.wait(1000)
                
        # Dibujado
        aliens.draw(SCREEN)
        player_group.draw(SCREEN)
        for player in player_group:
            player.lasers.draw(SCREEN)
        blocks.draw(SCREEN)
        extra_group.draw(SCREEN)
        enemy_lasers.draw(SCREEN)
        explosions.update()
        explosions.draw(SCREEN)

        # Dibujar puntuaciones y vidas
        score_text1 = FONT.render(f'{player1_name}: {player1.score}', True, WHITE)
        score_text2 = FONT.render(f'{player2_name}: {player2.score}', True, WHITE)
        SCREEN.blit(score_text1, (20, 10))
        SCREEN.blit(score_text2, (SCREEN_WIDTH - score_text2.get_width() - 20, 10))

        for i in range(player1.lives):
            SCREEN.blit(IMAGES['ship'], (20 + i * 60, 40))
        for i in range(player2.lives):
            SCREEN.blit(IMAGES['ship_2'], (SCREEN_WIDTH - (i + 1) * 60 - 20, 40))

        # Mostrar el número del nivel
        level_text = FONT.render(f"Nivel: {current_level + 1}", True, WHITE)
        SCREEN.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))
        
        if VHS_MODE:
            apply_vhs_effect(SCREEN)
        
        pygame.display.update()
        CLOCK.tick(60)

def run_game():
    main()

if __name__ == "__main__":
    main()
