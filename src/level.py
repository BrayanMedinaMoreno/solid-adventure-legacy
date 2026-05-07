# src/level.py
import pygame
import random
from settings import *

class Level:
    def __init__(self, profundidad=1):
        self.profundidad = profundidad
        self.width_tiles = MAP_WIDTH // TILESIZE
        self.height_tiles = HEIGHT // TILESIZE
        self.map_data = []
        self.floor_tiles = []
        self.stairs_up = None
        self.stairs_down = None
        self.generate_level()

    def generate_level(self):
        if self.profundidad == 0:
            # Pueblo (Zona Segura)
            self.map_data = [[1 for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
            for y in range(2, self.height_tiles - 2):
                for x in range(2, self.width_tiles - 2):
                    self.map_data[y][x] = 0
                    self.floor_tiles.append((x, y))
            self.stairs_down = (self.width_tiles // 2, self.height_tiles - 4)
            return

        # Llenar todo de muros (1) para calabozo
        self.map_data = [[1 for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
        
        # Generación procedimental simple: random walk (borracho)
        # Empezar en el centro
        x = self.width_tiles // 2
        y = self.height_tiles // 2
        self.map_data[y][x] = 0
        self.floor_tiles = [(x, y)]
        
        # Iteraciones para vaciar espacio
        max_floor_tiles = (self.width_tiles * self.height_tiles) // 3
        current_floor_tiles = 1
        
        while current_floor_tiles < max_floor_tiles:
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            x += direction[0]
            y += direction[1]
            
            # Mantenerse dentro de los límites
            x = max(1, min(self.width_tiles - 2, x))
            y = max(1, min(self.height_tiles - 2, y))
            
            if self.map_data[y][x] == 1:
                self.map_data[y][x] = 0
                self.floor_tiles.append((x, y))
                current_floor_tiles += 1
                
        # Colocar escaleras de subida en el punto de inicio
        self.stairs_up = self.floor_tiles[0]
        # Colocar escaleras de bajada en el último punto generado
        self.stairs_down = self.floor_tiles[-1]

    def draw(self, surface):
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
                if tile == 1:
                    # Muro
                    pygame.draw.rect(surface, LIGHT_GREY, rect)
                    pygame.draw.rect(surface, DARK_GREY, rect, 1) # Borde
                else:
                    # Suelo
                    pygame.draw.rect(surface, (20, 20, 20), rect)
                    pygame.draw.rect(surface, (30, 30, 30), rect, 1) # Borde

        # Decoración (estrellas/puntos en el suelo como en la imagen)
        for tile_x, tile_y in self.floor_tiles:
            # Dibujar un par de puntos aleatorios en cada tile de suelo para textura
            random.seed(tile_x * 100 + tile_y) # Seed consistente para no parpadear
            for _ in range(2):
                px = tile_x * TILESIZE + random.randint(5, TILESIZE - 5)
                py = tile_y * TILESIZE + random.randint(5, TILESIZE - 5)
                pygame.draw.circle(surface, (100, 100, 100), (px, py), 1)

        # Dibujar escaleras
        font = pygame.font.SysFont('Consolas', 30, bold=True)
        if self.stairs_down:
            rect = pygame.Rect(self.stairs_down[0] * TILESIZE, self.stairs_down[1] * TILESIZE, TILESIZE, TILESIZE)
            pygame.draw.rect(surface, (50, 20, 100), rect)
            surface.blit(font.render(">", True, WHITE), (rect.x + TILESIZE//3, rect.y + TILESIZE//4))
            
        if self.stairs_up:
            rect = pygame.Rect(self.stairs_up[0] * TILESIZE, self.stairs_up[1] * TILESIZE, TILESIZE, TILESIZE)
            pygame.draw.rect(surface, (20, 100, 50), rect)
            surface.blit(font.render("<", True, WHITE), (rect.x + TILESIZE//3, rect.y + TILESIZE//4))

