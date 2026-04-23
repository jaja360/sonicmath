from dataclasses import dataclass

import pygame

from asset_paths import get_music_path
from background import Background
from hud import Hud, HudData
from obstacle import Obstacle
from level_config import build_level_config
from math_problem import generate_problem
from music_player import MusicPlayer
from sonic import Sonic, SonicState

SCREEN_WIDTH = 1600
HUD_HEIGHT = 240
SCENE_HEIGHT = 1000
SCREEN_HEIGHT = HUD_HEIGHT + SCENE_HEIGHT
HUD_BACKGROUND_COLOR = (18, 22, 32)
HUD_BORDER_COLOR = (60, 82, 120)
GAME_OVER_COLOR = (255, 110, 110)
GAME_OVER_SHADOW_COLOR = (20, 8, 8)
BASE_SPEED = 150
SPEED_PER_LEVEL = 10


@dataclass
class GameState:
    level: int
    hud_data: HudData
    background: Background
    music_player: MusicPlayer
    sonic: Sonic
    obstacles: pygame.sprite.Group
    level_config: object = None
    current_problem: object = None
    is_game_over: bool = False


def get_speed_for_level(level):
    return BASE_SPEED + level * SPEED_PER_LEVEL


def advance_problem(state):
    state.current_problem = generate_problem(state.level_config)
    state.hud_data.question = state.current_problem.text
    state.hud_data.answer_text = ""


def apply_level(state):
    state.level_config = build_level_config(state.level)
    speed = get_speed_for_level(state.level)

    state.background.set_background(state.level_config.background_name)
    state.background.set_speed(speed)
    state.music_player.play(get_music_path(state.level_config.music_name))
    state.sonic.set_speed(speed)
    for obstacle in state.obstacles:
        obstacle.speed = speed

    advance_problem(state)


def level_up(state):
    state.level += 1
    apply_level(state)


def spawn_obstacle(state):
    obstacle = Obstacle(
        screen_width=SCREEN_WIDTH,
        ground_y=state.background.ground_y,
        speed=state.background.speed,
    )
    state.obstacles.add(obstacle)


def lose_health(state, amount=1):
    state.hud_data.health = max(0, state.hud_data.health - amount)
    state.hud_data.answer_text = ""

    if state.hud_data.health == 0:
        state.is_game_over = True
        state.sonic.set_state(SonicState.RUN_OBSTACLE_GAMEOVER)
    else:
        state.sonic.set_state(SonicState.RUN_OBSTACLE_RUN)


def submit_answer(state):
    if state.is_game_over or not state.hud_data.answer_text:
        return

    if int(state.hud_data.answer_text) == state.current_problem.answer:
        state.hud_data.score += 1

        if state.hud_data.score % 5 == 0:
            level_up(state)
            return

        advance_problem(state)
        return

    lose_health(state)


def handle_obstacle_collisions(state):
    collisions = pygame.sprite.spritecollide(state.sonic, state.obstacles, dokill=True)
    for obstacle in collisions:
        lose_health(state, obstacle.damage)
        if state.is_game_over:
            return


def draw_game_over(screen):
    if not hasattr(draw_game_over, "font"):
        draw_game_over.font = pygame.font.SysFont(None, 140)
    text = draw_game_over.font.render("GAME OVER", True, GAME_OVER_COLOR)
    shadow = draw_game_over.font.render("GAME OVER", True, GAME_OVER_SHADOW_COLOR)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 + 4))
    screen.blit(shadow, shadow_rect)
    screen.blit(text, text_rect)


def main():
    print(f"Starting Asteroids with pygame version {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")
    pygame.init()
    pygame.key.set_repeat(200, 30)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    Background.containers = (updatable, drawable)
    Obstacle.containers = (updatable, drawable)
    Sonic.containers = (updatable, drawable)

    hud_data = HudData()
    music_player = MusicPlayer()
    hud = Hud(SCREEN_WIDTH, HUD_HEIGHT)
    background = Background(SCREEN_WIDTH, SCENE_HEIGHT, HUD_HEIGHT)
    sonic = Sonic(ground_y=background.ground_y)
    state = GameState(
        level=0,
        hud_data=hud_data,
        background=background,
        music_player=music_player,
        sonic=sonic,
        obstacles=obstacles,
    )
    apply_level(state)

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if state.is_game_over:
                    continue
                if event.key == pygame.K_BACKSPACE:
                    state.hud_data.answer_text = state.hud_data.answer_text[:-1]
                elif event.key == pygame.K_RETURN:
                    submit_answer(state)
                elif event.unicode.isdigit():
                    state.hud_data.answer_text += event.unicode

        handle_obstacle_collisions(state)
        if state.background.did_wrap:
            spawn_obstacle(state)

        updatable.update(dt)

        screen.fill(HUD_BACKGROUND_COLOR)
        hud.draw(screen, state.hud_data, state.level)
        pygame.draw.line(screen, HUD_BORDER_COLOR, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 4)
        for d in drawable:
            d.draw(screen)
        if state.is_game_over:
            draw_game_over(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
