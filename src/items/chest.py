import pygame
import random
from settings import *
from logic.armas import Arma
from items.potion import Pocion

class Chest(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.chests
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        try:
            self.image = pygame.image.load('assets/sprites/cofre.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except FileNotFoundError:
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.rect(self.image, YELLOW, (10, TILESIZE//2, TILESIZE-20, TILESIZE//2-10))

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def open(self):
        # Generar aleatoriamente
        if random.random() < 0.4: # 40% de probabilidad de ser poción
            item = Pocion()
        else:
            nombres = ["Espada Oxidada", "Daga Rápida", "Hacha Pesada", "Pistola Vieja"]
            daño = random.randint(5, 20)
            item = Arma(random.choice(nombres), daño)
        
        self.game.log.add_message(f"[COFRE] Obtienes {item.nombre}")
        self.kill() # Eliminar cofre del mapa
        return item
