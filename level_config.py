from dataclasses import dataclass


@dataclass(frozen=True)
class LevelConfig:
    level: int
    background_name: str
    music_name: str
    speed: float
    max_operand: int


def build_level_config(level: int) -> LevelConfig:
    if level >= 20:
        background_name = "lv20"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            speed=350,
            max_operand=50,
        )

    if level >= 15:
        background_name = "lv15"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            speed=300,
            max_operand=30,
        )

    if level >= 10:
        background_name = "lv10"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            speed=250,
            max_operand=20,
        )

    if level >= 5:
        background_name = "lv5"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            speed=200,
            max_operand=15,
        )

    background_name = "lv0" if level >= 0 else "practice"
    return LevelConfig(
        level=level,
        background_name=background_name,
        music_name=background_name,
        speed=150,
        max_operand=10,
    )
