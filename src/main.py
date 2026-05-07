import pygame
import sys
import random
from settings import *
from level import Level
from entities.player import Player
from entities.enemy_types import Goblin, Orco
from items.chest import Chest
from items.potion import Pocion
from logic.armas import Arma
from entities.npc import Mercader, Banquero
from ui.panel import Panel
from ui.log import Log

class Game:
    def __init__(self):
        pygame.init()
        # Activar repetición de teclas: delay inicial 200ms, repite cada 150ms
        pygame.key.set_repeat(200, 150)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Solid Adventure Legacy")
        self.clock = pygame.time.Clock()
        self.running = True

    def new(self):
        self.state = "CLASS_SELECTION"
        self.clase_seleccionada = 0

    def start_game(self, clase_elegida):
        self.clase_elegida = clase_elegida
        self.profundidad = 0 # Empezamos en el Pueblo
        self.went_down = True
        
        self.panel = Panel(self)
        self.log = Log()
        self.player = None
        self.log.add_message(f"Entras al mundo como {clase_elegida.capitalize()}!")
        
        self.load_level()

    def load_level(self):
        self.level = Level(self.profundidad)
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.chests = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        
        self.state = "PLAYING"
        self.current_enemy = None
        self.menu_index = 0
        
        # Posicionar jugador
        if not self.player:
            # Crear nuevo jugador
            start_x, start_y = self.level.width_tiles // 2, self.level.height_tiles // 2
            self.player = Player(self, start_x, start_y, self.clase_elegida)
        else:
            # Mover jugador existente
            if self.went_down:
                start_x, start_y = self.level.stairs_up if self.level.stairs_up else self.level.floor_tiles[0]
            else:
                start_x, start_y = self.level.stairs_down if self.level.stairs_down else self.level.floor_tiles[0]
            self.player.x = start_x
            self.player.y = start_y
            self.player.rect.x = start_x * TILESIZE
            self.player.rect.y = start_y * TILESIZE
            self.all_sprites.add(self.player)
        
        if self.profundidad > 0:
            # Spawnear enemigos en calabozo
            for _ in range(4 + self.profundidad * 2):
                tile = random.choice(self.level.floor_tiles)
                if tile != (self.player.x, self.player.y):
                    tipo_enemigo = random.choice([Goblin, Orco])
                    enemy = tipo_enemigo(self, tile[0], tile[1])
                    # Escalar dificultad
                    enemy.max_vida += self.profundidad * 10
                    enemy.vida = enemy.max_vida
                    enemy.fuerza += self.profundidad * 3
                    enemy.defensa += self.profundidad * 2
                    enemy.xp_recompensa += self.profundidad * 15
                
            # Spawnear cofres
            for _ in range(3):
                tile = random.choice(self.level.floor_tiles)
                if tile != (self.player.x, self.player.y):
                    Chest(self, tile[0], tile[1])
        else:
            self.log.add_message("[PUEBLO] Estás a salvo aquí.")
            Mercader(self, self.level.width_tiles // 2 - 2, self.level.height_tiles // 2)
            Banquero(self, self.level.width_tiles // 2 + 2, self.level.height_tiles // 2)

    def get_chest_at(self, x, y):
        for chest in self.chests:
            if chest.x == x and chest.y == y:
                return chest
        return None

    def get_enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return enemy
        return None

    def get_npc_at(self, x, y):
        for npc in self.npcs:
            if npc.x == x and npc.y == y:
                return npc
        return None

    def start_combat(self, enemy):
        self.state = "COMBAT"
        self.current_enemy = enemy
        self.menu_index = 0
        self.log.add_message(f"--- COMBATE: {enemy.name.upper()} ---")

    def resolve_combat_action(self):
        if self.menu_index == 0: # Atacar
            self.player.logic.atacar(self.current_enemy, self.log)
            
            if self.current_enemy.vida <= 0:
                self.log.add_message(f"[SISTEMA] {self.current_enemy.name} muere.")
                self.player.logic.ganar_xp(self.current_enemy.xp_recompensa, self.log)
                
                monedas = random.randint(self.current_enemy.xp_recompensa // 2, self.current_enemy.xp_recompensa)
                monedas = int(monedas * (1 + (self.profundidad * 0.5)))
                self.player.logic.añadir_monedas(monedas)
                self.log.add_message(f"[LOOT] +{monedas} Cobre")
                
                self.state = "PLAYING"
                self.current_enemy = None
                return
        elif self.menu_index == 1: # Usar Objeto
            self.state = "INVENTORY"
            self.menu_index = 0
            return
        elif self.menu_index == 2: # Huir
            self.log.add_message("[TÚ] Huyes del combate.")
            self.state = "PLAYING"
            self.current_enemy = None
            return

        self.resolve_enemy_turn()

    def resolve_enemy_turn(self):
        if not self.current_enemy or self.current_enemy.vida <= 0: return
        enemy_dmg = max(1, self.current_enemy.fuerza - self.player.logic.defensa)
        self.player.logic.vida -= enemy_dmg
        self.log.add_message(f"[{self.current_enemy.name.upper()}] Ataca -> {enemy_dmg} DMG")
        if self.player.logic.vida <= 0:
            self.log.add_message("[SISTEMA] HAS MUERTO.")
            
            # Penalidad
            self.player.logic.cobre = 0
            self.player.logic.plata = 0
            self.player.logic.oro = 0
            self.player.logic.platino = 0
            
            arma_basica = Arma("Palo Roto", 5)
            self.player.inventory = [arma_basica]
            if hasattr(self.player.logic, 'arma'):
                self.player.logic.arma = arma_basica
            else:
                self.player.logic.espada = arma_basica
            self.player.logic.vida = self.player.logic.max_vida
            
            # Respawn en el pueblo
            self.profundidad = 0
            self.load_level()

    def use_item(self, item):
        if isinstance(item, Pocion):
            item.usar(self.player.logic, self.log)
            self.player.inventory.remove(item)
            if self.current_enemy:
                self.state = "COMBAT"
                self.resolve_enemy_turn()
            else:
                self.state = "PLAYING"
                
        elif isinstance(item, Arma):
            if hasattr(self.player.logic, 'arma'):
                self.player.logic.arma = item
            else:
                self.player.logic.espada = item
            self.log.add_message(f"[TÚ] Equipas {item.nombre}.")
            if self.current_enemy:
                self.state = "COMBAT"
                self.resolve_enemy_turn()
            else:
                self.state = "PLAYING"

    def run(self):
        # Bucle principal del juego
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0  # Delta time en segundos
            self.events()
            self.update()
            self.draw()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def update(self):
        # Actualizar lógica
        pass

    def draw_grid(self):
        # Dibujar líneas del grid para la zona del mapa
        for x in range(0, MAP_WIDTH, TILESIZE):
            pygame.draw.line(self.screen, DARK_GREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, DARK_GREY, (0, y), (MAP_WIDTH, y))

    def draw(self):
        # Dibujar gráficos
        self.screen.fill(BLACK)
        
        if self.state == "CLASS_SELECTION":
            self.draw_class_selection()
            pygame.display.flip()
            return
            
        self.level.draw(self.screen)
        
        self.all_sprites.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw_hp_bar(self.screen)
        
        self.draw_grid()

        # Separador UI
        pygame.draw.rect(self.screen, DARK_GREY, (MAP_WIDTH, 0, UI_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, WHITE, (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 2)

        self.panel.draw(self.screen)
        self.log.draw(self.screen)

        if self.state == "COMBAT":
            self.draw_combat_menu()
        elif self.state == "INVENTORY":
            self.draw_inventory_menu()
        elif self.state == "SHOP":
            self.draw_shop_menu()
        elif self.state == "BANK":
            self.draw_bank_menu()

        pygame.display.flip()

    def draw_class_selection(self):
        title_font = pygame.font.SysFont('Consolas', 40, bold=True)
        font = pygame.font.SysFont('Consolas', 24)
        
        self.screen.blit(title_font.render("ELIGE TU CLASE", True, CYAN), (WIDTH//2 - 150, HEIGHT//2 - 100))
        
        color1 = YELLOW if self.clase_seleccionada == 0 else WHITE
        self.screen.blit(font.render("1. Guerrero (100 HP, Def: 8) - Espada", True, color1), (WIDTH//2 - 250, HEIGHT//2))
        
        color2 = YELLOW if self.clase_seleccionada == 1 else WHITE
        self.screen.blit(font.render("2. Tirador (80 HP, Def: 4) - Pistola", True, color2), (WIDTH//2 - 250, HEIGHT//2 + 50))
        
        self.screen.blit(font.render("Usa las Flechas y pulsa ENTER", True, LIGHT_GREY), (WIDTH//2 - 200, HEIGHT//2 + 150))

    def draw_combat_menu(self):
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 150)
        pygame.draw.rect(self.screen, (20, 20, 20), menu_rect)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 2)
        
        font = pygame.font.SysFont('Consolas', 20)
        options = ["Atacar", "Usar Objeto", "Huir"]
        
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            text_surface = font.render(prefix + option, True, color)
            self.screen.blit(text_surface, (menu_rect.x + 20, menu_rect.y + 20 + i * 40))

    def draw_inventory_menu(self):
        inv = self.player.inventory
        # Ajustamos el tamaño del menú según la cantidad de items (o un mínimo)
        h = max(200, min(HEIGHT - 100, len(inv) * 30 + 60))
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - 150, HEIGHT // 2 - h // 2, 300, h)
        pygame.draw.rect(self.screen, (20, 20, 30), menu_rect)
        pygame.draw.rect(self.screen, CYAN, menu_rect, 2)
        
        font = pygame.font.SysFont('Consolas', 18)
        title_font = pygame.font.SysFont('Consolas', 22, bold=True)
        
        self.screen.blit(title_font.render("INVENTARIO [Enter para usar/equipar]", True, YELLOW), (menu_rect.x + 10, menu_rect.y + 10))
        
        if len(inv) == 0:
            self.screen.blit(font.render("Vacío", True, WHITE), (menu_rect.x + 20, menu_rect.y + 50))
            return
            
        for i, item in enumerate(inv):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            
            from logic.armas import Arma
            extra = f" ({item.daño} DMG)" if isinstance(item, Arma) else f" (+{item.curacion} HP)"
            
            text_surface = font.render(prefix + item.nombre + extra, True, color)
            self.screen.blit(text_surface, (menu_rect.x + 20, menu_rect.y + 50 + i * 30))

    def draw_shop_menu(self):
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
        pygame.draw.rect(self.screen, (30, 20, 20), menu_rect)
        pygame.draw.rect(self.screen, YELLOW, menu_rect, 2)
        font = pygame.font.SysFont('Consolas', 18)
        
        self.screen.blit(font.render("TIENDA DEL MERCADER", True, YELLOW), (menu_rect.x + 20, menu_rect.y + 10))
        
        options = ["Comprar Poción (100 Cobre)", "Arma Aleatoria (500 Cobre)", "Salir"]
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.screen.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 50 + i * 40))

    def draw_bank_menu(self):
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
        pygame.draw.rect(self.screen, (20, 30, 30), menu_rect)
        pygame.draw.rect(self.screen, LIGHT_GREY, menu_rect, 2)
        font = pygame.font.SysFont('Consolas', 18)
        
        banco = self.player.logic.banco_cobre
        self.screen.blit(font.render(f"BANCO (Ahorros: {banco} Cob)", True, CYAN), (menu_rect.x + 20, menu_rect.y + 10))
        
        options = ["Depositar todo", "Retirar todo", "Salir"]
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.screen.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 50 + i * 40))

    def events(self):
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()
                
                if self.state == "CLASS_SELECTION":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.clase_seleccionada = 0
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.clase_seleccionada = 1
                    elif event.key == pygame.K_RETURN:
                        clase_str = "guerrero" if self.clase_seleccionada == 0 else "tirador"
                        self.start_game(clase_str)
                        
                elif self.state == "PLAYING":
                    # Movimiento
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.move(dx=-1)
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.move(dx=1)
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.move(dy=-1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player.move(dy=1)
                    if event.key == pygame.K_i:
                        self.state = "INVENTORY"
                        self.menu_index = 0
                
                elif self.state == "COMBAT":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(2, self.menu_index + 1)
                    if event.key == pygame.K_RETURN:
                        self.resolve_combat_action()

                elif self.state == "INVENTORY":
                    inv = self.player.inventory
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if len(inv) > 0:
                            self.menu_index = min(len(inv) - 1, self.menu_index + 1)
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                        # Cerrar inventario
                        self.state = "COMBAT" if self.current_enemy else "PLAYING"
                    if event.key == pygame.K_RETURN:
                        if len(inv) > 0:
                            item = inv[self.menu_index]
                            self.use_item(item)

                elif self.state == "SHOP":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(2, self.menu_index + 1)
                    if event.key == pygame.K_RETURN:
                        if self.menu_index == 0:
                            if self.player.logic.gastar_monedas(100):
                                self.player.inventory.append(Pocion())
                                self.log.add_message("[MERCADER] ¡Aquí tienes!")
                            else:
                                self.log.add_message("[MERCADER] No tienes dinero.")
                        elif self.menu_index == 1:
                            if self.player.logic.gastar_monedas(500):
                                dmg = random.randint(20 + self.player.logic.nivel*2, 40 + self.player.logic.nivel*5)
                                self.player.inventory.append(Arma(f"Arma lvl {self.player.logic.nivel}", dmg))
                                self.log.add_message("[MERCADER] ¡Excelente arma!")
                            else:
                                self.log.add_message("[MERCADER] No tienes dinero.")
                        elif self.menu_index == 2:
                            self.state = "PLAYING"
                
                elif self.state == "BANK":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(2, self.menu_index + 1)
                    if event.key == pygame.K_RETURN:
                        l = self.player.logic
                        total_cobre = l.cobre + l.plata * 100 + l.oro * 10000 + l.platino * 1000000
                        if self.menu_index == 0:
                            if total_cobre > 0:
                                l.banco_cobre += total_cobre
                                l.gastar_monedas(total_cobre)
                                self.log.add_message("[BANQUERO] Protegido.")
                        elif self.menu_index == 1:
                            if l.banco_cobre > 0:
                                l.añadir_monedas(l.banco_cobre)
                                l.banco_cobre = 0
                                self.log.add_message("[BANQUERO] Dinero retirado.")
                        elif self.menu_index == 2:
                            self.state = "PLAYING"

if __name__ == "__main__":
    g = Game()
    while True:
        g.new()
        g.run()
