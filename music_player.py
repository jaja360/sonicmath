import pygame


class MusicPlayer:
    def __init__(self, sound_enabled=True):
        self.current_path = None
        self.sound_enabled = sound_enabled

        if not self.sound_enabled:
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1.0)
        except NotImplementedError:
            self.sound_enabled = False
            print("Audio disabled: pygame mixer is not available in this environment.")
        except pygame.error as exc:
            self.sound_enabled = False
            print(f"Audio disabled: {exc}")

    def play(self, music_path, loops=-1):
        if not self.sound_enabled:
            return

        if music_path == self.current_path:
            return

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops=loops)
            self.current_path = music_path
        except pygame.error as exc:
            print(f"Audio disabled: could not play {music_path}: {exc}")

    def stop(self):
        if not self.sound_enabled:
            return

        pygame.mixer.music.stop()
        self.current_path = None

    def pause(self):
        if not self.sound_enabled:
            return

        pygame.mixer.music.pause()

    def unpause(self):
        if not self.sound_enabled:
            return

        pygame.mixer.music.unpause()
