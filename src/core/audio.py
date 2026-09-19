import pygame
import os
import json


def load_sounds(game):
    sounds = {}
    sound_files = {
        "espada":   "assets/EfectosSonido/espada.wav",
        "hacha":    "assets/EfectosSonido/hacha_ataque.wav",
        "ballesta": "assets/EfectosSonido/ballesta_disparo.wav",
        "slime":    "assets/EfectosSonido/slime_ataque.wav",
        "goblin":   "assets/EfectosSonido/goblin_ataque.wav",
        "coins":    "assets/EfectosSonido/coins.wav",
        "muerte":   "assets/EfectosSonido/muerte.wav",
    }
    for name, path in sound_files.items():
        if os.path.exists(path):
            try:
                sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"No se pudo cargar sonido {path}: {e}")
    return sounds


def play_sfx(game, name):
    if hasattr(game, "sounds") and name in game.sounds:
        try:
            snd = game.sounds[name]
            if snd:
                vol = getattr(game, "sfx_volume", 0.6)
                snd.set_volume(vol)
                snd.play()
        except Exception as e:
            print(f"Error reproduciendo {name}: {e}")


def load_music_volume(game=None):
    try:
        if os.path.exists("saves/config.json"):
            with open("saves/config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return float(data.get("music_volume", 0.35))
    except Exception:
        pass
    return 0.35


def save_music_volume(game):
    try:
        os.makedirs("saves", exist_ok=True)
        with open("saves/config.json", "w", encoding="utf-8") as f:
            json.dump({"music_volume": game.music_volume}, f)
    except Exception as e:
        print("Error guardando config.json:", e)


def set_music_volume(game, vol):
    game.music_volume = round(max(0.0, min(1.0, vol)), 2)
    try:
        pygame.mixer.music.set_volume(game.music_volume)
    except Exception:
        pass
    save_music_volume(game)
    game.music_volume_display_timer = 1.8


def change_music_volume(game, delta):
    set_music_volume(game, game.music_volume + delta)


def play_music(game, path):
    """Carga y reproduce una pista de música si no está ya reproduciéndose."""
    if game.current_music != path:
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(game.music_volume)
            pygame.mixer.music.play(-1)
            game.current_music = path
        except Exception as e:
            print(f"Error al reproducir música {path}: {e}")
