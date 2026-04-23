from dataclasses import dataclass


@dataclass(frozen=True)
class LevelConfig:
    level: int
    background_name: str
    music_name: str
    max_operands: dict[str, int]


def build_level_config(level: int) -> LevelConfig:
    if level >= 20:
        background_name = "lv20"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            max_operands={"+": 60, "-": 60, "*": 15, "/": 120},
        )

    if level >= 15:
        background_name = "lv15"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            max_operands={"+": 40, "-": 40, "*": 12, "/": 60},
        )

    if level >= 10:
        background_name = "lv10"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            max_operands={"+": 30, "-": 30, "*": 8},
        )

    if level >= 5:
        background_name = "lv5"
        return LevelConfig(
            level=level,
            background_name=background_name,
            music_name=background_name,
            max_operands={"+": 25, "-": 25},
        )

    background_name = "lv0" if level >= 0 else "practice"
    return LevelConfig(
        level=level,
        background_name=background_name,
        music_name=background_name,
        max_operands={"+": 20},
    )
