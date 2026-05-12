# src/settings.py

# Dimensiones de la pantalla
WIDTH = 1024
HEIGHT = 768

# Tamaño del Grid / Tiles
TILESIZE = 32

# Configuración de FPS
FPS = 60

# Colores (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# UI Settings
UI_WIDTH = 300
MAP_WIDTH = WIDTH - UI_WIDTH

# Helper para PyInstaller (Rutas de recursos)
import sys
import os
def resource_path(relative_path):
    """ Obtiene la ruta absoluta del recurso, funciona para dev y para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
