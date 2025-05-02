import pygame
from pygame import display, event, font, image, mouse, mixer
import sys
from os.path import abspath, dirname, join
import json
from game_objects import SOUNDS
from game_objects import load_volume, update_sound_volumes, save_volume, save_controls, draw_volume_slider, draw_text_button, render_glow_text
from game_objects import draw_cursor, load_controls, save_controls, apply_vhs_effect, load_vhs_mode, save_vhs_mode, draw_vhs_toggle_button


BASE_PATH = abspath(dirname(__file__))
FONT_PATH = join(BASE_PATH, 'fonts/')
IMAGE_PATH = join(BASE_PATH, 'images/')
SETTINGS_PATH = join(BASE_PATH, 'settings.json')

WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

# --- Inicialización de Pygame ---
pygame.init()
pygame.font.init()
mixer.init()

# Canal exclusivo para la música de menú
MENU_CHANNEL = mixer.Channel(0)

ship_cursor = image.load(join(IMAGE_PATH, 'ship.png')).convert_alpha()
ship_cursor = pygame.transform.rotate(ship_cursor, 45)
ship_cursor = pygame.transform.scale(ship_cursor, (40, 40))
pygame.mouse.set_visible(False)

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
SCREEN = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
display.set_caption("Space Invaders Settings")

TITLE_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 64)
BUTTON_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 40)
FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 24)
SMALL_FONT = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 20)

background_image = image.load(join(IMAGE_PATH, 'background.jpg')).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

DEFAULT_CONTROLS_1 = {'shoot': 'UP', 'left': 'LEFT', 'right': 'RIGHT'}
DEFAULT_CONTROLS_2 = {'shoot': 'W', 'left': 'A', 'right': 'D'}

def exit_settings():
    import main_menu
    main_menu.main()


def main(SCREEN, FONT, SMALL_FONT, background_image):
    volume_level = load_volume()
    update_sound_volumes(volume_level)
    
    VHS_MODE = load_vhs_mode()
    last_vhs_toggle_time = 0

    if not MENU_CHANNEL.get_busy():
        MENU_CHANNEL.play(SOUNDS['menu_music'], loops=-1)

    running = True
    current_changing = None
    keys_list = ['shoot', 'left', 'right']
    dragging_volume = False
    volume_cooldown = 0
    volume_timer = 0

    def in_volume_mode():
        return dragging_volume or pygame.time.get_ticks() < volume_cooldown

    while running:
        SCREEN.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        # --- Eventos ---
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if current_changing:
                    key_name = pygame.key.name(ev.key).upper()
                    p, idx = current_changing
                    controls = load_controls(p)
                    controls[keys_list[idx]] = key_name
                    save_controls(controls, player=p)
                    current_changing = None
                elif ev.key == pygame.K_ESCAPE:
                    running = False
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if dragging_volume:
                    volume_cooldown = pygame.time.get_ticks() + 300
                    volume_timer = pygame.time.get_ticks()
                dragging_volume = False

        # --- Actualizar modo volumen ---
        if dragging_volume and pygame.time.get_ticks() - volume_timer > 1000:
            dragging_volume = False

        # --- Barra de volumen ---
        bar_x = SCREEN_WIDTH * 0.235
        bar_y = SCREEN_HEIGHT * 0.8
        bar_w = SCREEN_WIDTH * 0.3
        bar_h = 10
        handle_r = 11

        if mouse_click[0] and not dragging_volume:
            if bar_y - handle_r <= mouse_pos[1] <= bar_y + bar_h + handle_r:
                dragging_volume = True
                volume_timer = pygame.time.get_ticks()
                current_changing = None

        if dragging_volume and mouse_click[0]:
            rel_x = max(bar_x, min(mouse_pos[0], bar_x + bar_w))
            volume_level = (rel_x - bar_x) / bar_w
            volume_level = max(0.0, min(1.0, volume_level))
            save_volume(volume_level)
            update_sound_volumes(volume_level)
            volume_timer = pygame.time.get_ticks()

        # --- Dibujar controles P1/P2 ---
        for player_idx, x_off in enumerate([0.06, 0.65], start=1):
            controls = load_controls(player=player_idx)
            render_glow_text(f"Controles Player {player_idx}",
                             (SCREEN_WIDTH * x_off, SCREEN_HEIGHT * 0.2),
                             SMALL_FONT, GREEN, (40, 40, 40))

            for i, key in enumerate(keys_list):
                action_text = f"{key.capitalize()}: {controls[key]}"
                pos = (SCREEN_WIDTH * x_off, SCREEN_HEIGHT * (0.4 + 0.1 * i))
                rect = pygame.Rect(pos[0], pos[1], 300, 40)
                hovered = rect.collidepoint(mouse_pos)
                if in_volume_mode():
                    render_glow_text(action_text, pos, SMALL_FONT, (0, 0, 0), (40, 40, 40))
                else:
                    color = PURPLE if hovered else BLUE
                    render_glow_text(action_text, pos, SMALL_FONT, color, (40, 40, 40))
                    if hovered and mouse_click[0]:
                        current_changing = (player_idx, i)

        # --- Mensaje de cambio de tecla ---
        if current_changing and not in_volume_mode():
            p, idx = current_changing
            render_glow_text(f"Presiona nueva tecla para Player {p} ({keys_list[idx]})",
                             (SCREEN_WIDTH * 0.06, SCREEN_HEIGHT * 0.7),
                             SMALL_FONT, RED, (40, 40, 40))

        # --- Botones "Restablecer" ---
        for p, x_off, defaults in [(1, 0.06, DEFAULT_CONTROLS_1),
                                   (2, 0.65, DEFAULT_CONTROLS_2)]:
            reset_pos = (SCREEN_WIDTH * x_off, SCREEN_HEIGHT * 0.3)
            rect = pygame.Rect(reset_pos[0], reset_pos[1], 250, 40)
            hovered = rect.collidepoint(mouse_pos)
            color = (0, 0, 0) if in_volume_mode() else (PURPLE if hovered else RED)
            render_glow_text(f"Restablecer P{p}", reset_pos, SMALL_FONT, color, (40, 40, 40))
            if hovered and mouse_click[0] and not in_volume_mode():
                save_controls(defaults, player=p)
                current_changing = None

        # --- Slider Volumen y botón Back ---
        draw_volume_slider(SCREEN, volume_level, FONT, FONT)
        if not in_volume_mode():
            draw_text_button("Back", (SCREEN_WIDTH * 0.425, SCREEN_HEIGHT * 0.9),
                             RED, PURPLE, exit_settings)
        else:
            render_glow_text("Back", (SCREEN_WIDTH * 0.425, SCREEN_HEIGHT * 0.9),
                             BUTTON_FONT, (0, 0, 0), (40, 40, 40))

        # --- Toggle VHS ---
        VHS_MODE, last_vhs_toggle_time = draw_vhs_toggle_button(
            SCREEN, SMALL_FONT, mouse_pos, mouse_click, VHS_MODE, in_volume_mode(), last_vhs_toggle_time
        )
        save_vhs_mode(VHS_MODE)

        # --- Cursores y VHS ---
        draw_cursor(SCREEN, ship_cursor)
        
        if VHS_MODE:
            apply_vhs_effect(SCREEN)

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def run_game():
    main(SCREEN, FONT, SMALL_FONT, background_image)


if __name__ == "__main__":
    main(SCREEN, FONT, SMALL_FONT, background_image)