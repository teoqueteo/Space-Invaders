import pygame
from pygame import display, event, font, image, mouse, mixer
import sys
from os.path import abspath, dirname, join
from random import randint, uniform
import json
from game_objects import SOUNDS
from game_objects import load_volume, update_sound_volumes, single_load_ranking, multi_load_ranking, draw_text_button, render_glow_text
from game_objects import apply_vhs_effect, load_vhs_mode


BASE_PATH = abspath(dirname(__file__))
FONT_PATH = join(BASE_PATH, 'fonts/')
IMAGE_PATH = join(BASE_PATH, 'images/')
SETTINGS_PATH = join(BASE_PATH, 'settings.json')

WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

pygame.init()
pygame.font.init()
ship_cursor = image.load(join(IMAGE_PATH, 'ship.png')).convert_alpha()
ship_cursor = pygame.transform.rotate(ship_cursor, 45)
ship_cursor = pygame.transform.scale(ship_cursor, (40, 40))  # Ajusta el tamaño si es necesario
pygame.mouse.set_visible(False)

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
SCREEN = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
display.set_caption("Space Invaders Menu")

TITLE_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 64)
BUTTON_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 40)
FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 24)
SMALL_FONT = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 20)

background_image = image.load(join(IMAGE_PATH, 'background.jpg')).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

MENU_CHANNEL = mixer.Channel(0)

class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = randint(0, SCREEN_WIDTH)
        self.y = randint(-SCREEN_HEIGHT, 0)
        self.speed = uniform(0.5, 2)
        self.size = randint(1, 2)
        self.color = (randint(180, 255), randint(180, 255), randint(180, 255))

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.reset()

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(100)]

def start_single_player():
    MENU_CHANNEL.stop()
    import single_player
    single_player.run_game()


def start_multiplayer():
    MENU_CHANNEL.stop()
    import multiplayer
    multiplayer.run_game()


def start_p_vs_p():
    MENU_CHANNEL.stop()
    import p_vs_p
    p_vs_p.run_game()


def start_settings():
    import settings
    settings.main(SCREEN, FONT, SMALL_FONT, background_image)


def exit_game():
    MENU_CHANNEL.stop()
    pygame.quit()
    sys.exit()


def load_enemy_image(filename, size):
    img = image.load(join(IMAGE_PATH, filename)).convert_alpha()
    return pygame.transform.scale(img, size)

enemy_images = {
    "enemy1_1.png": {
        "points": "10 PTS",
        "color": (209, 43, 255),
        "size": (40, 30)
    },
    "enemy2_1.png": {
        "points": "20 PTS",
        "color": (0, 255, 240),
        "size": (45, 35)
    },
    "enemy3_1.png": {
        "points": "30 PTS",
        "color": (6, 253, 90),
        "size": (50, 40)
    },
    "mystery.png": {
        "points": "50 PTS",
        "color": (236, 28, 36),
        "size": (60, 30)
    }
}

y_start = int(SCREEN_HEIGHT * 0.7)
spacing = 45
x_img = int(SCREEN_WIDTH * 0.57)
x_text = int(SCREEN_WIDTH * 0.67)

for i, (key, data) in enumerate(enemy_images.items()):
    data["img"] = load_enemy_image(key, data["size"])
    data["pos"] = (x_img, y_start + i * spacing)
    data["text_pos"] = (x_text, y_start + i * spacing + 5)


# --- Loop principal del Menú ---
def main():
    running = True
    volume_level = load_volume()
    update_sound_volumes(volume_level)
    MENU_CHANNEL.set_volume(volume_level)
    VHS_MODE = load_vhs_mode()
    # Iniciar la música si no está sonando
    if not MENU_CHANNEL.get_busy():
        MENU_CHANNEL.play(SOUNDS['menu_music'], loops=-1)
    
    while running:
        SCREEN.blit(background_image, (0, 0))

        for star in stars:
            star.update()
            star.draw(SCREEN)

        title_pos = (SCREEN_WIDTH // 2 - 300, int(SCREEN_HEIGHT * 0.08))
        render_glow_text("Space Invaders", title_pos, TITLE_FONT, WHITE, (100, 100, 255))

        draw_text_button("Single Player", (SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.3), GREEN, BLUE, start_single_player)
        draw_text_button("Multiplayer", (SCREEN_WIDTH * 0.55, SCREEN_HEIGHT * 0.3), GREEN, BLUE, start_multiplayer)
        draw_text_button("P VS P", (SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.7), GREEN, BLUE, start_p_vs_p)
        draw_text_button("Exit", (SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.85), RED, PURPLE, exit_game)
        draw_text_button("Configuracion", (SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.85), GREEN, BLUE, start_settings)

        for data in enemy_images.values():
            SCREEN.blit(data["img"], data["pos"])
            text_surface = SMALL_FONT.render(data["points"], True, data["color"])
            SCREEN.blit(text_surface, data["text_pos"])

        for e in event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False

        single_ranking = single_load_ranking()
        start_y = int(SCREEN_HEIGHT * 0.45)
        colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]  # Oro, plata, bronce
        for i, player in enumerate(single_ranking):
            text = f"{i+1}. {player['name']} - {player['score']} pts"
            color = colors[i] if i < 3 else WHITE
            text_surface = font.Font(FONT_PATH + 'space_invaders.ttf', 18).render(text, True, color)
            SCREEN.blit(text_surface, (SCREEN_WIDTH * 0.05, start_y + i * 25))

        multi_ranking = multi_load_ranking()
        for i, player in enumerate(multi_ranking):
            text = f"{i+1}. {player['name']} - {player['score']} pts"
            color = colors[i] if i < 3 else WHITE
            text_surface = font.Font(FONT_PATH + 'space_invaders.ttf', 18).render(text, True, color)
            SCREEN.blit(text_surface, (SCREEN_WIDTH * 0.55, start_y + i * 25))

        mouse_pos = pygame.mouse.get_pos()
        cursor_rect = ship_cursor.get_rect(center=mouse_pos)
        SCREEN.blit(ship_cursor, cursor_rect.topleft)
        
        if VHS_MODE:
            apply_vhs_effect(SCREEN)
        
        display.update()
    
    MENU_CHANNEL.stop()
    pygame.quit()

if __name__ == "__main__":
    main()