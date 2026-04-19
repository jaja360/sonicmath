import pygame


class MusicPlayer:
    def __init__(self):
        self.current_path = None

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1.0)
        except NotImplementedError:
            print("Audio disabled: pygame mixer is not available in this environment.")
        except pygame.error as exc:
            print(f"Audio disabled: {exc}")

    def play(self, music_path, loops=-1):
        if music_path == self.current_path:
            return

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops=loops)
            self.current_path = music_path
        except pygame.error as exc:
            print(f"Audio disabled: could not play {music_path}: {exc}")

    def stop(self):
        pygame.mixer.music.stop()
        self.current_path = None
