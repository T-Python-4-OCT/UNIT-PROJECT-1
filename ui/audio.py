from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent.parent
SOUND_DIR = BASE_DIR / "assets" / "sounds"

SOUND_FILES = {
    "intro": "FantasyIntro",
    "forest": "forest",
    "gate": "gate",
    "success": "success",
    "mystery": "mystery",
    "journal": "journal",
}

SUPPORTED_FORMATS = (".mp3", ".wav", ".ogg")

SOUND_ENABLED = True
MUSIC_VOLUME = 0.25
EFFECT_VOLUME = 0.65

_audio_ready = False
_current_music = None
_sound_cache = {}


def initialize_audio():
    global _audio_ready

    if _audio_ready:
        return True

    try:
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=1024,
        )

        pygame.mixer.set_num_channels(8)
        _audio_ready = True

        return True

    except pygame.error as error:
        print(f"Audio unavailable: {error}")
        return False


def get_sound_path(sound_name):
    filename = SOUND_FILES.get(sound_name)

    if filename is None:
        return None

    for extension in SUPPORTED_FORMATS:
        path = SOUND_DIR / f"{filename}{extension}"

        if path.is_file():
            return path

    return None


def play_music(sound_name):
    global _current_music

    if not SOUND_ENABLED or not initialize_audio():
        return

    if (
        _current_music == sound_name
        and pygame.mixer.music.get_busy()
    ):
        return

    path = get_sound_path(sound_name)

    if path is None:
        print(f"Music file not found: {sound_name}")
        return

    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(loops=-1, fade_ms=800)

        _current_music = sound_name

    except pygame.error as error:
        print(f"Cannot play music: {error}")


def play_intro():
    play_music("intro")


def play_forest():
    play_music("forest")


def stop_forest():
    global _current_music

    if not _audio_ready:
        return

    if _current_music == "forest":
        pygame.mixer.music.stop()
        _current_music = None


def play_sound(sound_name):
    if not SOUND_ENABLED or not initialize_audio():
        return

    if sound_name in ("intro", "forest"):
        play_music(sound_name)
        return

    path = get_sound_path(sound_name)

    if path is None:
        print(f"Sound file not found: {sound_name}")
        return

    try:
        if sound_name not in _sound_cache:
            _sound_cache[sound_name] = pygame.mixer.Sound(
                str(path)
            )

        sound = _sound_cache[sound_name]
        sound.set_volume(EFFECT_VOLUME)
        sound.play()

    except pygame.error as error:
        print(f"Cannot play sound '{sound_name}': {error}")


def toggle_sound():
    global SOUND_ENABLED

    SOUND_ENABLED = not SOUND_ENABLED

    if not initialize_audio():
        return SOUND_ENABLED

    if SOUND_ENABLED:
        if _current_music is not None:
            pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()
        pygame.mixer.stop()

    return SOUND_ENABLED


def is_sound_enabled():
    return SOUND_ENABLED


def stop_all_audio():
    global _current_music

    if not _audio_ready:
        return

    pygame.mixer.music.stop()
    pygame.mixer.stop()
    _current_music = None


def set_music_volume(volume):
    global MUSIC_VOLUME

    MUSIC_VOLUME = max(0.0, min(1.0, float(volume)))

    if _audio_ready:
        pygame.mixer.music.set_volume(MUSIC_VOLUME)


def set_effect_volume(volume):
    global EFFECT_VOLUME

    EFFECT_VOLUME = max(0.0, min(1.0, float(volume)))

    for sound in _sound_cache.values():
        sound.set_volume(EFFECT_VOLUME)