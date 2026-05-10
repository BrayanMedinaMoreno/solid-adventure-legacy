import pygame
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
        pygame.draw.polygon(self.image, GREEN, [(TILESIZE//2, 4), (TILESIZE-4, TILESIZE-4), (4, TILESIZE-4)])

class Slime(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Slime Pegajoso"
        self.vida = 15
        self.max_vida = 15
        self.fuerza = 4
        self.defensa = 1
        self.xp_recompensa = 15
        
        # Cargar el nuevo sprite específico
        try:
            self.image = pygame.image.load('assets/sprites/slime definitivo.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except:
            pass # Mantiene el de enemigo_base si falla


