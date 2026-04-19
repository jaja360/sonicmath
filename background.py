import pygame

from asset_paths import get_background_path
from image_loader import load_image

# Height of the ground line as a ratio of the scene height
# Used to compute self.ground_y, which is used by the other classes to determine
# where the ground is.
GROUND_LINE_RATIO = 0.92


class Background:
    def __init__(self, screen_width, scene_height, top):
        self.screen_width = screen_width
        self.scene_height = scene_height
        self.top = top  # The y coordinate where background starts (i.e. the height of the HUD)
        self.x = 0.0
        self.speed = 150
        self.current_name = ""

    @property
    def ground_y(self):
        return self.top + round(self.scene_height * GROUND_LINE_RATIO)

    def _load_scaled_background(self, background_name):
        image = load_image(get_background_path(background_name))
        half_width = image.get_width() // 2
        tile = image.subsurface((0, 0, half_width, image.get_height())).copy()
        return pygame.transform.smoothscale(tile, (self.screen_width, self.scene_height))

    def set_background(self, background_name):
        if background_name == self.current_name:
            return

        self.current_name = background_name
        self.tile = self._load_scaled_background(background_name)
        self.tile_width = self.tile.get_width()
        self.x = 0.0

    def set_level(self, level):
        self.set_background(f"lv{level}")

    def set_speed(self, speed):
        self.speed = speed

    def update(self, dt):
        self.x -= self.speed * dt
        if self.x <= -self.tile_width:
            self.x += self.tile_width

    def draw(self, screen):
        x = round(self.x)
        screen.blit(self.tile, (x, self.top))
        screen.blit(self.tile, (x + self.tile_width, self.top))
