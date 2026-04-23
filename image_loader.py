import pygame
from PIL import Image


def load_image(path):
    if pygame.image.get_extended():
        return pygame.image.load(path).convert_alpha()

    image = Image.open(path).convert("RGBA")
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()


def load_sheet_frames(sheet, frame_width, frame_height, row=0, frame_count=None, scale_to=None):
    if frame_count is None:
        frame_count = sheet.get_width() // frame_width

    frames = []
    top = row * frame_height
    for col in range(frame_count):
        rect = pygame.Rect(col * frame_width, top, frame_width, frame_height)
        frame = sheet.subsurface(rect).copy()
        if scale_to is not None:
            frame = pygame.transform.scale(frame, scale_to)
        frames.append(frame)

    return frames
