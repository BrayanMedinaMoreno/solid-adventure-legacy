import pygame
from settings import *
from logic.personaje import Personaje
from logic.armas import Arma
from items.potion import Pocion, PocionRegreso, PocionMana

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, clase_elegida="guerrero", logic=None, inventory=None, nombre=None):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Cargar y escalar imagen
        try:
            self.image = pygame.image.load('assets/sprites/player.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except FileNotFoundError:
            # Fallback si no encuentra la imagen
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            color = CYAN if clase_elegida == "tirador" else BLUE
            pygame.draw.circle(self.image, color, (TILESIZE//2, TILESIZE//2), TILESIZE//2 - 4)

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.exact_x = float(self.rect.x)
        self.exact_y = float(self.rect.y)

        # Integración con la lógica
        if logic:
            self.logic = logic
            self.logic.game = self.game
            self.inventory = inventory if inventory is not None else []
        else:
            if not nombre:
                nombre = "Aventurero"

            # Stats de "Hoja en Blanco" (Equilibrado)
            self.logic = Personaje(nombre, fuerza=12, fe=0, defensa=6, vida=100)
            self.logic.game = self.game
            self.inventory = []
            
            # Equipo Inicial: El mundo te da las herramientas básicas para forjar tu camino
            espada_madera = Arma("Espada de Madera", 8, "fisico")
            honda_basica = Arma("Honda Vieja", 6, "distancia")
            
            self.logic.arma = espada_madera
            self.add_to_inventory(espada_madera)
            self.add_to_inventory(honda_basica)
            
            for _ in range(3):
                self.add_to_inventory(Pocion("media"))
            self.add_to_inventory(PocionRegreso())

    def move(self, dx=0, dy=0):
        # Comprobar si el destino es suelo o pared
        dest_x = self.x + dx
        dest_y = self.y + dy
        
        if 0 <= dest_x < self.game.level.width_tiles and 0 <= dest_y < self.game.level.height_tiles:
            if self.game.level.map_data[dest_y][dest_x] == 0:
                # Comprobar colisión con enemigos (Bump Combat)
                enemy = self.game.get_enemy_at(dest_x, dest_y)
                chest = self.game.get_chest_at(dest_x, dest_y)
                npc = self.game.get_npc_at(dest_x, dest_y)
                
                if enemy:
                    self.game.start_combat(enemy)
                elif npc:
                    npc.interact()
                elif chest:
                    nuevo_item = chest.open()
                    self.add_to_inventory(nuevo_item)
                    self.game.spawn_floating_text(f"+{nuevo_item.nombre}", self.rect.centerx, self.rect.top - 20, YELLOW)
                else:
                    self.x = dest_x
                    self.y = dest_y
                    
                    # Comprobar si hay una trampa en la nueva posición
                    trap = self.game.get_trap_at(self.x, self.y)
                    if trap:
                        trap.trigger()

                    # Comprobar escaleras
                    if self.game.level.stairs_down and (self.x, self.y) == self.game.level.stairs_down:
                        if self.game.profundidad == 0:
                            if self.game.max_profundidad > 1:
                                self.game.state = "LEVEL_SELECTION"
                                self.game.menu_index = 0
                            else:
                                self.game.went_down = True
                                self.game.profundidad = 1
                                self.game.log.add_message(f"[SISTEMA] Bajas al Nivel 1")
                                self.game.load_level()
                        elif len(self.game.enemies) > 0:
                            self.game.log.add_message("[SISTEMA] ¡Derrota a todos los enemigos para bajar!")
                        else:
                            self.game.went_down = True
                            self.game.profundidad += 1
                            self.game.max_profundidad = max(self.game.max_profundidad, self.game.profundidad)
                            self.game.log.add_message(f"[SISTEMA] Bajas al Nivel {self.game.profundidad}")
                            self.game.load_level()

    def add_to_inventory(self, item):
        # Solo apilar Pociones, Pociones de Regreso y Pociones de Maná
        if isinstance(item, (Pocion, PocionRegreso, PocionMana)):
            for inv_item in self.inventory:
                if type(inv_item) == type(item):
                    if isinstance(item, (Pocion, PocionMana)):
                        if inv_item.tipo == item.tipo:
                            inv_item.cantidad += 1
                            return
                    else: # PocionRegreso
                        inv_item.cantidad += 1
                        return
        
        # Si no es apilable o no se encontró en el inventario
        self.inventory.append(item)

    def update(self):
        target_x = self.x * TILESIZE
        target_y = self.y * TILESIZE
        
        # Revelar Niebla de Guerra (Radio de visión)
        if hasattr(self.game, 'level') and self.game.level:
            vision_radius = 5
            for y in range(max(0, self.y - vision_radius), min(self.game.level.height_tiles, self.y + vision_radius + 1)):
                for x in range(max(0, self.x - vision_radius), min(self.game.level.width_tiles, self.x + vision_radius + 1)):
                    # Distancia circular
                    if (x - self.x)**2 + (y - self.y)**2 <= vision_radius**2:
                        if not self.game.level.explored[y][x]:
                            self.game.level.explored[y][x] = True
                            # Notificar al minimapa
                            if hasattr(self.game, 'minimap') and self.game.minimap:
                                self.game.minimap.update_fog_pixel(x, y, self.game.level.map_data[y][x])

        # Velocidad de interpolación (aprox 0.1 segundos por casilla)
        speed = 300 * self.game.dt
        
        if self.exact_x < target_x:
            self.exact_x = min(target_x, self.exact_x + speed)
        elif self.exact_x > target_x:
            self.exact_x = max(target_x, self.exact_x - speed)
            
        if self.exact_y < target_y:
            self.exact_y = min(target_y, self.exact_y + speed)
        elif self.exact_y > target_y:
            self.exact_y = max(target_y, self.exact_y - speed)
            
        self.rect.x = int(self.exact_x)
        self.rect.y = int(self.exact_y)
