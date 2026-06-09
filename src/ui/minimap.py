# src/ui/minimap.py
import pygame
from settings import *

class Minimap:
    def __init__(self, game):
        self.game = game
        self.level = game.level
        self.width_tiles = self.level.width_tiles
        self.height_tiles = self.level.height_tiles
        
        # Tamaño de renderizado base (1 píxel por tile)
        self.base_surface = pygame.Surface((self.width_tiles, self.height_tiles), pygame.SRCALPHA)
        
        # Tamaño final en pantalla
        self.display_size = (150, 150)
        
        # Pre-renderizar terreno estático
        self.render_static_map()

    def render_static_map(self):
        self.base_surface.fill((0, 0, 0, 200)) # Oscuro por defecto
        
        is_pueblo = (self.game.profundidad == 0)
        
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                if hasattr(self.level, 'explored') and self.level.explored[y][x]:
                    self.update_fog_pixel(x, y, self.level.map_data[y][x], is_pueblo)

    def update_fog_pixel(self, x, y, tile, is_pueblo=None):
        if is_pueblo is None:
            is_pueblo = (self.game.profundidad == 0)
            
        if tile == 1:
            color = (100, 100, 100, 200) if not is_pueblo else (150, 150, 150, 200)
        else:
            color = (50, 40, 30, 200) if not is_pueblo else (34, 139, 34, 200)
            
        self.base_surface.set_at((x, y), color)

    def draw(self, surface):
        # 1. Copiamos la superficie estática a una temporal para superponer entidades dinámicas
        temp_surface = self.base_surface.copy()

        # 2. Dibujar entidades en la superficie temporal (1 píxel por tile)
        # Escaleras
        if self.level.stairs_down and hasattr(self.level, 'explored') and self.level.explored[self.level.stairs_down[1]][self.level.stairs_down[0]]:
            temp_surface.set_at(self.level.stairs_down, YELLOW)
            # Dibujar un poco más grande para visibilidad
            pygame.draw.circle(temp_surface, YELLOW, self.level.stairs_down, 1)

        # NPCs (Pueblo)
        if self.game.profundidad == 0:
            for npc in self.game.npcs:
                temp_surface.set_at((npc.x, npc.y), BLUE)

        # Enemigos (Calabozo)
        if self.game.profundidad > 0:
            for enemy in self.game.enemies:
                if hasattr(self.level, 'explored') and self.level.explored[enemy.y][enemy.x]:
                    temp_surface.set_at((enemy.x, enemy.y), RED)

        # Jugador
        if self.game.player:
            player_pos = (self.game.player.x, self.game.player.y)
            # Resaltar con círculo cyan
            pygame.draw.circle(temp_surface, CYAN, player_pos, 1)
            temp_surface.set_at(player_pos, CYAN)

        # 3. Escalar a tamaño de visualización
        scaled_minimap = pygame.transform.scale(temp_surface, self.display_size)

        # 4. Dibujar borde decorativo y fondo del panel
        # Posición superior derecha dentro del área de mapa
        margin = 15
        pos_x = MAP_WIDTH - self.display_size[0] - margin
        pos_y = margin
        
        # Fondo oscuro semi-transparente
        bg_rect = pygame.Rect(pos_x - 2, pos_y - 2, self.display_size[0] + 4, self.display_size[1] + 4)
        pygame.draw.rect(surface, (10, 10, 15), bg_rect)
        pygame.draw.rect(surface, CYAN, bg_rect, 1) # Borde

        # 5. Volcar minimapa en pantalla
        surface.blit(scaled_minimap, (pos_x, pos_y))
