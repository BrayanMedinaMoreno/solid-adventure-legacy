import pygame
import random
from settings import *
from logic.armas import Arma
from logic.armaduras import Armadura
from items.potion import Pocion, PocionRegreso

class Chest(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.chests
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        try:
            self.image = pygame.image.load('assets/sprites/cofre.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except FileNotFoundError:
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.rect(self.image, YELLOW, (10, TILESIZE//2, TILESIZE-20, TILESIZE//2-10))

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def open(self):
        # Generar aleatoriamente
        if random.random() < 0.4: # 40% de probabilidad de ser poción
            tipo_p = random.choices(["pequeña", "media", "grande"], weights=[80, 15, 5])[0]
            if random.random() < 0.5:
                item = Pocion(tipo_p)
            else:
                from items.potion import PocionMana
                item = PocionMana(tipo_p)
        else:
            clases = ["guerrero", "tirador"]
            clase_p = random.choice(clases)
            nombres = {
                "guerrero": ["Espada Oxidada", "Daga Rápida", "Hacha Pesada", "Mazo de Guerra"],
                "tirador": ["Pistola Vieja", "Rifle de Caza", "Ballesta", "Escopeta Recortada"]
            }
            nombres_armadura = {
                "guerrero": ["Armadura de Cuero", "Cota de Malla", "Pechera de Hierro"],
                "tirador": ["Capa de Viaje", "Túnica Reforzada", "Chaqueta de Piel"]
            }
            
            daño_def = random.randint(5, 20)
            
            rand_gear = random.random()
            if rand_gear < 0.2: # 20% Accesorio
                from logic.accesorios import Accesorio
                nombres_acc = ["Anillo de Rubí", "Amuleto de Hierro", "Brazalete de Zafiro", "Collar Místico"]
                stat = random.choice(["fuerza", "defensa", "magia", "max_vida", "max_mana"])
                val = random.randint(2, 15)
                if stat in ["max_vida", "max_mana"]: val *= 5
                item = Accesorio(random.choice(nombres_acc), {stat: val})
            elif rand_gear < 0.7: # 50% Arma
                item = Arma(random.choice(nombres[clase_p]), daño_def, clase_p)
            else: # 30% Armadura
                defensa = daño_def // 2 + 2
                item = Armadura(random.choice(nombres_armadura[clase_p]), defensa, clase_p)
        
        self.game.log.add_message(f"[COFRE] Obtienes {item.nombre}")
        self.kill() # Eliminar cofre del mapa
        return item
