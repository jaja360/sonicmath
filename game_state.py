import random
from dataclasses import dataclass
from enum import Enum, auto

from asset_paths import get_music_path
from background import Background
from level_config import LevelConfig, build_level_config
from math_problem import MathProblem, generate_problem
from music_player import MusicPlayer
from obstacle import Obstacle
from power_down import PowerDown
from power_up import PowerUp
from sonic import Sonic, SonicState

BASE_SPEED = 200
SPEED_PER_LEVEL = 40
JUMP_TRIGGER_DELAY = 20
LOW_HEALTH_THRESHOLD = 15
POINTS_PER_CORRECT_ANSWER = 10
POINT_EFFECT_DURATION = 5
SPEED_EFFECT_DURATION = 5
STATUS_EFFECT_DURATION = 5
HAZARD_POWER_DOWN_CHANCE = 0.30
POWER_UP_SPAWN_CHANCE = 0.30


class RunState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    ENDGAME = auto()


class Status(Enum):
    NORMAL = "normal"
    BURNED = "burned"
    POISONED = "poisoned"


class SpeedEffect(Enum):
    NORMAL = "normal"
    SLOWER = "slower"
    FASTER = "faster"


class DamageEffect(Enum):
    NORMAL = "normal"
    REDUCED = "reduced"
    INCREASED = "increased"


class ScoreEffect(Enum):
    NORMAL = "normal"
    BOOSTED = "boosted"
    REDUCED = "reduced"


class SpecialEffect(Enum):
    NONE = "none"
    DEBUFF_IMMUNE = "debuff_immune"
    HEAL_BLOCKED = "heal_blocked"
    BUFF_BLOCKED = "buff_blocked"
    VISUAL_DEBUFF = "visual_debuff"


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
    speed_effect: SpeedEffect
    speed_turns: int
    damage_effect: DamageEffect
    damage_turns: int
    score_effect: ScoreEffect
    score_turns: int
    special_effect: SpecialEffect
    special_turns: int
    answer_text: str
    background: Background
    music_player: MusicPlayer
    sonic: Sonic
    run_state: RunState = RunState.PLAYING
    base_speed: int = BASE_SPEED
    next_hit_immune: bool = False
    current_hazard: Obstacle | PowerDown | None = None
    current_power_up: PowerUp | None = None
    level_config: LevelConfig = None
    current_problem: MathProblem = None
    is_answer_pending: bool = False


def get_speed_for_level(level):
    return BASE_SPEED + SPEED_PER_LEVEL * (1 + (level % 5))


def get_effective_speed(state):
    speed = state.base_speed
    if state.speed_effect == SpeedEffect.SLOWER:
        speed -= 2 * SPEED_PER_LEVEL
    if state.speed_effect == SpeedEffect.FASTER:
        speed += 2 * SPEED_PER_LEVEL
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


def reset_modifier_categories(
    state,
    *,
    clear_speed=True,
    clear_damage=True,
    clear_score=True,
    clear_special=True,
):
    if clear_speed:
        state.speed_effect = SpeedEffect.NORMAL
        state.speed_turns = 0
    if clear_damage:
        state.damage_effect = DamageEffect.NORMAL
        state.damage_turns = 0
    if clear_score:
        state.score_effect = ScoreEffect.NORMAL
        state.score_turns = 0
    if clear_special:
        state.special_effect = SpecialEffect.NONE
        state.special_turns = 0
    refresh_speeds(state)


def clear_temporary_effects(state):
    reset_modifier_categories(state)
    state.next_hit_immune = False
    state.status = Status.NORMAL
    state.status_turns = 0


def heal_health(state, amount):
    state.health = min(100, state.health + amount)
    sync_music(state)


def can_receive_buff(state):
    return state.special_effect != SpecialEffect.BUFF_BLOCKED


def can_receive_debuff(state):
    return state.special_effect != SpecialEffect.DEBUFF_IMMUNE


def can_heal(state):
    return state.special_effect != SpecialEffect.HEAL_BLOCKED


def is_negative_special(effect):
    return effect in {
        SpecialEffect.HEAL_BLOCKED,
        SpecialEffect.BUFF_BLOCKED,
        SpecialEffect.VISUAL_DEBUFF,
    }


def set_status(state, status, turns):
    state.status = status
    state.status_turns = turns


def set_speed_effect(state, effect, turns):
    state.speed_effect = effect
    state.speed_turns = turns
    refresh_speeds(state)


def set_damage_effect(state, effect, turns):
    state.damage_effect = effect
    state.damage_turns = turns


def set_score_effect(state, effect, turns):
    state.score_effect = effect
    state.score_turns = turns


def set_special_effect(state, effect, turns):
    state.special_effect = effect
    state.special_turns = turns


def clear_status(state):
    state.status = Status.NORMAL
    state.status_turns = 0


def clear_negative_modifiers(state):
    reset_modifier_categories(
        state,
        clear_speed=state.speed_effect == SpeedEffect.FASTER,
        clear_damage=state.damage_effect == DamageEffect.INCREASED,
        clear_score=state.score_effect == ScoreEffect.REDUCED,
        clear_special=is_negative_special(state.special_effect),
    )


def clear_negative_effects(state):
    clear_status(state)
    clear_negative_modifiers(state)


def get_effective_damage(state, base_damage):
    if state.damage_effect == DamageEffect.REDUCED:
        return max(1, (base_damage + 1) // 2)
    if state.damage_effect == DamageEffect.INCREASED:
        return max(1, (base_damage * 3 + 1) // 2)
    return base_damage


def get_score_reward(state):
    reward = POINTS_PER_CORRECT_ANSWER
    if state.score_effect == ScoreEffect.BOOSTED:
        reward = reward * 3 // 2
    if state.score_effect == ScoreEffect.REDUCED:
        reward //= 2
    return reward


def apply_power_up(state, effect_name):
    if effect_name == "heal_small" and can_heal(state):
        heal_health(state, 10)
        return
    if effect_name == "heal_large" and can_heal(state):
        heal_health(state, 20)
        return
    if effect_name == "score_boost" and can_receive_buff(state):
        set_score_effect(state, ScoreEffect.BOOSTED, POINT_EFFECT_DURATION)
        return
    if effect_name == "damage_reduce_long" and can_receive_buff(state):
        set_damage_effect(state, DamageEffect.REDUCED, 5)
        return
    if effect_name == "damage_reduce_short" and can_receive_buff(state):
        set_damage_effect(state, DamageEffect.REDUCED, 3)
        return
    if effect_name == "debuff_immunity" and can_receive_buff(state):
        set_special_effect(state, SpecialEffect.DEBUFF_IMMUNE, 5)
        return
    if effect_name == "clear_debuffs":
        clear_negative_modifiers(state)
        return
    if effect_name == "clear_status":
        clear_status(state)
        return
    if effect_name == "cleanse_and_immunity":
        clear_negative_effects(state)
        if can_receive_buff(state):
            set_special_effect(state, SpecialEffect.DEBUFF_IMMUNE, 3)
        return
    if effect_name == "slow_time" and can_receive_buff(state):
        set_speed_effect(state, SpeedEffect.SLOWER, SPEED_EFFECT_DURATION)
        return
    if effect_name == "full_cleanse":
        clear_negative_effects(state)
        return
    if effect_name == "shield":
        state.next_hit_immune = True


def apply_power_down(state, effect_name):
    if effect_name == "burn" and can_receive_debuff(state):
        set_status(state, Status.BURNED, STATUS_EFFECT_DURATION)
        return
    if effect_name == "poison" and can_receive_debuff(state):
        set_status(state, Status.POISONED, STATUS_EFFECT_DURATION)
        return
    if effect_name == "damage_up_long" and can_receive_debuff(state):
        set_damage_effect(state, DamageEffect.INCREASED, 5)
        return
    if effect_name == "damage_up_short" and can_receive_debuff(state):
        set_damage_effect(state, DamageEffect.INCREASED, 3)
        return
    if effect_name == "buff_blocked" and can_receive_debuff(state):
        set_special_effect(state, SpecialEffect.BUFF_BLOCKED, 5)
        return
    if effect_name == "score_penalty" and can_receive_debuff(state):
        set_score_effect(state, ScoreEffect.REDUCED, POINT_EFFECT_DURATION)
        return
    if effect_name == "speed_up" and can_receive_debuff(state):
        set_speed_effect(state, SpeedEffect.FASTER, SPEED_EFFECT_DURATION)
        return
    if effect_name == "heal_blocked" and can_receive_debuff(state):
        set_special_effect(state, SpecialEffect.HEAL_BLOCKED, 5)
        return
    if effect_name == "visual_debuff" and can_receive_debuff(state):
        set_special_effect(state, SpecialEffect.VISUAL_DEBUFF, 5)
        return
    if effect_name == "purge":
        clear_temporary_effects(state)


def tick_effects_after_question(state):
    if state.status == Status.BURNED and state.status_turns > 0:
        lose_health(state, 1)
        state.status_turns -= 1
    elif state.status == Status.POISONED and state.status_turns > 0:
        lose_health(state, 2)
        state.status_turns -= 1
    if state.status_turns == 0:
        state.status = Status.NORMAL
    if state.speed_turns > 0:
        state.speed_turns -= 1
        if state.speed_turns == 0:
            state.speed_effect = SpeedEffect.NORMAL
    if state.damage_turns > 0:
        state.damage_turns -= 1
        if state.damage_turns == 0:
            state.damage_effect = DamageEffect.NORMAL
    if state.score_turns > 0:
        state.score_turns -= 1
        if state.score_turns == 0:
            state.score_effect = ScoreEffect.NORMAL
    if state.special_turns > 0:
        state.special_turns -= 1
        if state.special_turns == 0:
            state.special_effect = SpecialEffect.NONE
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
    state.music_player.play_sound("levelUp")
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
        speed_effect=SpeedEffect.NORMAL,
        speed_turns=0,
        damage_effect=DamageEffect.NORMAL,
        damage_turns=0,
        score_effect=ScoreEffect.NORMAL,
        score_turns=0,
        special_effect=SpecialEffect.NONE,
        special_turns=0,
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
        state.music_player.play_sound("goodAnswer")
        state.is_answer_pending = True
        return

    state.music_player.play_sound("badAnswer")
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
        state.music_player.play_sound("jump")
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
        state.music_player.play_sound("powerDown")
        tick_effects_after_question(state)
        if state.run_state != RunState.PLAYING:
            advance_problem(state)
            return
        apply_power_down(state, hazard.effect_name)
        lose_health(state, 0, trigger_hit_animation=True)
    else:
        state.music_player.play_sound("impact")
        lose_health(state, get_effective_damage(state, hazard.damage), trigger_hit_animation=True)
        tick_effects_after_question(state)
    advance_problem(state)


def handle_power_up_collection(state):
    if state.current_power_up is None or not state.sonic.rect.colliderect(state.current_power_up.rect):
        return

    state.music_player.play_sound("powerUp")
    apply_power_up(state, state.current_power_up.effect_name)
    state.current_power_up.kill()
    state.current_power_up = None
