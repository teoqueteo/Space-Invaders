import pygame
import sys
import os
from os.path import abspath, dirname, join
from game_objects import apply_vhs_effect


# --- Rutas ---
BASE_PATH = abspath(dirname(__file__))
IMAGE_PATH = join(BASE_PATH, 'images/')
FONT_PATH = join(BASE_PATH, 'fonts/')
AUDIO_PATH = join(BASE_PATH, 'audio/')
SETTINGS_PATH = join(BASE_PATH, 'settings.json')

# --- Inicialización de Pygame ---
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)

# --- Fuente principal ---
FONT = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 24)

# --- Configuración de pantalla completa ---
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders - Intro")

# --- Reloj para controlar los FPS ---
CLOCK = pygame.time.Clock()

# --- Colores ---
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
GRIS = (70, 70, 70)


# --- Animación de introducción ---
def play_intro_animation(
    logo_filename,
    final_size,
    intro_text,
    text_font_size=36,
    text_delay=1500,
    final_pause=False,
):
    clock = pygame.time.Clock()

    try:
        logo_path = os.path.join(IMAGE_PATH, logo_filename)
        original_logo = pygame.image.load(logo_path).convert_alpha()
    except pygame.error:
        print(f"No se pudo cargar la imagen '{logo_filename}', se usará texto.")
        original_logo = None

    text_font = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', text_font_size)

    max_scale = 2.0
    final_width, final_height = final_size

    animation_duration = 1500
    scaling_duration = 300
    text_slide_duration = 200

    shockwave_color = (255, 255, 255, 255)
    shockwave_max_radius = 400
    shockwave_speed = 800
    shockwave_width = 8

    start_time = pygame.time.get_ticks()
    shockwave_active = False
    shockwave_start_time = 0
    animating = True

    while animating:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time

        if elapsed >= animation_duration + 1000:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                animating = False

        SCREEN.fill(NEGRO)

        if elapsed < scaling_duration:
            scale_factor = max_scale - ((max_scale - 1.0) * (elapsed / scaling_duration))
            current_width = int(final_width * scale_factor)
            current_height = int(final_height * scale_factor)
            if not shockwave_active and abs(scale_factor - 1.0) < 0.01:
                shockwave_active = True
                shockwave_start_time = current_time
        else:
            current_width, current_height = final_width, final_height
            if not shockwave_active and elapsed < scaling_duration + 50:
                shockwave_active = True
                shockwave_start_time = current_time

        if shockwave_active:
            shockwave_elapsed = current_time - shockwave_start_time
            radius = (shockwave_speed * shockwave_elapsed) / 1000
            if 0 < radius < shockwave_max_radius:
                alpha = int(shockwave_color[3] * (1 - radius / shockwave_max_radius))
                color = (*shockwave_color[:3], alpha)
                wave_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(wave_surface, color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(radius), shockwave_width)
                SCREEN.blit(wave_surface, (0, 0))

        if original_logo:
            logo = pygame.transform.scale(original_logo, (current_width, current_height))
            logo_x = SCREEN_WIDTH // 2 - current_width // 2
            logo_y = SCREEN_HEIGHT // 2 - current_height // 2
            SCREEN.blit(logo, (logo_x, logo_y))
        else:
            fallback_text = text_font.render("SPACE INVADERS", True, VERDE)
            logo_x = SCREEN_WIDTH // 2 - fallback_text.get_width() // 2
            logo_y = SCREEN_HEIGHT // 2 - fallback_text.get_height() // 2
            SCREEN.blit(fallback_text, (logo_x, logo_y))

        if elapsed >= text_delay:
            text_progress = min(1.0, (elapsed - text_delay) / text_slide_duration)
            text_render = text_font.render(intro_text, True, BLANCO)
            start_x = SCREEN_WIDTH + 50
            final_x = SCREEN_WIDTH // 2 - text_render.get_width() // 2
            text_x = start_x - ((start_x - final_x) * text_progress)
            text_y = logo_y + final_height + 20
            SCREEN.blit(text_render, (text_x, text_y))

        draw_press_any_key()
        draw_credits()

            
        apply_vhs_effect(SCREEN)
        pygame.display.update()
        clock.tick(60)

    # Pausa de 0.5s con logo y texto visibles + VHS activo
    pause_start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - pause_start < 500:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill(NEGRO)

        if original_logo:
            logo = pygame.transform.scale(original_logo, (final_width, final_height))
            logo_x = SCREEN_WIDTH // 2 - final_width // 2
            logo_y = SCREEN_HEIGHT // 2 - final_height // 2
            SCREEN.blit(logo, (logo_x, logo_y))
        else:
            fallback_text = text_font.render("SPACE INVADERS", True, VERDE)
            logo_x = SCREEN_WIDTH // 2 - fallback_text.get_width() // 2
            logo_y = SCREEN_HEIGHT // 2 - fallback_text.get_height() // 2
            SCREEN.blit(fallback_text, (logo_x, logo_y))

        text_render = text_font.render(intro_text, True, BLANCO)
        text_x = SCREEN_WIDTH // 2 - text_render.get_width() // 2
        text_y = logo_y + final_height + 20
        SCREEN.blit(text_render, (text_x, text_y))

        apply_vhs_effect(SCREEN)
        pygame.display.update()
        clock.tick(60)

    # Pausa final con pantalla negra (si está activado)
    if final_pause:
        black_pause_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - black_pause_start < 400:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            SCREEN.fill(NEGRO)
            apply_vhs_effect(SCREEN)
            pygame.display.update()
            clock.tick(60)


def draw_loading_bar():
    loading_width = SCREEN_WIDTH * 0.6
    loading_height = 20
    loading_x = SCREEN_WIDTH // 2 - loading_width // 2
    loading_y = SCREEN_HEIGHT // 2

    progress = 0.0
    clock = pygame.time.Clock()

    # Mostrar "LOADING..." antes de la barra
    loading_text_font = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 36)
    loading_text = loading_text_font.render("LOADING...", True, BLANCO)
    text_x = SCREEN_WIDTH // 2 - loading_text.get_width() // 2
    text_y = loading_y - 40
    SCREEN.blit(loading_text, (text_x, text_y))

    pygame.display.update()
    pygame.time.delay(500)  # Esperar un poco antes de empezar

    while progress < 1.0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill(NEGRO)

        # Marco de la barra
        pygame.draw.rect(SCREEN, (100, 100, 100), (loading_x, loading_y, loading_width, loading_height), 2)

        # Barra interna (progreso falso con random)
        segment_width = loading_width * progress
        pygame.draw.rect(SCREEN, BLANCO, (loading_x, loading_y, segment_width, loading_height))

        apply_vhs_effect(SCREEN)
        pygame.display.update()
        CLOCK.tick(60)

        progress += 0.01 + 0.01 * (pygame.time.get_ticks() % 3)
        pygame.time.delay(30)


def draw_press_any_key():
    font = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 18)
    text = font.render("Presiona cualquier tecla para saltar", True, GRIS)
    text_x = SCREEN_WIDTH - text.get_width() - 20
    text_y = SCREEN_HEIGHT - text.get_height() - 15
    alpha = (pygame.time.get_ticks() // 500) % 2 * 255  # Intermitente

    text.set_alpha(alpha)
    SCREEN.blit(text, (text_x, text_y))


def draw_credits():
    font = pygame.font.Font(FONT_PATH + 'space_invaders.ttf', 18)
    credits = font.render("© 1980 INVADER CORP", True, BLANCO)
    text_x = SCREEN_WIDTH - credits.get_width() - 20
    text_y = SCREEN_HEIGHT - credits.get_height() - 50

    SCREEN.blit(credits, (text_x, text_y))


# --- Loop principal de introducción ---
def main():

    VHS_MODE = True

    if VHS_MODE:
        # Intro principal
        play_intro_animation("logo_space_invaders.png", (300, 300), "SPACE INVADERS")

        # Intro secundaria
        play_intro_animation("logo_python.png", (300, 300), "MADE WITH PYTHON", final_pause=True)

        # Mostrar barra de carga con efecto random
        draw_loading_bar()

        # Ejecutar menú principal después de la barra de carga
        import main_menu
        main_menu.main()


    # Aquí comienza el juego o menú principal
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        SCREEN.fill((0, 0, 0))
        if VHS_MODE:
            apply_vhs_effect(SCREEN)

        draw_press_any_key()
        draw_credits()

        pygame.display.update()
        CLOCK.tick(60)

    pygame.quit()
    sys.exit()


def run_game():
    main()

if __name__ == "__main__":
    main()
