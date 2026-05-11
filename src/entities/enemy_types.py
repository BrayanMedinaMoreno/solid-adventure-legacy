import pygame
from entities.enemy import Enemy
from settings import *

class Goblin(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Goblin"
        self.vida = 50
        self.max_vida = 50
        self.fuerza = 14
        self.defensa = 2
        self.xp_recompensa = 20

class Orco(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Orco Fuerte"
        self.vida = 100
        self.max_vida = 100
        self.fuerza = 28
        self.defensa = 10
        self.xp_recompensa = 50
        
        # Le cambiamos el color al fallback si no hay imagen propia
        self.image.fill((0,0,0,0)) # Limpiar
        pygame.draw.polygon(self.image, GREEN, [(TILESIZE//2, 4), (TILESIZE-4, TILESIZE-4), (4, TILESIZE-4)])

class Slime(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Slime Pegajoso"
        self.vida = 40
        self.max_vida = 40
        self.fuerza = 10
        self.defensa = 1
        self.xp_recompensa = 15
        
        # Cargar el nuevo sprite específico
        try:
            self.image = pygame.image.load('assets/sprites/slime definitivo.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except:
            pass # Mantiene el de enemigo_base si falla

class SlimeBoss(Slime):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "REY SLIME (BOSS)"
        self.max_vida = 300
        self.vida = 300
        self.fuerza = 35
        self.defensa = 5
        self.xp_recompensa = 500
        self.titulo = "Soberano de la Viscosidad"
        self.last_stand_used = False
        
        # Escalar visualmente para que se vea como un jefe
        self.image = pygame.transform.scale(self.image, (int(TILESIZE*1.5), int(TILESIZE*1.5)))
        self.rect = self.image.get_rect(center=self.rect.center)
