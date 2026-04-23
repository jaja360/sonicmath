import pygame

from background import Background
from game_state import (
    clear_inactive_obstacle,
    create_initial_gamestate,
    handle_obstacle_collisions,
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


def draw_game_over(screen):
    if not hasattr(draw_game_over, "font"):
        draw_game_over.font = pygame.font.SysFont(None, 140)
    text = draw_game_over.font.render("GAME OVER", True, GAME_OVER_COLOR)
    shadow = draw_game_over.font.render("GAME OVER", True, GAME_OVER_SHADOW_COLOR)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 + 4))
    screen.blit(shadow, shadow_rect)
    screen.blit(text, text_rect)


def reset_game(updatable, drawable):
    updatable.empty()
    drawable.empty()
    return create_initial_gamestate(SCREEN_WIDTH, SCENE_HEIGHT, HUD_HEIGHT)


def main():
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
    state = reset_game(updatable, drawable)

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if state.is_game_over:
                    if event.key == pygame.K_RETURN:
                        state = reset_game(updatable, drawable)
                    continue
                if event.key == pygame.K_BACKSPACE:
                    state.hud_data.answer_text = state.hud_data.answer_text[:-1]
                elif event.key == pygame.K_RETURN:
                    submit_answer(state)
                elif event.unicode.isdigit():
                    state.hud_data.answer_text += event.unicode

        if state.background.did_wrap:
            spawn_obstacle(state, SCREEN_WIDTH)
        if not state.is_game_over:
            handle_obstacle_collisions(state)
        updatable.update(dt)
        clear_inactive_obstacle(state)

        screen.fill(HUD_BACKGROUND_COLOR)
        hud.draw(screen, state.hud_data, state.level, state.is_answer_pending)
        pygame.draw.line(screen, HUD_BORDER_COLOR, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 4)
        for d in drawable:
            d.draw(screen)
        if state.is_game_over:
            draw_game_over(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
