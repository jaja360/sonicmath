import argparse

import pygame

from background import Background
from game_state import (
    clear_inactive_obstacle,
    create_initial_gamestate,
    GameOptions,
    handle_obstacle_collisions,
    RunState,
    spawn_obstacle,
    submit_answer,
)
from hud import Hud
from obstacle import Obstacle
from sonic import Sonic

SCREEN_WIDTH = 1600
HUD_HEIGHT = 240
SCENE_HEIGHT = 1000
SCREEN_HEIGHT = HUD_HEIGHT + SCENE_HEIGHT
HUD_BACKGROUND_COLOR = (18, 22, 32)
HUD_BORDER_COLOR = (60, 82, 120)
GAME_OVER_COLOR = (255, 110, 110)
GAME_OVER_SHADOW_COLOR = (20, 8, 8)
ENDGAME_OVERLAY_COLOR = (10, 16, 28, 190)
ENDGAME_TITLE_COLOR = (255, 232, 130)
ENDGAME_TITLE_SHADOW = (52, 32, 0)
ENDGAME_TEXT_COLOR = (230, 239, 255)
ENDGAME_ACCENT_COLOR = (118, 198, 255)
MAX_START_LEVEL = 24


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-sound", action="store_true", help="disable music playback")
    parser.add_argument("--start-level", type=int, default=0, help="start the first run at this level")
    args = parser.parse_args()
    if not 0 <= args.start_level <= MAX_START_LEVEL:
        parser.error(f"--start-level must be between 0 and {MAX_START_LEVEL}")
    return args


def draw_game_over(screen):
    if not hasattr(draw_game_over, "font"):
        draw_game_over.font = pygame.font.SysFont(None, 140)
    text = draw_game_over.font.render("GAME OVER", True, GAME_OVER_COLOR)
    shadow = draw_game_over.font.render("GAME OVER", True, GAME_OVER_SHADOW_COLOR)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 + 4))
    screen.blit(shadow, shadow_rect)
    screen.blit(text, text_rect)


def draw_endgame(screen, state):
    if not hasattr(draw_endgame, "title_font"):
        draw_endgame.title_font = pygame.font.SysFont(None, 132)
        draw_endgame.subtitle_font = pygame.font.SysFont(None, 56)
        draw_endgame.body_font = pygame.font.SysFont(None, 42)

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(ENDGAME_OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))

    title = draw_endgame.title_font.render("LEVEL 25 CLEARED", True, ENDGAME_TITLE_COLOR)
    title_shadow = draw_endgame.title_font.render("LEVEL 25 CLEARED", True, ENDGAME_TITLE_SHADOW)
    subtitle = draw_endgame.subtitle_font.render("Sonic made it to the finish line.", True, ENDGAME_TEXT_COLOR)
    score = draw_endgame.body_font.render(f"Final score: {state.hud_data.score}", True, ENDGAME_ACCENT_COLOR)
    prompt = draw_endgame.body_font.render("Press Enter to play again", True, ENDGAME_TEXT_COLOR)

    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
    title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 - 116))
    subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 18))
    score_rect = score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 42))
    prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 124))

    screen.blit(title_shadow, title_shadow_rect)
    screen.blit(title, title_rect)
    screen.blit(subtitle, subtitle_rect)
    screen.blit(score, score_rect)
    screen.blit(prompt, prompt_rect)


def reset_game(updatable, drawable, options):
    updatable.empty()
    drawable.empty()
    return create_initial_gamestate(SCREEN_WIDTH, SCENE_HEIGHT, HUD_HEIGHT, options)


def main():
    args = parse_args()
    initial_options = GameOptions(sound_enabled=not args.no_sound, start_level=args.start_level)
    restart_options = GameOptions(sound_enabled=not args.no_sound)

    print(f"Starting SonicMath with pygame version {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")
    pygame.init()
    pygame.key.set_repeat(200, 30)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    Background.containers = (updatable, drawable)
    Obstacle.containers = (updatable, drawable)
    Sonic.containers = (updatable, drawable)

    hud = Hud(SCREEN_WIDTH, HUD_HEIGHT)
    state = reset_game(updatable, drawable, initial_options)

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if state.run_state != RunState.PLAYING:
                    if event.key == pygame.K_RETURN:
                        state = reset_game(updatable, drawable, restart_options)
                    continue
                if event.key == pygame.K_BACKSPACE:
                    state.hud_data.answer_text = state.hud_data.answer_text[:-1]
                elif event.key == pygame.K_RETURN:
                    submit_answer(state)
                elif event.unicode.isdigit():
                    state.hud_data.answer_text += event.unicode

        if state.run_state == RunState.PLAYING:
            handle_obstacle_collisions(state)
            if state.background.did_wrap:
                spawn_obstacle(state, SCREEN_WIDTH)
        updatable.update(dt)
        clear_inactive_obstacle(state)

        screen.fill(HUD_BACKGROUND_COLOR)
        hud.draw(screen, state.hud_data, state.level, state.is_answer_pending)
        pygame.draw.line(screen, HUD_BORDER_COLOR, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 4)
        for d in drawable:
            d.draw(screen)
        if state.run_state == RunState.GAME_OVER:
            draw_game_over(screen)
        elif state.run_state == RunState.ENDGAME:
            draw_endgame(screen, state)

        pygame.display.flip()


if __name__ == "__main__":
    main()
