import pygame
from settings import *
from logic.personaje import Guerrero, Tirador
from logic.armas import Arma
from items.potion import Pocion

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, clase_elegida="guerrero"):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Cargar y escalar imagen
        try:
            self.image = pygame.image.load('../assets/sprites/player.png').convert_alpha()
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

        # Integración con la lógica antigua
        if clase_elegida == "tirador":
            arma_inicial = Arma("Pistola Básica", 20)
            self.logic = Tirador("Tirador", fuerza=15, fe=0, defensa=4, vida=80, arma=arma_inicial)
        else:
            arma_inicial = Arma("Espada Corta", 15)
            self.logic = Guerrero("Guerrero", fuerza=12, fe=0, defensa=8, vida=100, espada=arma_inicial)
        
        self.inventory = [arma_inicial]

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
                    self.inventory.append(nuevo_item)
                    # Equipar automáticamente si es un arma y es mejor
                    if isinstance(nuevo_item, Arma):
                        # Helper para obtener el arma actual
                        arma_actual = self.logic.arma if hasattr(self.logic, 'arma') else self.logic.espada
                        if nuevo_item.daño > arma_actual.daño:
                            if hasattr(self.logic, 'arma'):
                                self.logic.arma = nuevo_item
                            else:
                                self.logic.espada = nuevo_item
                            self.game.log.add_message(f"Has equipado: {nuevo_item.nombre}")
                else:
                    self.x = dest_x
                    self.y = dest_y
                    self.rect.x = self.x * TILESIZE
                    self.rect.y = self.y * TILESIZE

                    # Comprobar escaleras
                    if self.game.level.stairs_down and (self.x, self.y) == self.game.level.stairs_down:
                        self.game.went_down = True
                        self.game.profundidad += 1
                        self.game.log.add_message(f"[SISTEMA] Bajas al Nivel {self.game.profundidad}")
                        self.game.load_level()
                    elif self.game.level.stairs_up and (self.x, self.y) == self.game.level.stairs_up:
                        self.game.went_down = False
                        self.game.profundidad -= 1
                        self.game.log.add_message("[SISTEMA] Subes por las escaleras.")
                        self.game.load_level()
