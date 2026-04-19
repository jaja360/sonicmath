import os

ASSET_NAMES = (
    "practice",
    "lv0",
    "lv5",
    "lv10",
    "lv15",
    "lv20",
)

SPECIAL_MUSIC_NAMES = (
    "ending",
    "gameOver",
    "lowHP",
)
SOUND_NAMES = (
    "badAnswer",
    "goodAnswer",
    "impact",
    "jump",
    "levelUp",
    "powerDown",
    "powerUp",
)


def _build_paths(folder, extension, names):
    return {
        name: os.path.join("assets", folder, f"{name}.{extension}") for name in names
    }


BACKGROUND_PATHS = _build_paths("backgrounds", "jpg", ASSET_NAMES)
MUSIC_PATHS = _build_paths("music", "ogg", (*ASSET_NAMES, *SPECIAL_MUSIC_NAMES))
SOUND_PATHS = _build_paths("sounds", "ogg", SOUND_NAMES)


def get_background_path(name):
    try:
        return BACKGROUND_PATHS[name]
    except KeyError as exc:
        raise ValueError(f"unknown background: {name}") from exc


def get_music_path(name):
    try:
        path = MUSIC_PATHS[name]
    except KeyError as exc:
        raise ValueError(f"unknown music track: {name}") from exc

    if not os.path.exists(path):
        raise ValueError(f"missing music track: {path}")

    return path


def get_sound_path(name):
    try:
        path = SOUND_PATHS[name]
    except KeyError as exc:
        raise ValueError(f"unknown sound effect: {name}") from exc

    if not os.path.exists(path):
        raise ValueError(f"missing sound effect: {path}")

    return path
