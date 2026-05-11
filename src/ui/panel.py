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

    def draw_bar(self, surface, x, y, w, h, current, maximum, color, label=""):
        # Fondo de la barra
        pygame.draw.rect(surface, (40, 40, 40), (x, y, w, h))
        # Progreso
        if maximum > 0:
            fill_w = int((current / maximum) * w)
            fill_w = max(0, min(w, fill_w))
            pygame.draw.rect(surface, color, (x, y, fill_w, h))
        # Borde
        pygame.draw.rect(surface, WHITE, (x, y, w, h), 1)
        # Texto centrado o label
        if label:
            text = self.font.render(f"{label}: {current}/{maximum}", True, WHITE)
            surface.blit(text, (x + 5, y - 20))

    def draw(self, surface):
        player = self.game.player
        start_x = MAP_WIDTH + 20
        y = 20

        # Ubicación (Piso actual)
        loc_text = "PUEBLO (SEGURO)" if self.game.profundidad == 0 else f"CALABOZO: PISO {self.game.profundidad}"
        loc_color = GREEN if self.game.profundidad == 0 else (255, 100, 100)
        
        # Recuadro de ubicación
        pygame.draw.rect(surface, (25, 25, 35), (MAP_WIDTH + 10, y - 10, UI_WIDTH - 20, 40))
        pygame.draw.rect(surface, loc_color, (MAP_WIDTH + 10, y - 10, UI_WIDTH - 20, 40), 1)
        self.draw_text(surface, loc_text, start_x + 10, y, self.title_font, loc_color)
        y += 60

        # Sección Jugador
        logic = player.logic
        self.draw_text(surface, f"NIVEL {logic.nivel}", start_x, y, self.title_font, YELLOW)
        y += 25
        self.draw_text(surface, logic.titulo_actual, start_x, y, self.font, CYAN)
        y += 35
        
        # Barra de HP
        self.draw_bar(surface, start_x, y + 20, UI_WIDTH - 50, 15, logic.vida, logic.max_vida, RED, "HP")
        y += 55
        
        # Barra de XP
        self.draw_bar(surface, start_x, y + 20, UI_WIDTH - 50, 10, logic.xp, logic.xp_necesaria, CYAN, "XP")
        y += 50

        # Atributos con iconos simples
        arma_actual = logic.arma if hasattr(logic, 'arma') else logic.espada
        stats = [
            (f" ATK: {logic.fuerza} (+{arma_actual.daño})", (255, 150, 50)),
            (f" DEF: {logic.defensa}", (100, 150, 255))
        ]
        for text, color in stats:
            pygame.draw.rect(surface, color, (start_x, y + 5, 8, 8))
            self.draw_text(surface, text, start_x + 15, y, self.font, WHITE)
            y += 25

        # Dinero (Sección visual)
        y += 20
        pygame.draw.line(surface, (60, 60, 60), (MAP_WIDTH + 20, y), (WIDTH - 20, y), 1)
        y += 15
        self.draw_text(surface, "RIQUEZAS", start_x, y, self.title_font, (255, 215, 0))
        y += 30
        
        monedas = [
            (f"Platino: {logic.platino}", (200, 200, 255)),
            (f"Oro:     {logic.oro}", YELLOW),
            (f"Plata:   {logic.plata}", LIGHT_GREY),
            (f"Cobre:   {logic.cobre}", (205, 127, 50))
        ]
        for text, color in monedas:
            pygame.draw.circle(surface, color, (start_x + 5, y + 10), 5)
            self.draw_text(surface, text, start_x + 15, y, self.font, WHITE)
            y += 22

        # Equipamiento Actual
        y += 20
        pygame.draw.line(surface, (60, 60, 60), (MAP_WIDTH + 20, y), (WIDTH - 20, y), 1)
        y += 15
        self.draw_text(surface, "EQUIPO", start_x, y, self.title_font, CYAN)
        y += 30
        
        arma_actual = logic.arma if hasattr(logic, 'arma') else logic.espada
        armadura_actual = logic.armadura if hasattr(logic, 'armadura') else None
        
        self.draw_text(surface, "Arma:", start_x, y, self.font, LIGHT_GREY)
        self.draw_text(surface, arma_actual.nombre if arma_actual else "Ninguna", start_x + 60, y, self.font, YELLOW)
        y += 20
        self.draw_text(surface, "Armor:", start_x, y, self.font, LIGHT_GREY)
        self.draw_text(surface, armadura_actual.nombre if armadura_actual else "Ninguna", start_x + 60, y, self.font, YELLOW)
        y += 25

        # Enemigo en combate
        if self.game.state == "COMBAT" and self.game.current_enemy:
            y += 40
            pygame.draw.line(surface, RED, (MAP_WIDTH + 20, y), (WIDTH - 20, y), 2)
            y += 15
            enemy = self.game.current_enemy
            self.draw_text(surface, enemy.name.upper(), start_x, y, self.title_font, RED)
            y += 25
            if enemy.titulo:
                self.draw_text(surface, f"[{enemy.titulo}]", start_x, y, self.font, CYAN)
            y += 15
            self.draw_bar(surface, start_x, y, UI_WIDTH - 50, 12, enemy.vida, enemy.max_vida, RED, "ENEMIGO")
            y += 25
            self.draw_text(surface, f" ATK: {enemy.fuerza}  DEF: {enemy.defensa}", start_x, y, self.font, (255, 100, 100))
        
