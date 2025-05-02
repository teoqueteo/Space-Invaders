import pygame
import sys
from os.path import abspath, dirname, join
from game_objects import SOUNDS, IMAGES
from game_objects import Player, Laser, Block
from game_objects import create_block_pattern, mute_all, load_controls_from_settings, open_settings_menu
from game_objects import load_volume, update_sound_volumes, apply_vhs_effect, load_vhs_mode
import json


# --- Paths ---
BASE_PATH = abspath(dirname(__file__))
IMAGE_PATH = join(BASE_PATH, 'images/')
FONT_PATH = join(BASE_PATH, 'fonts/')
AUDIO_PATH = join(BASE_PATH, 'audio/')
BACKGROUND_PATH = join(IMAGE_PATH, 'background.jpg')
SETTINGS_PATH = join(BASE_PATH, 'settings.json')

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
RED = (237, 28, 36)
BLUE = (0, 162, 232)

# player-specific colors
PLAYER1_COLOR = (0, 255, 90)    # #00ff5a
PLAYER2_COLOR = (255, 115, 0)   # #ff7300

# --- Initialize ---
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)  # Oculta el puntero
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders - Player vs Player")
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(join(FONT_PATH, 'space_invaders.ttf'), 24)
background_image = pygame.transform.scale(pygame.image.load(BACKGROUND_PATH), (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Load settings.json ---
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
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10 and event.unicode.isalnum():
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
def handle_collisions(player1, player2, blocks1, blocks2, player1_name, player2_name):
    # --- Láseres del jugador 1 ---
    for laser in player1.lasers:
        # Colisión con ambos sets de escudos
        if pygame.sprite.spritecollide(laser, blocks1, True) or pygame.sprite.spritecollide(laser, blocks2, True):
            laser.kill()
        # Colisión con el jugador 2
        if pygame.sprite.collide_rect(laser, player2):
            laser.kill()
            player2.take_damage()

    # --- Láseres del jugador 2 ---
    for laser in player2.lasers:
        # Colisión con ambos sets de escudos
        if pygame.sprite.spritecollide(laser, blocks1, True) or pygame.sprite.spritecollide(laser, blocks2, True):
            laser.kill()
        # Colisión con el jugador 1
        if pygame.sprite.collide_rect(laser, player1):
            laser.kill()
            player1.take_damage()

    # --- Colisión entre láseres de ambos jugadores ---
    for laser1 in player1.lasers:
        for laser2 in player2.lasers:
            if pygame.sprite.collide_rect(laser1, laser2):
                laser1.kill()
                laser2.kill()

    # Verificar ganador
    if player1.lives <= 0:
        return f"¡{player2_name} gana!"
    if player2.lives <= 0:
        return f"¡{player1_name} gana!"
    return None


# --- Pause menu ---
def pause_menu(player1_name, player2_name):
    selected = 0
    options = ["Reanudar", "Volver al Menu", "Configuracion", "Salir del Juego"]
    base_font = pygame.font.Font(join(FONT_PATH, 'space_invaders.ttf'), 32)

    while True:
        SCREEN.blit(background_image, (0, 0))
        title_text = base_font.render('PAUSA', True, WHITE)
        SCREEN.blit(title_text,
                    (SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                     SCREEN_HEIGHT // 2 - 150))
        VHS_MODE = load_vhs_mode()
        if VHS_MODE:
            apply_vhs_effect(SCREEN)

        for i, option in enumerate(options):
            color = GREEN if i == selected else WHITE
            text = base_font.render(option, True, color)
            SCREEN.blit(text,
                        (SCREEN_WIDTH // 2 - text.get_width() // 2,
                         SCREEN_HEIGHT // 2 - 50 + i * 60))

        pygame.display.flip()
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
                    choice = options[selected]

                    if choice == "Reanudar":
                        return

                    elif choice == "Volver al Menu":
                        # Juego cancelado con pantalla de 5s y VHS
                        result = "¡Juego cancelado!"
                        game_over_text = FONT.render(result, True, RED)

                        mute_all()
                        SOUNDS['game_over'].play(-1)
                        VHS_MODE = load_vhs_mode()
                        start = pygame.time.get_ticks()

                        while pygame.time.get_ticks() - start < 5000:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()

                            SCREEN.blit(background_image, (0, 0))
                            SCREEN.blit(game_over_text,
                                        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - 50))
                            if VHS_MODE:
                                apply_vhs_effect(SCREEN)
                            pygame.display.update()
                            CLOCK.tick(60)

                        SOUNDS['game_over'].stop()
                        import main_menu
                        main_menu.main()
                        pygame.quit()
                        sys.exit()

                    elif choice == "Configuracion":
                        open_settings_menu(player_names=[player1_name, player2_name])

                    elif choice == "Salir del Juego":
                        pygame.quit()
                        sys.exit()


# --- Loop principal del juego P vs P ---
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
    SOUNDS['game_music_1'].play(-1)
    
    player1 = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20), SCREEN_WIDTH, 6, SCREEN_HEIGHT, controls_p1, player_id=1)
    player2 = Player((SCREEN_WIDTH // 2, 80), SCREEN_WIDTH, 6, SCREEN_HEIGHT, controls_p2, player_id=-2)

    player1_group = pygame.sprite.GroupSingle(player1)
    player2_group = pygame.sprite.GroupSingle(player2)
    
    blocks1_speed = -1
    blocks2_speed = 1

    blocks1 = pygame.sprite.Group()
    blocks2 = pygame.sprite.Group()

    for i in range(5):
        x_offset = SCREEN_WIDTH // 6 * (i + 1) - 40
        blocks1.add(*create_block_pattern(x_offset, SCREEN_HEIGHT // 2 + 150, 6, PLAYER1_COLOR))
        blocks2.add(*create_block_pattern(x_offset, SCREEN_HEIGHT // 2 - 190, 6, PLAYER2_COLOR, flip_vertical=True))

    running = True
    while running:
        VHS_MODE = load_vhs_mode()
        new_vol = load_volume()
        if new_vol != volume_level:
            volume_level = new_vol
            pygame.mixer.music.set_volume(volume_level)
            update_sound_volumes(volume_level)

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
                pause_menu(player1_name, player2_name)

        player1_group.update()
        player2_group.update()

        # Mover barreras
        for block in blocks1:
            block.rect.x += blocks1_speed
        if min(block.rect.left for block in blocks1) <= 0 or max(block.rect.right for block in blocks1) >= SCREEN_WIDTH:
            blocks1_speed *= -1

        for block in blocks2:
            block.rect.x += blocks2_speed
        if min(block.rect.left for block in blocks2) <= 0 or max(block.rect.right for block in blocks2) >= SCREEN_WIDTH:
            blocks2_speed *= -1

        # Colisiones y fin del juego
        result = handle_collisions(player1, player2, blocks1, blocks2, player1_name, player2_name)
        if result:
            game_over_text = FONT.render(result, True, GREEN)

            mute_all()
            SOUNDS['victory'].play()
            VHS_MODE = load_vhs_mode()
            start = pygame.time.get_ticks()

            while pygame.time.get_ticks() - start < 5000:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                SCREEN.blit(background_image, (0, 0))
                SCREEN.blit(game_over_text,
                            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                             SCREEN_HEIGHT // 2 - 50))
                if VHS_MODE:
                    apply_vhs_effect(SCREEN)
                pygame.display.update()
                CLOCK.tick(60)

            SOUNDS['victory'].stop()
            import main_menu
            main_menu.main()
            return


        # Dibujar jugadores, barreras y UI
        player1_group.draw(SCREEN)
        player2_group.draw(SCREEN)
        player1.lasers.draw(SCREEN)
        player2.lasers.draw(SCREEN)
        blocks1.draw(SCREEN)
        blocks2.draw(SCREEN)

        text1 = FONT.render(player1_name, True, PLAYER1_COLOR)
        SCREEN.blit(text1, (20, SCREEN_HEIGHT // 2 + 30))
        for i in range(player1.lives):
            SCREEN.blit(IMAGES['ship'], (20 + i * 60, SCREEN_HEIGHT // 2 + 70))

        text2 = FONT.render(player2_name, True, PLAYER2_COLOR)
        SCREEN.blit(text2, (SCREEN_WIDTH - 20 - text2.get_width(), SCREEN_HEIGHT // 2 - 30))
        for i in range(player2.lives):
            SCREEN.blit(IMAGES['ship_2'], (SCREEN_WIDTH - 20 - (i + 1) * 60, SCREEN_HEIGHT // 2 - 100))

        if VHS_MODE:
            apply_vhs_effect(SCREEN)
            
        pygame.display.update()
        CLOCK.tick(60)

def run_game():
    main()

if __name__ == "__main__":
    main()
