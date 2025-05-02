import json
import os
import pygame
import sys
from pygame import display, event, font, image, mouse, mixer
from random import randint, uniform, choice
from os.path import abspath, dirname, join
import math

# --- Paths ---
BASE_PATH = abspath(dirname(__file__))
IMAGE_PATH = join(BASE_PATH, 'images/')
FONT_PATH = join(BASE_PATH, 'fonts/')
AUDIO_PATH = join(BASE_PATH, 'audio/')
SETTINGS_PATH = join(BASE_PATH, 'settings.json')


# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

# --- Initialize ---
pygame.init()
pygame.font.init()
pygame.mixer.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - Single Player")
CLOCK = pygame.time.Clock()

# Cargar y ajustar imagen de fondo
background_image = image.load(join(IMAGE_PATH, 'background.jpg')).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Canal exclusivo para la música de menú
MENU_CHANNEL = mixer.Channel(0)

# --- Load image utility ---
def load_image(name, scale=None):
    img = pygame.image.load(join(IMAGE_PATH, name)).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

# --- Load images ---
IMAGES = {
    'ship': load_image('ship.png'),
    'ship_2': load_image('ship_2.png'),
    'ship_hit': load_image('ship_hit.png'),
    'laser': load_image('laser.png'),
    'laser_purple': load_image('laser_purple.png'),
    'laser_blue': load_image('laser_blue.png'),
    'laser_green': load_image('laser_green.png'),
    'laser_2': load_image('laser_2.png'),
    'enemy1_1': load_image('enemy1_1.png'),
    'enemy1_2': load_image('enemy1_2.png'),
    'enemy2_1': load_image('enemy2_1.png'),
    'enemy2_2': load_image('enemy2_2.png'),
    'enemy3_1': load_image('enemy3_1.png'),
    'enemy3_2': load_image('enemy3_2.png'),
    'mystery': load_image('mystery.png'),
    'explosiongreen': load_image('explosionGreen.png'),
    'explosionblue': load_image('explosionBlue.png'),
    'explosionpurple': load_image('explosionPurple.png'),
    'explosionorange': load_image('explosionOrange.png'),
    'explosionred': load_image('explosionRed.png'),
    'logo_space_invaders' : load_image('logo_space_invaders.png'),
    'logo_python' : load_image('logo_python.png'),
}


def load_volume():
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            return settings.get('volume', 0.5)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0.5


def save_volume(volume_level):
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
        settings['volume'] = volume_level
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o tiene un error, creamos uno nuevo
        settings = {"volume": volume_level}
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=4)


def update_sound_volumes(new_volume):
    for name, sound in SOUNDS.items():
        base = BASE_VOLUMES.get(name, 1.0)
        sound.set_volume(base * new_volume)
    MENU_CHANNEL.set_volume(new_volume)
    save_volume(new_volume) 


BASE_VOLUMES = {
    'shoot':           0.15,
    'shoot2':          0.15,
    'invaderkilled':   0.15,
    'mysteryentered':  0.15,
    'mysterykilled':   0.15,
    'shipexplosion':   0.15,
    # música
    'menu_music':      0.6,
    'transition_music':0.6,
    'game_over':       0.6,
    'victory':         0.6,
    'game_music_1':    0.6,
    'game_music_2':    0.6,
    'game_music_3':    0.6,
    'game_music_4':    0.6,
    'game_music_5':    0.6,
    'game_music_6':    0.6,
    'game_music_7':    0.6,
}

volume_level = load_volume()  # De tu settings.json

SOUNDS = {}
for name, filename in {
    'shoot': 'shoot.wav',
    'shoot2': 'shoot2.wav',
    'invaderkilled': 'invaderkilled.wav',
    'mysteryentered': 'mysteryentered.wav',
    'mysterykilled': 'mysterykilled.wav',
    'shipexplosion': 'shipexplosion.wav',
    'menu_music': 'menu_music.ogg',
    'transition_music': 'transition_music.mp3',
    'game_over': 'game_over.mp3',
    'victory': 'victory.mp3',
    'game_music_1': 'game_music_1.mp3',
    'game_music_2': 'game_music_2.mp3',
    'game_music_3': 'game_music_3.mp3',
    'game_music_4': 'game_music_4.mp3',
    'game_music_5': 'game_music_5.mp3',
    'game_music_6': 'game_music_6.mp3',
    'game_music_7': 'game_music_7.mp3',
}.items():
    sound = pygame.mixer.Sound(join(AUDIO_PATH, filename))
    # volumen = base * escala desde settings.json
    base = BASE_VOLUMES.get(name, 1.0)
    sound.set_volume(base * volume_level)
    SOUNDS[name] = sound

# Ajusta también tu canal de menú, si usas uno:
MENU_CHANNEL.set_volume(volume_level)


ship_cursor = image.load(join(IMAGE_PATH, 'ship.png')).convert_alpha()
ship_cursor = pygame.transform.rotate(ship_cursor, 45)
ship_cursor = pygame.transform.scale(ship_cursor, (40, 40))

TITLE_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 64)
BUTTON_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 40)
FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 24)
SMALL_FONT = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 20)

# Cargar y ajustar imagen de fondo
background_image = image.load(join(IMAGE_PATH, 'background.jpg')).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

DEFAULT_CONTROLS_1 = {'shoot': 'UP', 'left': 'LEFT', 'right': 'RIGHT'}
DEFAULT_CONTROLS_2 = {'shoot': 'W', 'left': 'A', 'right': 'D'}



def mute_all():
    for i in range(1, 8):
        sound_key = f'game_music_{i}'
        if sound_key in SOUNDS:
            SOUNDS[sound_key].stop()


def play_music_for_level(level):
    mute_all()
    if level in [1, 2, 3, 4]:
        SOUNDS['game_music_2'].play(-1)
    elif level in [5, 6, 7, 8]:
        SOUNDS['game_music_3'].play(-1)
    elif level in [9, 10, 11, 12]:
        SOUNDS['game_music_4'].play(-1)
    elif level in [13, 14, 15, 16]:
        SOUNDS['game_music_5'].play(-1)
    elif level in [17, 18, 19]:
        SOUNDS['game_music_6'].play(-1)
    elif level in [20, 21, 22, 23]:
        SOUNDS['game_music_7'].play(-1)
    elif level >= 25:
        SOUNDS['game_music_1'].play(-1)
    else:
        SOUNDS['game_music_1'].play(-1)  # por defecto


# --- Función para cargar el ranking ---
SINGLE_RANKING_FILE = os.path.join(os.path.dirname(__file__), 'single_ranking.json')


def single_load_ranking():
    if os.path.exists(SINGLE_RANKING_FILE):
        with open(SINGLE_RANKING_FILE, 'r') as f:
            return json.load(f)
    return []


def single_save_score(name, score):
    single_ranking = single_load_ranking()
    single_ranking.append({'name': name, 'score': score})
    single_ranking = sorted(single_ranking, key=lambda x: x['score'], reverse=True)[:5]  # Top 5
    with open(SINGLE_RANKING_FILE, 'w') as f:
        json.dump(single_ranking, f)


# --- Función para cargar el ranking ---
MULTI_RANKING_FILE = os.path.join(os.path.dirname(__file__), 'multi_ranking.json')


def multi_load_ranking():
    if os.path.exists(MULTI_RANKING_FILE):
        with open(MULTI_RANKING_FILE, 'r') as f:
            return json.load(f)
    return []


def multi_save_score(name, score):
    multi_ranking = multi_load_ranking()
    multi_ranking.append({'name': name, 'score': score})
    multi_ranking = sorted(multi_ranking, key=lambda x: x['score'], reverse=True)[:5]  # Top 5
    with open(MULTI_RANKING_FILE, 'w') as f:
        json.dump(multi_ranking, f)


LEVEL_PATTERNS = [
    [
        '  111111  ',
        '  222222  ',
        '3333333333',
    ],
    [
        '  222222  ',
        '  111111  ',
        '3333333333',
        '   2222   ',
    ],
    [
        '1111111111',
        '  222222  ',
        '   3333   ',
    ],
    [
        '   1111   ',
        ' 22222222 ',
        '  333333  ',
        '   1111   ',
    ],
    [
        '    1     ',
        '   222    ',
        '  33333   ',
        ' 2222222  ',
    ],
    [
        '1 1 1 1 1 ',
        ' 2 2 2 2 2',
        ' 33333333',
    ],
    [
        '1111111111',
        '2222222222',
        '3333333333',
    ],
    [
        '1 3 3 3 1 ',
        '3 1 2 1 3',
        '2 3 1 3 2',
    ],
    [
        '1 1 1 1 1 ',
        '2 2 2 2 2 ',
        '3 3 3 3 3 ',
        '1 2 3 2 1 ',
    ],
    [
        '    111   ',
        '  2222222 ',
        ' 333333333',
        '    111   ',
    ],
    [
        '1 2 3 2 1 ',
        '3 2 1 2 3 ',
        '1 2 3 2 1 ',
        '3 2 1 2 3 ',
    ],
    [
        '1   1  333 ',
        ' 1 1   3  3',
        '  1    3  3',
        ' 1 1   3  3',
        '1   1  333 ',
    ],
    [
        '1111111111',
        '   2222   ',
        '3333333333',
        '   2222   ',
    ],
    [
        '1 3 1 3 1 ',
        '2 2 2 2 2 ',
        '3 1 3 1 3 ',
    ],
    [
        ' 1 2 3 1 2',
        '3 1 2 3 1 ',
        ' 2 3 1 2 3',
    ],
    [
        '1         ',
        ' 2        ',
        '  3       ',
        '   2      ',
        '    1     ',
    ],
    [
        '111   111 ',
        '222   222 ',
        '333   333 ',
    ],
    [
        '     222 ',
        '   2    2',
        '      22 ',
        '   2    2',
        '     222 ',
    ],
    [
        '1 1 1 1 1 ',
        ' 2 2 2 2 2',
        '  3 3 3 3 ',
        '   1 1 1  ',
    ],
    [
        '    1     ',
        '   222    ',
        '  33333   ',
        '   222    ',
        '    1     ',
    ],
    [
        ' 12321 ',
        '1223221',
        ' 12321 ',
    ],
    [
        '111  3  111 ',
        '222  3  222 ',
        '111  3  111 ',
    ],
    [ 
        '3 3 3 3 3 ',
        '2 2 2 2 2 ',
        '1 1 1 1 1 ',
        '2 2 2 2 2 ',
        '3 3 3 3 3 ',
    ],
    [
        '1111111111',
        '   2222   ',
        '   3333   ',
        '   2222   ',
        '1111111111',
    ],
    [
        '1111331111',
        '  222222  ',
        '   3333   ',          #GG bruh
        '  222222  ',
        '1111331111',
    ],
]


# --- Player class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, constraint, speed, screen_height, controls, player_id):
        super().__init__()

        # Asignación de imagen según player_id
        if player_id == 1:
            self.normal_image = IMAGES['ship']
            self.hit_image = IMAGES.get('ship_hit', IMAGES['ship'])
        elif player_id == 2:
            self.normal_image = IMAGES['ship_2']
            self.hit_image = IMAGES.get('ship_hit', IMAGES['ship_2'])
        elif player_id == -2:
            self.normal_image = pygame.transform.rotate(IMAGES['ship_2'], 180)
            self.hit_image = pygame.transform.rotate(IMAGES.get('ship_hit', IMAGES['ship_2']), 180)
        else:
            self.normal_image = IMAGES['ship']
            self.hit_image = IMAGES.get('ship_hit', IMAGES['ship'])

        self.image = self.normal_image
        self.hit_timer = 0
        self.hit_duration = 300
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = speed
        self.max_x_constraint = constraint
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600
        self.lasers = pygame.sprite.Group()
        self.screen_height = screen_height
        self.laser_sound = SOUNDS['shoot']
        self.controls = controls
        self.player_id = player_id
        self.score = 0
        self.lives = 3
        self.is_alive = True

    def get_input(self):
        if not self.is_alive:
            return
        keys = pygame.key.get_pressed()
        if self.controls['right'] and keys[self.controls['right']]:
            self.rect.x += self.speed
        if self.controls['left'] and keys[self.controls['left']]:
            self.rect.x -= self.speed
        if self.controls['shoot'] and keys[self.controls['shoot']] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    def shoot_laser(self):
        if self.player_id == 1:
            direction = -8
            source = 'player1'
        elif self.player_id == 2:
            direction = -8
            source = 'player2'
        elif self.player_id == -2:
            direction = 8
            source = 'player2vs'
        else:
            direction = -8
            source = f'player{self.player_id}'
        self.lasers.add(Laser(self.rect.center, direction, self.screen_height, source=source))

    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint

    def take_damage(self):
        if self.lives > 0:
            self.lives -= 1
            self.image = self.hit_image
            self.hit_timer = pygame.time.get_ticks()
            SOUNDS['shipexplosion'].play()
        if self.lives <= 0:
            self.die()

    def update_hit_state(self):
        if self.hit_timer and pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
            self.image = self.normal_image
            self.hit_timer = 0

    def update(self):
        if not self.is_alive:
            return
        self.get_input()
        self.constraint()
        self.recharge()
        self.update_hit_state()
        self.lasers.update()

    def die(self):
        self.is_alive = False
        explosion_image_key = 'explosiongreen' if self.player_id == 1 else 'explosionorange'
        self.image = IMAGES[explosion_image_key]
        self.rect = self.image.get_rect(center=self.rect.center)
        SOUNDS['shipexplosion'].play()
        pygame.time.wait(500)
        self.lasers.empty()


# --- Alien class ---
class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        # Definir las imágenes de animación para cada tipo de enemigo
        self.animations = {
            '1': [IMAGES['enemy1_1'], IMAGES['enemy1_2']],
            '2': [IMAGES['enemy2_1'], IMAGES['enemy2_2']],
            '3': [IMAGES['enemy3_1'], IMAGES['enemy3_2']],
        }
        self.image = self.animations[color][0]  # Empezamos con la primera imagen
        self.rect = self.image.get_rect(topleft=(x, y))
        self.value = {'1': 10, '2': 20, '3': 30}[color]
        self.color = color  # Guardamos el color para seleccionar la animación correcta
        self.animation_timer = 0  # Temporizador para alternar la imagen
        self.animation_speed = 500  # Cada cuántos milisegundos cambiar la imagen (500 ms)
    
    def update(self, direction):
        # Actualizamos el temporizador
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_speed:
            # Alternamos entre las dos imágenes
            current_image_index = self.animations[self.color].index(self.image)
            next_image_index = (current_image_index + 1) % 2
            self.image = self.animations[self.color][next_image_index]
            self.animation_timer = current_time  # Reiniciamos el temporizador
        
        self.rect.x += direction


alien_lasers = pygame.sprite.Group()


# --- Extra (mystery ship) class ---
class Extra(pygame.sprite.Sprite):
    def __init__(self, side, screen_width):
        super().__init__()
        self.image = IMAGES['mystery']
        self.speed = -3 if side == 'right' else 3
        x = screen_width + 50 if side == 'right' else -50
        self.rect = self.image.get_rect(topleft=(x, 80))

    def update(self):
        self.rect.x += self.speed


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.images = {
            '1': [IMAGES['explosionpurple']],
            '2': [IMAGES['explosionblue']],
            '3': [IMAGES['explosiongreen']],
            'extra': [IMAGES['explosionred']],
        }
        self.image = self.images[enemy_type][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.life_time = 500  # Duración de la explosión en milisegundos
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.life_time:
            self.kill()


# --- Laser class ---
class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_height, source='player1'):
        super().__init__()
        if source == 'player1':
            self.image = IMAGES['laser']
        elif source == 'player2':
            self.image = IMAGES['laser_2']
        elif source == 'player2vs':
            self.image = pygame.transform.rotate(IMAGES['laser_2'], 180)
        elif source == 'enemy1':
            self.image = IMAGES['laser_purple']
        elif source == 'enemy2':
            self.image = IMAGES['laser_blue']
        elif source == 'enemy3':
            self.image = IMAGES['laser_green']
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.height_y_constraint = screen_height

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_y_constraint + 50:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()


def create_aliens(level_pattern):
    aliens = pygame.sprite.Group()
    cols = max(len(row) for row in level_pattern)
    total_width = cols * 60
    start_x = (SCREEN_WIDTH - total_width) // 2
    for row_index, row in enumerate(level_pattern):
        for col_index, char in enumerate(row):
            if char in '123':
                x = start_x + col_index * 60
                y = 100 + row_index * 60
                aliens.add(Alien(char, x, y))
    return aliens


def alien_shoot(aliens, enemy_lasers, screen_height, sound):
    if aliens:
        random_alien = choice(aliens.sprites())
        source = f'enemy{random_alien.color}'
        laser = Laser(random_alien.rect.center, 6, screen_height, source=source)
        enemy_lasers.add(laser)
        sound.play()


# --- Block class ---
class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Create block pattern ---
def create_block_pattern(x_offset, y_offset, size, color, flip_vertical=False):
    shape = [
        '     x     ',
        '    xxx    ',
        '  xxxxxxx  ',
        ' xxxxxxxxx ',
        'xxxxxxxxxxx',
        'xxxxxxxxxxx',
        'xxxxxxxxxxx',
        'xxx     xxx',
        'xx       xx'
    ]
    if flip_vertical:
        shape = shape[::-1]  # invierte el patrón verticalmente

    blocks = pygame.sprite.Group()
    for row_idx, row in enumerate(shape):
        for col_idx, char in enumerate(row):
            if char == 'x':
                x = x_offset + col_idx * size
                y = y_offset + row_idx * size
                blocks.add(Block(size, color, x, y))
    return blocks


def draw_volume_slider(SCREEN, volume_level, FONT, SMALL_FONT):
    bar_x = SCREEN.get_width() * 0.235
    bar_y = SCREEN.get_height() * 0.8
    bar_width = SCREEN.get_width() * 0.3
    bar_height = 10
    handle_radius = 11
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    adjusting_volume = False

    if mouse_click[0] and (bar_y - handle_radius) <= mouse_pos[1] <= (bar_y + bar_height + handle_radius):
        adjusting_volume = True
        relative_x = max(bar_x, min(mouse_pos[0], bar_x + bar_width))
        volume_level = (relative_x - bar_x) / bar_width
        volume_level = max(0.0, min(1.0, volume_level))
        save_volume(volume_level)
        update_sound_volumes(volume_level)

    # Dibujar barra
    pygame.draw.rect(SCREEN, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(SCREEN, (0, 255, 0), (bar_x, bar_y, bar_width * volume_level, bar_height))
    handle_x = bar_x + bar_width * volume_level
    pygame.draw.circle(SCREEN, (255, 255, 255), (int(handle_x), int(bar_y + bar_height / 2)), handle_radius)

    # Texto
    render_glow_text("Volumen", (int(bar_x - 140), int(bar_y - 10)), SMALL_FONT, GREEN, (40, 40, 40))
    percent_text = f"{int(volume_level * 100)}%"
    render_glow_text(percent_text, (int(bar_x + bar_width + 20), int(bar_y - 10)), SMALL_FONT, GREEN, (40, 40, 40))

    return volume_level, adjusting_volume


def draw_text_button(text, pos, default_color, hover_color, action=None):
    mouse_pos = mouse.get_pos()
    mouse_click = mouse.get_pressed()

    text_surface = BUTTON_FONT.render(text, True, default_color)
    rect = text_surface.get_rect(topleft=pos)
    is_hovered = rect.collidepoint(mouse_pos)

    if is_hovered and mouse_click[0] and action:
        action()

    inner_color = hover_color if is_hovered else default_color
    render_glow_text(text, pos, BUTTON_FONT, inner_color, (40, 40, 40))


def render_glow_text(text, pos, font_obj, base_color, glow_color):
    for offset in range(1, 5):
        glow_surface = font_obj.render(text, True, glow_color)
        SCREEN.blit(glow_surface, (pos[0] - offset, pos[1] - offset))
        SCREEN.blit(glow_surface, (pos[0] + offset, pos[1] + offset))
        SCREEN.blit(glow_surface, (pos[0] - offset, pos[1] + offset))
        SCREEN.blit(glow_surface, (pos[0] + offset, pos[1] - offset))
    SCREEN.blit(font_obj.render(text, True, base_color), pos)


def draw_cursor(SCREEN, cursor_image):
    mouse_pos = pygame.mouse.get_pos()
    cursor_rect = cursor_image.get_rect(center=mouse_pos)
    SCREEN.blit(cursor_image, cursor_rect.topleft)


def load_controls(player=1):
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            return settings.get(f'controls_player_{player}',
                                 DEFAULT_CONTROLS_1 if player == 1 else DEFAULT_CONTROLS_2)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONTROLS_1 if player == 1 else DEFAULT_CONTROLS_2


def save_controls(controls, player=1):
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    settings[f'controls_player_{player}'] = controls
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)


def string_to_key(key_str):
    key_str = key_str.upper()
    special_keys = {
        'UP': pygame.K_UP,
        'DOWN': pygame.K_DOWN,
        'LEFT': pygame.K_LEFT,
        'RIGHT': pygame.K_RIGHT,
        'SPACE': pygame.K_SPACE,
        'RETURN': pygame.K_RETURN,
        'ESCAPE': pygame.K_ESCAPE,
        'TAB': pygame.K_TAB,
        'SHIFT': pygame.K_LSHIFT,
        'CTRL': pygame.K_LCTRL,
        'ALT': pygame.K_LALT,
    }
    if key_str in special_keys:
        return special_keys[key_str]
    try:
        return getattr(pygame, f'K_{key_str.lower()}')
    except AttributeError:
        print(f"[Advertencia] Tecla desconocida: '{key_str}'")
        return None


def load_controls_from_settings():
    try:
        with open(SETTINGS_PATH, 'r') as f:
            updated_settings = json.load(f)

        controls_p1_json = updated_settings.get("controls_player_1", {})
        controls_p2_json = updated_settings.get("controls_player_2", {})

        controls_p1 = {
            'left':  string_to_key(controls_p1_json.get("left", "LEFT")),
            'right': string_to_key(controls_p1_json.get("right", "RIGHT")),
            'shoot': string_to_key(controls_p1_json.get("shoot", "SPACE"))
        }
        controls_p2 = {
            'left':  string_to_key(controls_p2_json.get("left", "A")),
            'right': string_to_key(controls_p2_json.get("right", "D")),
            'shoot': string_to_key(controls_p2_json.get("shoot", "W"))
        }

        return controls_p1, controls_p2

    except Exception as e:
        print(f"[Error] Al cargar controles: {e}")
        return (
            {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'shoot': pygame.K_SPACE},
            {'left': pygame.K_a, 'right': pygame.K_d, 'shoot': pygame.K_w}
        )


# --- Función del menú de configuración ---
def open_settings_menu(player_names=("Jugador 1", "Jugador 2")):
    volume_level = load_volume()
    update_sound_volumes(volume_level)
    DEFAULT_CONTROLS = {
        1: {'shoot': 'UP', 'left': 'LEFT', 'right': 'RIGHT'},
        2: {'shoot': 'W', 'left': 'A', 'right': 'D'}
    }
    running = True
    current_changing = None
    keys_list = ['shoot', 'left', 'right']
    dragging_volume = False
    volume_cooldown = 0
    volume_timer = 0
    VHS_MODE = load_vhs_mode()
    last_vhs_toggle_time = 0
    
    def in_volume_mode():
        return dragging_volume or pygame.time.get_ticks() < volume_cooldown

    while running:
        SCREEN.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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

        if dragging_volume and pygame.time.get_ticks() - volume_timer > 1000:
            dragging_volume = False

        bar_x = SCREEN.get_width() * 0.235
        bar_y = SCREEN.get_height() * 0.8
        bar_width = SCREEN.get_width() * 0.3
        bar_height = 10
        handle_radius = 11

        if mouse_click[0] and not dragging_volume:
            if (bar_y - handle_radius) <= mouse_pos[1] <= (bar_y + bar_height + handle_radius):
                dragging_volume = True
                volume_timer = pygame.time.get_ticks()
                current_changing = None

        if dragging_volume and mouse_click[0]:
            relative_x = max(bar_x, min(mouse_pos[0], bar_x + bar_width))
            volume_level = (relative_x - bar_x) / bar_width
            volume_level = max(0.0, min(1.0, volume_level))
            save_volume(volume_level)
            update_sound_volumes(volume_level)
            volume_timer = pygame.time.get_ticks()

        for player_idx, x_offset in enumerate([0.06, 0.65], start=1):
            controls = load_controls(player=player_idx)
            name_display = player_names[player_idx - 1] if player_idx <= len(player_names) else f"Player {player_idx}"
            render_glow_text(f"Controles {name_display}",
                             (SCREEN_WIDTH * x_offset, SCREEN_HEIGHT * 0.2),
                             SMALL_FONT, GREEN, (40, 40, 40))

            for i, key in enumerate(keys_list):
                action_text = f"{key.capitalize()}: {controls[key]}"
                pos = (SCREEN_WIDTH * x_offset, SCREEN_HEIGHT * (0.4 + 0.1 * i))
                rect = pygame.Rect(pos[0], pos[1], 300, 40)
                hovered = rect.collidepoint(mouse_pos)
                if in_volume_mode():
                    render_glow_text(action_text, pos, SMALL_FONT, (0, 0, 0), (40, 40, 40))
                else:
                    color = PURPLE if hovered else BLUE
                    render_glow_text(action_text, pos, SMALL_FONT, color, (40, 40, 40))
                    if hovered and mouse_click[0]:
                        current_changing = (player_idx, i)

        if current_changing and not in_volume_mode():
            p, idx = current_changing
            render_glow_text(
                f"Presiona nueva tecla para Player {p} ({keys_list[idx]})",
                (SCREEN_WIDTH * 0.06, SCREEN_HEIGHT * 0.7),
                SMALL_FONT, RED, (40, 40, 40))

        for p, x_offset in [(1, 0.06), (2, 0.65)]:
            reset_pos = (SCREEN_WIDTH * x_offset, SCREEN_HEIGHT * 0.3)
            rect = pygame.Rect(reset_pos[0], reset_pos[1], 250, 40)
            hovered = rect.collidepoint(mouse_pos)
            color = (0, 0, 0) if in_volume_mode() else (PURPLE if hovered else RED)
            render_glow_text(f"Restablecer P{p}", reset_pos, SMALL_FONT, color, (40, 40, 40))
            if hovered and mouse_click[0] and not in_volume_mode():
                save_controls(DEFAULT_CONTROLS[p], player=p)
                current_changing = None

        draw_volume_slider(SCREEN, volume_level, FONT, FONT)

        def set_running_false():
            nonlocal running
            running = False

        back_pos = (SCREEN_WIDTH * 0.425, SCREEN_HEIGHT * 0.9)
        if not in_volume_mode():
            draw_text_button("Back", back_pos, RED, PURPLE, action=set_running_false)
        else:
            render_glow_text("Back", back_pos, BUTTON_FONT, (0, 0, 0), (40, 40, 40))
        
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


# Variables persistentes globales
vhs_offset = 0
vhs_alpha_pulse = 0
color_shift_phase = 0

def apply_vhs_effect(surface):
    global vhs_offset, vhs_alpha_pulse, color_shift_phase

    width, height = surface.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)

    line_height = 2
    spacing = 5

    # Parpadeo de opacidad
    alpha = 40 + int(10 * math.sin(vhs_alpha_pulse))
    vhs_alpha_pulse += 0.1

    # Líneas negras horizontales (bajando lentamente)
    for i, y in enumerate(range(0, height, spacing)):
        x_offset = int(2 * math.sin(pygame.time.get_ticks() * 0.002 + i))
        y_offset = (y + int(vhs_offset)) % height
        pygame.draw.rect(overlay, (0, 0, 0, alpha), (x_offset, y_offset, width, line_height))

    # Más puntos negros (ruido estático)
    for _ in range(60):  # Aumentado
        x = randint(0, width - 1)
        y = randint(0, height - 1)
        overlay.set_at((x, y), (0, 0, 0, randint(100, 255)))

    # Glitches blancos en bordes
    if randint(0, 30) < 3:
        border_glitch_width = randint(2, 5)
        border_color = (255, 255, 255, randint(30, 80))
        pygame.draw.rect(overlay, border_color, (0, 0, width, border_glitch_width))  # Top
        pygame.draw.rect(overlay, border_color, (0, height - border_glitch_width, width, border_glitch_width))  # Bottom

    # Glitch de barra de color ocasional
    if randint(0, 25) < 2:
        glitch_bar_y = randint(0, height - 10)
        glitch_color = (randint(100, 255), randint(0, 100), randint(0, 100), 40)
        pygame.draw.rect(overlay, glitch_color, (0, glitch_bar_y, width, 4))

    # Ruido blanco horizontal (como interferencia breve)
    if randint(0, 20) < 2:
        for _ in range(5):
            y = randint(0, height)
            pygame.draw.line(overlay, (200, 200, 255, randint(30, 60)), (0, y), (width, y))

    # RGB Split: desplazamiento de canales de color
    r = surface.copy()
    g = surface.copy()
    b = surface.copy()

    color_shift_amount = int(0.5 + 0.8 * math.sin(color_shift_phase))
    color_shift_phase += 0.2

    r.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
    g.fill((0, 255, 0), special_flags=pygame.BLEND_MULT)
    b.fill((0, 0, 255), special_flags=pygame.BLEND_MULT)

    surface.blit(r, (-color_shift_amount, 0), special_flags=pygame.BLEND_ADD)
    surface.blit(g, (0, 0), special_flags=pygame.BLEND_ADD)
    surface.blit(b, (color_shift_amount, 0), special_flags=pygame.BLEND_ADD)

    # Barrido senoidal (ligero desplazamiento horizontal)
    for y in range(height):
        shift = int(2 * math.sin(y * 0.04 + pygame.time.get_ticks() * 0.005))
        surface.blit(surface, (shift, y), area=pygame.Rect(0, y, width, 1))

    # Combinar todo
    surface.blit(overlay, (0, 0))

    # Movimiento vertical de líneas negras
    vhs_offset += 0.2
    if vhs_offset >= spacing:
        vhs_offset = 0


def load_vhs_mode():
    with open(SETTINGS_PATH, 'r') as f:
        data = json.load(f)
    return data.get("vhs_mode", False)


def save_vhs_mode(value: bool):
    with open(SETTINGS_PATH, 'r+') as f:
        data = json.load(f)
        data["vhs_mode"] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

last_vhs_toggle_time = 0
def draw_vhs_toggle_button(screen, font, mouse_pos, mouse_click, vhs_mode, in_volume_mode, last_toggle_time):
    
    toggle_text = f"Modo VHS: {'ON' if vhs_mode else 'OFF'}"
    button_pos = (SCREEN_WIDTH * 0.42, SCREEN_HEIGHT * 0.2)
    rect = pygame.Rect(button_pos[0], button_pos[1], 300, 40)
    hovered = rect.collidepoint(mouse_pos)
    color = (0, 0, 0) if in_volume_mode else (GREEN if vhs_mode else RED)

    render_glow_text(toggle_text, button_pos, font, color, (40, 40, 40))

    current_time = pygame.time.get_ticks()
    if hovered and mouse_click[0] and not in_volume_mode:
        if current_time - last_toggle_time > 300:
            return not vhs_mode, current_time
    return vhs_mode, last_toggle_time