# src/entities/enemy_types.py
from entities.enemy import Enemy
from settings import *

class Goblin(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Goblin"
        self.vida = 20
        self.max_vida = 20
        self.fuerza = 5
        self.defensa = 2
        self.xp_recompensa = 20

class Orco(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Orco Fuerte"
        self.vida = 40
        self.max_vida = 40
        self.fuerza = 12
        self.defensa = 8
        self.xp_recompensa = 50
        
        # Le cambiamos el color al fallback si no hay imagen propia
        self.image.fill((0,0,0,0)) # Limpiar
        import pygame
        pygame.draw.polygon(self.image, GREEN, [(TILESIZE//2, 4), (TILESIZE-4, TILESIZE-4), (4, TILESIZE-4)])

# ¡Aquí puedes añadir más clases de enemigos en el futuro!
# Simplemente copia Orco o Goblin y cámbiale las stats.
