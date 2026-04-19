import pygame

from asset_paths import get_music_path
from background import Background
from level_config import build_level_config
from music_player import MusicPlayer
from sonic import Sonic

SCREEN_WIDTH = 1600
HUD_HEIGHT = 240
SCENE_HEIGHT = 1000
SCREEN_HEIGHT = HUD_HEIGHT + SCENE_HEIGHT
HUD_BACKGROUND_COLOR = (18, 22, 32)
HUD_BORDER_COLOR = (60, 82, 120)


def main():
    print(f"Starting Asteroids with pygame version {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")
    pygame.init()

    level = 0
    level_config = build_level_config(level)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    background = Background(SCREEN_WIDTH, SCENE_HEIGHT, HUD_HEIGHT)
    background.set_background(level_config.background_name)
    background.speed = level_config.speed

    music_player = MusicPlayer()
    music_player.play(get_music_path(level_config.music_name))

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    Sonic.containers = (updatable, drawable)

    sonic = Sonic(ground_y=background.ground_y)
    sonic.set_speed(level_config.speed)

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        background.update(dt)
        updatable.update(dt)

        screen.fill(HUD_BACKGROUND_COLOR)
        background.draw(screen)
        pygame.draw.line(screen, HUD_BORDER_COLOR, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 4)
        for d in drawable:
            d.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
