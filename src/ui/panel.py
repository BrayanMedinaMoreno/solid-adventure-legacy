# src/ui/panel.py
import pygame
from settings import *

class Panel:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont('Consolas', 18)
        self.title_font = pygame.font.SysFont('Consolas', 24, bold=True)

    def draw_text(self, surface, text, x, y, font, color=WHITE):
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def draw(self, surface):
        player = self.game.player
        start_x = MAP_WIDTH + 20
        y = 20

        # Ubicación (Piso actual)
        loc_text = "PUEBLO (SEGURO)" if self.game.profundidad == 0 else f"CALABOZO: NIVEL {self.game.profundidad}"
        loc_color = GREEN if self.game.profundidad == 0 else RED
        self.draw_text(surface, loc_text, start_x, y, self.title_font, loc_color)
        y += 40

        # Título
        self.draw_text(surface, "PLAYER STATS", start_x, y, self.title_font, CYAN)
        y += 40

        # Stats (Leemos de la lógica antigua integrada)
        logic = player.logic
        arma_actual = logic.arma if hasattr(logic, 'arma') else logic.espada
        self.draw_text(surface, f"Lvl: {logic.nivel}  XP: {logic.xp}/{logic.xp_necesaria}", start_x, y, self.font, YELLOW)
        y += 25
        
        stats = [
            f"HP:  {logic.vida}/{logic.max_vida}",
            f"ATT: {logic.fuerza} (+{arma_actual.daño})",
            f"DEF: {logic.defensa}"
        ]
        
        for stat in stats:
            self.draw_text(surface, stat, start_x, y, self.font)
            y += 20

        # Dinero
        y += 20
        self.draw_text(surface, "DINERO:", start_x, y, self.title_font, CYAN)
        y += 30
        self.draw_text(surface, f"Platino: {logic.platino}", start_x, y, self.font, (200, 200, 255))
        y += 20
        self.draw_text(surface, f"Oro:     {logic.oro}", start_x, y, self.font, YELLOW)
        y += 20
        self.draw_text(surface, f"Plata:   {logic.plata}", start_x, y, self.font, LIGHT_GREY)
        y += 20
        self.draw_text(surface, f"Cobre:   {logic.cobre}", start_x, y, self.font, (205, 127, 50))
        y += 20

        y += 20
        self.draw_text(surface, "INVENTARIO:", start_x, y, self.title_font, CYAN)
        y += 30
        
        self.draw_text(surface, "[Tecla I] Abrir Mochila", start_x, y, self.font, LIGHT_GREY)
        
        # Mostrar estadísticas del enemigo si estamos en combate
        if self.game.state == "COMBAT" and self.game.current_enemy:
            y += 50
            enemy = self.game.current_enemy
            self.draw_text(surface, f"VS: {enemy.name.upper()}", start_x, y, self.title_font, RED)
            y += 30
            self.draw_text(surface, f"HP:  {enemy.vida}/{enemy.max_vida}", start_x, y, self.font, RED)
            y += 20
            self.draw_text(surface, f"ATT: {enemy.fuerza}", start_x, y, self.font, RED)
            y += 20
            self.draw_text(surface, f"DEF: {enemy.defensa}", start_x, y, self.font, RED)
        
