import pygame
from settings import *
from logic.armas import Arma


class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, color, nombre, image_path=None):
        self.groups = game.all_sprites, game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.nombre = nombre
        self.x = x
        self.y = y

        self.image = None
        if image_path:
            try:
                img = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(img, (TILESIZE, TILESIZE))
            except FileNotFoundError:
                pass

        if not self.image:
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.circle(
                self.image, color, (TILESIZE // 2, TILESIZE // 2), TILESIZE // 2 - 4
            )

        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def interact(self):
        pass


class Mercader(NPC):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, YELLOW, "Mercader", "assets/sprites/mercader.png")

    def interact(self):
        self.game.log.add_message("[MERCADER] ¡Bienvenido a mi tienda!")
        self.game.state = "SHOP"
        self.game.menu_index = 0


class Banquero(NPC):
    def __init__(self, game, x, y):
        super().__init__(
            game, x, y, LIGHT_GREY, "Banquero", "assets/sprites/npc_banquero.png"
        )

    def interact(self):
        self.game.log.add_message("[BANQUERO] Protejo tus riquezas.")
        self.game.state = "BANK"
        self.game.menu_index = 0


class CruzInteractiva(NPC):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, YELLOW, "Cruz Sagrada", "assets/sprites/Cruz.png")

    def interact(self):
        self.game.log.add_message("[CRUZ] Te aproximas a la Cruz Sagrada.")
        self.game.state = "CROSS_MENU"
        self.game.menu_index = 0


class Herrero(NPC):
    def __init__(self, game, x, y):
        super().__init__(
            game, x, y, (200, 100, 50), "Herrero", "assets/sprites/npc_banquero.png"
        )

    def armas_del_jugador(game):
        armas = []
        if isinstance(getattr(game.player.logic, "arma", None), Arma):
            armas.append((game.player.logic.arma, "equipada"))
        for item in game.player.inventory:
            if isinstance(item, Arma):
                armas.append((item, "inventario"))
        return armas

    def interact(self):
        self.game.log.add_message("[HERRERO] Trae tus armas, tengo trabajo que hacer.")
        self.game.state = "HERRERO"
        self.game.menu_index = 0
        self.game.herrero_armas = self.armas_del_jugador(self.game)
