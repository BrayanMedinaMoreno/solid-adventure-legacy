import os
import pygame

pygame.init()
pygame.display.set_mode((100, 100))

images = [
    'assets/sprites/pasto_mucho.png',
    'assets/sprites/pasto_poco.png',
    'assets/sprites/tierra camino.png',
    'assets/sprites/dungeon_wall.png',
    'assets/sprites/dungeon_floor.png',
    'assets/sprites/wall_top.png',
    'assets/sprites/wall_front.png',
    'assets/sprites/floor_tile.png',
    'assets/sprites/escaleras.png'
]

for img in images:
    path = os.path.join("dist", "SolidAdventureLegacy", img)
    if not os.path.exists(path):
        print(f"Missing: {img}")
