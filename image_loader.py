import pygame
from PIL import Image


def load_image(path):
    if pygame.image.get_extended():
        return pygame.image.load(path).convert_alpha()

    image = Image.open(path).convert("RGBA")
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()
