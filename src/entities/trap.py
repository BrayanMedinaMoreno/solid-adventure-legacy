# src/entities/trap.py
import pygame
import random
from settings import *

class Trap(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.traps
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        
        # Imagen de la trampa (subtle para que el jugador tenga que fijarse)
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        # Dibujamos unas púas pequeñas o una placa de presión
        pygame.draw.rect(self.image, (40, 40, 40), (TILESIZE//4, TILESIZE//4, TILESIZE//2, TILESIZE//2), 2)
        pygame.draw.line(self.image, (60, 60, 60), (TILESIZE//2, TILESIZE//4), (TILESIZE//2, TILESIZE*3//4), 1)
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        
        # Posibilidad baja de 25 de daño, resto 15
        if random.random() < 0.15:
            self.damage = 25
            self.rarity = "CRÍTICA"
        else:
            self.damage = 15
            self.rarity = "COMÚN"
            
        self.triggered = False

    def trigger(self):
        if self.triggered: return
        self.triggered = True
        
        self.game.log.add_message(f"[TRAMPA] ¡Has pisado una trampa {self.rarity}!")
        
        # Intentar recibir daño (aquí es donde entra la ESQUIVA de títulos)
        if self.game.player.logic.recibir_daño(self.damage, tipo="trampa", log=self.game.log):
            # Si NO esquivó
            self.game.spawn_floating_text(f"-{self.damage} HP", self.rect.centerx, self.rect.top, RED)
        
        # Cambiar apariencia para mostrar que se activó
        self.image.fill((100, 0, 0, 100))
        # Desaparece después de un tiempo o simplemente queda ahí
        # self.kill() 
