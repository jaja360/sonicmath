from enum import Enum
import os

import pygame

from image_loader import load_image

SPRITE_PATH = os.path.join("assets", "sprites", "sonic.png")

BASE_FRAME_TIME = 0.1
SONIC_SCALE = 3
SONIC_X = 10

FRAME_WIDTH = 50
FRAME_HEIGHT = 100
FRAME_COLUMNS = 12
FRAME_ROWS = 7


class SonicState(Enum):
    STOP_TO_RUN = 0
    RUN_LOOP = 1
    RUN_OBSTACLE_RUN = 2
    RUN_JUMP_RUN = 3
    LATE_JUMP_HIT = 4
    RUN_OBSTACLE_GAMEOVER = 5
    RUN_ENDGAME = 6


TRANSITION_STATES = {
    SonicState.STOP_TO_RUN: SonicState.RUN_LOOP,
    SonicState.RUN_OBSTACLE_RUN: SonicState.RUN_LOOP,
}
HOLD_FINAL_FRAME_STATES = {
    SonicState.RUN_OBSTACLE_GAMEOVER,
}


class Sonic(pygame.sprite.Sprite):

    def __init__(self, ground_y):
        super().__init__(self.containers)
        self.current_state = SonicState.STOP_TO_RUN
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_time = BASE_FRAME_TIME
        self.set_speed(150)
        self.ground_y = ground_y

        sheet = load_image(SPRITE_PATH)
        self.animations = self._load_animations(sheet)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self._set_image(self.animations[self.current_state][self.current_frame])

    def _load_animations(self, sheet):
        animations = {}
        for state in SonicState:
            animations[state] = self._load_row_frames(sheet, state.value)

        return animations

    def _load_row_frames(self, sheet, row):
        frames = []
        for col in range(FRAME_COLUMNS):
            rect = pygame.Rect(col * FRAME_WIDTH, row * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
            frame = sheet.subsurface(rect).copy()
            frame = pygame.transform.scale(frame, (FRAME_WIDTH * SONIC_SCALE, FRAME_HEIGHT * SONIC_SCALE))
            frames.append(frame)

        return frames

    def set_state(self, state):
        if not isinstance(state, SonicState):
            raise TypeError("state must be a SonicState")

        if state == self.current_state:
            return

        self.current_state = state
        self.current_frame = 0
        self.frame_timer = 0.0
        self._set_image(self.animations[self.current_state][self.current_frame])

    def set_speed(self, speed):
        self.frame_time = BASE_FRAME_TIME * 150 / speed

    def _set_image(self, image):
        bottomleft = self.rect.bottomleft
        if bottomleft == (0, 0):
            bottomleft = (SONIC_X, self.ground_y)
        self.image = image
        self.rect = self.image.get_rect(bottomleft=bottomleft)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer < self.frame_time:
            return

        self.frame_timer = 0.0
        frames = self.animations[self.current_state]

        if self.current_frame == len(frames) - 1:
            next_state = TRANSITION_STATES.get(self.current_state)
            if next_state is not None:
                self.set_state(next_state)
                return

            if self.current_state in HOLD_FINAL_FRAME_STATES:
                return

        self.current_frame = (self.current_frame + 1) % len(frames)
        self._set_image(frames[self.current_frame])
