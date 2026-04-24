import os
import random
import pygame

from image_loader import load_image, load_sheet_frames

SPRITE_PATH = os.path.join("assets", "sprites", "power-downs.png")
FRAME_SIZE = 50
DISPLAY_SIZE = 100
GROUND_OFFSET = 20
POWER_DOWN_EFFECTS = {
    0: "burn",
    1: "poison",
    2: "damage_up_long",
    3: "damage_up_short",
    4: "buff_blocked",
    5: "score_penalty",
    6: "speed_up",
    7: "heal_blocked",
    8: "visual_debuff",
    9: "purge",
}


class PowerDown(pygame.sprite.Sprite):
    _frames = None

    def __init__(self, screen_width, ground_y, speed, power_down_index=None):
        super().__init__(self.containers)
        self.screen_width = screen_width
        self.ground_y = ground_y
        self.speed = speed
        self.collidable = True
        available_indices = tuple(POWER_DOWN_EFFECTS)
        self.power_down_index = power_down_index if power_down_index is not None else random.choice(available_indices)
        self.effect_name = POWER_DOWN_EFFECTS[self.power_down_index]
        self.damage = 0

        frames = self._load_frames()
        self.image = frames[self.power_down_index]
        self.rect = self.image.get_rect(bottomright=(screen_width, ground_y - GROUND_OFFSET))
        self.x = float(self.rect.x)

    @classmethod
    def _load_frames(cls):
        if cls._frames is not None:
            return cls._frames

        sheet = load_image(SPRITE_PATH)
        cls._frames = load_sheet_frames(sheet, FRAME_SIZE, FRAME_SIZE, scale_to=(DISPLAY_SIZE, DISPLAY_SIZE))
        return cls._frames

    def update(self, dt):
        self.x -= self.speed * dt
        self.rect.x = round(self.x)
        if self.rect.right < 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
