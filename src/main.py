from logic.personaje import Personaje, TITULOS_DATA
import pygame
import sys
import os
import random
import time
random.seed(time.time())
from settings import *
from level import Level
from entities.player import Player
from entities.enemy_types import Goblin, Orco, Slime, SlimeBoss
from items.chest import Chest
from items.potion import Pocion, PocionRegreso
from logic.armas import Arma
from logic.armaduras import Armadura
from entities.npc import Mercader, Banquero
from entities.trap import Trap
from ui.panel import Panel
from ui.log import Log
from ui.floating_text import FloatingText
from ui.minimap import Minimap
from logic.save_manager import SaveManager

class Game:
    def __init__(self):
        pygame.init()
        # Activar repetición de teclas: delay inicial 200ms, repite cada 150ms
        pygame.key.set_repeat(200, 150)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.virtual_surface = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption("Solid Adventure Legacy")
        self.clock = pygame.time.Clock()
        self.running = True
        self.floating_texts = pygame.sprite.Group()
        self.max_profundidad = 1
        self.combat_intro_timer = 0
        self.fullscreen = False

    def new(self):
        self.state = "TITLE_SCREEN"
        self.menu_index = 0
        self.clase_seleccionada = 0

    def start_game(self, clase_elegida, nombre=None):
        self.clase_elegida = clase_elegida
        self.profundidad = 0 # Empezamos en el Pueblo
        self.went_down = True
        
        self.panel = Panel(self)
        self.log = Log()
        self.player = None
        self.log.add_message(f"¡Bienvenido al mundo, {nombre}!")
        self.character_name = nombre
        
        self.load_level()

    def start_saved_game(self, save_data):
        self.max_profundidad = save_data["max_profundidad"]
        self.profundidad = 0 # Siempre empezamos en el pueblo al cargar
        self.went_down = True
        
        self.panel = Panel(self)
        self.log = Log()
        
        # Reconstruir lógica del jugador
        p_data = save_data["player_logic"]
        
        logic = Personaje(p_data["nombre"], 0, 0, 0, 0)
        logic.load_base_stats(p_data)
            
        logic.load_base_stats(p_data)
        
        # Reconstruir baúl
        logic.baul = []
        for item_data in p_data["baul"]:
            item = SaveManager.reconstruct_item(item_data)
            if item: logic.baul.append(item)
            
        # Reconstruir inventario
        inventory = []
        for item_data in save_data["inventory"]:
            item = SaveManager.reconstruct_item(item_data)
            if item: inventory.append(item)
            
        # Crear jugador con lógica cargada
        self.player = None # Forzar creación en load_level
        self.loaded_logic = logic
        self.loaded_inventory = inventory
        self.character_name = p_data["nombre"]
        self.clase_elegida = "aventurero" # Valor por defecto legacy
        
        self.log.add_message(f"¡Bienvenido de vuelta, {self.character_name}!")
        self.load_level()

    def load_level(self):
        self.level = Level(self.profundidad)
        # Trackear piso máximo
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.chests = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()
        
        self.state = "PLAYING"
        self.current_enemy = None
        self.menu_index = 0
        
        # Posicionar jugador
        if not self.player:
            # Crear nuevo jugador
            start_x, start_y = self.level.width_tiles // 2, self.level.height_tiles // 2
            if hasattr(self, 'loaded_logic'):
                self.player = Player(self, start_x, start_y, self.clase_elegida, self.loaded_logic, self.loaded_inventory)
                del self.loaded_logic
                del self.loaded_inventory
            else:
                self.player = Player(self, start_x, start_y, self.clase_elegida, nombre=self.character_name)
        else:
            # Mover jugador existente
            if self.went_down:
                start_x, start_y = self.level.entrance if self.level.entrance else self.level.floor_tiles[0]
            else:
                start_x, start_y = self.level.stairs_down if self.level.stairs_down else self.level.floor_tiles[0]
            self.player.x = start_x
            self.player.y = start_y
            self.player.rect.x = start_x * TILESIZE
            self.player.rect.y = start_y * TILESIZE
            self.player.exact_x = float(self.player.rect.x)
            self.player.exact_y = float(self.player.rect.y)
            self.all_sprites.add(self.player)

        # Trackear piso máximo
        if self.profundidad > self.player.logic.acciones.get("piso_maximo", 0):
            self.player.logic.acciones["piso_maximo"] = self.profundidad
            self.player.logic.verificar_titulos(self.log)
        
        # Ocupar baldosas críticas
        occupied_tiles = set()
        occupied_tiles.add((self.player.x, self.player.y))
        if hasattr(self.level, 'entrance') and self.level.entrance: 
            occupied_tiles.add(self.level.entrance)
        if self.level.stairs_down: occupied_tiles.add(self.level.stairs_down)
        
        if self.profundidad > 0:
            # Spawnear enemigos en calabozo
            num_enemies = 4 + self.profundidad * 2
            if self.profundidad % 5 == 0:
                # Jefe
                available_tiles = [t for t in self.level.floor_tiles if t not in occupied_tiles]
                if available_tiles:
                    tile = random.choice(available_tiles)
                    enemy = SlimeBoss(self, tile[0], tile[1])
                    enemy.max_vida += self.profundidad * 10
                    enemy.vida = enemy.max_vida
                    occupied_tiles.add(tile)
            if self.profundidad % 5 == 0:
                # NIVEL DE JEFE
                self.log.add_message(f"[ALERTA] ¡HAS LLEGADO AL REINO DEL REY SLIME!")
                available_tiles = [t for t in self.level.floor_tiles if t not in occupied_tiles]
                if available_tiles:
                    tile = random.choice(available_tiles)
                    boss = SlimeBoss(self, tile[0], tile[1])
                    # Escalar stats del boss según profundidad
                    multiplicador = self.profundidad // 5
                    boss.max_vida += multiplicador * 500
                    boss.vida = boss.max_vida
                    boss.fuerza += multiplicador * 20
                    boss.defensa += multiplicador * 10
                    boss.xp_recompensa += multiplicador * 1000
                    occupied_tiles.add(tile)
            else:
                for _ in range(num_enemies):
                    available_tiles = [t for t in self.level.floor_tiles if t not in occupied_tiles]
                    if not available_tiles: break
                    tile = random.choice(available_tiles)
                    
                    if self.profundidad <= 3:
                        tipo_enemigo = random.choice([Goblin, Slime, Slime, Slime])
                    else:
                        tipo_enemigo = random.choice([Goblin, Orco, Slime])
                    
                    enemy = tipo_enemigo(self, tile[0], tile[1])
                    enemy.max_vida += self.profundidad * 20
                    enemy.vida = enemy.max_vida
                    enemy.fuerza += self.profundidad * 5
                    enemy.defensa += self.profundidad * 2
                    enemy.xp_recompensa += self.profundidad * 15
                    occupied_tiles.add(tile)
                
            # Spawnear cofres
            for _ in range(3):
                available_tiles = [t for t in self.level.floor_tiles if t not in occupied_tiles]
                if not available_tiles: break
                tile = random.choice(available_tiles)
                Chest(self, tile[0], tile[1])
                occupied_tiles.add(tile)
            
            # Spawnear Trampas (Máximo 3)
            num_traps = random.randint(1, 3)
            for _ in range(num_traps):
                available_tiles = [t for t in self.level.floor_tiles if t not in occupied_tiles]
                if not available_tiles: break
                tile = random.choice(available_tiles)
                Trap(self, tile[0], tile[1])
                occupied_tiles.add(tile)
        else:
            self.log.add_message("[PUEBLO] Estás a salvo aquí.")
            Mercader(self, self.level.width_tiles // 2 - 2, self.level.height_tiles // 2)
            Banquero(self, self.level.width_tiles // 2 + 2, self.level.height_tiles // 2)

        # Inicializar minimapa
        self.minimap = Minimap(self)

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

    def get_trap_at(self, x, y):
        for trap in self.traps:
            if trap.x == x and trap.y == y:
                return trap
        return None

    def start_combat(self, enemy):
        self.state = "COMBAT"
        self.current_enemy = enemy
        self.menu_index = 0
        self.combat_intro_timer = 0.8 # Segundos de alerta
        self.player.logic.aliento_usado_combate = False
        self.player.logic.min_porcentaje_vida_combate = (self.player.logic.vida / self.player.logic.max_vida) * 100
        self.log.add_message(f"--- COMBATE: {enemy.name.upper()} ---")

    def resolve_combat_action(self):
        # Al iniciar la resolución de la acción, el jugador recupera por su turno
        self.player.logic.ejecutar_regen_turno(self.log)
        
        options = self.get_combat_options()
        action = options[self.menu_index]
        
        should_end_turn = False
        
        if action == "Ataque Básico":
            self.player.logic.atacar(self.current_enemy, self.log, tipo_forzado="fisico")
            should_end_turn = True
        elif action == "Golpe Habilidad":
            self.player.logic.atacar(self.current_enemy, self.log, tipo_forzado="habilidad")
            should_end_turn = True
        elif action == "Ataque Distancia":
            self.player.logic.atacar(self.current_enemy, self.log, tipo_forzado="distancia")
            should_end_turn = True
        elif action == "Huir":
            # Aumentar probabilidad a 70% para mejor fluidez
            if random.random() < 0.7:
                self.log.add_message("[SISTEMA] ¡Has escapado del combate!")
                self.spawn_floating_text("¡ESCAPASTE!", self.player.rect.centerx, self.player.rect.top - 20, GREEN)
                self.state = "PLAYING"
                self.current_enemy = None
                self.menu_index = 0 # Resetear para el próximo encuentro
                return
            else:
                self.log.add_message("[SISTEMA] ¡No pudiste escapar!")
                self.spawn_floating_text("¡FALLASTE!", self.player.rect.centerx, self.player.rect.top - 20, RED)
                should_end_turn = True
        elif action == "Inventario":
            self.state = "INVENTORY"
            self.menu_index = 0
            return
        if self.current_enemy and self.current_enemy.vida <= 0:
            self.log.add_message(f"[SISTEMA] {self.current_enemy.name} muere.")
            self.player.logic.ganar_xp(self.current_enemy.xp_recompensa, self.log)
            self.spawn_floating_text(f"+{self.current_enemy.xp_recompensa} XP", self.player.rect.centerx, self.player.rect.top, YELLOW)
            
            # Registrar combate sobrevivido en riesgo
            min_hp = self.player.logic.min_porcentaje_vida_combate
            if min_hp < 25: self.player.logic.acciones["combates_bajo_25hp"] += 1
            if min_hp < 20: self.player.logic.acciones["combates_bajo_20hp"] += 1
            if min_hp < 15: self.player.logic.acciones["combates_bajo_15hp"] += 1
            self.player.logic.verificar_titulos(self.log)
            
            monedas = int(random.randint(self.current_enemy.xp_recompensa // 2, self.current_enemy.xp_recompensa) * (1 + (self.profundidad * 0.5)))
            self.player.logic.añadir_monedas(monedas)
            self.log.add_message(f"[LOOT] +{monedas} Cobre")
            self.spawn_floating_text(f"+{monedas} Cob", self.player.rect.centerx, self.player.rect.centery, (205, 127, 50))
            
            self.state = "PLAYING"
            self.current_enemy.kill()
            self.current_enemy = None
            
            # Comprobar si el nivel está despejado
            if len(self.enemies) == 0:
                self.log.add_message("[SISTEMA] ¡ZONA DESPEJADA! Las escaleras están abiertas.")
                self.spawn_floating_text("¡ZONA DESPEJADA!", self.player.rect.centerx, self.player.rect.top - 40, GREEN)
        elif should_end_turn and self.current_enemy:
            self.resolve_enemy_turn()

    def resolve_enemy_turn(self):
        if not self.current_enemy or self.current_enemy.vida <= 0: return
        
        # Lógica especial del enemigo (ej: curación del boss)
        self.current_enemy.act()
        
        # Determinar tipo de daño del enemigo
        damage_type = "fisico"
        enemy_name = self.current_enemy.__class__.__name__
        
        chance = random.random()
        if enemy_name == "Goblin" and chance < 0.25:
            damage_type = "distancia"
            self.log.add_message("[GOBIN] ¡Lanza una flecha!")
        elif enemy_name == "Orco" and chance < 0.15:
            damage_type = "habilidad"
            self.log.add_message("[ORCO] ¡Golpe de habilidad pesado!")
        elif enemy_name == "SlimeBoss" and chance < 0.20:
            damage_type = "magico"
            self.log.add_message("[REY SLIME] ¡Explosión mágica viscosa!")
        
        enemy_dmg = max(1, self.current_enemy.fuerza - self.player.logic.defensa)
        if self.player.logic.recibir_daño(enemy_dmg, tipo=damage_type, log=self.log):
            self.spawn_floating_text(f"-{enemy_dmg}", self.player.rect.centerx, self.player.rect.top, RED)
            # Activar vibración de pantalla al recibir daño (Reducida para que sea más sutil)
            if not hasattr(self, 'screen_shake'): self.screen_shake = 0
            self.screen_shake = min(8, self.screen_shake + 2 + enemy_dmg // 5)
        
        if self.player.logic.vida <= 0:
            self.log.add_message("[SISTEMA] HAS MUERTO.")
            
            # Penalidad: Pierde todo el dinero
            self.player.logic.cobre = 0
            self.player.logic.plata = 0
            self.player.logic.oro = 0
            self.player.logic.platino = 0
            
            # Penalidad de XP: 20% (sin bajar de nivel, ya que la lógica de nivel no resta)
            xp_perdida = int(self.player.logic.xp * 0.20)
            self.player.logic.xp -= xp_perdida
            
            # Filtrar inventario: Solo se conserva la Pocion de Regreso
            # Importamos PocionRegreso localmente para evitar problemas de circularidad si los hay
            from items.potion import PocionRegreso
            regreso_items = [item for item in self.player.inventory if isinstance(item, PocionRegreso)]
            
            # Resetear equipo a básico
            arma_basica = Arma("Espada de Madera", 8, "fisico")
            self.player.inventory = [arma_basica] + regreso_items
            self.player.logic.arma = arma_basica
            self.player.logic.armadura = None
            
            self.player.logic.vida = self.player.logic.max_vida
            self.log.add_message(f"[SISTEMA] Perdiste {xp_perdida} XP y tu equipo. Solo conservas tus Pociones de Regreso.")
            
            # Respawn en el pueblo
            self.profundidad = 0
            self.load_level()

    def spawn_floating_text(self, text, x, y, color=WHITE):
        FloatingText(self.floating_texts, text, x, y, color)

    def use_item(self, item):
        if isinstance(item, Pocion):
            item.usar(self.player.logic, self.log)
            item.cantidad -= 1
            if item.cantidad <= 0:
                self.player.inventory.remove(item)
            if self.current_enemy:
                self.state = "COMBAT"
                self.resolve_enemy_turn()
            else:
                self.state = "PLAYING"
                
        elif isinstance(item, PocionRegreso):
            item.usar(self.player.logic, self.log)
            item.cantidad -= 1
            if item.cantidad <= 0:
                self.player.inventory.remove(item)
            # Al regresar al pueblo, siempre salimos del combate si estábamos en uno
            self.current_enemy = None
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

        elif isinstance(item, Armadura):
            # Determinar slot por nombre o tipo si estuviera implementado
            nombre = item.nombre.lower()
            slot = "pechera" # Default
            if "casco" in nombre or "corona" in nombre or "yelmo" in nombre:
                slot = "casco"
            elif "botas" in nombre or "pies" in nombre or "calzado" in nombre:
                slot = "botas"
            
            setattr(self.player.logic, slot, item)
            self.log.add_message(f"[TÚ] Equipas {item.nombre} en {slot.upper()}.")
                
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

    def quit_game(self, save_filename=None):
        if hasattr(self, 'player') and self.player:
            if self.profundidad == 0:
                if save_filename:
                    SaveManager.save_game(self, save_filename)
        pygame.quit()
        sys.exit()

    def update(self):
        # Actualizar lógica
        self.floating_texts.update(self.dt)
        if self.combat_intro_timer > 0:
            self.combat_intro_timer -= self.dt
            
        if hasattr(self, 'screen_shake') and self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - 30 * self.dt)
            
        if self.state == "PLAYING":
            self.player.logic.update_regen(self.dt)
            self.all_sprites.update()


    def draw_grid(self, cam_x=0, cam_y=0):
        # Dibujar líneas del grid compensando la cámara
        offset_x = cam_x % TILESIZE
        offset_y = cam_y % TILESIZE
        
        for x in range(0, MAP_WIDTH + TILESIZE, TILESIZE):
            pygame.draw.line(self.virtual_surface, DARK_GREY, (x - offset_x, 0), (x - offset_x, HEIGHT))
        for y in range(0, HEIGHT + TILESIZE, TILESIZE):
            pygame.draw.line(self.virtual_surface, DARK_GREY, (0, y - offset_y), (MAP_WIDTH, y - offset_y))

    def draw(self):
        # Dibujar todo en la superficie virtual primero
        self.virtual_surface.fill(BLACK)
        
        if self.state == "TITLE_SCREEN":
            self.draw_title_screen()
            self.flip_to_screen()
            return
            
        if self.state == "NAME_INPUT":
            self.draw_name_input_screen()
            self.flip_to_screen()
            return

        if self.state == "LOAD_SELECTION":
            self.draw_load_selection()
            self.flip_to_screen()
            return

        if self.state == "HELP_SCREEN":
            self.draw_help_screen()
            self.flip_to_screen()
            return
            
        # Calcular cámara para seguir al jugador
        player_cx = self.player.rect.x + TILESIZE // 2
        player_cy = self.player.rect.y + TILESIZE // 2
        
        # Centrar en el área del mapa (MAP_WIDTH x HEIGHT)
        cam_x = player_cx - MAP_WIDTH // 2
        cam_y = player_cy - HEIGHT // 2
        
        # Limitar cámara a los bordes del mapa
        cam_x = max(0, min(cam_x, self.level.width_tiles * TILESIZE - MAP_WIDTH))
        cam_y = max(0, min(cam_y, self.level.height_tiles * TILESIZE - HEIGHT))

        self.level.draw(self.virtual_surface, cam_x, cam_y, self)
        
        # Dibujar todos los sprites con offset de cámara
        for sprite in self.all_sprites:
            # Solo dibujar si está cerca de la pantalla para optimizar un poco
            screen_rect = pygame.Rect(cam_x - TILESIZE, cam_y - TILESIZE, MAP_WIDTH + TILESIZE*2, HEIGHT + TILESIZE*2)
            if sprite.rect.colliderect(screen_rect):
                offset_pos = (sprite.rect.x - cam_x, sprite.rect.y - cam_y)
                self.virtual_surface.blit(sprite.image, offset_pos)

        self.floating_texts.draw(self.virtual_surface) # Estos pueden ser relativos a pantalla o mapa, asumo mapa
        # Re-ajustar floating texts si es necesario (asumo que se quedan donde nacieron en el mapa)
        
        for enemy in self.enemies:
            if enemy.rect.colliderect(screen_rect):
                # HP Bar con offset
                bar_width = TILESIZE - 8
                bar_height = 6
                fill = (enemy.vida / enemy.max_vida) * bar_width
                outline_rect = pygame.Rect(enemy.rect.x - cam_x + 4, enemy.rect.y - cam_y - 10, bar_width, bar_height)
                fill_rect = pygame.Rect(enemy.rect.x - cam_x + 4, enemy.rect.y - cam_y - 10, fill, bar_height)
                pygame.draw.rect(self.virtual_surface, RED, fill_rect)
                pygame.draw.rect(self.virtual_surface, WHITE, outline_rect, 1)
        
        # El grid también debe seguir la cámara si queremos que se vea bien
        self.draw_grid(cam_x, cam_y)

        # Separador UI
        pygame.draw.line(self.virtual_surface, WHITE, (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 2)
        
        # UI
        self.panel.draw(self.virtual_surface)
        self.log.draw(self.virtual_surface)
        if hasattr(self, 'minimap'):
            self.minimap.draw(self.virtual_surface)
        
        if self.state == "COMBAT":
            self.draw_combat_menu()
            if self.combat_intro_timer > 0:
                self.draw_combat_alert()
        elif self.state == "INVENTORY":
            self.draw_inventory_menu()
        elif self.state == "SHOP":
            self.draw_shop_menu()
        elif self.state == "SELL":
            self.draw_sell_menu()
        elif self.state == "BANK":
            self.draw_bank_menu()
        elif self.state == "BANK_STORE":
            self.draw_bank_store_menu()
        elif self.state == "BANK_RETRIEVE":
            self.draw_bank_retrieve_menu()
        elif self.state == "CONFIRM_EXIT":
            self.draw_confirm_exit()
        elif self.state == "SAVE_SELECTION":
            self.draw_save_selection()
        elif self.state == "TITLE_MENU":
            self.draw_title_menu()
        elif self.state == "LEVEL_SELECTION":
            self.draw_level_selection()
        elif self.state == "DIALOG":
            self.draw_dialog_box()

        self.flip_to_screen()

    def flip_to_screen(self):
        # Escalar la superficie virtual a la ventana real manteniendo el aspecto
        window_w, window_h = self.screen.get_size()
        scale_w = window_w / WIDTH
        scale_h = window_h / HEIGHT
        scale = min(scale_w, scale_h)
        
        new_w = int(WIDTH * scale)
        new_h = int(HEIGHT * scale)
        
        scaled_surf = pygame.transform.scale(self.virtual_surface, (new_w, new_h))
        
        # Centrar en la pantalla (barras negras si el aspect ratio es distinto)
        pos_x = (window_w - new_w) // 2
        pos_y = (window_h - new_h) // 2
        
        # Aplicar Screen Shake (temblor aleatorio)
        if hasattr(self, 'screen_shake') and self.screen_shake > 0:
            offset = int(self.screen_shake)
            if offset > 0:
                pos_x += random.randint(-offset, offset)
                pos_y += random.randint(-offset, offset)
        
        self.screen.fill(BLACK)
        self.screen.blit(scaled_surf, (pos_x, pos_y))
        pygame.display.flip()

    def draw_description_box(self, text):
        if not text: return
        w = 450
        panel_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT - 130, w, 110)
        # Sombra
        pygame.draw.rect(self.virtual_surface, (5, 5, 5), (panel_rect.x + 5, panel_rect.y + 5, panel_rect.width, panel_rect.height))
        # Fondo con degradado simulado (bordes más claros)
        pygame.draw.rect(self.virtual_surface, (25, 25, 40), panel_rect)
        pygame.draw.rect(self.virtual_surface, (60, 60, 80), panel_rect, 1) # Borde sutil
        pygame.draw.rect(self.virtual_surface, YELLOW, (panel_rect.x, panel_rect.y, panel_rect.width, 4)) # Línea superior decorativa
        
        font = pygame.font.SysFont('Consolas', 16)
        title_font = pygame.font.SysFont('Consolas', 16, bold=True)
        
        self.virtual_surface.blit(title_font.render("DETALLES DEL OBJETO:", True, YELLOW), (panel_rect.x + 15, panel_rect.y + 12))
        
        # Wrap text
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            if font.size(current_line + word)[0] < (w - 30):
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for i, line in enumerate(lines[:3]):
            self.virtual_surface.blit(font.render(line, True, LIGHT_GREY), (panel_rect.x + 15, panel_rect.y + 40 + i * 20))

    def draw_title_screen(self):
        title_font = pygame.font.SysFont('Consolas', 50, bold=True)
        font = pygame.font.SysFont('Consolas', 24)
        
        # Fondo oscuro con algo de estilo
        self.virtual_surface.fill((10, 10, 20))
        
        # Título
        title_text = "SOLID ADVENTURE LEGACY"
        shadow = title_font.render(title_text, True, (40, 40, 60))
        self.virtual_surface.blit(shadow, (WIDTH//2 - 295, HEIGHT//3 - 45))
        self.virtual_surface.blit(title_font.render(title_text, True, CYAN), (WIDTH//2 - 300, HEIGHT//3 - 50))
        
        options = ["NUEVA PARTIDA", "CONTINUAR", "AYUDA", "SALIR"]
        self.save_files = SaveManager.get_save_files()
        save_exists = len(self.save_files) > 0
        
        for i, option in enumerate(options):
            if i == 1 and not save_exists:
                color = DARK_GREY
                text = option + " (Sin guardado)"
            else:
                color = YELLOW if i == self.menu_index else WHITE
                text = option
                
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + text, True, color), (WIDTH//2 - 100, HEIGHT//2 + i * 50))

    def get_combat_options(self):
        options = ["Ataque Básico"]
        t_actual = self.player.logic.titulo_actual
        
        # Solo mostrar habilidades especiales si NO es el título inicial
        if t_actual != "Hoja en Blanco":
            if "Espada" in t_actual or "Hoja" in t_actual:
                options.append("Golpe Habilidad")
            elif "Proyectil" in t_actual or "Arquero" in t_actual or "Halcón" in t_actual:
                options.append("Ataque Distancia")
                
        options.extend(["Huir", "Inventario"])
        return options

    def draw_combat_menu(self):
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - 120, HEIGHT // 2 + 80, 240, 180)
        pygame.draw.rect(self.virtual_surface, (20, 20, 20), menu_rect)
        pygame.draw.rect(self.virtual_surface, WHITE, menu_rect, 2)
        
        font = pygame.font.SysFont('Consolas', 20)
        options = self.get_combat_options()
        
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            text_surface = font.render(prefix + option, True, color)
            self.virtual_surface.blit(text_surface, (menu_rect.x + 20, menu_rect.y + 20 + i * 35))

    def draw_inventory_menu(self):
        inv = self.player.inventory
        w, h = 600, 500
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        
        # Fondo y bordes
        pygame.draw.rect(self.virtual_surface, (15, 15, 25), menu_rect)
        pygame.draw.rect(self.virtual_surface, CYAN, menu_rect, 2)
        
        # Cabecera
        pygame.draw.rect(self.virtual_surface, (30, 30, 50), (menu_rect.x, menu_rect.y, menu_rect.width, 40))
        title_font = pygame.font.SysFont('Consolas', 22, bold=True)
        self.virtual_surface.blit(title_font.render(" MOCHILA DE AVENTURERO ", True, YELLOW), (menu_rect.x + 10, menu_rect.y + 8))
        
        # Panel Izquierdo: Lista de Objetos
        list_rect = pygame.Rect(menu_rect.x + 10, menu_rect.y + 50, 350, h - 70)
        pygame.draw.rect(self.virtual_surface, (10, 10, 15), list_rect)
        pygame.draw.rect(self.virtual_surface, (50, 50, 70), list_rect, 1)
        
        # Panel Derecho: Estado de Equipo
        eq_rect = pygame.Rect(menu_rect.x + 370, menu_rect.y + 50, 220, h - 70)
        pygame.draw.rect(self.virtual_surface, (20, 20, 35), eq_rect)
        pygame.draw.rect(self.virtual_surface, CYAN, eq_rect, 1)
        
        font = pygame.font.SysFont('Consolas', 18)
        small_font = pygame.font.SysFont('Consolas', 14)
        
        # Dibujar Equipo Actual en el panel derecho
        self.virtual_surface.blit(font.render("EQUIPADO:", True, CYAN), (eq_rect.x + 10, eq_rect.y + 10))
        y_eq = eq_rect.y + 40
        slots = [
            ("ARMA", self.player.logic.arma),
            ("CABEZA", self.player.logic.casco),
            ("PECHO", self.player.logic.pechera),
            ("PIES", self.player.logic.botas)
        ]
        for label, item in slots:
            self.virtual_surface.blit(small_font.render(label, True, LIGHT_GREY), (eq_rect.x + 10, y_eq))
            nombre = item.nombre if item else "---"
            color = YELLOW if item else (100, 100, 100)
            self.virtual_surface.blit(font.render(nombre, True, color), (eq_rect.x + 10, y_eq + 15))
            y_eq += 45

        # Lista de inventario con Scroll
        max_visible = (list_rect.height - 40) // 30
        if not hasattr(self, 'inv_scroll'): self.inv_scroll = 0
        
        # Ajustar scroll según menu_index
        if self.menu_index < self.inv_scroll:
            self.inv_scroll = self.menu_index
        elif self.menu_index >= self.inv_scroll + max_visible:
            self.inv_scroll = self.menu_index - max_visible + 1

        # Dibujar items visibles
        for i in range(self.inv_scroll, min(len(inv), self.inv_scroll + max_visible)):
            item = inv[i]
            # Comprobar si está equipado
            logic = self.player.logic
            is_equipped = False
            if isinstance(item, Arma):
                if item == logic.arma: is_equipped = True
            elif isinstance(item, Armadura):
                if item in [logic.casco, logic.pechera, logic.botas]: is_equipped = True

            color = CYAN if i == self.menu_index else (GREEN if is_equipped else WHITE)
            prefix = "> " if i == self.menu_index else "  "
            eq_tag = " [E]" if is_equipped else ""
            cant_tag = f" x{item.cantidad}" if hasattr(item, 'cantidad') and item.cantidad > 1 else ""
            
            draw_y = menu_rect.y + 50 + (i - self.inv_scroll) * 30
            text_surface = font.render(f"{prefix}{item.nombre}{cant_tag}{eq_tag}", True, color)
            self.virtual_surface.blit(text_surface, (menu_rect.x + 20, draw_y))

        # Opción Salir (siempre al final de la lista)
        exit_idx = len(inv)
        if exit_idx >= self.inv_scroll and exit_idx < self.inv_scroll + max_visible:
            color = CYAN if exit_idx == self.menu_index else WHITE
            prefix = "> " if exit_idx == self.menu_index else "  "
            draw_y = menu_rect.y + 50 + (exit_idx - self.inv_scroll) * 30
            self.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 20, draw_y))

        # Mostrar descripción del seleccionado
        if self.menu_index < len(inv):
            item = inv[self.menu_index]
            self.draw_description_box(getattr(item, 'descripcion', "Sin descripción."))
        else:
            self.draw_description_box("Cerrar el inventario y volver al juego.")

    def draw_shop_menu(self):
        w = 450
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 110, w, 220)
        pygame.draw.rect(self.virtual_surface, (30, 20, 20), menu_rect)
        pygame.draw.rect(self.virtual_surface, YELLOW, menu_rect, 2)
        font = pygame.font.SysFont('Consolas', 18)
        self.virtual_surface.blit(font.render("TIENDA DEL MERCADER", True, YELLOW), (menu_rect.x + 20, menu_rect.y + 10))
        options = ["Pocion Media (100 Cobre)", "Arma Aleatoria (500 Cobre)", "Pocion Regreso (10 Cobre)", "Vender Objeto", "Salir"]
        descriptions = [
            "Restaura el 50% de tu salud máxima.",
            "Un arma poderosa acorde a tu nivel actual.",
            "Te permite volver al pueblo pero pierdes XP.",
            "Vende tus objetos por la mitad de su valor.",
            "Cierra la tienda del mercader."
        ]
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 40 + i * 32))
        
        self.draw_description_box(descriptions[self.menu_index])

    def draw_sell_menu(self):
        self.draw_inventory_menu()
        title_font = pygame.font.SysFont('Consolas', 22, bold=True)
        self.virtual_surface.blit(title_font.render("VENDER (Enter para 1/2 valor)", True, RED), (MAP_WIDTH // 2 - 130, 60))

    def draw_bank_menu(self):
        w = 450
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 110, w, 220)
        pygame.draw.rect(self.virtual_surface, (20, 30, 30), menu_rect)
        pygame.draw.rect(self.virtual_surface, LIGHT_GREY, menu_rect, 2)
        font = pygame.font.SysFont('Consolas', 18)
        banco = self.player.logic.banco_cobre
        self.virtual_surface.blit(font.render(f"BANCO (Ahorros: {banco} Cob)", True, CYAN), (menu_rect.x + 20, menu_rect.y + 10))
        options = ["Depositar todo", "Retirar todo", "Guardar Objeto", "Retirar Objeto", "Salir"]
        descriptions = [
            "Guarda todo tu dinero actual en la caja fuerte.",
            "Retira todos tus ahorros del banco.",
            "Abre el baúl para guardar objetos de tu inventario.",
            "Abre el baúl para recuperar objetos guardados.",
            "Cierra el menú del banco."
        ]
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 50 + i * 32))
            
        self.draw_description_box(descriptions[self.menu_index])

    def draw_vault_menu(self, items, title):
        w = 450
        h = 500
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (10, 10, 20), menu_rect)
        pygame.draw.rect(self.virtual_surface, CYAN, menu_rect, 2)
        font = pygame.font.SysFont('Consolas', 18)
        self.virtual_surface.blit(font.render(title, True, YELLOW), (menu_rect.x + 10, menu_rect.y + 10))

        # Lógica de Scroll
        max_visible = (h - 100) // 30
        if not hasattr(self, 'vault_scroll'): self.vault_scroll = 0
        
        if self.menu_index < self.vault_scroll:
            self.vault_scroll = self.menu_index
        elif self.menu_index >= self.vault_scroll + max_visible:
            self.vault_scroll = self.menu_index - max_visible + 1

        for i in range(self.vault_scroll, min(len(items), self.vault_scroll + max_visible)):
            item = items[i]
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            cant_tag = f" x{item.cantidad}" if hasattr(item, 'cantidad') and item.cantidad > 1 else ""
            draw_y = menu_rect.y + 40 + (i - self.vault_scroll) * 30
            self.virtual_surface.blit(font.render(prefix + item.nombre + cant_tag, True, color), (menu_rect.x + 20, draw_y))
            
        # Opción Salir
        exit_idx = len(items)
        if exit_idx >= self.vault_scroll and exit_idx < self.vault_scroll + max_visible:
            color = CYAN if exit_idx == self.menu_index else WHITE
            prefix = "> " if exit_idx == self.menu_index else "  "
            draw_y = menu_rect.y + 40 + (exit_idx - self.vault_scroll) * 30
            self.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 20, draw_y))
        
        if self.menu_index < len(items):
            item = items[self.menu_index]
            self.draw_description_box(getattr(item, 'descripcion', "Sin descripción."))
        else:
            self.draw_description_box("Volver al menú principal del banco.")

    def draw_confirm_exit(self):
        w, h = 400, 200
        rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (30, 10, 10), rect)
        pygame.draw.rect(self.virtual_surface, RED, rect, 3)
        
        title_font = pygame.font.SysFont('Consolas', 24, bold=True)
        font = pygame.font.SysFont('Consolas', 20)
        
        self.virtual_surface.blit(title_font.render("¿SALIR DEL JUEGO?", True, WHITE), (rect.x + 80, rect.y + 40))
        
        color_y = YELLOW if self.menu_index == 0 else WHITE
        color_n = YELLOW if self.menu_index == 1 else WHITE
        
        self.virtual_surface.blit(font.render("> SÍ (Cerrar)", True, color_y), (rect.x + 100, rect.y + 100))
        self.virtual_surface.blit(font.render("> NO (Seguir)", True, color_n), (rect.x + 100, rect.y + 140))
        
        # Mensaje de guardado
        msg_font = pygame.font.SysFont('Consolas', 16)
        if self.profundidad == 0:
            msg = "Se guardará tu progreso automáticamente."
            color = GREEN
        else:
            msg = "¡CUIDADO! Perderás el progreso de este piso."
            color = RED
        self.virtual_surface.blit(msg_font.render(msg, True, color), (rect.x + 30, rect.y + 175))

    def draw_level_selection(self):
        w, h = 500, 250
        rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (10, 20, 30), rect)
        pygame.draw.rect(self.virtual_surface, CYAN, rect, 2)
        
        title_font = pygame.font.SysFont('Consolas', 24, bold=True)
        font = pygame.font.SysFont('Consolas', 20)
        
        self.virtual_surface.blit(title_font.render("¿A DÓNDE QUIERES IR?", True, YELLOW), (rect.x + 100, rect.y + 30))
        
        options = [
            f"Entrar al Piso 1",
            f"Saltar al Piso {self.max_profundidad}",
            "Cancelar"
        ]
        
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + option, True, color), (rect.x + 50, rect.y + 80 + i * 40))

    def draw_name_input_screen(self):
        self.virtual_surface.fill((10, 10, 20))
        title_font = pygame.font.SysFont('Consolas', 40, bold=True)
        font = pygame.font.SysFont('Consolas', 30)
        
        self.virtual_surface.blit(title_font.render("NOMBRE DE TU HÉROE", True, CYAN), (WIDTH//2 - 200, HEIGHT//2 - 100))
        
        # Caja de texto
        box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2, 400, 50)
        pygame.draw.rect(self.virtual_surface, (30, 30, 40), box_rect)
        pygame.draw.rect(self.virtual_surface, YELLOW, box_rect, 2)
        
        name_surface = font.render(self.character_name, True, WHITE)
        self.virtual_surface.blit(name_surface, (box_rect.x + 10, box_rect.y + 10))
        
        if len(self.character_name) < 15:
            # Cursor parpadeante
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = box_rect.x + 10 + font.size(self.character_name)[0]
                pygame.draw.line(self.virtual_surface, WHITE, (cursor_x, box_rect.y + 10), (cursor_x, box_rect.y + 40), 2)

        self.virtual_surface.blit(pygame.font.SysFont('Consolas', 20).render("Pulsa ENTER para confirmar", True, LIGHT_GREY), (WIDTH//2 - 130, HEIGHT//2 + 100))

    def draw_load_selection(self):
        self.virtual_surface.fill((10, 10, 20))
        title_font = pygame.font.SysFont('Consolas', 40, bold=True)
        font = pygame.font.SysFont('Consolas', 24)
        
        self.virtual_surface.blit(title_font.render("CARGAR PARTIDA", True, CYAN), (WIDTH//2 - 150, HEIGHT//2 - 200))
        
        if not self.save_files:
            self.virtual_surface.blit(font.render("No hay archivos de guardado.", True, RED), (WIDTH//2 - 180, HEIGHT//2))
            self.virtual_surface.blit(font.render("Pulsa ESC para volver", True, WHITE), (WIDTH//2 - 130, HEIGHT//2 + 50))
            return

        # Lista de archivos con scroll si es necesario
        max_visible = 6
        if not hasattr(self, 'load_scroll'): self.load_scroll = 0
        if self.menu_index < self.load_scroll: self.load_scroll = self.menu_index
        elif self.menu_index >= self.load_scroll + max_visible: self.load_scroll = self.menu_index - max_visible + 1

        for i in range(self.load_scroll, min(len(self.save_files), self.load_scroll + max_visible)):
            filename = self.save_files[i]
            color = YELLOW if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + filename, True, color), (WIDTH//2 - 200, HEIGHT//2 - 100 + (i - self.load_scroll) * 40))

        self.virtual_surface.blit(font.render("ESC para Volver", True, LIGHT_GREY), (WIDTH//2 - 100, HEIGHT//2 + 180))

    def draw_save_selection(self):
        w, h = 500, 400
        rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (10, 10, 20), rect)
        pygame.draw.rect(self.virtual_surface, YELLOW, rect, 2)
        
        title_font = pygame.font.SysFont('Consolas', 24, bold=True)
        font = pygame.font.SysFont('Consolas', 20)
        
        self.virtual_surface.blit(title_font.render("¿DÓNDE QUIERES GUARDAR?", True, CYAN), (rect.x + 100, rect.y + 20))
        
        options = ["NUEVO GUARDADO"]
        for f in self.save_files:
            options.append(f"Sobrescribir: {f}")
        options.append("SALIR SIN GUARDAR")
        options.append("CANCELAR")

        max_visible = 8
        if not hasattr(self, 'save_scroll'): self.save_scroll = 0
        if self.menu_index < self.save_scroll: self.save_scroll = self.menu_index
        elif self.menu_index >= self.save_scroll + max_visible: self.save_scroll = self.menu_index - max_visible + 1

        for i in range(self.save_scroll, min(len(options), self.save_scroll + max_visible)):
            color = YELLOW if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            text = options[i]
            if len(text) > 40: text = text[:37] + "..."
            self.virtual_surface.blit(font.render(prefix + text, True, color), (rect.x + 30, rect.y + 60 + (i - self.save_scroll) * 35))

    def draw_combat_alert(self):
        if not self.current_enemy: return
        
        # Flash effect
        alpha = int(abs(pygame.time.get_ticks() % 1000 - 500) / 500 * 150) + 100
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 40 if self.combat_intro_timer > 0.5 else 0))
        self.virtual_surface.blit(overlay, (0, 0))
        
        font_big = pygame.font.SysFont('Consolas', 80, bold=True)
        font_small = pygame.font.SysFont('Consolas', 30, bold=True)
        
        text_vs = f"{self.character_name.upper()} VS {self.current_enemy.name.upper()}"
        
        # Sombra
        shadow = font_big.render("¡COMBATE!", True, (50, 0, 0))
        self.virtual_surface.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 5, HEIGHT//2 - 100 + 5))
        
        # Texto principal
        text_surf = font_big.render("¡COMBATE!", True, RED)
        self.virtual_surface.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 - 100))
        
        # Texto secundario (VS)
        vs_surf = font_small.render(text_vs, True, WHITE)
        self.virtual_surface.blit(vs_surf, (WIDTH//2 - vs_surf.get_width()//2, HEIGHT//2))
        
        # Líneas decorativas
        line_w = 400 * (self.combat_intro_timer / 0.8)
        pygame.draw.line(self.virtual_surface, RED, (WIDTH//2 - line_w//2, HEIGHT//2 - 120), (WIDTH//2 + line_w//2, HEIGHT//2 - 120), 4)
        pygame.draw.line(self.virtual_surface, RED, (WIDTH//2 - line_w//2, HEIGHT//2 + 50), (WIDTH//2 + line_w//2, HEIGHT//2 + 50), 4)

    def draw_help_screen(self):
        self.virtual_surface.fill((10, 10, 20))
        title_font = pygame.font.SysFont('Consolas', 40, bold=True)
        sub_font = pygame.font.SysFont('Consolas', 22, bold=True)
        font = pygame.font.SysFont('Consolas', 18)
        
        self.virtual_surface.blit(title_font.render("GUÍA DEL JUEGO", True, CYAN), (WIDTH//2 - 250, 50))
        
        sections = [
            ("CONTROLES BÁSICOS", [
                "- Flechas / WASD: Moverse por el mundo.",
                "- Enter: Confirmar acciones en menús.",
                "- Esc: Volver o salir.",
                "- Tecla I: Abrir el Inventario.",
                "- Tecla T: Menú de Títulos (Identidad)."
            ]),
            ("EL SISTEMA DE TÍTULOS", [
                "Cada título otorga beneficios únicos y especializaciones.",
                "El mundo observa cómo luchas y cómo vives.",
                "Descubre como obtener los titulos jugando, esto reemplaza el sistema de clases."
            ]),
            ("COMBATE Y EXPLORACIÓN", [
                "- El combate es por turnos. Elige bien tu estrategia.",
                "- Puedes encontrar cofres y NPCs en el calabozo y el pueblo.",
                "- Solo puedes guardar tu partida en el PUEBLO.",
                "- Morir en el calabozo tiene penalizaciones de equipo y dinero."
            ])
        ]
        
        y = 130
        for title, lines in sections:
            self.virtual_surface.blit(sub_font.render(title, True, YELLOW), (100, y))
            y += 30
            for line in lines:
                self.virtual_surface.blit(font.render(line, True, WHITE), (120, y))
                y += 25
            y += 20
            
        self.virtual_surface.blit(font.render("Pulsa ESC o ENTER para volver", True, LIGHT_GREY), (WIDTH//2 - 150, HEIGHT - 80))

    def draw_title_menu(self):
        w, h = 500, 450
        rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (20, 20, 35), rect)
        pygame.draw.rect(self.virtual_surface, CYAN, rect, 2)
        
        font = pygame.font.SysFont('Consolas', 18)
        title_font = pygame.font.SysFont('Consolas', 22, bold=True)
        self.virtual_surface.blit(title_font.render("CONTRATOS DE IDENTIDAD (TÍTULOS)", True, YELLOW), (rect.x + 20, rect.y + 20))
        
        from logic.personaje import TITULOS_DATA
        titulos = self.player.logic.titulos_desbloqueados
        
        for i, t_name in enumerate(titulos):
            t_data = TITULOS_DATA.get(t_name, {})
            is_passive = t_data.get("tipo") == "pasivo"
            is_active = t_name == self.player.logic.titulo_actual
            
            color = YELLOW if i == self.menu_index else (GREEN if is_active else (CYAN if is_passive else WHITE))
            prefix = "> " if i == self.menu_index else ("* " if is_active else ("+ " if is_passive else "  "))
            suffix = " (PASIVO)" if is_passive else ""
            
            self.virtual_surface.blit(font.render(f"{prefix}{t_name}{suffix}", True, color), (rect.x + 30, rect.y + 70 + i * 35))
            
        # Opción Salir
        exit_idx = len(titulos)
        color = YELLOW if exit_idx == self.menu_index else WHITE
        self.virtual_surface.blit(font.render(f"{'> ' if exit_idx == self.menu_index else '  '}VOLVER", True, color), (rect.x + 30, rect.y + 70 + exit_idx * 35))
        
        # Descripción del seleccionado
        if self.menu_index < len(titulos):
            t_name = titulos[self.menu_index]
            desc = TITULOS_DATA[t_name]["descripcion"]
            self.draw_description_box(desc)
        else:
            self.draw_description_box("Cerrar el menú de títulos.")

    def events(self):
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_ESCAPE:
                    if self.state == "CONFIRM_EXIT":
                        self.state = self.prev_state
                    else:
                        self.prev_state = self.state
                        self.state = "CONFIRM_EXIT"
                        self.menu_index = 1 # Por defecto en 'NO'
                
                if self.state == "TITLE_SCREEN":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(3, self.menu_index + 1)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_index == 0: # Nueva Partida
                            self.state = "NAME_INPUT"
                            self.character_name = ""
                        elif self.menu_index == 1: # Continuar
                            self.save_files = SaveManager.get_save_files()
                            if self.save_files:
                                self.state = "LOAD_SELECTION"
                                self.menu_index = 0
                        elif self.menu_index == 2: # Ayuda
                            self.state = "HELP_SCREEN"
                        elif self.menu_index == 3: # Salir
                            self.quit_game()

                elif self.state == "HELP_SCREEN":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = "TITLE_SCREEN"
                        self.menu_index = 2

                elif self.state == "LOAD_SELECTION":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "TITLE_SCREEN"
                        self.menu_index = 1
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(len(self.save_files) - 1, self.menu_index + 1)
                    elif event.key == pygame.K_RETURN:
                        if self.save_files:
                            filename = self.save_files[self.menu_index]
                            save_data = SaveManager.load_game(filename)
                            if save_data:
                                self.start_saved_game(save_data)

                elif self.state == "NAME_INPUT":
                    if event.key == pygame.K_BACKSPACE:
                        self.character_name = self.character_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if len(self.character_name.strip()) > 0:
                            self.start_game("aventurero", self.character_name.strip())
                    elif event.unicode.isalnum() or event.key == pygame.K_SPACE:
                        if len(self.character_name) < 15:
                            self.character_name += event.unicode
                        
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
                    if event.key == pygame.K_t:
                        self.state = "TITLE_MENU"
                        self.menu_index = 0

                elif self.state == "DIALOG":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = self.next_state
                        if self.state in ["SHOP", "BANK"]:
                            self.menu_index = 0
                
                elif self.state == "COMBAT":
                    options = self.get_combat_options()
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(len(options) - 1, self.menu_index + 1)
                    if event.key == pygame.K_RETURN:
                        self.resolve_combat_action()

                elif self.state == "INVENTORY":
                    inv = self.player.inventory
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(len(inv), self.menu_index + 1)
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                        # Cerrar inventario
                        self.state = "COMBAT" if self.current_enemy else "PLAYING"
                    if event.key == pygame.K_RETURN:
                        if self.menu_index < len(inv):
                            item = inv[self.menu_index]
                            self.use_item(item)
                        else:
                            self.state = "COMBAT" if self.current_enemy else "PLAYING"

                elif self.state == "SHOP":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(4, self.menu_index + 1)
                    if event.key == pygame.K_RETURN:
                        if self.menu_index == 0:
                            if self.player.logic.gastar_monedas(100):
                                item = Pocion("media")
                                self.player.add_to_inventory(item)
                                self.log.add_message("[MERCADER] ¡Aquí tienes!")
                                self.spawn_floating_text(f"+{item.nombre}", self.player.rect.centerx, self.player.rect.top, YELLOW)
                            else:
                                self.log.add_message("[MERCADER] No tienes dinero.")
                        elif self.menu_index == 1:
                            if self.player.logic.gastar_monedas(500):
                                dmg = random.randint(20 + self.player.logic.nivel*2, 40 + self.player.logic.nivel*5)
                                # Determinar tipo basado en título activo o azar
                                t_actual = self.player.logic.titulo_actual
                                if "Proyectil" in t_actual or "Arquero" in t_actual or "Halcón" in t_actual:
                                    item = Arma(f"Arco lvl {self.player.logic.nivel}", dmg, "distancia")
                                else:
                                    item = Arma(f"Espada lvl {self.player.logic.nivel}", dmg, "fisico")
                                self.player.add_to_inventory(item)
                                self.log.add_message("[MERCADER] ¡Excelente arma!")
                                self.spawn_floating_text(f"+{item.nombre}", self.player.rect.centerx, self.player.rect.top, YELLOW)
                            else:
                                self.log.add_message("[MERCADER] No tienes dinero.")
                        elif self.menu_index == 2:
                            if self.player.logic.gastar_monedas(10):
                                item = PocionRegreso()
                                self.player.add_to_inventory(item)
                                self.log.add_message("[MERCADER] Regresa a salvo.")
                                self.spawn_floating_text(f"+{item.nombre}", self.player.rect.centerx, self.player.rect.top, YELLOW)
                            else:
                                self.log.add_message("[MERCADER] No tienes dinero.")
                        elif self.menu_index == 3:
                            self.state = "SELL"
                            self.menu_index = 0
                        elif self.menu_index == 4:
                            self.state = "PLAYING"
                
                elif self.state == "SELL":
                    inv = self.player.inventory
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(len(inv), self.menu_index + 1)
                    if event.key == pygame.K_ESCAPE:
                        self.state = "SHOP"
                        self.menu_index = 0
                    if event.key == pygame.K_RETURN:
                        if self.menu_index < len(inv):
                            item = inv[self.menu_index]
                            # Precio de venta: 1/2 del precio de compra aprox
                            valor = 50 # Base
                            if isinstance(item, Arma): valor = 200
                            elif isinstance(item, Armadura): valor = 150
                            
                            self.player.logic.añadir_monedas(valor)
                            self.log.add_message(f"[MERCADER] Te doy {valor} Cob por {item.nombre}.")
                            
                            if hasattr(item, 'cantidad') and item.cantidad > 1:
                                item.cantidad -= 1
                            else:
                                inv.pop(self.menu_index)
                                self.menu_index = max(0, self.menu_index - 1)
                        else:
                            self.state = "SHOP"
                            self.menu_index = 3
                
                elif self.state == "BANK":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(4, self.menu_index + 1)
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
                            self.state = "BANK_STORE"
                            self.menu_index = 0
                        elif self.menu_index == 3:
                            self.state = "BANK_RETRIEVE"
                            self.menu_index = 0
                        elif self.menu_index == 4:
                            self.state = "PLAYING"

                elif self.state == "BANK_STORE":
                    inv = self.player.inventory
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(len(inv), self.menu_index + 1)
                    if event.key == pygame.K_ESCAPE:
                        self.state = "BANK"
                        self.menu_index = 2
                    if event.key == pygame.K_RETURN:
                        if self.menu_index < len(inv):
                            item = inv[self.menu_index]
                            
                            # Intentar apilar en el baúl
                            found = False
                            if isinstance(item, (Pocion, PocionRegreso)):
                                for b_item in self.player.logic.baul:
                                    if type(b_item) == type(item):
                                        if isinstance(item, Pocion):
                                            if b_item.tipo == item.tipo:
                                                b_item.cantidad += 1
                                                found = True
                                                break
                                        else: # PocionRegreso
                                            b_item.cantidad += 1
                                            found = True
                                            break
                            
                            if not found:
                                # Crear una copia para el baúl o mover el objeto
                                # Si es un stack, creamos uno nuevo con cantidad 1
                                if hasattr(item, 'cantidad') and item.cantidad > 1:
                                    import copy
                                    new_item = copy.copy(item)
                                    new_item.cantidad = 1
                                    self.player.logic.baul.append(new_item)
                                else:
                                    self.player.logic.baul.append(inv.pop(self.menu_index))
                                    self.menu_index = max(0, self.menu_index - 1)
                            else:
                                # Si se apiló, reducir cantidad del inv
                                if hasattr(item, 'cantidad') and item.cantidad > 1:
                                    item.cantidad -= 1
                                else:
                                    inv.pop(self.menu_index)
                                    self.menu_index = max(0, self.menu_index - 1)

                            self.log.add_message(f"[BANQUERO] {item.nombre} guardado.")
                        else:
                            self.state = "BANK"
                            self.menu_index = 2

                elif self.state == "BANK_RETRIEVE":
                    baul = self.player.logic.baul
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(len(baul), self.menu_index + 1)
                    if event.key == pygame.K_ESCAPE:
                        self.state = "BANK"
                        self.menu_index = 3
                    if event.key == pygame.K_RETURN:
                        if self.menu_index < len(baul):
                            item = baul[self.menu_index]
                            self.player.add_to_inventory(item)
                            
                            if hasattr(item, 'cantidad') and item.cantidad > 1:
                                item.cantidad -= 1
                            else:
                                baul.pop(self.menu_index)
                                self.menu_index = max(0, self.menu_index - 1)
                            
                            self.log.add_message(f"[BANQUERO] {item.nombre} retirado.")
                        else:
                            self.state = "BANK"
                            self.menu_index = 3

                elif self.state == "CONFIRM_EXIT":
                    if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = 1 - self.menu_index # Alternar entre 0 y 1
                    if event.key == pygame.K_RETURN:
                        if self.menu_index == 0:
                            if self.profundidad == 0:
                                self.state = "SAVE_SELECTION"
                                self.save_files = SaveManager.get_save_files()
                                self.menu_index = 0
                            else:
                                self.quit_game()
                        else:
                            self.state = self.prev_state
                    if event.key == pygame.K_n:
                        self.state = self.prev_state
                    if event.key == pygame.K_y or event.key == pygame.K_s:
                        if self.profundidad == 0:
                            self.state = "SAVE_SELECTION"
                            self.save_files = SaveManager.get_save_files()
                            self.menu_index = 0
                        else:
                            self.quit_game()

                elif self.state == "SAVE_SELECTION":
                    options_count = len(self.save_files) + 3 # Nuevo, Existentes, Salir sin guardar, Cancelar
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(options_count - 1, self.menu_index + 1)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_index == 0: # Nuevo Guardado
                            self.quit_game() # SaveManager.save_game se llama con None (genera uno nuevo)
                        elif self.menu_index <= len(self.save_files): # Sobrescribir existente
                            filename = self.save_files[self.menu_index - 1]
                            self.quit_game(filename)
                        elif self.menu_index == len(self.save_files) + 1: # Salir sin guardar
                            pygame.quit()
                            sys.exit()
                        else: # Cancelar
                            self.state = "CONFIRM_EXIT"
                            self.menu_index = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "CONFIRM_EXIT"
                        self.menu_index = 0

                elif self.state == "TITLE_MENU":
                    titulos = self.player.logic.titulos_desbloqueados
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(len(titulos), self.menu_index + 1)
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_t:
                        self.state = "PLAYING"
                    if event.key == pygame.K_RETURN:
                        if self.menu_index < len(titulos):
                            nuevo = titulos[self.menu_index]
                            t_data = TITULOS_DATA.get(nuevo, {})
                            if t_data.get("tipo") == "pasivo":
                                self.log.add_message("[SISTEMA] Este título es pasivo y ya está activo.")
                            elif self.player.logic.cambiar_titulo(nuevo):
                                self.log.add_message(f"[TITULO] Equipado: {nuevo}")
                                self.state = "PLAYING"
                        else:
                            self.state = "PLAYING"

                elif self.state == "LEVEL_SELECTION":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(2, self.menu_index + 1)
                    if event.key == pygame.K_RETURN:
                        if self.menu_index == 0: # Piso 1
                            self.profundidad = 1
                            self.went_down = True
                            self.load_level()
                        elif self.menu_index == 1: # Max Piso
                            self.profundidad = self.max_profundidad
                            self.went_down = True
                            self.load_level()
                        else: # Cancelar
                            self.state = "PLAYING"
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"

if __name__ == "__main__":
    g = Game()
    while True:
        g.new()
        g.run()
