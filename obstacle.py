import os
import random

import pygame

from image_loader import load_image

SPRITE_PATH = os.path.join("assets", "sprites", "obstacles.png")
FRAME_WIDTH = 100
FRAME_HEIGHT = 100
FRAME_COLUMNS = 18

# Damage dealt by each obstacle frame in the sheet, from left to right.
OBSTACLE_DAMAGE = [
    1, 2, 3, 4, 7,
    2, 8, 4, 5, 8,
    7, 4, 8, 6, 6,
    5, 0, 10,
]


class Obstacle(pygame.sprite.Sprite):
    _frames = None

    def __init__(self, screen_width, ground_y, speed, obstacle_index=None):
        super().__init__(self.containers)
        self.screen_width = screen_width
        self.ground_y = ground_y
        self.speed = speed
        self.collidable = True
        self.obstacle_index = obstacle_index if obstacle_index is not None else random.randrange(FRAME_COLUMNS)

        frames = self._load_frames()
        self.image = frames[self.obstacle_index]
        self.damage = OBSTACLE_DAMAGE[self.obstacle_index]
        self.rect = self.image.get_rect(bottomleft=(screen_width + 40, ground_y))

    @classmethod
    def _load_frames(cls):
        if cls._frames is not None:
            return cls._frames

        sheet = load_image(SPRITE_PATH)
        cls._frames = []
        for col in range(FRAME_COLUMNS):
            rect = pygame.Rect(col * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
            cls._frames.append(sheet.subsurface(rect).copy())

        return cls._frames

    def update(self, dt):
        self.rect.x -= round(self.speed * dt)
        if self.rect.right < 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
