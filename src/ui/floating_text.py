import pygame
from settings import *

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, groups, text, x, y, color=WHITE):
        super().__init__(groups)
        self.font = pygame.font.SysFont('Consolas', 20, bold=True)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.y_pos = float(y)
        self.speed = 1.0  # Velocidad de ascenso
        self.alpha = 255
        self.fade_speed = 3 # Velocidad de desvanecimiento
        
    def update(self, dt):
        # Mover hacia arriba
        self.y_pos -= self.speed
        self.rect.y = int(self.y_pos)
        
        # Desvanecer
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()
        else:
            # Crear una superficie con el alpha actual
            # Nota: para que funcione el alpha, la superficie debe ser compatible
            self.image.set_alpha(self.alpha)
