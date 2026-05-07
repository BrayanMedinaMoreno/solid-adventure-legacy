# src/entities/npc.py
import pygame
from settings import *

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, color, nombre):
        self.groups = game.all_sprites, game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.nombre = nombre
        self.x = x
        self.y = y
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (TILESIZE//2, TILESIZE//2), TILESIZE//2 - 4)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def interact(self):
        pass

class Mercader(NPC):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, YELLOW, "Mercader")

    def interact(self):
        self.game.log.add_message("[MERCADER] ¡Bienvenido a mi tienda!")
        self.game.state = "SHOP"
        self.game.menu_index = 0

class Banquero(NPC):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, LIGHT_GREY, "Banquero")

    def interact(self):
        self.game.log.add_message("[BANQUERO] Protejo tus riquezas.")
        self.game.state = "BANK"
        self.game.menu_index = 0
