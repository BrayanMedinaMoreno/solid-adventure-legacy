import os
import sys
import pygame

# Asegurar que estamos en la raíz del proyecto para poder cargar assets/
if getattr(sys, 'frozen', False):
    # Si estamos corriendo como un ejecutable compilado con PyInstaller
    root_path = os.path.dirname(sys.executable)
else:
    # Si estamos corriendo desde el código fuente python
    root_path = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(root_path) == 'src':
        root_path = os.path.dirname(root_path)

os.chdir(root_path)
if os.path.join(root_path, "src") not in sys.path:
    sys.path.insert(0, os.path.join(root_path, "src"))


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
from entities.enemy_types import Goblin, Orco, Slime, SlimeBoss, SlimeMutante, SlimeRosa, SlimeArcano
from items.chest import Chest
from items.potion import Pocion, PocionRegreso
from logic.armas import Arma
from logic.armaduras import Armadura
from entities.npc import Mercader, Banquero, CruzInteractiva
from entities.trap import Trap
from ui.panel import Panel
from ui.log import Log
from ui.floating_text import FloatingText
from ui.minimap import Minimap
from logic.save_manager import SaveManager
import core.audio as audio
import core.combat as combat
import core.spawner as spawner
import screens.draw_world as draw_world
import screens.title_screens as title_screens
import screens.help_screen as help_screen
import screens.game_screens as game_screens

class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception as e:
            print("No se pudo inicializar el mixer de audio:", e)
        self.current_music = None
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
        self.title_particles = []
        self.save_return_state = "QUIT"
        self.chest_reward_item = None
        self.options_menu_index = 0
        self.options_return_state = "TITLE_SCREEN"
        self.music_volume_display_timer = 0.0
        self.music_volume = self.load_music_volume()
        self.sfx_volume = 0.6
        self.sounds = self.load_sounds()
        self.qty_mode = "BUY"
        self.qty_item_name = ""
        self.qty_unit_price = 0
        self.qty_current = 1
        self.qty_max = 1
        self.qty_item_factory = None
        self.qty_inv_index = 0
        self.qty_item = None
        self.inventory_tab = "INVENTARIO"
        self.title_scroll = 0
        self.help_page = 0

    def load_sounds(self):
        return audio.load_sounds(self)

    def play_sfx(self, name):
        audio.play_sfx(self, name)

    def load_music_volume(self):
        return audio.load_music_volume(self)

    def save_music_volume(self):
        audio.save_music_volume(self)

    def set_music_volume(self, vol):
        audio.set_music_volume(self, vol)

    def change_music_volume(self, delta):
        audio.change_music_volume(self, delta)


    def show_chest_reward(self, item):
        self.chest_reward_item = item
        self.state = "CHEST_REWARD"

    def open_quantity_buy(self, item_name, unit_price, item_factory):
        l = self.player.logic
        total_dinero = l.cobre + l.plata * 100 + l.oro * 10000 + l.platino * 1000000
        max_posible = total_dinero // unit_price
        if max_posible < 1:
            self.log.add_message("[MERCADER] No tienes suficiente dinero.")
            self.spawn_floating_text("¡SIN DINERO!", self.player.rect.centerx, self.player.rect.top - 20, RED)
            return
        self.qty_mode = "BUY"
        self.qty_item_name = item_name
        self.qty_unit_price = unit_price
        self.qty_current = 1
        self.qty_max = max(1, min(99, max_posible))
        self.qty_item_factory = item_factory
        self.state = "SHOP_QUANTITY_BUY"

    def open_quantity_sell(self, inv_index, item, unit_price):
        self.qty_mode = "SELL"
        self.qty_inv_index = inv_index
        self.qty_item = item
        self.qty_item_name = item.nombre
        self.qty_unit_price = unit_price
        self.qty_current = 1
        self.qty_max = getattr(item, 'cantidad', 1)
        self.state = "SHOP_QUANTITY_SELL"

    def new(self):
        self.state = "TITLE_SCREEN"
        self.menu_index = 0
        self.clase_seleccionada = 0
        
        # Reproducir música del Hub
        music_to_play = 'assets/Music/Morning_at_the_Gate_MusicaHub.mp3'
        if self.current_music != music_to_play:
            try:
                pygame.mixer.music.load(music_to_play)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.current_music = music_to_play
            except Exception as e:
                print("Error al reproducir música del hub:", e)

    def start_game(self, clase_elegida, nombre=None, dificultad="normal"):
        self.clase_elegida = clase_elegida
        self.dificultad = dificultad
        self.profundidad = 0 # Empezamos en el Pueblo
        self.went_down = True
        self.current_save_file = None
        
        self.panel = Panel(self)
        self.log = Log()
        self.player = None
        self.log.add_message(f"¡Bienvenido al mundo, {nombre}!")
        self.log.add_message(f"Dificultad: {'Fácil' if dificultad == 'facil' else 'Normal'}")
        self.character_name = nombre
        
        self.load_level()

    def start_saved_game(self, save_data, filename=None):
        self.max_profundidad = save_data["max_profundidad"]
        self.dificultad = save_data.get("dificultad", "normal")
        self.profundidad = 0 # Siempre empezamos en el pueblo al cargar
        self.went_down = True
        self.current_save_file = filename
        
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
        
        # Reproducir música según el nivel (pueblo o calabozo)
        music_to_play = None
        if self.profundidad == 0:
            music_to_play = 'assets/Music/The_Road_Back_Home_Pueblo_Inicial.mp3'
        else:
            music_to_play = 'assets/Music/Under_the_Weight_of_Stone_Masmorra.mp3'
            
        if music_to_play and self.current_music != music_to_play:
            try:
                pygame.mixer.music.load(music_to_play)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.current_music = music_to_play
            except Exception as e:
                print("Error cargando o reproduciendo música:", e)
                
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
            if self.profundidad == 0:
                start_x, start_y = self.level.entrance if self.level.entrance else (self.level.width_tiles // 2, self.level.height_tiles // 2 + 2)
            elif self.went_down:
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
            spawner.populate_level(self, occupied_tiles)
        else:
            spawner.populate_level(self, occupied_tiles)

        # Inicializar minimapa
        self.minimap = Minimap(self)

    def get_chest_at(self, x, y):
        return combat.get_chest_at(self, x, y)

    def get_enemy_at(self, x, y):
        return combat.get_enemy_at(self, x, y)

    def get_npc_at(self, x, y):
        return combat.get_npc_at(self, x, y)

    def get_trap_at(self, x, y):
        return combat.get_trap_at(self, x, y)

    def start_combat(self, enemy):
        combat.start_combat(self, enemy)

    def resolve_combat_action(self):
        combat.resolve_combat_action(self)

    def resolve_enemy_turn(self):
        combat.resolve_enemy_turn(self)

    def spawn_floating_text(self, text, x, y, color=WHITE):
        combat.spawn_floating_text(self, text, x, y, color)

    def use_item(self, item):
        combat.use_item(self, item)

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
                SaveManager.save_game(self, save_filename)
        pygame.quit()
        sys.exit()

    def return_to_title_screen(self):
        self.state = "TITLE_SCREEN"
        self.menu_index = 0
        self.player = None
        self.current_enemy = None
        self.current_chest = None
        self.chest_reward_item = None
        
        # Limpiar grupos de sprites
        if hasattr(self, 'all_sprites'): self.all_sprites.empty()
        if hasattr(self, 'enemies'): self.enemies.empty()
        if hasattr(self, 'chests'): self.chests.empty()
        if hasattr(self, 'npcs'): self.npcs.empty()
        if hasattr(self, 'decorations'): self.decorations.empty()
        if hasattr(self, 'stairs'): self.stairs.empty()
        if hasattr(self, 'traps'): self.traps.empty()
        if hasattr(self, 'floating_texts'): self.floating_texts.empty()
        
        # Reproducir música del Hub
        music_to_play = 'assets/Music/Morning_at_the_Gate_MusicaHub.mp3'
        if self.current_music != music_to_play:
            try:
                pygame.mixer.music.load(music_to_play)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.current_music = music_to_play
            except Exception as e:
                print("Error al reproducir música del hub:", e)

    def update(self):
        # Actualizar lógica
        if hasattr(self, 'player') and self.player:
            self.player.logic.tiempo_juego = getattr(self.player.logic, 'tiempo_juego', 0.0) + self.dt
            
        self.floating_texts.update(self.dt)
        if self.combat_intro_timer > 0:
            self.combat_intro_timer -= self.dt
            
        if hasattr(self, 'music_volume_display_timer') and self.music_volume_display_timer > 0:
            self.music_volume_display_timer -= self.dt
            
        if hasattr(self, 'screen_shake') and self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - 30 * self.dt)
            
        if self.state == "PLAYING":
            self.player.logic.update_regen(self.dt)
            self.all_sprites.update()


    def draw_grid(self, cam_x=0, cam_y=0):
        draw_world.draw_grid(self, cam_x, cam_y)

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
            
        if self.state == "DIFFICULTY_SELECTION":
            self.draw_difficulty_selection_screen()
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
            
        if self.state == "OPTIONS_SCREEN":
            self.draw_options_screen()
            self.flip_to_screen()
            return
            
        # Si el jugador no existe, no intentar dibujar el mapa ni seguir con la cámara
        if not hasattr(self, 'player') or self.player is None:
            if self.state == "CONFIRM_EXIT":
                self.draw_confirm_exit()
            elif self.state == "SAVE_SELECTION":
                self.draw_save_selection()
            elif self.state == "OPTIONS_SCREEN":
                self.draw_options_screen()
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

        # Establecer el clip para restringir el dibujado al área del mapa
        self.virtual_surface.set_clip(pygame.Rect(0, 0, MAP_WIDTH, HEIGHT))

        self.level.draw(self.virtual_surface, cam_x, cam_y, self)
        
        # Dibujar todos los sprites con offset de cámara
        for sprite in self.all_sprites:
            # Solo dibujar si está cerca de la pantalla para optimizar un poco
            screen_rect = pygame.Rect(cam_x - TILESIZE, cam_y - TILESIZE, MAP_WIDTH + TILESIZE*2, HEIGHT + TILESIZE*2)
            if sprite.rect.colliderect(screen_rect):
                # Comprobar niebla de guerra
                if self.profundidad > 0 and sprite != self.player:
                    grid_x = getattr(sprite, 'x', sprite.rect.x // TILESIZE)
                    grid_y = getattr(sprite, 'y', sprite.rect.y // TILESIZE)
                    if 0 <= grid_x < self.level.width_tiles and 0 <= grid_y < self.level.height_tiles:
                        if not self.level.explored[grid_y][grid_x]:
                            continue
                    else:
                        continue
                        
                offset_pos = (sprite.rect.x - cam_x, sprite.rect.y - cam_y)
                self.virtual_surface.blit(sprite.image, offset_pos)

        self.floating_texts.draw(self.virtual_surface) # Estos pueden ser relativos a pantalla o mapa, asumo mapa
        # Re-ajustar floating texts si es necesario (asumo que se quedan donde nacieron en el mapa)
        
        for enemy in self.enemies:
            if enemy.rect.colliderect(screen_rect):
                # Comprobar niebla de guerra para la barra de vida
                if self.profundidad > 0:
                    grid_x = enemy.x
                    grid_y = enemy.y
                    if not (0 <= grid_x < self.level.width_tiles and 0 <= grid_y < self.level.height_tiles and self.level.explored[grid_y][grid_x]):
                        continue
                        
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

        # Quitar el clip para poder dibujar la interfaz en toda la pantalla
        self.virtual_surface.set_clip(None)

        # Separador UI
        pygame.draw.line(self.virtual_surface, WHITE, (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 2)
        
        # UI
        self.panel.draw(self.virtual_surface)
        self.log.draw(self.virtual_surface)
        if hasattr(self, 'minimap'):
            self.minimap.draw(self.virtual_surface)
        
        if self.state == "COMBAT":
            if self.combat_intro_timer > 0:
                self.draw_combat_alert()
            else:
                self.draw_combat_menu()
                self.draw_enemy_info_box()
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
            self.inventory_tab = "TITULOS"
            self.draw_inventory_menu()
        elif self.state == "LEVEL_SELECTION":
            self.draw_level_selection()
        elif self.state == "CROSS_MENU":
            self.draw_cross_menu()
        elif self.state == "CHEST_REWARD":
            self.draw_chest_reward()
        elif self.state == "OPTIONS_SCREEN":
            self.draw_options_screen()
        elif self.state in ["SHOP_QUANTITY_BUY", "SHOP_QUANTITY_SELL"]:
            self.draw_quantity_selector()

        if getattr(self, 'music_volume_display_timer', 0) > 0:
            self.draw_volume_hud()

        self.flip_to_screen()

    def flip_to_screen(self):
        draw_world.flip_to_screen(self)

    def draw_description_box(self, text):
        draw_world.draw_description_box(self, text)

    def draw_title_screen(self):
        title_screens.draw_title_screen(self)
        
    def draw_name_input_screen(self):
        title_screens.draw_name_input_screen(self)
        
    def draw_difficulty_selection_screen(self):
        title_screens.draw_difficulty_selection_screen(self)
        
    def draw_load_selection(self):
        title_screens.draw_load_selection(self)
        
    def draw_save_selection(self):
        title_screens.draw_save_selection(self)
        
    def draw_title_menu(self):
        title_screens.draw_title_menu(self)
        
    def draw_options_screen(self):
        title_screens.draw_options_screen(self)
        
    def draw_level_selection(self):
        title_screens.draw_level_selection(self)
        
    def draw_help_screen(self):
        help_screen.draw_help_screen(self)
        
    def draw_volume_hud(self):
        draw_world.draw_volume_hud(self)

    def get_combat_options(self):
        return combat.get_combat_options(self)

    def draw_combat_menu(self):
        game_screens.draw_combat_menu(self)

    def draw_enemy_info_box(self):
        game_screens.draw_enemy_info_box(self)

    def draw_inventory_menu(self):
        game_screens.draw_inventory_menu(self)

    def draw_shop_menu(self):
        game_screens.draw_shop_menu(self)

    def draw_cross_menu(self):
        game_screens.draw_cross_menu(self)

    def draw_sell_menu(self):
        game_screens.draw_sell_menu(self)

    def draw_quantity_selector(self):
        game_screens.draw_quantity_selector(self)

    def draw_bank_menu(self):
        game_screens.draw_bank_menu(self)

    def draw_bank_store_menu(self):
        import screens.game_screens as game_screens
        game_screens.draw_vault_menu(self, self.player.inventory, "BAÚL (GUARDAR OBJETOS)")

    def draw_bank_retrieve_menu(self):
        import screens.game_screens as game_screens
        game_screens.draw_vault_menu(self, self.player.logic.baul, "BAÚL (RETIRAR OBJETOS)")

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

    def draw_chest_reward(self):
        game_screens.draw_chest_reward(self)

    def draw_confirm_exit(self):
        game_screens.draw_confirm_exit(self)

    def draw_combat_alert(self):
        game_screens.draw_combat_alert(self)

    def events(self):
        import events.events_title as events_title
        import events.events_playing as events_playing
        import events.events_combat as events_combat
        import events.events_ui as events_ui
        import pygame
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]:
                    self.change_music_volume(0.05)
                elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                    self.change_music_volume(-0.05)
                
                if self.state in ["TITLE_SCREEN", "NAME_INPUT", "DIFFICULTY_SELECTION", "LOAD_SELECTION", "SAVE_SELECTION", "OPTIONS_SCREEN", "HELP_SCREEN"]:
                    events_title.handle(self, event)
                elif self.state == "PLAYING":
                    events_playing.handle(self, event)
                elif self.state == "COMBAT":
                    events_combat.handle(self, event)
                else:
                    events_ui.handle(self, event)



if __name__ == "__main__":
    g = Game()
    while True:
        g.new()
        g.run()
