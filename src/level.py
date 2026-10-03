import pygame
import random
from settings import *

class Level:
    def __init__(self, profundidad=1):
        self.profundidad = profundidad
        self.width_tiles = 100 # Mapa mucho más grande
        self.height_tiles = 100
        self.map_data = []
        self.floor_tiles = []
        self.entrance = None
        self.stairs_down = None
        
        # Cargar Sprites
        self.sprites = {}
        try:
            self.sprites['pasto_mucho'] = pygame.image.load('assets/sprites/pasto_mucho.png').convert_alpha()
            self.sprites['pasto_poco'] = pygame.image.load('assets/sprites/pasto_poco.png').convert_alpha()
            self.sprites['tierra_camino'] = pygame.image.load('assets/sprites/tierra camino.png').convert_alpha()
            self.sprites['dungeon_wall'] = pygame.image.load('assets/sprites/dungeon_wall.png').convert_alpha()
            self.sprites['dungeon_floor'] = pygame.image.load('assets/sprites/dungeon_floor.png').convert_alpha()
            self.sprites['wall_top'] = pygame.image.load('assets/sprites/wall_top.png').convert_alpha()
            self.sprites['wall_front'] = pygame.image.load('assets/sprites/wall_front.png').convert_alpha()
            self.sprites['floor_tile'] = pygame.image.load('assets/sprites/floor_tile.png').convert_alpha()
            self.sprites['escaleras'] = pygame.image.load('assets/sprites/escaleras.png').convert_alpha()
            
            # Nuevos Assets de Kenney
            self.sprites['kenney_grass'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0000.png').convert_alpha()
            self.sprites['kenney_grass_var'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0001.png').convert_alpha()
            self.sprites['kenney_path'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0025.png').convert_alpha()
            self.sprites['kenney_wall'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0101.png').convert_alpha()
            self.sprites['kenney_tree'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0004.png').convert_alpha()
            self.sprites['kenney_pine'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0003.png').convert_alpha()
            
            # Blue Roof House
            self.sprites['house_blue_r_l'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0048.png').convert_alpha()
            self.sprites['house_blue_r_m'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0049.png').convert_alpha()
            self.sprites['house_blue_r_r'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0050.png').convert_alpha()
            self.sprites['house_brown_w_w'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0072.png').convert_alpha()
            self.sprites['house_brown_w_d'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0073.png').convert_alpha()
            
            # Red Roof House
            self.sprites['house_red_r_l'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0052.png').convert_alpha()
            self.sprites['house_red_r_m'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0053.png').convert_alpha()
            self.sprites['house_red_r_r'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0054.png').convert_alpha()
            self.sprites['house_grey_w_w'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0076.png').convert_alpha()
            self.sprites['house_grey_w_d'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0077.png').convert_alpha()
            self.sprites['kenney_grass_var'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0001.png').convert_alpha()
            self.sprites['kenney_path'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0025.png').convert_alpha()
            self.sprites['kenney_wall'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0048.png').convert_alpha()
            self.sprites['kenney_water'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0112.png').convert_alpha()
            self.sprites['kenney_tree'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0005.png').convert_alpha()
            self.sprites['kenney_roof'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0064.png').convert_alpha()
            self.sprites['kenney_house'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0076.png').convert_alpha()
            self.sprites['kenney_grass_var'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0001.png').convert_alpha()
            self.sprites['kenney_path'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0025.png').convert_alpha()
            self.sprites['kenney_wall'] = pygame.image.load('assets/kenney_tiny_town/Tiles/tile_0048.png').convert_alpha()
            
            # Escalar
            for key in self.sprites:
                self.sprites[key] = pygame.transform.scale(self.sprites[key], (TILESIZE, TILESIZE))
        except FileNotFoundError:
            pass

        self.generate_level()
        
        # Inicializar Niebla de Guerra
        if self.profundidad == 0:
            # En el pueblo todo está explorado
            self.explored = [[True for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
        else:
            self.explored = [[False for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]

    def generate_level(self):
        if self.profundidad == 0:
            # Pueblo (Zona Segura)
            self.map_data = [[4 for _ in range(self.width_tiles)] for _ in range(self.height_tiles)] # Fondo de bosque
            
            # Area central de pasto
            for y in range(30, 70):
                for x in range(30, 70):
                    self.map_data[y][x] = 0
                    self.floor_tiles.append((x, y))
                    
            # Muros del pueblo
            for x in range(29, 71):
                self.map_data[29][x] = 1
                self.map_data[70][x] = 1
            for y in range(29, 71):
                self.map_data[y][29] = 1
                self.map_data[y][70] = 1
            
            # Arboles decorativos dentro del pueblo
            import random as rnd
            rng = rnd.Random(88) # Nueva semilla
            for _ in range(60):
                tx = rng.randint(31, 68)
                ty = rng.randint(31, 68)
                if self.map_data[ty][tx] == 0:
                    self.map_data[ty][tx] = 3 if rng.random() > 0.5 else 4
                    
            # Limpiar el centro para caminos y NPCs
            mid_y = self.height_tiles // 2
            mid_x = self.width_tiles // 2
            for y in range(mid_y-10, mid_y+10):
                for x in range(mid_x-10, mid_x+10):
                    if self.map_data[y][x] in [3, 4]:
                        self.map_data[y][x] = 0
            
            # Caminos de tierra (hacemos un camino continuo y natural)
            for x in range(mid_x - 8, mid_x + 9):
                self.map_data[mid_y][x] = 2
                self.map_data[mid_y+1][x] = 2
            for y in range(mid_y - 8, mid_y + 6):
                self.map_data[y][mid_x] = 2
                self.map_data[y][mid_x-1] = 2
                
            # Conectar Herrero al camino vertical
            for x in range(mid_x - 6, mid_x):
                self.map_data[mid_y + 4][x] = 2
                
            # Construir casas (3x2)
            def build_house(hx, hy, type='blue'):
                roof = [10, 11, 12] if type == 'blue' else [20, 21, 22]
                wall = [13, 14, 13] if type == 'blue' else [23, 24, 23]
                
                # Techo
                self.map_data[hy-1][hx-1] = roof[0]
                self.map_data[hy-1][hx] = roof[1]
                self.map_data[hy-1][hx+1] = roof[2]
                # Paredes
                self.map_data[hy][hx-1] = wall[0]
                self.map_data[hy][hx] = wall[1] # Puerta
                self.map_data[hy][hx+1] = wall[2]
                
                # Caminito a la puerta
                self.map_data[hy+1][hx] = 2
            
            build_house(mid_x - 3, mid_y - 2, 'blue')  # Mercader casa
            build_house(mid_x + 4, mid_y - 2, 'red')   # Banquero casa (ampliamos 1 para que no choquen)
            build_house(mid_x - 6, mid_y + 3, 'red')   # Herrero casa

            self.stairs_down = (mid_x, mid_y - 6) # Escalera hacia la cruz / calabozo
            self.entrance = (mid_x, mid_y + 4)
            return

        # Llenar todo de muros (1) para calabozo
        self.map_data = [[1 for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
        self.floor_tiles = []
        rooms = []
        max_rooms = 15 + self.profundidad * 2
        min_room_size = 5
        max_room_size = 15

        for _ in range(max_rooms):
            # Tamaño y posición aleatoria
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, self.width_tiles - w - 1)
            y = random.randint(1, self.height_tiles - h - 1)

            new_room = pygame.Rect(x, y, w, h)
            
            # Verificar si se cruza con otras habitaciones
            intersects = False
            for other_room in rooms:
                if new_room.inflate(2, 2).colliderect(other_room): # Margen de 1 tile
                    intersects = True
                    break
            
            if not intersects:
                self.carve_room(new_room)
                if len(rooms) > 0:
                    # Conectar con la habitación anterior
                    prev_x, prev_y = rooms[-1].center
                    new_x, new_y = new_room.center
                    self.carve_corridor(prev_x, prev_y, new_x, new_y)
                
                rooms.append(new_room)

        # Recopilar todas las baldosas de suelo
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                if self.map_data[y][x] == 0:
                    self.floor_tiles.append((x, y))

        if rooms:
            # La entrada es el centro de la primera habitación
            self.entrance = rooms[0].center
            # Colocar escaleras de bajada en la última habitación
            self.stairs_down = rooms[-1].center
        else:
            # Fallback
            self.stairs_down = (self.width_tiles // 2, self.height_tiles // 2)

    def carve_room(self, room):
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                self.map_data[y][x] = 0

    def carve_corridor(self, x1, y1, x2, y2):
        # Pasillo en L
        if random.random() < 0.5:
            # Horizontal luego vertical
            self.carve_h_line(x1, x2, y1)
            self.carve_v_line(y1, y2, x2)
        else:
            # Vertical luego horizontal
            self.carve_v_line(y1, y2, x1)
            self.carve_h_line(x1, x2, y2)

    def carve_h_line(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map_data[y][x] = 0

    def carve_v_line(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map_data[y][x] = 0

    def draw(self, surface, camera_x=0, camera_y=0, game=None):
        # Limitar el rango de dibujo para optimizar
        start_x = max(0, int(camera_x // TILESIZE))
        end_x = min(self.width_tiles, int((camera_x + MAP_WIDTH) // TILESIZE) + 1)
        start_y = max(0, int(camera_y // TILESIZE))
        end_y = min(self.height_tiles, int((camera_y + HEIGHT) // TILESIZE) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                rect = pygame.Rect(x * TILESIZE - camera_x, y * TILESIZE - camera_y, TILESIZE, TILESIZE)
                
                # Niebla de Guerra
                if not self.explored[y][x]:
                    pygame.draw.rect(surface, (0, 0, 0), rect) # Dibujar negro absoluto
                    continue
                
                tile = self.map_data[y][x]
                
                if self.profundidad == 0:
                    # Siempre dibujar el pasto base debajo de cualquier estructura del pueblo
                    local_rng = random.Random(x * 77 + y * 33)
                    if local_rng.random() < 0.15:
                        surface.blit(self.sprites['kenney_grass_var'], rect)
                    else:
                        surface.blit(self.sprites['kenney_grass'], rect)
                        
                    # Dibujar Pueblo con sprites de Kenney
                    if tile == 1:
                        surface.blit(self.sprites['kenney_wall'], rect)
                    elif tile == 2:
                        surface.blit(self.sprites['kenney_path'], rect)
                    elif tile == 3:
                        surface.blit(self.sprites['kenney_tree'], rect)
                    elif tile == 4:
                        surface.blit(self.sprites['kenney_pine'], rect)
                    elif tile == 10:
                        surface.blit(self.sprites['house_blue_r_l'], rect)
                    elif tile == 11:
                        surface.blit(self.sprites['house_blue_r_m'], rect)
                    elif tile == 12:
                        surface.blit(self.sprites['house_blue_r_r'], rect)
                    elif tile == 13:
                        surface.blit(self.sprites['house_brown_w_w'], rect)
                    elif tile == 14:
                        surface.blit(self.sprites['house_brown_w_d'], rect)
                    elif tile == 20:
                        surface.blit(self.sprites['house_red_r_l'], rect)
                    elif tile == 21:
                        surface.blit(self.sprites['house_red_r_m'], rect)
                    elif tile == 22:
                        surface.blit(self.sprites['house_red_r_r'], rect)
                    elif tile == 23:
                        surface.blit(self.sprites['house_grey_w_w'], rect)
                    elif tile == 24:
                        surface.blit(self.sprites['house_grey_w_d'], rect)
                else:
                    # Dibujar Calabozo con Profundidad (Estilo Zelda/Reference)
                    if tile == 1:
                        # Determinar si es parte superior o cara frontal
                        # Si abajo hay suelo (0), es una cara frontal
                        is_front = False
                        if y + 1 < self.height_tiles and self.map_data[y+1][x] == 0:
                            is_front = True
                            
                        if is_front and 'wall_front' in self.sprites:
                            surface.blit(self.sprites['wall_front'], rect)
                        elif not is_front and 'wall_top' in self.sprites:
                            surface.blit(self.sprites['wall_top'], rect)
                        else:
                            # Fallback
                            color = DARK_GREY if is_front else LIGHT_GREY
                            pygame.draw.rect(surface, color, rect)
                    else:
                        # Suelo
                        if 'floor_tile' in self.sprites:
                            surface.blit(self.sprites['floor_tile'], rect)
                        else:
                            pygame.draw.rect(surface, (30, 25, 20), rect) # Color tierra/piedra

        # Decoración (estrellas/puntos en el suelo para el calabozo)
        # Solo dibujar si NO estamos usando sprites de suelo para evitar "ruido"
        if self.profundidad > 0 and 'dungeon_floor' not in self.sprites:
            for tile_x, tile_y in self.floor_tiles:
                local_rng = random.Random(tile_x * 100 + tile_y) 
                for _ in range(2):
                    px = tile_x * TILESIZE + local_rng.randint(5, TILESIZE - 5) - camera_x
                    py = tile_y * TILESIZE + local_rng.randint(5, TILESIZE - 5) - camera_y
                    pygame.draw.circle(surface, (100, 100, 100), (px, py), 1)

        # Dibujar escaleras
        font = pygame.font.SysFont('Consolas', 30, bold=True)
        # En el calabozo, las escaleras se ven "bloqueadas" (rojas) si hay enemigos
        is_cleared = True
        if game and self.profundidad > 0 and len(game.enemies) > 0:
            is_cleared = False
            
        if self.stairs_down:
            rect = pygame.Rect(self.stairs_down[0] * TILESIZE - camera_x, self.stairs_down[1] * TILESIZE - camera_y, TILESIZE, TILESIZE)
            if 'escaleras' in self.sprites:
                surface.blit(self.sprites['escaleras'], rect)
                if not is_cleared:
                    # Tinte rojo semitransparente y cruz
                    s = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
                    s.fill((150, 0, 0, 150))
                    surface.blit(s, rect)
                    surface.blit(font.render("X", True, WHITE), (rect.x + TILESIZE//3, rect.y + TILESIZE//4))
            else:
                color = (50, 20, 100) if is_cleared else (150, 0, 0)
                pygame.draw.rect(surface, color, rect)
                label = ">" if is_cleared else "X"
                surface.blit(font.render(label, True, WHITE), (rect.x + TILESIZE//3, rect.y + TILESIZE//4))

