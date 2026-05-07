# src/entities/enemy.py
import pygame
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Cargar y escalar imagen
        try:
            self.image = pygame.image.load('../assets/sprites/enemigo_base.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except FileNotFoundError:
            # Fallback si no encuentra la imagen (triangulo rojo como en la imagen de referencia)
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, RED, [(TILESIZE//2, 4), (TILESIZE-4, TILESIZE-4), (4, TILESIZE-4)])

        self.rect = self.image.get_rect()
        
        # Posición en el grid
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

        # Stats del enemigo
        self.vida = 20
        self.max_vida = 20
        self.fuerza = 5
        self.defensa = 2
        self.name = "Goblin"
        self.xp_recompensa = 10

    def vivo(self):
        return self.vida > 0

    def morir(self, log=None):
        self.kill() # Eliminar del grupo de sprites

    def draw_hp_bar(self, surface):
        # Dibujar barra de vida sobre el enemigo
        bar_width = TILESIZE - 8
        bar_height = 6
        fill = (self.vida / self.max_vida) * bar_width
        outline_rect = pygame.Rect(self.rect.x + 4, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x + 4, self.rect.y - 10, fill, bar_height)
        
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)

