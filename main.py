import argparse
import pygame

from background import Background
from game_state import (
    clear_inactive_obstacle,
    clear_inactive_power_up,
    create_initial_gamestate,
    GameOptions,
    handle_obstacle_collisions,
    handle_power_up_collection,
    RunState,
    SpecialEffect,
    spawn_obstacle,
    spawn_power_up,
    submit_answer,
)
from hud import Hud
from obstacle import Obstacle
from power_down import PowerDown
from power_up import PowerUp
from sonic import Sonic

SCREEN_WIDTH = 1600
HUD_HEIGHT = 280
SCENE_HEIGHT = 1000
SCREEN_HEIGHT = HUD_HEIGHT + SCENE_HEIGHT
HUD_BACKGROUND_COLOR = (18, 22, 32)
HUD_BORDER_COLOR = (60, 82, 120)
GAME_OVER_COLOR = (255, 110, 110)
GAME_OVER_SHADOW_COLOR = (20, 8, 8)
OVERLAY_DEFAULT_COLOR = (10, 16, 28, 190)
PAUSE_OVERLAY_COLOR = (8, 12, 22, 185)
ENDGAME_TITLE_COLOR = (255, 232, 130)
ENDGAME_TITLE_SHADOW = (52, 32, 0)
ENDGAME_TEXT_COLOR = (230, 239, 255)
ENDGAME_ACCENT_COLOR = (118, 198, 255)
PAUSE_TITLE_COLOR = (241, 246, 255)
PAUSE_TITLE_SHADOW = (24, 31, 48)
PAUSE_TEXT_COLOR = (188, 204, 232)
TARGET_FPS = 60
WINDOW_BACKGROUND_COLOR = (0, 0, 0)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-sound", action="store_true", help="disable music playback")
    parser.add_argument("--start-level", type=int, default=0, help="start the first run at this level")
    parser.add_argument("--start-hp", type=int, default=100, help="start the game with this many HP")
    parser.add_argument("--fullscreen", action="store_true", help="start in fullscreen mode")
    args = parser.parse_args()
    if not 0 <= args.start_level < 25:
        parser.error("--start-level must be between 0 and 24")
    if not 1 <= args.start_hp <= 100:
        parser.error("--start-hp must be between 1 and 100")
    return args


def draw_overlay(screen, title, title_color, title_shadow_color, body_lines=(), body_colors=(), overlay_color=OVERLAY_DEFAULT_COLOR):
    if not hasattr(draw_overlay, "title_font"):
        draw_overlay.title_font = pygame.font.SysFont(None, 132)
        draw_overlay.body_font = pygame.font.SysFont(None, 42)

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(overlay_color)
    screen.blit(overlay, (0, 0))

    title_surface = draw_overlay.title_font.render(title, True, title_color)
    title_shadow = draw_overlay.title_font.render(title, True, title_shadow_color)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 110))
    title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 - 106))
    screen.blit(title_shadow, title_shadow_rect)
    screen.blit(title_surface, title_rect)

    total_body_height = 0
    rendered_lines = []
    for index, line in enumerate(body_lines):
        color = body_colors[index] if index < len(body_colors) else ENDGAME_TEXT_COLOR
        line_surface = draw_overlay.body_font.render(line, True, color)
        rendered_lines.append(line_surface)
        total_body_height += line_surface.get_height()

    if rendered_lines:
        total_body_height += 22 * (len(rendered_lines) - 1)
        start_y = SCREEN_HEIGHT // 2 - total_body_height // 2 + 40
        for line_surface in rendered_lines:
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + line_surface.get_height() // 2))
            screen.blit(line_surface, line_rect)
            start_y += line_surface.get_height() + 22


def draw_game_over(screen):
    draw_overlay(screen, "GAME OVER", GAME_OVER_COLOR, GAME_OVER_SHADOW_COLOR)


def draw_endgame(screen, state):
    draw_overlay(
        screen,
        "LEVEL 25 CLEARED",
        ENDGAME_TITLE_COLOR,
        ENDGAME_TITLE_SHADOW,
        body_lines=(
            "Sonic made it to the finish line.",
            f"Final score: {state.score}",
            "Press Enter to play again",
        ),
        body_colors=(ENDGAME_TEXT_COLOR, ENDGAME_ACCENT_COLOR, ENDGAME_TEXT_COLOR),
    )


def draw_pause_menu(screen):
    draw_overlay(
        screen,
        "PAUSED",
        PAUSE_TITLE_COLOR,
        PAUSE_TITLE_SHADOW,
        body_lines=("Press ESC to resume",),
        body_colors=(PAUSE_TEXT_COLOR,),
        overlay_color=PAUSE_OVERLAY_COLOR,
    )


def reset_game(updatable, drawable, options):
    updatable.empty()
    drawable.empty()
    return create_initial_gamestate(SCREEN_WIDTH, SCENE_HEIGHT, HUD_HEIGHT, options)


def create_screen(fullscreen=False):
    flags = pygame.RESIZABLE
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    if fullscreen:
        flags |= pygame.FULLSCREEN
        size = (0, 0)

    try:
        return pygame.display.set_mode(size, flags=flags, vsync=1)
    except TypeError:
        return pygame.display.set_mode(size, flags=flags)


def present_screen(window, game_surface):
    window_width, window_height = window.get_size()
    scale = min(window_width / SCREEN_WIDTH, window_height / SCREEN_HEIGHT)
    scaled_width = round(SCREEN_WIDTH * scale)
    scaled_height = round(SCREEN_HEIGHT * scale)
    x = (window_width - scaled_width) // 2
    y = (window_height - scaled_height) // 2

    window.fill(WINDOW_BACKGROUND_COLOR)
    if scaled_width == SCREEN_WIDTH and scaled_height == SCREEN_HEIGHT:
        window.blit(game_surface, (x, y))
    else:
        scaled_surface = pygame.transform.scale(game_surface, (scaled_width, scaled_height))
        window.blit(scaled_surface, (x, y))


def main():
    args = parse_args()
    initial_options = GameOptions(
        sound_enabled=not args.no_sound,
        start_level=args.start_level,
        start_hp=args.start_hp,
    )
    restart_options = GameOptions(sound_enabled=not args.no_sound)

    print(f"Starting SonicMath with pygame version {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")
    pygame.init()
    pygame.key.set_repeat(200, 30)
    is_fullscreen = args.fullscreen
    window = create_screen(is_fullscreen)
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    Background.containers = (updatable, drawable)
    Obstacle.containers = (updatable, drawable)
    PowerDown.containers = (updatable, drawable)
    PowerUp.containers = (updatable, drawable)
    Sonic.containers = (updatable, drawable)

    hud = Hud(SCREEN_WIDTH, HUD_HEIGHT)
    state = reset_game(updatable, drawable, initial_options)

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick_busy_loop(TARGET_FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and state.run_state in {RunState.PLAYING, RunState.PAUSED}:
                    if state.run_state == RunState.PLAYING:
                        state.run_state = RunState.PAUSED
                        state.music_player.pause()
                    else:
                        state.run_state = RunState.PLAYING
                        state.music_player.unpause()
                    continue
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    window = create_screen(is_fullscreen)
                    continue

                if state.run_state == RunState.PAUSED:
                    continue

                if state.run_state != RunState.PLAYING:
                    if event.key == pygame.K_RETURN:
                        state = reset_game(updatable, drawable, restart_options)
                    continue
                if event.key == pygame.K_BACKSPACE:
                    state.answer_text = state.answer_text[:-1]
                elif event.key == pygame.K_RETURN:
                    submit_answer(state)
                elif event.unicode.isdigit():
                    state.answer_text += event.unicode

        if state.run_state == RunState.PLAYING:
            handle_obstacle_collisions(state)
            handle_power_up_collection(state)
            if state.background.did_wrap:
                spawn_obstacle(state, SCREEN_WIDTH)
            if state.background.did_mid_cycle:
                spawn_power_up(state, SCREEN_WIDTH)
            updatable.update(dt)
            clear_inactive_obstacle(state)
            clear_inactive_power_up(state)
        elif state.run_state in {RunState.GAME_OVER, RunState.ENDGAME} and not state.sonic.is_animation_complete():
            updatable.update(dt)
            clear_inactive_obstacle(state)
            clear_inactive_power_up(state)

        screen.fill(HUD_BACKGROUND_COLOR)
        hud.draw(screen, state)
        pygame.draw.line(screen, HUD_BORDER_COLOR, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 4)
        for d in drawable:
            if d is state.current_hazard and state.special_effect == SpecialEffect.VISUAL_DEBUFF:
                image = d.image.copy()
                image.set_alpha(90)
                screen.blit(image, d.rect)
                continue
            d.draw(screen)
        if state.run_state == RunState.GAME_OVER and state.sonic.is_animation_complete():
            draw_game_over(screen)
        elif state.run_state == RunState.ENDGAME and state.sonic.is_animation_complete():
            draw_endgame(screen, state)
        elif state.run_state == RunState.PAUSED:
            draw_pause_menu(screen)

        present_screen(window, screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
