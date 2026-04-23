from dataclasses import dataclass
from enum import Enum, auto

from asset_paths import get_music_path
from background import Background
from level_config import build_level_config
from math_problem import generate_problem
from music_player import MusicPlayer
from obstacle import Obstacle
from sonic import Sonic, SonicState

BASE_SPEED = 150
SPEED_PER_LEVEL = 10
JUMP_TRIGGER_DELAY = 20
LOW_HEALTH_THRESHOLD = 15
POINTS_PER_CORRECT_ANSWER = 10


class RunState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    ENDGAME = auto()


@dataclass
class GameOptions:
    sound_enabled: bool = True
    start_level: int = 0
    start_hp: int = 100


@dataclass
class GameState:
    level: int
    health: int
    score: int
    correct_answers: int
    status: str
    question: str
    answer_text: str
    background: Background
    music_player: MusicPlayer
    sonic: Sonic
    current_obstacle: Obstacle | None = None
    level_config: object = None
    current_problem: object = None
    is_answer_pending: bool = False
    run_state: RunState = RunState.PLAYING


def get_speed_for_level(level):
    return BASE_SPEED + level * SPEED_PER_LEVEL


def advance_problem(state):
    state.current_problem = generate_problem(state.level_config)
    state.question = state.current_problem.text
    state.answer_text = ""
    state.is_answer_pending = False


def get_current_music_name(state):
    if state.run_state == RunState.ENDGAME:
        return "ending"
    if state.run_state == RunState.GAME_OVER:
        return "gameOver"
    if state.health <= LOW_HEALTH_THRESHOLD:
        return "lowHP"
    return state.level_config.music_name


def sync_music(state):
    state.music_player.play(get_music_path(get_current_music_name(state)))


def apply_level(state):
    state.level_config = build_level_config(state.level)
    speed = get_speed_for_level(state.level)

    state.background.set_background(state.level_config.background_name)
    state.background.set_speed(speed)
    sync_music(state)
    state.sonic.set_speed(speed)
    if state.current_obstacle is not None:
        state.current_obstacle.speed = speed
    advance_problem(state)


def level_up(state):
    state.level += 1
    if state.level >= 25:
        trigger_endgame(state)
        return
    apply_level(state)


def resolve_correct_answer(state):
    state.score += POINTS_PER_CORRECT_ANSWER
    state.correct_answers += 1
    if state.correct_answers % 5 == 0:
        level_up(state)
        return

    advance_problem(state)


def create_initial_gamestate(screen_width, scene_height, hud_height, options):
    music_player = MusicPlayer(sound_enabled=options.sound_enabled)
    background = Background(screen_width, scene_height, hud_height)
    sonic = Sonic(ground_y=background.ground_y)
    state = GameState(
        level=options.start_level,
        health=options.start_hp,
        score=0,
        correct_answers=0,
        status="normal",
        question="1+1",
        answer_text="",
        background=background,
        music_player=music_player,
        sonic=sonic,
    )
    apply_level(state)
    return state


def spawn_obstacle(state, screen_width):
    if state.current_obstacle is not None:
        return

    state.current_obstacle = Obstacle(
        screen_width=screen_width,
        ground_y=state.background.ground_y,
        speed=state.background.speed,
    )


def clear_inactive_obstacle(state):
    if state.current_obstacle is not None and not state.current_obstacle.alive():
        state.current_obstacle = None


def trigger_endgame(state):
    if state.current_obstacle is not None:
        state.current_obstacle.kill()
        state.current_obstacle = None
    state.run_state = RunState.ENDGAME
    sync_music(state)
    state.sonic.set_state(SonicState.RUN_ENDGAME)


def lose_health(state, amount=1, trigger_hit_animation=False):
    state.health = max(0, state.health - amount)
    state.answer_text = ""

    if state.health == 0:
        state.run_state = RunState.GAME_OVER
        state.sonic.set_state(SonicState.RUN_OBSTACLE_GAMEOVER)
    elif trigger_hit_animation:
        state.sonic.set_state(SonicState.RUN_OBSTACLE_RUN)

    sync_music(state)


def submit_answer(state):
    if state.run_state != RunState.PLAYING or state.is_answer_pending or not state.answer_text:
        return

    if int(state.answer_text) == state.current_problem.answer:
        state.is_answer_pending = True
        return

    lose_health(state)


def handle_obstacle_collisions(state):
    obstacle = state.current_obstacle
    if obstacle is None or not obstacle.collidable or not state.sonic.rect.colliderect(obstacle.rect):
        return

    if state.is_answer_pending:
        if obstacle.rect.left > state.sonic.rect.right - JUMP_TRIGGER_DELAY:
            return

        obstacle.collidable = False
        state.current_obstacle = None
        state.sonic.set_state(SonicState.RUN_JUMP_RUN)
        resolve_correct_answer(state)
        return

    obstacle.kill()
    state.current_obstacle = None
    lose_health(state, obstacle.damage, trigger_hit_animation=True)
    advance_problem(state)
