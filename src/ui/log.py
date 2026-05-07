# src/ui/log.py
import pygame
from settings import *

class Log:
    def __init__(self):
        self.messages = []
        self.font = pygame.font.SysFont('Consolas', 16)
        self.max_messages = 4

    def add_message(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def draw(self, surface):
        start_x = MAP_WIDTH + 20
        y_start = HEIGHT - (self.max_messages * 20) - 40
        
        # Fondo oscuro para el log
        log_rect = pygame.Rect(MAP_WIDTH + 10, y_start, UI_WIDTH - 20, (self.max_messages * 20) + 30)
        pygame.draw.rect(surface, (15, 15, 15), log_rect)
        pygame.draw.rect(surface, (50, 50, 50), log_rect, 1)

        y = y_start + 10
        
        # Título Log
        title_font = pygame.font.SysFont('Consolas', 18, bold=True)
        text_surface = title_font.render("LOG:", True, CYAN)
        surface.blit(text_surface, (start_x, y))
        y += 25

        for message in self.messages:
            text_surface = self.font.render(message, True, LIGHT_GREY)
            surface.blit(text_surface, (start_x, y))
            y += 20
