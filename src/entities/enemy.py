import pygame
from settings import *


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # Cargar y escalar imagen
        try:
            self.image = pygame.image.load(
                "assets/sprites/enemigo_base.png"
            ).convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        except FileNotFoundError:
            # Fallback si no encuentra la imagen (triangulo rojo como en la imagen de referencia)
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.image,
                RED,
                [(TILESIZE // 2, 4), (TILESIZE - 4, TILESIZE - 4), (4, TILESIZE - 4)],
            )

        self.rect = self.image.get_rect()

        # Posición en el grid
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

        # Stats del enemigo
        self.vida = 20
        self.max_vida = 20
        self.armadura = None  # Los enemigos no suelen usar armaduras equipables
        self.fuerza = 5
        self.defensa = 2
        self.defensa_magica = 0
        self.name = "Goblin"
        self.xp_recompensa = 10
        self.titulo = None

    def vivo(self):
        return self.vida > 0

    def _get_active_titles(self):
        titles = getattr(self, 'titulos', [])
        if not titles and getattr(self, 'titulo', None):
            titles = [self.titulo]
        cuestionados = getattr(self, 'titulos_cuestionados', [])
        return [t for t in titles if t not in cuestionados]

    def recibir_daño(self, dmg, tipo="fisico"):
        from logic.titulos_enemigos import TITULOS_ENEMIGOS
        active_titles = self._get_active_titles()
        
        dano_final = dmg
        # Fase 1: Pre-daño (esquivas y mitigaciones)
        for t in active_titles:
            data = TITULOS_ENEMIGOS.get(t)
            # Soporte retrocompatible: si usa on_recibir_daño, lo tratamos como antiguo a menos que devuelva int
            if data and "on_recibir_daño" in data:
                # El sistema antiguo aplicaba el daño dentro. 
                # Si estamos migrando, on_recibir_daño debe devolver False (fallo) o el daño modificado.
                result = data["on_recibir_daño"](self, dano_final, tipo=tipo)
                if result is False:
                    return False
                elif isinstance(result, (int, float)) and not isinstance(result, bool):
                    dano_final = result

        # Aplicar el daño
        self.vida -= dano_final
        if self.vida < 0:
            self.vida = 0
            
        # Fase 2: Post-daño (Last Stand, reacciones)
        for t in active_titles:
            data = TITULOS_ENEMIGOS.get(t)
            if data and "on_post_daño" in data:
                data["on_post_daño"](self)
                
        return True

    def act(self):
        from logic.titulos_enemigos import TITULOS_ENEMIGOS
        active_titles = self._get_active_titles()
        for t in active_titles:
            data = TITULOS_ENEMIGOS.get(t)
            if data and "on_turno" in data:
                data["on_turno"](self)

    def morir(self, log=None):
        self.kill()  # Eliminar del grupo de sprites

    def draw_hp_bar(self, surface):
        # Dibujar barra de vida sobre el enemigo
        bar_width = TILESIZE - 8
        bar_height = 6
        fill = (self.vida / self.max_vida) * bar_width
        outline_rect = pygame.Rect(
            self.rect.x + 4, self.rect.y - 10, bar_width, bar_height
        )
        fill_rect = pygame.Rect(self.rect.x + 4, self.rect.y - 10, fill, bar_height)

        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)
