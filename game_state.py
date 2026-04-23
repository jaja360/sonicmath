import random
from dataclasses import dataclass
from enum import Enum, auto

from asset_paths import get_music_path
from background import Background
from level_config import build_level_config
from math_problem import generate_problem
from music_player import MusicPlayer
from obstacle import Obstacle
from power_down import PowerDown
from power_up import PowerUp
from sonic import Sonic, SonicState

BASE_SPEED = 150
SPEED_PER_LEVEL = 10
JUMP_TRIGGER_DELAY = 20
LOW_HEALTH_THRESHOLD = 15
POINTS_PER_CORRECT_ANSWER = 10
POINT_EFFECT_DURATION = 5
SPEED_EFFECT_DURATION = 5
STATUS_EFFECT_DURATION = 5
HAZARD_POWER_DOWN_CHANCE = 0.30
POWER_UP_SPAWN_CHANCE = 0.30
SPEED_EFFECT_DELTA = 40


class RunState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    ENDGAME = auto()


class Status(Enum):
    NORMAL = "normal"
    BURNED = "burned"
    POISONED = "poisoned"


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
    status: Status
    status_turns: int
    question: str
    answer_text: str
    background: Background
    music_player: MusicPlayer
    sonic: Sonic
    run_state: RunState = RunState.PLAYING
    base_speed: int = BASE_SPEED
    score_boost_turns: int = 0
    score_penalty_turns: int = 0
    slow_turns: int = 0
    speed_up_turns: int = 0
    next_hit_immune: bool = False
    current_hazard: Obstacle | PowerDown | None = None
    current_power_up: PowerUp | None = None
    level_config: object = None
    current_problem: object = None
    is_answer_pending: bool = False


def get_speed_for_level(level):
    return BASE_SPEED + level * SPEED_PER_LEVEL


def get_effective_speed(state):
    speed = state.base_speed
    if state.slow_turns > 0:
        speed -= SPEED_EFFECT_DELTA
    if state.speed_up_turns > 0:
        speed += SPEED_EFFECT_DELTA
    return speed


def refresh_speeds(state):
    speed = get_effective_speed(state)
    state.background.set_speed(speed)
    state.sonic.set_speed(speed)
    if state.current_hazard is not None:
        state.current_hazard.speed = speed
    if state.current_power_up is not None:
        state.current_power_up.speed = speed


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


def clear_temporary_effects(state):
    state.score_boost_turns = 0
    state.score_penalty_turns = 0
    state.slow_turns = 0
    state.speed_up_turns = 0
    state.next_hit_immune = False
    state.status = Status.NORMAL
    state.status_turns = 0
    refresh_speeds(state)


def heal_health(state, amount):
    state.health = min(100, state.health + amount)
    sync_music(state)


def get_score_reward(state):
    reward = POINTS_PER_CORRECT_ANSWER
    if state.score_boost_turns > 0:
        reward *= 2
    if state.score_penalty_turns > 0:
        reward //= 2
    return reward


def apply_power_up(state, effect_name):
    if effect_name == "heal_small":
        heal_health(state, 10)
        return
    if effect_name == "heal_large":
        heal_health(state, 20)
        return
    if effect_name == "score_boost":
        state.score_boost_turns = POINT_EFFECT_DURATION
        return
    if effect_name == "slow_time":
        state.slow_turns = SPEED_EFFECT_DURATION
        refresh_speeds(state)
        return
    if effect_name == "shield":
        state.next_hit_immune = True


def apply_power_down(state, effect_name):
    if effect_name == "burn":
        state.status = Status.BURNED
        state.status_turns = STATUS_EFFECT_DURATION
        return
    if effect_name == "poison":
        state.status = Status.POISONED
        state.status_turns = STATUS_EFFECT_DURATION
        return
    if effect_name == "score_penalty":
        state.score_penalty_turns = POINT_EFFECT_DURATION
        return
    if effect_name == "speed_up":
        state.speed_up_turns = SPEED_EFFECT_DURATION
        refresh_speeds(state)
        return
    if effect_name == "purge":
        clear_temporary_effects(state)


def tick_effects_after_question(state):
    if state.status == Status.BURNED and state.status_turns > 0:
        lose_health(state, 1)
        state.status_turns -= 1
    if state.status == Status.POISONED and state.status_turns > 0:
        lose_health(state, 2)
        state.status_turns -= 1
    if state.score_boost_turns > 0:
        state.score_boost_turns -= 1
    if state.score_penalty_turns > 0:
        state.score_penalty_turns -= 1
    if state.slow_turns > 0:
        state.slow_turns -= 1
    if state.speed_up_turns > 0:
        state.speed_up_turns -= 1
    if state.status_turns == 0:
        state.status = Status.NORMAL
    refresh_speeds(state)


def apply_level(state):
    state.level_config = build_level_config(state.level)
    state.base_speed = get_speed_for_level(state.level)

    state.background.set_background(state.level_config.background_name)
    refresh_speeds(state)
    sync_music(state)
    advance_problem(state)


def level_up(state):
    state.level += 1
    if state.level >= 25:
        trigger_endgame(state)
        return
    apply_level(state)


def resolve_correct_answer(state):
    state.score += get_score_reward(state)
    state.correct_answers += 1
    tick_effects_after_question(state)
    if state.run_state != RunState.PLAYING:
        return
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
        status=Status.NORMAL,
        status_turns=0,
        question="1+1",
        answer_text="",
        background=background,
        music_player=music_player,
        sonic=sonic,
    )
    apply_level(state)
    return state


def spawn_obstacle(state, screen_width):
    if state.current_hazard is not None:
        return

    hazard_cls = PowerDown if random.random() < HAZARD_POWER_DOWN_CHANCE else Obstacle
    state.current_hazard = hazard_cls(screen_width=screen_width, ground_y=state.background.ground_y, speed=get_effective_speed(state))


def spawn_power_up(state, screen_width):
    if state.current_power_up is not None or random.random() >= POWER_UP_SPAWN_CHANCE:
        return False

    state.current_power_up = PowerUp(screen_width=screen_width, ground_y=state.background.ground_y, speed=get_effective_speed(state))
    return True


def clear_inactive_obstacle(state):
    if state.current_hazard is not None and not state.current_hazard.alive():
        state.current_hazard = None


def clear_inactive_power_up(state):
    if state.current_power_up is not None and not state.current_power_up.alive():
        state.current_power_up = None


def trigger_endgame(state):
    if state.current_hazard is not None:
        state.current_hazard.kill()
        state.current_hazard = None
    if state.current_power_up is not None:
        state.current_power_up.kill()
        state.current_power_up = None
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
    hazard = state.current_hazard
    if hazard is None or not hazard.collidable or not state.sonic.rect.colliderect(hazard.rect):
        return

    if state.is_answer_pending:
        if hazard.rect.left > state.sonic.rect.right - JUMP_TRIGGER_DELAY:
            return

        hazard.collidable = False
        state.current_hazard = None
        state.sonic.set_state(SonicState.RUN_JUMP_RUN)
        resolve_correct_answer(state)
        return

    hazard.kill()
    state.current_hazard = None
    if state.next_hit_immune:
        state.next_hit_immune = False
        advance_problem(state)
        return

    if isinstance(hazard, PowerDown):
        tick_effects_after_question(state)
        if state.run_state != RunState.PLAYING:
            advance_problem(state)
            return
        apply_power_down(state, hazard.effect_name)
        lose_health(state, 0, trigger_hit_animation=True)
    else:
        lose_health(state, hazard.damage, trigger_hit_animation=True)
        tick_effects_after_question(state)
    advance_problem(state)


def handle_power_up_collection(state):
    if state.current_power_up is None or not state.sonic.rect.colliderect(state.current_power_up.rect):
        return

    apply_power_up(state, state.current_power_up.effect_name)
    state.current_power_up.kill()
    state.current_power_up = None
