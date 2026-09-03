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
        sounds = {}
        sound_files = {
            "espada": "assets/EfectosSonido/espada.wav",
            "hacha": "assets/EfectosSonido/hacha_ataque.wav",
            "ballesta": "assets/EfectosSonido/ballesta_disparo.wav",
            "slime": "assets/EfectosSonido/slime_ataque.wav",
            "goblin": "assets/EfectosSonido/goblin_ataque.wav",
            "coins": "assets/EfectosSonido/coins.wav",
            "muerte": "assets/EfectosSonido/muerte.wav"
        }
        for name, path in sound_files.items():
            if os.path.exists(path):
                try:
                    sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"No se pudo cargar sonido {path}: {e}")
        return sounds

    def play_sfx(self, name):
        if hasattr(self, 'sounds') and name in self.sounds:
            try:
                snd = self.sounds[name]
                if snd:
                    vol = getattr(self, 'sfx_volume', 0.6)
                    snd.set_volume(vol)
                    snd.play()
            except Exception as e:
                print(f"Error reproduciendo {name}: {e}")

    def load_music_volume(self):
        try:
            import json
            if os.path.exists("saves/config.json"):
                with open("saves/config.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return float(data.get("music_volume", 0.35))
        except Exception:
            pass
        return 0.35

    def save_music_volume(self):
        try:
            import json
            os.makedirs("saves", exist_ok=True)
            with open("saves/config.json", "w", encoding="utf-8") as f:
                json.dump({"music_volume": self.music_volume}, f)
        except Exception as e:
            print("Error guardando config.json:", e)

    def set_music_volume(self, vol):
        self.music_volume = round(max(0.0, min(1.0, vol)), 2)
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass
        self.save_music_volume()
        self.music_volume_display_timer = 1.8

    def change_music_volume(self, delta):
        self.set_music_volume(self.music_volume + delta)

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
                    
                    if self.profundidad <= 2:
                        # Slimes comunes, algunos goblins y muy rara vez mutantes
                        tipo_enemigo = random.choice([Slime, Slime, Slime, Goblin, SlimeMutante])
                    elif self.profundidad <= 4:
                        # Slimes mutantes y arcanos, orcos, goblins y slimes rosas especiales
                        tipo_enemigo = random.choice([Slime, SlimeMutante, SlimeMutante, SlimeArcano, SlimeArcano, Goblin, Orco, SlimeRosa])
                    else:
                        # Masmorra profunda: Orcos, Slimes Arcanos y Slimes Rosas Especiales
                        tipo_enemigo = random.choice([Goblin, Orco, Orco, SlimeArcano, SlimeRosa, SlimeRosa])
                    
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
            CruzInteractiva(self, self.level.width_tiles // 2, self.level.height_tiles // 2 - 3)

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
        self.menu_index = max(0, min(self.menu_index, len(options) - 1))
        action = options[self.menu_index]
        
        should_end_turn = False
        
        if action == "Ataque Básico":
            arma_p = getattr(self.player.logic, 'arma', None) or getattr(self.player.logic, 'espada', None)
            if arma_p and "hacha" in arma_p.nombre.lower():
                self.play_sfx("hacha")
            else:
                self.play_sfx("espada")
            self.player.logic.atacar(self.current_enemy, self.log, tipo_forzado="fisico")
            should_end_turn = True
        elif action.startswith("Golpe Habilidad"):
            if self.player.logic.cooldowns.get("habilidad", 0) > 0:
                self.log.add_message("[SISTEMA] Habilidad en enfriamiento.")
                self.spawn_floating_text("¡EN ENFRIAMIENTO!", self.player.rect.centerx, self.player.rect.top - 20, YELLOW)
                return
            self.player.logic.cooldowns["habilidad"] = 3
            arma_p = getattr(self.player.logic, 'arma', None) or getattr(self.player.logic, 'espada', None)
            if arma_p and "hacha" in arma_p.nombre.lower():
                self.play_sfx("hacha")
            else:
                self.play_sfx("espada")
            self.player.logic.atacar(self.current_enemy, self.log, tipo_forzado="habilidad")
            should_end_turn = True
        elif action.startswith("Ataque Distancia"):
            if self.player.logic.cooldowns.get("distancia", 0) > 0:
                self.log.add_message("[SISTEMA] Habilidad en enfriamiento.")
                self.spawn_floating_text("¡EN ENFRIAMIENTO!", self.player.rect.centerx, self.player.rect.top - 20, YELLOW)
                return
            self.player.logic.cooldowns["distancia"] = 3
            self.play_sfx("ballesta")
            self.player.logic.atacar(self.current_enemy, self.log, tipo_forzado="distancia")
            should_end_turn = True
        elif action.startswith("Ataque Mágico"):
            if self.player.logic.gastar_mana(15):
                self.play_sfx("espada")
                self.player.logic.atacar(self.current_enemy, self.log, tipo_forzado="magico")
                should_end_turn = True
            else:
                self.log.add_message("[SISTEMA] No tienes suficiente maná.")
                self.spawn_floating_text("¡SIN MANÁ!", self.player.rect.centerx, self.player.rect.top - 20, BLUE)
                return
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
            self.play_sfx("muerte")
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
            self.play_sfx("coins")
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
        
        # Reproducir sonido de ataque del enemigo
        if damage_type == "distancia":
            self.play_sfx("ballesta")
        elif "Goblin" in enemy_name:
            self.play_sfx("goblin")
        elif "Orco" in enemy_name:
            self.play_sfx("hacha")
        elif "Slime" in enemy_name:
            self.play_sfx("slime")
        else:
            self.play_sfx("espada")

        enemy_dmg = max(1, self.current_enemy.fuerza - self.player.logic.defensa)
        if self.player.logic.recibir_daño(enemy_dmg, tipo=damage_type, log=self.log):
            self.spawn_floating_text(f"-{enemy_dmg}", self.player.rect.centerx, self.player.rect.top, RED)
            # Activar vibración de pantalla al recibir daño (Reducida para que sea más sutil)
            if not hasattr(self, 'screen_shake'): self.screen_shake = 0
            self.screen_shake = min(8, self.screen_shake + 2 + enemy_dmg // 5)
        
        if self.player.logic.vida <= 0:
            self.play_sfx("muerte")
            self.log.add_message("[SISTEMA] HAS MUERTO.")
            
            # Penalidad de XP: 20% (sin bajar de nivel, ya que la lógica de nivel no resta)
            xp_perdida = int(self.player.logic.xp * 0.20)
            self.player.logic.xp -= xp_perdida
            
            dificultad = getattr(self, "dificultad", "normal")
            
            if dificultad == "facil":
                # Pierde la mitad del dinero
                self.player.logic.cobre //= 2
                self.player.logic.plata //= 2
                self.player.logic.oro //= 2
                self.player.logic.platino //= 2
                
                self.log.add_message(f"[SISTEMA] Perdiste {xp_perdida} XP y la mitad de tu dinero, pero conservas tus objetos.")
            else:
                # Dificultad Normal (Hardcore)
                self.player.logic.cobre = 0
                self.player.logic.plata = 0
                self.player.logic.oro = 0
                self.player.logic.platino = 0
                
                # Filtrar inventario: Solo se conserva la Pocion de Regreso
                from items.potion import PocionRegreso
                regreso_items = [item for item in self.player.inventory if isinstance(item, PocionRegreso)]
                
                # Resetear equipo a básico (incluyendo los slots nuevos)
                arma_basica = Arma("Espada de Madera", 8, "fisico")
                self.player.inventory = [arma_basica] + regreso_items
                self.player.logic.arma = arma_basica
                self.player.logic.armadura = None
                if hasattr(self.player.logic, 'casco'): self.player.logic.casco = None
                if hasattr(self.player.logic, 'pechera'): self.player.logic.pechera = None
                if hasattr(self.player.logic, 'botas'): self.player.logic.botas = None
                if hasattr(self.player.logic, 'accesorio'): self.player.logic.accesorio = None
                
                self.log.add_message(f"[SISTEMA] Perdiste {xp_perdida} XP, tu dinero y tu equipo. Solo conservas Pociones de Regreso.")

            self.player.logic.vida = self.player.logic.max_vida
            
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
                
        else:
            try:
                from items.potion import PocionMana, LibroMagia
                from logic.accesorios import Accesorio
                if isinstance(item, PocionMana):
                    item.usar(self.player.logic, self.log)
                    item.cantidad -= 1
                    if item.cantidad <= 0:
                        self.player.inventory.remove(item)
                    if self.current_enemy:
                        self.state = "COMBAT"
                        self.resolve_enemy_turn()
                    else:
                        self.state = "PLAYING"
                elif isinstance(item, LibroMagia):
                    item.usar(self.player.logic, self.log)
                    item.cantidad -= 1
                    if item.cantidad <= 0:
                        self.player.inventory.remove(item)
                    if self.current_enemy:
                        self.state = "COMBAT"
                        self.resolve_enemy_turn()
                    else:
                        self.state = "PLAYING"
                elif isinstance(item, Accesorio):
                    self.player.logic.accesorio = item
                    self.log.add_message(f"[TÚ] Equipas {item.nombre}.")
                    if self.current_enemy:
                        self.state = "COMBAT"
                        self.resolve_enemy_turn()
                    else:
                        self.state = "PLAYING"
            except ImportError:
                pass

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
        small_font = pygame.font.SysFont('Consolas', 14)
        
        # Fondo oscuro
        self.virtual_surface.fill((10, 10, 20))
        
        # Inicializar partículas si no existen
        if not self.title_particles:
            import random
            for _ in range(60):
                self.title_particles.append({
                    'x': random.randint(0, WIDTH),
                    'y': random.randint(0, HEIGHT),
                    'speed_y': random.uniform(15, 45),
                    'size': random.randint(1, 3),
                    'color': random.choice([(70, 70, 110), (100, 100, 160), (45, 60, 95)])
                })
                
        # Dibujar y actualizar partículas
        for p in self.title_particles:
            p['y'] += p['speed_y'] * self.dt
            if p['y'] > HEIGHT:
                import random
                p['y'] = 0
                p['x'] = random.randint(0, WIDTH)
            pygame.draw.circle(self.virtual_surface, p['color'], (int(p['x']), int(p['y'])), p['size'])

        # Efecto de pulso en sombra de título
        import math
        pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) / 2
        shadow_color = (int(30 + pulse * 25), int(30 + pulse * 25), int(55 + pulse * 35))
        
        # Título con sombra pulsante
        title_text = "SOLID ADVENTURE LEGACY"
        shadow = title_font.render(title_text, True, shadow_color)
        self.virtual_surface.blit(shadow, (WIDTH//2 - 295, HEIGHT//3 - 45))
        self.virtual_surface.blit(title_font.render(title_text, True, CYAN), (WIDTH//2 - 300, HEIGHT//3 - 50))
        
        # Caja del menú
        menu_box = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 30, 360, 275)
        menu_bg = pygame.Surface((menu_box.width, menu_box.height), pygame.SRCALPHA)
        menu_bg.fill((15, 15, 25, 200)) # Oscuro semitransparente
        self.virtual_surface.blit(menu_bg, (menu_box.x, menu_box.y))
        pygame.draw.rect(self.virtual_surface, CYAN, menu_box, 2)
        
        # Opciones
        options = ["NUEVA PARTIDA", "CONTINUAR", "OPCIONES", "AYUDA", "SALIR"]
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
            self.virtual_surface.blit(font.render(prefix + text, True, color), (menu_box.x + 40, menu_box.y + 25 + i * 48))
            
        # Footer
        self.virtual_surface.blit(small_font.render("V1.2.0 - Brayan Medina Moreno", True, (100, 100, 120)), (20, HEIGHT - 40))
        self.virtual_surface.blit(small_font.render("Desarrollado con Pygame", True, (100, 100, 120)), (WIDTH - 200, HEIGHT - 40))

    def get_combat_options(self):
        options = ["Ataque Básico"]
        t_actual = self.player.logic.titulo_actual
        cd_h = self.player.logic.cooldowns.get("habilidad", 0)
        cd_d = self.player.logic.cooldowns.get("distancia", 0)
        
        # Solo mostrar habilidades especiales si NO es el título inicial
        if t_actual != "Hoja en Blanco":
            if "Espada" in t_actual or "Hoja" in t_actual:
                options.append(f"Golpe Habilidad{' (CD: ' + str(cd_h) + ')' if cd_h > 0 else ''}")
            elif "Proyectil" in t_actual or "Arquero" in t_actual or "Halcón" in t_actual:
                options.append(f"Ataque Distancia{' (CD: ' + str(cd_d) + ')' if cd_d > 0 else ''}")
                
        # Magia
        if getattr(self.player.logic, 'magia_desbloqueada', False):
            costo_mp = 15
            if self.player.logic.mana >= costo_mp:
                options.append(f"Ataque Mágico (-{costo_mp} MP)")
            else:
                options.append(f"Ataque Mágico (Sin MP)")
                
        options.extend(["Huir", "Inventario"])
        return options

    def draw_combat_menu(self):
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - 120, HEIGHT // 2 + 80, 240, 180)
        pygame.draw.rect(self.virtual_surface, (20, 20, 20), menu_rect)
        pygame.draw.rect(self.virtual_surface, WHITE, menu_rect, 2)
        
        font = pygame.font.SysFont('Consolas', 20)
        options = self.get_combat_options()
        self.menu_index = max(0, min(self.menu_index, len(options) - 1))
        
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            text_surface = font.render(prefix + option, True, color)
            self.virtual_surface.blit(text_surface, (menu_rect.x + 20, menu_rect.y + 20 + i * 35))

    def draw_enemy_info_box(self):
        if not self.current_enemy:
            return
            
        enemy = self.current_enemy
        w, h = 400, 160
        box_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 140, w, h)
        
        # Fondo y Borde
        pygame.draw.rect(self.virtual_surface, (25, 15, 15), box_rect)
        pygame.draw.rect(self.virtual_surface, RED, box_rect, 2)
        
        # Título
        title_font = pygame.font.SysFont('Consolas', 14, bold=True)
        self.virtual_surface.blit(title_font.render("ENEMIGO EN COMBATE", True, RED), (box_rect.x + 10, box_rect.y + 8))
        
        # Dibujar sprite del enemigo grande (64x64)
        if hasattr(enemy, 'image') and enemy.image:
            enemy_img = pygame.transform.scale(enemy.image, (64, 64))
            self.virtual_surface.blit(enemy_img, (box_rect.x + 20, box_rect.y + 45))
        
        # Fuentes para la información
        font = pygame.font.SysFont('Consolas', 18)
        bold_font = pygame.font.SysFont('Consolas', 18, bold=True)
        small_font = pygame.font.SysFont('Consolas', 14)
        
        # Nombre del enemigo
        nombre_completo = enemy.name
        if hasattr(enemy, 'titulo') and enemy.titulo:
            nombre_completo += f" '{enemy.titulo}'"
        self.virtual_surface.blit(bold_font.render(nombre_completo, True, YELLOW), (box_rect.x + 100, box_rect.y + 35))
        
        # Barra de HP
        bar_x = box_rect.x + 100
        bar_y = box_rect.y + 60
        bar_w = 280
        bar_h = 14
        pygame.draw.rect(self.virtual_surface, DARK_GREY, (bar_x, bar_y, bar_w, bar_h))
        fill = (enemy.vida / enemy.max_vida) * bar_w
        pygame.draw.rect(self.virtual_surface, RED, (bar_x, bar_y, fill, bar_h))
        pygame.draw.rect(self.virtual_surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
        
        # Texto HP
        hp_text = f"HP: {enemy.vida}/{enemy.max_vida}"
        hp_surface = small_font.render(hp_text, True, WHITE)
        self.virtual_surface.blit(hp_surface, (bar_x + bar_w // 2 - hp_surface.get_width() // 2, bar_y - 1))
        
        # Stats
        stats_y = box_rect.y + 85
        self.virtual_surface.blit(small_font.render(f"Fuerza (ATK): {enemy.fuerza}", True, LIGHT_GREY), (box_rect.x + 100, stats_y))
        self.virtual_surface.blit(small_font.render(f"Defensa (DEF): {enemy.defensa}", True, LIGHT_GREY), (box_rect.x + 100, stats_y + 18))
        self.virtual_surface.blit(small_font.render(f"Def. Mág. (MAG): {getattr(enemy, 'defensa_magica', 0)}", True, LIGHT_GREY), (box_rect.x + 100, stats_y + 36))
        
        # Recompensa
        self.virtual_surface.blit(small_font.render(f"Recompensa: +{enemy.xp_recompensa} XP", True, CYAN), (box_rect.x + 250, stats_y))

    def draw_inventory_menu(self):
        w, h = 600, 500
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        
        # Fondo y bordes
        pygame.draw.rect(self.virtual_surface, (15, 15, 25), menu_rect)
        pygame.draw.rect(self.virtual_surface, CYAN, menu_rect, 2)
        
        # Barra de Cabecera con Pestañas
        tab_h = 42
        pygame.draw.rect(self.virtual_surface, (25, 25, 40), (menu_rect.x, menu_rect.y, menu_rect.width, tab_h))
        
        title_font = pygame.font.SysFont('Consolas', 18, bold=True)
        small_hint_font = pygame.font.SysFont('Consolas', 14)
        
        # Pestaña 1: MOCHILA
        tab1_active = self.inventory_tab == "INVENTARIO"
        tab1_rect = pygame.Rect(menu_rect.x + 8, menu_rect.y + 6, 175, 30)
        bg_tab1 = (45, 45, 75) if tab1_active else (20, 20, 30)
        border_tab1 = YELLOW if tab1_active else (60, 60, 80)
        color_tab1 = YELLOW if tab1_active else LIGHT_GREY
        pygame.draw.rect(self.virtual_surface, bg_tab1, tab1_rect)
        pygame.draw.rect(self.virtual_surface, border_tab1, tab1_rect, 2)
        t1_surf = title_font.render("[ 1. MOCHILA ]", True, color_tab1)
        self.virtual_surface.blit(t1_surf, (tab1_rect.x + (tab1_rect.width - t1_surf.get_width()) // 2, tab1_rect.y + 5))

        # Pestaña 2: TÍTULOS
        tab2_active = self.inventory_tab == "TITULOS"
        tab2_rect = pygame.Rect(menu_rect.x + 190, menu_rect.y + 6, 175, 30)
        bg_tab2 = (45, 45, 75) if tab2_active else (20, 20, 30)
        border_tab2 = YELLOW if tab2_active else (60, 60, 80)
        color_tab2 = YELLOW if tab2_active else LIGHT_GREY
        pygame.draw.rect(self.virtual_surface, bg_tab2, tab2_rect)
        pygame.draw.rect(self.virtual_surface, border_tab2, tab2_rect, 2)
        t2_surf = title_font.render("[ 2. TÍTULOS ]", True, color_tab2)
        self.virtual_surface.blit(t2_surf, (tab2_rect.x + (tab2_rect.width - t2_surf.get_width()) // 2, tab2_rect.y + 5))

        # Indicador de cambio de pestaña a la derecha
        hint_surf = small_hint_font.render("[TAB/Q/E] Cambiar", True, (170, 170, 200))
        self.virtual_surface.blit(hint_surf, (menu_rect.right - hint_surf.get_width() - 15, menu_rect.y + 13))

        font = pygame.font.SysFont('Consolas', 18)
        small_font = pygame.font.SysFont('Consolas', 14)

        if self.inventory_tab == "INVENTARIO":
            inv = self.player.inventory
            self.menu_index = max(0, min(self.menu_index, len(inv)))
            
            # Panel Izquierdo: Lista de Objetos
            list_rect = pygame.Rect(menu_rect.x + 10, menu_rect.y + 50, 350, h - 70)
            pygame.draw.rect(self.virtual_surface, (10, 10, 15), list_rect)
            pygame.draw.rect(self.virtual_surface, (50, 50, 70), list_rect, 1)
            
            # Panel Derecho: Estado de Equipo
            eq_rect = pygame.Rect(menu_rect.x + 370, menu_rect.y + 50, 220, h - 70)
            pygame.draw.rect(self.virtual_surface, (20, 20, 35), eq_rect)
            pygame.draw.rect(self.virtual_surface, CYAN, eq_rect, 1)
            
            # Dibujar Equipo Actual en el panel derecho
            self.virtual_surface.blit(font.render("EQUIPADO:", True, CYAN), (eq_rect.x + 10, eq_rect.y + 10))
            y_eq = eq_rect.y + 40
            slots = [
                ("ARMA", self.player.logic.arma),
                ("CABEZA", self.player.logic.casco),
                ("PECHO", self.player.logic.pechera),
                ("PIES", self.player.logic.botas),
                ("ACCES.", getattr(self.player.logic, 'accesorio', None))
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
            
            if self.menu_index < self.inv_scroll:
                self.inv_scroll = self.menu_index
            elif self.menu_index >= self.inv_scroll + max_visible:
                self.inv_scroll = self.menu_index - max_visible + 1

            for i in range(self.inv_scroll, min(len(inv), self.inv_scroll + max_visible)):
                item = inv[i]
                logic = self.player.logic
                is_equipped = False
                if isinstance(item, Arma):
                    if item == logic.arma: is_equipped = True
                elif isinstance(item, Armadura):
                    if item in [logic.casco, logic.pechera, logic.botas]: is_equipped = True
                elif item.__class__.__name__ == "Accesorio":
                    if item == getattr(logic, 'accesorio', None): is_equipped = True

                color = CYAN if i == self.menu_index else (GREEN if is_equipped else WHITE)
                prefix = "> " if i == self.menu_index else "  "
                eq_tag = " [E]" if is_equipped else ""
                cant_tag = f" x{item.cantidad}" if hasattr(item, 'cantidad') and item.cantidad > 1 else ""
                
                draw_y = menu_rect.y + 50 + (i - self.inv_scroll) * 30
                text_surface = font.render(f"{prefix}{item.nombre}{cant_tag}{eq_tag}", True, color)
                self.virtual_surface.blit(text_surface, (menu_rect.x + 20, draw_y))

            exit_idx = len(inv)
            if exit_idx >= self.inv_scroll and exit_idx < self.inv_scroll + max_visible:
                color = CYAN if exit_idx == self.menu_index else WHITE
                prefix = "> " if exit_idx == self.menu_index else "  "
                draw_y = menu_rect.y + 50 + (exit_idx - self.inv_scroll) * 30
                self.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 20, draw_y))

            if self.menu_index < len(inv):
                item = inv[self.menu_index]
                self.draw_description_box(getattr(item, 'descripcion', "Sin descripción."))
            else:
                self.draw_description_box("Cerrar el inventario y volver al juego.")

        else: # TITULOS
            from logic.personaje import TITULOS_DATA
            titulos = self.player.logic.titulos_desbloqueados
            self.menu_index = max(0, min(self.menu_index, len(titulos)))

            # Panel Izquierdo: Lista de Títulos
            list_rect = pygame.Rect(menu_rect.x + 10, menu_rect.y + 50, 350, h - 70)
            pygame.draw.rect(self.virtual_surface, (10, 10, 15), list_rect)
            pygame.draw.rect(self.virtual_surface, (50, 50, 70), list_rect, 1)

            # Panel Derecho: Estado de Título Activo y Resumen
            info_rect = pygame.Rect(menu_rect.x + 370, menu_rect.y + 50, 220, h - 70)
            pygame.draw.rect(self.virtual_surface, (20, 20, 35), info_rect)
            pygame.draw.rect(self.virtual_surface, CYAN, info_rect, 1)

            self.virtual_surface.blit(font.render("CONTRATO ACTIVO:", True, CYAN), (info_rect.x + 10, info_rect.y + 15))
            act_nombre = self.player.logic.titulo_actual or "Ninguno"
            self.virtual_surface.blit(title_font.render(act_nombre, True, GREEN), (info_rect.x + 10, info_rect.y + 40))

            self.virtual_surface.blit(small_font.render(f"Desbloqueados: {len(titulos)}/{len(TITULOS_DATA)}", True, YELLOW), (info_rect.x + 10, info_rect.y + 80))
            
            p_count = sum(1 for t in titulos if TITULOS_DATA.get(t, {}).get("tipo") == "pasivo")
            self.virtual_surface.blit(small_font.render(f"Pasivos activos: {p_count}", True, CYAN), (info_rect.x + 10, info_rect.y + 105))

            inst_lines = [
                "Los pasivos (+) siempre",
                "están activos.",
                "",
                "Presiona [ENTER] para",
                "equipar un título",
                "activo (*)."
            ]
            for idx_l, line in enumerate(inst_lines):
                self.virtual_surface.blit(small_font.render(line, True, LIGHT_GREY), (info_rect.x + 10, info_rect.y + 145 + idx_l * 20))

            # Scroll de Títulos
            max_visible = (list_rect.height - 40) // 30
            if not hasattr(self, 'title_scroll'): self.title_scroll = 0
            if self.menu_index < self.title_scroll:
                self.title_scroll = self.menu_index
            elif self.menu_index >= self.title_scroll + max_visible:
                self.title_scroll = self.menu_index - max_visible + 1

            for i in range(self.title_scroll, min(len(titulos), self.title_scroll + max_visible)):
                t_name = titulos[i]
                t_data = TITULOS_DATA.get(t_name, {})
                is_passive = t_data.get("tipo") == "pasivo"
                is_active = t_name == self.player.logic.titulo_actual

                color = YELLOW if i == self.menu_index else (GREEN if is_active else (CYAN if is_passive else WHITE))
                prefix = "> " if i == self.menu_index else ("* " if is_active else ("+ " if is_passive else "  "))
                suffix = " [PASIVO]" if is_passive else (" [ACTIVO]" if is_active else "")

                draw_y = menu_rect.y + 50 + (i - self.title_scroll) * 30
                self.virtual_surface.blit(font.render(f"{prefix}{t_name}{suffix}", True, color), (menu_rect.x + 20, draw_y))

            exit_idx = len(titulos)
            if exit_idx >= self.title_scroll and exit_idx < self.title_scroll + max_visible:
                color = CYAN if exit_idx == self.menu_index else WHITE
                prefix = "> " if exit_idx == self.menu_index else "  "
                draw_y = menu_rect.y + 50 + (exit_idx - self.title_scroll) * 30
                self.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 20, draw_y))

            if self.menu_index < len(titulos):
                t_name = titulos[self.menu_index]
                desc = TITULOS_DATA.get(t_name, {}).get("descripcion", "Sin descripción.")
                self.draw_description_box(desc)
            else:
                self.draw_description_box("Cerrar el menú de títulos y volver al juego.")

    def draw_shop_menu(self):
        w = 470
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 120, w, 240)
        pygame.draw.rect(self.virtual_surface, (30, 20, 20), menu_rect)
        pygame.draw.rect(self.virtual_surface, YELLOW, menu_rect, 2)
        font = pygame.font.SysFont('Consolas', 18)
        self.virtual_surface.blit(font.render("TIENDA DEL MERCADER", True, YELLOW), (menu_rect.x + 20, menu_rect.y + 10))
        options = ["Pocion Media (100 Cobre)", "Arma Aleatoria (500 Cobre)", "Pocion Regreso (10 Cobre)", "Grimorio Mágico (1 Oro)", "Vender Objeto", "Salir"]
        descriptions = [
            "Restaura el 50% de tu salud máxima.",
            "Un arma poderosa acorde a tu nivel actual.",
            "Te permite volver al pueblo pero pierdes XP.",
            "Desbloquea la habilidad de usar magia (Ataque Mágico).",
            "Vende tus objetos por la mitad de su valor.",
            "Cierra la tienda del mercader."
        ]
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 40 + i * 32))
        
        self.draw_description_box(descriptions[self.menu_index])

    def draw_cross_menu(self):
        w = 400
        menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 110, w, 220)
        pygame.draw.rect(self.virtual_surface, (20, 20, 30), menu_rect)
        pygame.draw.rect(self.virtual_surface, YELLOW, menu_rect, 2)
        font = pygame.font.SysFont('Consolas', 18)
        self.virtual_surface.blit(font.render("CRUZ SAGRADA", True, YELLOW), (menu_rect.x + 20, menu_rect.y + 10))
        
        tiempo_actual = self.player.logic.tiempo_juego
        ultimo_tiempo = self.player.logic.cruz_ultimo_tiempo
        segundos_por_dia = 15 * 60
        
        dia_actual = int(tiempo_actual // segundos_por_dia)
        dia_ultimo = int(ultimo_tiempo // segundos_por_dia)
        
        if dia_actual > dia_ultimo:
            self.player.logic.cruz_usos_hoy = 3
            
        usos = self.player.logic.cruz_usos_hoy
        options = [
            "Guardar Partida",
            f"Rezar ({usos} usos hoy)",
            "Cuestionar las Creencias",
            "Salir"
        ]
        descriptions = [
            "Guarda tu progreso actual en el pueblo.",
            "Recupera toda tu vida y maná.",
            "Cuestiona tu fe. Consume los 3 usos del día (penalizado para curarte hoy).",
            "Te alejas de la Cruz Sagrada."
        ]
        
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 50 + i * 30))
            
        self.draw_description_box(descriptions[self.menu_index])

    def draw_sell_menu(self):
        self.draw_inventory_menu()
        title_font = pygame.font.SysFont('Consolas', 22, bold=True)
        self.virtual_surface.blit(title_font.render("VENDER (Enter para 1/2 valor)", True, RED), (MAP_WIDTH // 2 - 130, 60))

    def draw_quantity_selector(self):
        # Dibujar fondo según el modo
        if self.qty_mode == "BUY":
            self.draw_shop_menu()
        else:
            self.draw_sell_menu()

        # Oscurecimiento de fondo
        overlay = pygame.Surface((MAP_WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.virtual_surface.blit(overlay, (0, 0))

        # Cuadro modal
        w, h = 480, 250
        rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((25, 20, 30, 245))
        self.virtual_surface.blit(bg, (rect.x, rect.y))
        
        border_color = (255, 200, 50) if self.qty_mode == "BUY" else (255, 100, 100)
        pygame.draw.rect(self.virtual_surface, border_color, rect, 3)
        pygame.draw.rect(self.virtual_surface, (100, 80, 40), pygame.Rect(rect.x + 4, rect.y + 4, w - 8, h - 8), 1)

        title_font = pygame.font.SysFont('Consolas', 20, bold=True)
        name_font = pygame.font.SysFont('Consolas', 22, bold=True)
        qty_font = pygame.font.SysFont('Consolas', 32, bold=True)
        info_font = pygame.font.SysFont('Consolas', 17)
        prompt_font = pygame.font.SysFont('Consolas', 15)

        # Título
        title_text = "★ COMPRA DE CONSUMIBLES ★" if self.qty_mode == "BUY" else "★ VENTA DE CONSUMIBLES ★"
        t_surf = title_font.render(title_text, True, YELLOW if self.qty_mode == "BUY" else (255, 120, 120))
        self.virtual_surface.blit(t_surf, (rect.x + (w - t_surf.get_width()) // 2, rect.y + 18))

        # Nombre del ítem
        n_surf = name_font.render(self.qty_item_name, True, WHITE)
        self.virtual_surface.blit(n_surf, (rect.x + (w - n_surf.get_width()) // 2, rect.y + 48))

        # Selector de Cantidad
        qty_text = f"◄   [  {self.qty_current}  ]   ►"
        q_surf = qty_font.render(qty_text, True, CYAN)
        self.virtual_surface.blit(q_surf, (rect.x + (w - q_surf.get_width()) // 2, rect.y + 85))

        # Información de costo o ganancia
        total_val = self.qty_current * self.qty_unit_price
        if self.qty_mode == "BUY":
            info_text = f"Precio: {self.qty_unit_price} Cob c/u  |  Total: {total_val} Cob"
            sub_info = f"(Máx posible: {self.qty_max} unidades)"
        else:
            info_text = f"Valor: {self.qty_unit_price} Cob c/u  |  Ganancia: +{total_val} Cob"
            sub_info = f"(Tienes: {self.qty_max}  |  Te quedarán: {self.qty_max - self.qty_current})"

        i_surf = info_font.render(info_text, True, YELLOW)
        self.virtual_surface.blit(i_surf, (rect.x + (w - i_surf.get_width()) // 2, rect.y + 132))

        s_surf = info_font.render(sub_info, True, LIGHT_GREY)
        self.virtual_surface.blit(s_surf, (rect.x + (w - s_surf.get_width()) // 2, rect.y + 156))

        # Instrucciones de teclas
        instr_text = "[←/→] -1/+1   [↑/↓] -10/+10   [M] Máx   [ENTER] OK   [ESC] Salir"
        instr_surf = prompt_font.render(instr_text, True, (160, 160, 180))
        self.virtual_surface.blit(instr_surf, (rect.x + (w - instr_surf.get_width()) // 2, rect.y + 204))

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

    def draw_chest_reward(self):
        if not self.chest_reward_item:
            return
            
        item = self.chest_reward_item
        w, h = 480, 260
        rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        
        # Fondo oscuro translúcido cubriendo el área del mapa
        overlay = pygame.Surface((MAP_WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.virtual_surface.blit(overlay, (0, 0))
        
        # Panel principal
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((20, 18, 28, 245))
        self.virtual_surface.blit(bg, (rect.x, rect.y))
        
        # Bordes dorados de calidad
        pygame.draw.rect(self.virtual_surface, (235, 195, 55), rect, 3)
        inner_rect = pygame.Rect(rect.x + 4, rect.y + 4, w - 8, h - 8)
        pygame.draw.rect(self.virtual_surface, (120, 95, 30), inner_rect, 1)
        
        title_font = pygame.font.SysFont('Consolas', 22, bold=True)
        name_font = pygame.font.SysFont('Consolas', 24, bold=True)
        sub_font = pygame.font.SysFont('Consolas', 15)
        detail_font = pygame.font.SysFont('Consolas', 17)
        prompt_font = pygame.font.SysFont('Consolas', 15, bold=True)
        
        # Título
        title_text = "★ ¡COFRE ABIERTO! ★"
        t_surf = title_font.render(title_text, True, YELLOW)
        self.virtual_surface.blit(t_surf, (rect.x + (w - t_surf.get_width()) // 2, rect.y + 18))
        
        # Línea separadora dorada
        pygame.draw.line(self.virtual_surface, (180, 150, 40), (rect.x + 30, rect.y + 52), (rect.right - 30, rect.y + 52), 2)
        
        # Clasificar objeto para dar color y detalles visuales
        color_item = WHITE
        tipo_str = "Objeto de Aventura"
        detalles = []
        
        from logic.armas import Arma
        from logic.armaduras import Armadura
        from logic.accesorios import Accesorio
        from items.potion import Pocion, PocionMana, PocionRegreso
        
        if isinstance(item, Arma):
            color_item = (255, 140, 50)
            tipo_str = f"ARMA [{getattr(item, 'tipo_daño', 'FÍSICO').upper()}]"
            detalles.append(f"⚔ Daño de Ataque: +{getattr(item, 'daño', 0)}")
            if hasattr(item, 'clase_permitida') and item.clase_permitida:
                detalles.append(f"Clase recomendada: {item.clase_permitida.capitalize()}")
        elif isinstance(item, Armadura):
            color_item = (100, 200, 255)
            tipo_str = "PIEZA DE ARMADURA"
            detalles.append(f"🛡 Protección / Defensa: +{getattr(item, 'defensa', 0)}")
        elif isinstance(item, Accesorio):
            color_item = (225, 150, 255)
            tipo_str = "ACCESORIO MÍSTICO"
            bonos = getattr(item, 'bono_stats', {})
            bono_strs = [f"+{val} {stat.replace('_', ' ').capitalize()}" for stat, val in bonos.items()]
            detalles.append(f"✨ Atributos: {', '.join(bono_strs)}")
        elif isinstance(item, PocionMana):
            color_item = (80, 180, 255)
            tipo_str = "POCIÓN DE MANÁ"
            detalles.append(getattr(item, 'descripcion', "Restaura puntos de Maná."))
        elif isinstance(item, Pocion):
            color_item = (100, 240, 130)
            tipo_str = "POCIÓN DE CURACIÓN"
            detalles.append(getattr(item, 'descripcion', "Restaura puntos de Salud."))
        elif isinstance(item, PocionRegreso):
            color_item = (255, 230, 100)
            tipo_str = "POCIÓN DE REGRESO"
            detalles.append("Teletransporta de inmediato al Pueblo.")
        else:
            color_item = (240, 240, 240)
            detalles.append(getattr(item, 'descripcion', "Añadido a tu mochila."))
            
        # Icono del ítem si está disponible
        item_icon = None
        icon_path = getattr(item, 'sprite_path', None)
        if not icon_path and (isinstance(item, Pocion) or isinstance(item, PocionMana)):
            icon_path = 'assets/sprites/potis.png'
        if icon_path and os.path.exists(icon_path):
            try:
                raw_img = pygame.image.load(icon_path).convert_alpha()
                item_icon = pygame.transform.scale(raw_img, (32, 32))
            except Exception:
                item_icon = None

        # Nombre del ítem (con icono a la izquierda si existe)
        nombre_surf = name_font.render(item.nombre, True, color_item)
        if item_icon:
            total_w = item_icon.get_width() + 10 + nombre_surf.get_width()
            start_name_x = rect.x + (w - total_w) // 2
            self.virtual_surface.blit(item_icon, (start_name_x, rect.y + 68))
            self.virtual_surface.blit(nombre_surf, (start_name_x + item_icon.get_width() + 10, rect.y + 72))
        else:
            self.virtual_surface.blit(nombre_surf, (rect.x + (w - nombre_surf.get_width()) // 2, rect.y + 72))
        
        # Subtítulo (Tipo)
        tipo_surf = sub_font.render(tipo_str, True, (170, 170, 190))
        self.virtual_surface.blit(tipo_surf, (rect.x + (w - tipo_surf.get_width()) // 2, rect.y + 106))
        
        # Estadísticas / Descripción
        for idx, det in enumerate(detalles[:2]):
            d_surf = detail_font.render(det, True, (230, 230, 240))
            self.virtual_surface.blit(d_surf, (rect.x + (w - d_surf.get_width()) // 2, rect.y + 138 + idx * 24))
            
        # Línea separadora inferior
        pygame.draw.line(self.virtual_surface, (70, 60, 40), (rect.x + 40, rect.y + 200), (rect.right - 40, rect.y + 200), 1)
        
        # Prompt de confirmación
        p_surf = prompt_font.render("Presiona [ESPACIO] o [ENTER] para recoger", True, CYAN)
        self.virtual_surface.blit(p_surf, (rect.x + (w - p_surf.get_width()) // 2, rect.y + 218))

    def draw_options_screen(self):
        w, h = 520, 320
        rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (15, 15, 25), rect)
        pygame.draw.rect(self.virtual_surface, CYAN, rect, 2)
        
        title_font = pygame.font.SysFont('Consolas', 26, bold=True)
        font = pygame.font.SysFont('Consolas', 20)
        small_font = pygame.font.SysFont('Consolas', 14)
        
        # Título
        self.virtual_surface.blit(title_font.render("AJUSTES Y OPCIONES", True, YELLOW), (rect.x + 120, rect.y + 30))
        pygame.draw.line(self.virtual_surface, (50, 70, 90), (rect.x + 30, rect.y + 70), (rect.right - 30, rect.y + 70), 2)
        
        col_vol = YELLOW if self.options_menu_index == 0 else WHITE
        col_mute = YELLOW if self.options_menu_index == 1 else WHITE
        col_back = YELLOW if self.options_menu_index == 2 else WHITE
        
        pref_vol = "> " if self.options_menu_index == 0 else "  "
        pref_mute = "> " if self.options_menu_index == 1 else "  "
        pref_back = "> " if self.options_menu_index == 2 else "  "
        
        # Fila 1: Volumen de Música
        vol_pct = int(self.music_volume * 100)
        bar_w = 160
        bar_h = 16
        bar_x = rect.x + 270
        bar_y = rect.y + 112
        
        self.virtual_surface.blit(font.render(f"{pref_vol}Volumen Música:", True, col_vol), (rect.x + 40, rect.y + 110))
        pygame.draw.rect(self.virtual_surface, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * self.music_volume)
        if fill_w > 0:
            pygame.draw.rect(self.virtual_surface, CYAN if self.options_menu_index == 0 else (70, 160, 180), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.virtual_surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
        self.virtual_surface.blit(small_font.render(f"{vol_pct}%", True, WHITE), (bar_x + bar_w + 12, bar_y))
        
        # Fila 2: Silenciar
        is_muted = self.music_volume == 0.0
        mute_str = "SÍ (Mudo)" if is_muted else "NO"
        self.virtual_surface.blit(font.render(f"{pref_mute}Silenciar: [{mute_str}]", True, col_mute), (rect.x + 40, rect.y + 165))
        
        # Fila 3: Volver
        self.virtual_surface.blit(font.render(f"{pref_back}VOLVER", True, col_back), (rect.x + 40, rect.y + 220))
        
        # Ayuda al pie
        self.virtual_surface.blit(small_font.render("Usa [FLECHAS] o [A/D] para ajustar volumen | [ENTER] seleccionar | [ESC] volver", True, (130, 130, 150)), (rect.x + 20, rect.y + 280))

    def draw_volume_hud(self):
        w, h = 230, 46
        x = WIDTH - w - 20
        y = 20
        hud_rect = pygame.Rect(x, y, w, h)
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((15, 15, 25, 220))
        self.virtual_surface.blit(bg, (x, y))
        pygame.draw.rect(self.virtual_surface, CYAN, hud_rect, 1)
        
        font = pygame.font.SysFont('Consolas', 15, bold=True)
        vol_pct = int(self.music_volume * 100)
        self.virtual_surface.blit(font.render(f"MÚSICA: {vol_pct}%", True, YELLOW), (x + 10, y + 6))
        
        bar_w = 210
        bar_h = 8
        bar_x = x + 10
        bar_y = y + 28
        pygame.draw.rect(self.virtual_surface, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * self.music_volume)
        if fill_w > 0:
            pygame.draw.rect(self.virtual_surface, CYAN, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.virtual_surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)

    def draw_confirm_exit(self):
        w, h = 500, 290
        rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (20, 18, 25), rect)
        pygame.draw.rect(self.virtual_surface, (70, 80, 110), rect, 2)
        
        title_font = pygame.font.SysFont('Consolas', 24, bold=True)
        font = pygame.font.SysFont('Consolas', 19)
        
        t_surf = title_font.render("PAUSA / MENÚ", True, YELLOW)
        self.virtual_surface.blit(t_surf, (rect.x + (w - t_surf.get_width()) // 2, rect.y + 20))
        
        vol_str = f"{int(self.music_volume * 100)}%"
        options = [
            "SEGUIR JUGANDO",
            f"VOLUMEN MÚSICA: < {vol_str} >",
            "PANTALLA PRINCIPAL (MENÚ)",
            "SALIR AL ESCRITORIO"
        ]
        
        opt_y = rect.y + 65
        for i, opt in enumerate(options):
            is_sel = self.menu_index == i
            col = YELLOW if is_sel else WHITE
            pref = "> " if is_sel else "  "
            self.virtual_surface.blit(font.render(f"{pref}{opt}", True, col), (rect.x + 50, opt_y))
            opt_y += 36
        
        # Mensaje de guardado
        msg_font = pygame.font.SysFont('Consolas', 14)
        if self.profundidad == 0:
            msg = "En el Pueblo: se guardará tu progreso."
            color = GREEN
        else:
            msg = "¡Atención! En mazmorra perderás el avance del piso."
            color = (255, 130, 130)
        self.virtual_surface.blit(msg_font.render(msg, True, color), (rect.x + 35, rect.y + 245))

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

    def draw_difficulty_selection_screen(self):
        self.virtual_surface.fill((10, 10, 20))
        title_font = pygame.font.SysFont('Consolas', 40, bold=True)
        font = pygame.font.SysFont('Consolas', 30)
        
        self.virtual_surface.blit(title_font.render("SELECCIONA LA DIFICULTAD", True, YELLOW), (WIDTH//2 - 250, HEIGHT//2 - 150))
        
        options = ["La vida es fácil", "La vida es normal"]
        descriptions = [
            "Dificultad pensada para facilitar la partida.",
            "Dificultad pensada como la dificultad normal del juego."
        ]
        
        for i, option in enumerate(options):
            color = CYAN if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            self.virtual_surface.blit(font.render(prefix + option, True, color), (WIDTH//2 - 200, HEIGHT//2 - 50 + i * 50))
            
        desc_font = pygame.font.SysFont('Consolas', 18)
        desc_surf = desc_font.render(descriptions[self.menu_index], True, LIGHT_GREY)
        self.virtual_surface.blit(desc_surf, (WIDTH // 2 - desc_surf.get_width() // 2, HEIGHT // 2 + 100))

    def draw_load_selection(self):
        self.virtual_surface.fill((10, 10, 20))
        title_font = pygame.font.SysFont('Consolas', 40, bold=True)
        font = pygame.font.SysFont('Consolas', 24)
        small_font = pygame.font.SysFont('Consolas', 18)
        
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

        # Indicaciones de teclas
        self.virtual_surface.blit(small_font.render("[ENTER] Cargar   [D / SUPR] Borrar Guardado", True, YELLOW), (WIDTH//2 - 200, HEIGHT//2 + 180))
        self.virtual_surface.blit(font.render("ESC para Volver", True, LIGHT_GREY), (WIDTH//2 - 100, HEIGHT//2 + 220))

    def draw_save_selection(self):
        w, h = 540, 420
        rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(self.virtual_surface, (10, 10, 20), rect)
        pygame.draw.rect(self.virtual_surface, YELLOW, rect, 2)
        
        title_font = pygame.font.SysFont('Consolas', 24, bold=True)
        font = pygame.font.SysFont('Consolas', 20)
        small_font = pygame.font.SysFont('Consolas', 14)
        
        self.virtual_surface.blit(title_font.render("¿DÓNDE QUIERES GUARDAR?", True, CYAN), (rect.x + 110, rect.y + 20))
        
        # Generar lista de opciones filtrando según el límite
        options = []
        if len(self.save_files) < 5:
            options.append("NUEVO GUARDADO")
        for f in self.save_files:
            options.append(f"Sobrescribir: {f}")
        if getattr(self, 'save_return_state', 'QUIT') == 'QUIT':
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
            if len(text) > 42: text = text[:39] + "..."
            self.virtual_surface.blit(font.render(prefix + text, True, color), (rect.x + 30, rect.y + 60 + (i - self.save_scroll) * 35))

        # Indicaciones de teclas para borrar
        info_text = "[ENTER] Seleccionar  [D] Borrar partida  [ESC] Cancelar"
        self.virtual_surface.blit(small_font.render(info_text, True, YELLOW), (rect.x + 30, rect.y + h - 35))

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
        self.virtual_surface.fill((12, 12, 22))
        
        # Marco exterior
        pygame.draw.rect(self.virtual_surface, (50, 60, 90), pygame.Rect(20, 20, WIDTH - 40, HEIGHT - 40), 2)
        
        header_font = pygame.font.SysFont('Consolas', 26, bold=True)
        tab_font = pygame.font.SysFont('Consolas', 16, bold=True)
        sec_title_font = pygame.font.SysFont('Consolas', 19, bold=True)
        text_font = pygame.font.SysFont('Consolas', 16)
        code_font = pygame.font.SysFont('Consolas', 15)
        small_hint_font = pygame.font.SysFont('Consolas', 14)
        
        # Título superior
        title_surf = header_font.render("★ MANUAL DE AVENTURAS Y GUÍA DE COMBATE ★", True, YELLOW)
        self.virtual_surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 35))
        
        # Pestañas de secciones
        tab_names = [
            "1. CONTROLES",
            "2. TIPOS DE DAÑO",
            "3. SISTEMA DE TÍTULOS",
            "4. BESTIARIO"
        ]
        
        tab_total_w = len(tab_names) * 230 + (len(tab_names) - 1) * 10
        start_tab_x = WIDTH // 2 - tab_total_w // 2
        tab_y = 80
        
        for idx, name in enumerate(tab_names):
            t_rect = pygame.Rect(start_tab_x + idx * 240, tab_y, 230, 32)
            is_active = self.help_page == idx
            bg_col = (45, 45, 80) if is_active else (20, 20, 30)
            brd_col = YELLOW if is_active else (60, 60, 80)
            txt_col = YELLOW if is_active else LIGHT_GREY
            
            pygame.draw.rect(self.virtual_surface, bg_col, t_rect)
            pygame.draw.rect(self.virtual_surface, brd_col, t_rect, 2)
            
            t_surf = tab_font.render(name, True, txt_col)
            self.virtual_surface.blit(t_surf, (t_rect.x + (t_rect.width - t_surf.get_width()) // 2, t_rect.y + 7))

        # Contenedor central
        content_rect = pygame.Rect(40, 125, WIDTH - 80, HEIGHT - 200)
        pygame.draw.rect(self.virtual_surface, (18, 18, 28), content_rect)
        pygame.draw.rect(self.virtual_surface, (40, 45, 65), content_rect, 1)

        # Contenido dinámico según help_page
        if self.help_page == 0:
            # PÁGINA 1: CONTROLES
            columns = [
                ("EXPLORACIÓN Y MOVIMIENTO", [
                    ("[Flechas / WASD]", "Moverse por el mundo."),
                    ("[Tecla I / TAB]", "Abrir menú de Mochila y Títulos."),
                    ("[Tecla ESC]", "Menú de pausa o cancelar."),
                    ("[F11]", "Alternar pantalla completa."),
                    ("[+] / [-]", "Ajustar volumen de música.")
                ]),
                ("MENÚ DE PERSONAJE", [
                    ("[TAB / Q / E]", "Alternar Mochila y Títulos."),
                    ("[Tecla 1 / 2]", "Ir directo a Mochila o Títulos."),
                    ("[Arriba / Abajo]", "Navegar objetos o contratos."),
                    ("[ENTER]", "Usar o equipar ítem / título.")
                ]),
                ("TIENDA Y BANCO", [
                    ("[← / →] o [A / D]", "Ajustar cantidad (-1 / +1)."),
                    ("[↑ / ↓] o [W / S]", "Ajuste rápido (-10 / +10)."),
                    ("[Tecla M]", "Seleccionar cantidad máxima."),
                    ("[ENTER]", "Confirmar compra o venta.")
                ]),
                ("REGLAS DEL MUNDO", [
                    ("Guardado:", "Solo en la Cruz del PUEBLO."),
                    ("Muerte:", "Pierdes 20% de XP y algo de cobre."),
                    ("Escaleras:", "Derrota a todos los enemigos.")
                ])
            ]
            
            cx = content_rect.x + 35
            cy = content_rect.y + 20
            col_w = 420
            
            for col_idx, (sec_title, items) in enumerate(columns):
                col_x = cx if col_idx % 2 == 0 else cx + 455
                col_y = cy if col_idx < 2 else cy + 245
                
                self.virtual_surface.blit(sec_title_font.render(sec_title, True, CYAN), (col_x, col_y))
                pygame.draw.line(self.virtual_surface, (60, 80, 110), (col_x, col_y + 24), (col_x + col_w - 20, col_y + 24), 1)
                
                row_y = col_y + 34
                for key_tag, desc_text in items:
                    self.virtual_surface.blit(code_font.render(key_tag, True, YELLOW), (col_x + 5, row_y))
                    self.virtual_surface.blit(text_font.render(desc_text, True, WHITE), (col_x + 5, row_y + 18))
                    row_y += 38

        elif self.help_page == 1:
            # PÁGINA 2: TIPOS DE DAÑO
            sections = [
                ("1. DAÑO FÍSICO (MELEE)", YELLOW, [
                    "• Fórmula: Daño = (Fuerza del Personaje + Daño del Arma) - Defensa Física del Enemigo",
                    "• Mecánica: Es el daño elemental cuerpo a cuerpo (espadas, hachas de combate).",
                    "• Cómo Aumentarlo:",
                    "   - Equipa armas de mayor nivel o categoría (hachas para daño pesado, espadas ágiles).",
                    "   - Sube de nivel para incrementar la Fuerza base de tu héroe.",
                    "   - Equipa títulos orientados al combate marcial y accesorios que aumenten Fuerza o Daño Melee.",
                    "• Nota táctica: Los enemigos acorazados (como los Orcos) absorben gran parte de este daño."
                ]),
                ("2. DAÑO A DISTANCIA (PROYECTILES)", (100, 255, 150), [
                    "• Fórmula: Daño = (Ataque a Distancia + Daño Proyectil) - Defensa del Enemigo",
                    "• Mecánica: Ataques seguros con arcos, ballestas o hondas. Tiene tiempo de recarga (cooldown).",
                    "• Cómo Aumentarlo: Equipa títulos de puntería y armas o accesorios de proyectil."
                ]),
                ("3. DAÑO MÁGICO (LO ARCANO)", CYAN, [
                    "• Fórmula: Daño Mágico = Magia del Personaje - Defensa Mágica del Enemigo",
                    "• ¡GRAN VENTAJA!: Ignora por completo la armadura física de los enemigos (daño puro).",
                    "• Requisito: Requiere leer el 'Grimorio de Aprendiz' y consume 15 de Maná por conjuro.",
                    "• Cómo Aumentarlo:",
                    "   - Cada nivel que subas te otorga de forma pasiva +1 Magia Base y +10 de Maná Máximo.",
                    "   - Equipa títulos arcanos en la pestaña de títulos para obtener bonificaciones masivas a Magia.",
                    "   - Encuentra y equipa anillos o amuletos con bonificaciones de Magia en los cofres del calabozo."
                ])
            ]
            
            y_sec = content_rect.y + 20
            for sec_title, title_col, lines in sections:
                self.virtual_surface.blit(sec_title_font.render(sec_title, True, title_col), (content_rect.x + 30, y_sec))
                pygame.draw.line(self.virtual_surface, (50, 60, 85), (content_rect.x + 30, y_sec + 22), (content_rect.right - 30, y_sec + 22), 1)
                y_sec += 30
                for line in lines:
                    col = WHITE if not line.startswith("• ¡GRAN VENTAJA!:") else (120, 255, 180)
                    self.virtual_surface.blit(text_font.render(line, True, col), (content_rect.x + 40, y_sec))
                    y_sec += 21
                y_sec += 14

        elif self.help_page == 2:
            # PÁGINA 3: SISTEMA DE TÍTULOS
            paragraphs = [
                ("¿QUÉ ES EL SISTEMA DE TÍTULOS?", YELLOW, [
                    "Solid Adventure prescinde de las clases fijas tradicionales. En su lugar, tu identidad se",
                    "construye dinámicamente a través de Contratos de Títulos.",
                    "Tus acciones, tus hábitos de combate y las decisiones que tomes moldearán quién eres en el mundo."
                ]),
                ("TÍTULOS ACTIVOS (Marcados con *)", (100, 255, 100), [
                    "• Son especializaciones directas de combate (vías de espada, proyectiles, magia, etc.).",
                    "• Solo puedes tener UN título activo equipado a la vez en tu pestaña [ 2. TÍTULOS ].",
                    "• Al equiparlo, te confiere aumentos significativos a estadísticas (Fuerza, Magia, Defensa, Vida).",
                    "• ¡Cámbialo libremente según el enemigo o situación que enfrentes!"
                ]),
                ("TÍTULOS PASIVOS (Marcados con +)", CYAN, [
                    "• Representan instintos, reflejos y experiencia de supervivencia aprendida.",
                    "• ¡NO NECESITAN EQUIPARSE! Una vez que un título pasivo es descubierto, sus efectos",
                    "  (como esquivas básicas, resistencia a trampas o último aliento) quedan activos para siempre.",
                    "• Todos los bonos pasivos se acumulan continuamente entre sí de forma permanente."
                ]),
                ("DESCUBRIMIENTO ORGÁNICO", (255, 180, 100), [
                    "• No existen manuales que te digan qué hacer: los títulos se desbloquean jugando de verdad.",
                    "• Arriésgate en combate, prueba distintas tácticas y forja tu propia leyenda."
                ])
            ]
            
            y_p = content_rect.y + 20
            for p_title, p_col, p_lines in paragraphs:
                self.virtual_surface.blit(sec_title_font.render(p_title, True, p_col), (content_rect.x + 30, y_p))
                pygame.draw.line(self.virtual_surface, (50, 60, 85), (content_rect.x + 30, y_p + 22), (content_rect.right - 30, y_p + 22), 1)
                y_p += 30
                for pline in p_lines:
                    self.virtual_surface.blit(text_font.render(pline, True, WHITE), (content_rect.x + 40, y_p))
                    y_p += 22
                y_p += 12

        elif self.help_page == 3:
            # PÁGINA 4: BESTIARIO
            beasts = [
                ("FAMILIA DE SLIMES (CRIATURAS VISCOSAS)", YELLOW, [
                    "• Slime Verde: La criatura más común de las primeras plantas. Ataques cuerpo a cuerpo lentos.",
                    "• Slime Mutante (Azul): Variedad endurecida con mayor vitalidad y capacidad ofensiva.",
                    "• Slime Rosa (Élite): Criaturas veloces y escurridizas con jugosas recompensas de botín.",
                    "• Slime Arcano (Púrpura): Criaturas imbuidas con magia antigua en las plantas intermedias.",
                    "• Rey Slime (Jefe de Zona): Coloso viscoso con gran vitalidad y curación pasiva.",
                    "  Desata peligrosas explosiones mágicas viscosas en área."
                ]),
                ("GOBLINS DE LAS CAVERNAS", (120, 255, 120), [
                    "• Combatientes astutos y rápidos que merodean en grupos.",
                    "• Además de sus ataques físicos cuerpo a cuerpo, poseen la facultad de disparar flechas sorpresivas.",
                    "• Consejo: Elimínalos con prontitud para evitar daño a distancia continuo."
                ]),
                ("ORCOS FUERTES", (255, 120, 120), [
                    "• Gigantes acorazados con altísima defensa física (10 DEF) y golpes demoledores.",
                    "• Consejo táctico: Debido a su densa armadura, el daño de espada común se reduce drásticamente.",
                    "  Son especialmente vulnerables al DAÑO MÁGICO, el cual penetra directamente su blindaje."
                ])
            ]
            
            y_b = content_rect.y + 20
            for b_title, b_col, b_lines in beasts:
                self.virtual_surface.blit(sec_title_font.render(b_title, True, b_col), (content_rect.x + 30, y_b))
                pygame.draw.line(self.virtual_surface, (50, 60, 85), (content_rect.x + 30, y_b + 22), (content_rect.right - 30, y_b + 22), 1)
                y_b += 30
                for bline in b_lines:
                    self.virtual_surface.blit(text_font.render(bline, True, WHITE), (content_rect.x + 40, y_b))
                    y_b += 22
                y_b += 14

        # Barra inferior de ayuda de navegación
        footer_y = HEIGHT - 65
        footer_text = "[← / →] o [TAB] Cambiar Página   |   [1 - 4] Salto Directo   |   [ESC / ENTER] Volver al Menú"
        f_surf = text_font.render(footer_text, True, (180, 190, 210))
        self.virtual_surface.blit(f_surf, (WIDTH // 2 - f_surf.get_width() // 2, footer_y))

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

                # Controles globales rápidos de volumen de música (+ y -)
                if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]:
                    self.change_music_volume(0.05)
                elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                    self.change_music_volume(-0.05)

                if self.state == "TITLE_SCREEN":
                    if event.key == pygame.K_ESCAPE:
                        self.quit_game()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(4, self.menu_index + 1)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_index == 0: # Nueva Partida
                            self.state = "NAME_INPUT"
                            self.character_name = ""
                        elif self.menu_index == 1: # Continuar
                            self.save_files = SaveManager.get_save_files()
                            if self.save_files:
                                self.state = "LOAD_SELECTION"
                                self.menu_index = 0
                        elif self.menu_index == 2: # Opciones
                            self.state = "OPTIONS_SCREEN"
                            self.options_return_state = "TITLE_SCREEN"
                            self.options_menu_index = 0
                        elif self.menu_index == 3: # Ayuda
                            self.state = "HELP_SCREEN"
                        elif self.menu_index == 4: # Salir
                            self.quit_game()

                elif self.state == "OPTIONS_SCREEN":
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.options_menu_index = max(0, self.options_menu_index - 1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.options_menu_index = min(2, self.options_menu_index + 1)
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.options_menu_index == 0:
                            self.change_music_volume(-0.05)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.options_menu_index == 0:
                            self.change_music_volume(0.05)
                    elif event.key == pygame.K_RETURN:
                        if self.options_menu_index == 0:
                            self.change_music_volume(0.10)
                        elif self.options_menu_index == 1: # Silenciar / Desilenciar
                            if self.music_volume > 0:
                                self.pre_mute_volume = self.music_volume
                                self.set_music_volume(0.0)
                            else:
                                self.set_music_volume(getattr(self, 'pre_mute_volume', 0.35))
                        elif self.options_menu_index == 2: # Volver
                            self.state = getattr(self, 'options_return_state', 'TITLE_SCREEN')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = getattr(self, 'options_return_state', 'TITLE_SCREEN')

                elif self.state == "CHEST_REWARD":
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_e]:
                        self.state = "PLAYING"
                        self.chest_reward_item = None

                elif self.state == "HELP_SCREEN":
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.help_page = (self.help_page - 1) % 4
                    elif event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_TAB]:
                        self.help_page = (self.help_page + 1) % 4
                    elif event.key == pygame.K_1:
                        self.help_page = 0
                    elif event.key == pygame.K_2:
                        self.help_page = 1
                    elif event.key == pygame.K_3:
                        self.help_page = 2
                    elif event.key == pygame.K_4:
                        self.help_page = 3
                    elif event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                        self.state = "TITLE_SCREEN"
                        self.menu_index = 3

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
                                self.start_saved_game(save_data, filename)
                    elif event.key == pygame.K_d or event.key == pygame.K_DELETE:
                        # BORRAR ARCHIVO DE GUARDADO
                        if self.save_files and 0 <= self.menu_index < len(self.save_files):
                            filename = self.save_files[self.menu_index]
                            filepath = os.path.join("saves", filename)
                            try:
                                if os.path.exists(filepath):
                                    os.remove(filepath)
                                    self.save_files = SaveManager.get_save_files()
                                    self.menu_index = max(0, min(self.menu_index, len(self.save_files) - 1))
                            except Exception as e:
                                print("Error al borrar guardado:", e)

                elif self.state == "NAME_INPUT":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "TITLE_SCREEN"
                        self.menu_index = 0
                    elif event.key == pygame.K_BACKSPACE:
                        self.character_name = self.character_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if len(self.character_name.strip()) > 0:
                            self.state = "DIFFICULTY_SELECTION"
                            self.menu_index = 0
                    elif event.unicode.isalnum() or event.key == pygame.K_SPACE:
                        if len(self.character_name) < 15:
                            self.character_name += event.unicode
                            
                elif self.state == "DIFFICULTY_SELECTION":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "NAME_INPUT"
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(1, self.menu_index + 1)
                    elif event.key == pygame.K_RETURN:
                        dificultad = "facil" if self.menu_index == 0 else "normal"
                        self.start_game("aventurero", self.character_name.strip(), dificultad)
                        
                elif self.state == "PLAYING":
                    if event.key == pygame.K_ESCAPE:
                        self.prev_state = "PLAYING"
                        self.state = "CONFIRM_EXIT"
                        self.menu_index = 0
                    # Movimiento
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.move(dx=-1)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.move(dx=1)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.move(dy=-1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player.move(dy=1)
                    if event.key in [pygame.K_i, pygame.K_TAB]:
                        self.inventory_tab = "INVENTARIO"
                        self.state = "INVENTORY"
                        self.menu_index = 0
                    elif event.key == pygame.K_t:
                        self.inventory_tab = "TITULOS"
                        self.state = "INVENTORY"
                        self.menu_index = 0

                elif self.state == "DIALOG":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = self.next_state
                        if self.state in ["SHOP", "BANK"]:
                            self.menu_index = 0
                
                elif self.state == "COMBAT":
                    if self.combat_intro_timer > 0:
                        pass
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.prev_state = "COMBAT"
                            self.state = "CONFIRM_EXIT"
                            self.menu_index = 0
                        else:
                            options = self.get_combat_options()
                            if event.key == pygame.K_UP or event.key == pygame.K_w:
                                self.menu_index = max(0, self.menu_index - 1)
                            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                                self.menu_index = min(len(options) - 1, self.menu_index + 1)
                            if event.key == pygame.K_RETURN:
                                self.resolve_combat_action()

                elif self.state == "INVENTORY":
                    # Alternancia rápida de pestañas
                    if event.key in [pygame.K_TAB, pygame.K_q, pygame.K_e]:
                        self.inventory_tab = "TITULOS" if self.inventory_tab == "INVENTARIO" else "INVENTARIO"
                        self.menu_index = 0
                    elif event.key == pygame.K_1:
                        self.inventory_tab = "INVENTARIO"
                        self.menu_index = 0
                    elif event.key == pygame.K_2:
                        self.inventory_tab = "TITULOS"
                        self.menu_index = 0
                    elif event.key in [pygame.K_ESCAPE, pygame.K_i]:
                        # Cerrar menú unificado
                        self.state = "COMBAT" if self.current_enemy else "PLAYING"
                    else:
                        if self.inventory_tab == "INVENTARIO":
                            inv = self.player.inventory
                            if event.key in [pygame.K_UP, pygame.K_w]:
                                self.menu_index = max(0, self.menu_index - 1)
                            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                                self.menu_index = min(len(inv), self.menu_index + 1)
                            elif event.key == pygame.K_RETURN:
                                if self.menu_index < len(inv):
                                    item = inv[self.menu_index]
                                    self.use_item(item)
                                else:
                                    self.state = "COMBAT" if self.current_enemy else "PLAYING"
                        else: # Pestaña TITULOS
                            titulos = self.player.logic.titulos_desbloqueados
                            if event.key in [pygame.K_UP, pygame.K_w]:
                                self.menu_index = max(0, self.menu_index - 1)
                            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                                self.menu_index = min(len(titulos), self.menu_index + 1)
                            elif event.key == pygame.K_RETURN:
                                if self.menu_index < len(titulos):
                                    nuevo = titulos[self.menu_index]
                                    from logic.personaje import TITULOS_DATA
                                    t_data = TITULOS_DATA.get(nuevo, {})
                                    if t_data.get("tipo") == "pasivo":
                                        self.log.add_message("[SISTEMA] Este título es pasivo y ya está activo.")
                                        self.spawn_floating_text("¡PASIVO YA ACTIVO!", self.player.rect.centerx, self.player.rect.top - 20, CYAN)
                                    elif self.player.logic.cambiar_titulo(nuevo):
                                        self.play_sfx("coins")
                                        self.log.add_message(f"[TITULO] Equipado: {nuevo}")
                                        self.spawn_floating_text(f"★ {nuevo} ★", self.player.rect.centerx, self.player.rect.top - 20, GREEN)
                                else:
                                    self.state = "COMBAT" if self.current_enemy else "PLAYING"

                elif self.state == "SHOP":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                        self.menu_index = 0
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(5, self.menu_index + 1)
                    if event.key == pygame.K_RETURN:
                        if self.menu_index == 0:
                            self.open_quantity_buy("Pocion Media", 100, lambda: Pocion("media"))
                        elif self.menu_index == 1:
                            if self.player.logic.gastar_monedas(500):
                                self.play_sfx("coins")
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
                            self.open_quantity_buy("Pocion Regreso", 10, lambda: PocionRegreso())
                        elif self.menu_index == 3:
                            if self.player.logic.gastar_monedas(10000):
                                self.play_sfx("coins")
                                from items.potion import LibroMagia
                                item = LibroMagia()
                                self.player.add_to_inventory(item)
                                self.log.add_message("[MERCADER] El conocimiento es poder.")
                                self.spawn_floating_text(f"+{item.nombre}", self.player.rect.centerx, self.player.rect.top, YELLOW)
                            else:
                                self.log.add_message("[MERCADER] Ese libro es muy caro para ti.")
                        elif self.menu_index == 4:
                            self.state = "SELL"
                            self.menu_index = 0
                        elif self.menu_index == 5:
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
                            
                            if hasattr(item, 'cantidad') and item.cantidad > 1:
                                self.open_quantity_sell(self.menu_index, item, valor)
                            else:
                                self.player.logic.añadir_monedas(valor)
                                self.play_sfx("coins")
                                self.log.add_message(f"[MERCADER] Te doy {valor} Cob por {item.nombre}.")
                                inv.pop(self.menu_index)
                                self.menu_index = max(0, min(self.menu_index, len(inv) - 1))
                        else:
                            self.state = "SHOP"
                            self.menu_index = 3

                elif self.state == "SHOP_QUANTITY_BUY":
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.qty_current = max(1, self.qty_current - 1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.qty_current = min(self.qty_max, self.qty_current + 1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.qty_current = max(1, self.qty_current - 10)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.qty_current = min(self.qty_max, self.qty_current + 10)
                    elif event.key in [pygame.K_m, pygame.K_t]:
                        self.qty_current = self.qty_max
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "SHOP"
                    elif event.key == pygame.K_RETURN:
                        costo = self.qty_current * self.qty_unit_price
                        if self.player.logic.gastar_monedas(costo):
                            self.play_sfx("coins")
                            item = self.qty_item_factory()
                            self.player.add_to_inventory(item, cantidad=self.qty_current)
                            self.log.add_message(f"[MERCADER] ¡Compraste {self.qty_current}x {self.qty_item_name}!")
                            self.spawn_floating_text(f"+{self.qty_current} {self.qty_item_name}", self.player.rect.centerx, self.player.rect.top, YELLOW)
                        else:
                            self.log.add_message("[MERCADER] No tienes suficiente dinero.")
                        self.state = "SHOP"

                elif self.state == "SHOP_QUANTITY_SELL":
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.qty_current = max(1, self.qty_current - 1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.qty_current = min(self.qty_max, self.qty_current + 1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.qty_current = max(1, self.qty_current - 10)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.qty_current = min(self.qty_max, self.qty_current + 10)
                    elif event.key in [pygame.K_m, pygame.K_t]:
                        self.qty_current = self.qty_max
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "SELL"
                    elif event.key == pygame.K_RETURN:
                        ganancia = self.qty_current * self.qty_unit_price
                        self.player.logic.añadir_monedas(ganancia)
                        self.play_sfx("coins")
                        self.log.add_message(f"[MERCADER] Vendiste {self.qty_current}x {self.qty_item_name} por {ganancia} Cob.")
                        self.spawn_floating_text(f"+{ganancia} Cob", self.player.rect.centerx, self.player.rect.top, (205, 127, 50))
                        
                        inv = self.player.inventory
                        if self.qty_inv_index < len(inv):
                            target_item = inv[self.qty_inv_index]
                            if hasattr(target_item, 'cantidad'):
                                if self.qty_current >= target_item.cantidad:
                                    inv.pop(self.qty_inv_index)
                                    self.menu_index = max(0, min(self.menu_index, len(inv) - 1))
                                else:
                                    target_item.cantidad -= self.qty_current
                            else:
                                inv.pop(self.qty_inv_index)
                                self.menu_index = max(0, min(self.menu_index, len(inv) - 1))
                        self.state = "SELL"
                
                elif self.state == "BANK":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                        self.menu_index = 0
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
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
                                self.play_sfx("coins")
                                self.log.add_message("[BANQUERO] Protegido.")
                        elif self.menu_index == 1:
                            if l.banco_cobre > 0:
                                l.añadir_monedas(l.banco_cobre)
                                l.banco_cobre = 0
                                self.play_sfx("coins")
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
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.menu_index = (self.menu_index - 1) % 4
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.menu_index = (self.menu_index + 1) % 4
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.menu_index == 1:
                            self.change_music_volume(-0.05)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.menu_index == 1:
                            self.change_music_volume(0.05)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_index == 0: # Seguir jugando
                            self.state = self.prev_state
                        elif self.menu_index == 1: # Ajustes / Opciones de volumen
                            self.change_music_volume(0.05)
                        elif self.menu_index == 2: # Volver a la Pantalla Principal (Hub)
                            if self.profundidad == 0:
                                self.save_return_state = "TITLE_SCREEN"
                                self.state = "SAVE_SELECTION"
                                self.save_files = SaveManager.get_save_files()
                                self.menu_index = 0
                            else:
                                self.return_to_title_screen()
                        elif self.menu_index == 3: # Salir al escritorio
                            if self.profundidad == 0:
                                self.save_return_state = "QUIT"
                                self.state = "SAVE_SELECTION"
                                self.save_files = SaveManager.get_save_files()
                                self.menu_index = 0
                            else:
                                self.quit_game()
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        self.state = self.prev_state

                elif self.state == "SAVE_SELECTION":
                    options = []
                    if len(self.save_files) < 5:
                        options.append("NUEVO GUARDADO")
                    for f in self.save_files:
                        options.append(f"Sobrescribir: {f}")
                    if getattr(self, 'save_return_state', 'QUIT') in ['QUIT', 'TITLE_SCREEN']:
                        options.append("SALIR SIN GUARDAR")
                    options.append("CANCELAR")
                    
                    options_count = len(options)
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(options_count - 1, self.menu_index + 1)
                    elif event.key == pygame.K_ESCAPE:
                        if getattr(self, 'save_return_state', 'QUIT') in ['QUIT', 'TITLE_SCREEN']:
                            self.state = "CONFIRM_EXIT"
                        else:
                            self.state = self.save_return_state
                        self.menu_index = 0
                    elif event.key == pygame.K_RETURN:
                        selected_option = options[self.menu_index]
                        ret_target = getattr(self, 'save_return_state', 'QUIT')
                        if selected_option == "NUEVO GUARDADO":
                            if ret_target == 'QUIT':
                                self.quit_game(None)
                            elif ret_target == 'TITLE_SCREEN':
                                SaveManager.save_game(self, None)
                                self.return_to_title_screen()
                            else:
                                save_success = SaveManager.save_game(self, None)
                                if save_success:
                                    self.log.add_message("[SISTEMA] Partida guardada en nuevo archivo.")
                                    self.spawn_floating_text("¡Partida Guardada!", self.player.rect.centerx, self.player.rect.top - 20, GREEN)
                                else:
                                    self.log.add_message("[SISTEMA] No se pudo guardar la partida.")
                                self.state = self.save_return_state
                        elif selected_option.startswith("Sobrescribir: "):
                            filename = selected_option[len("Sobrescribir: "):]
                            if ret_target == 'QUIT':
                                self.quit_game(filename)
                            elif ret_target == 'TITLE_SCREEN':
                                SaveManager.save_game(self, filename)
                                self.return_to_title_screen()
                            else:
                                save_success = SaveManager.save_game(self, filename)
                                if save_success:
                                    self.log.add_message(f"[SISTEMA] Partida sobrescrita en {filename}.")
                                    self.spawn_floating_text("¡Partida Sobrescrita!", self.player.rect.centerx, self.player.rect.top - 20, GREEN)
                                else:
                                    self.log.add_message("[SISTEMA] No se pudo guardar la partida.")
                                self.state = self.save_return_state
                        elif selected_option == "SALIR SIN GUARDAR":
                            if ret_target == 'TITLE_SCREEN':
                                self.return_to_title_screen()
                            else:
                                pygame.quit()
                                sys.exit()
                        elif selected_option == "CANCELAR":
                            if ret_target in ['QUIT', 'TITLE_SCREEN']:
                                self.state = "CONFIRM_EXIT"
                            else:
                                self.state = self.save_return_state
                            self.menu_index = 0
                    elif event.key == pygame.K_d or event.key == pygame.K_DELETE:
                        selected_option = options[self.menu_index]
                        if selected_option.startswith("Sobrescribir: "):
                            filename = selected_option[len("Sobrescribir: "):]
                            filepath = os.path.join("saves", filename)
                            try:
                                if os.path.exists(filepath):
                                    os.remove(filepath)
                                    self.save_files = SaveManager.get_save_files()
                                    self.menu_index = 0
                            except Exception as e:
                                print("Error al borrar guardado:", e)

                elif self.state == "TITLE_MENU":
                    self.inventory_tab = "TITULOS"
                    self.state = "INVENTORY"
                    self.menu_index = 0

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

                elif self.state == "CROSS_MENU":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_index = min(3, self.menu_index + 1)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                    elif event.key == pygame.K_RETURN:
                        tiempo_actual = self.player.logic.tiempo_juego
                        ultimo_tiempo = self.player.logic.cruz_ultimo_tiempo
                        segundos_por_dia = 15 * 60 # 900 segundos por día
                        
                        dia_actual = int(tiempo_actual // segundos_por_dia)
                        dia_ultimo = int(ultimo_tiempo // segundos_por_dia)
                        
                        # Si ha pasado un día en tiempo de juego (cambio de tramo de 15 min)
                        if dia_actual > dia_ultimo:
                            self.player.logic.cruz_usos_hoy = 3
                            
                        if self.menu_index == 0:
                            # GUARDAR
                            self.save_files = SaveManager.get_save_files()
                            if getattr(self, "current_save_file", None) is None and len(self.save_files) >= 5:
                                self.state = "SAVE_SELECTION"
                                self.save_return_state = "CROSS_MENU"
                                self.menu_index = 0
                                self.log.add_message("[SISTEMA] Límite de 5 guardados alcanzado. Selecciona uno para sobrescribir o presiona 'D' para borrar.")
                            else:
                                save_success = SaveManager.save_game(self, getattr(self, "current_save_file", None))
                                if save_success:
                                    self.log.add_message("[SISTEMA] Partida guardada correctamente.")
                                    self.spawn_floating_text("¡Partida Guardada!", self.player.rect.centerx, self.player.rect.top - 20, GREEN)
                                else:
                                    self.log.add_message("[SISTEMA] No se pudo guardar la partida.")
                        elif self.menu_index == 1:
                            # REZAR (Curación)
                            if self.player.logic.cruz_usos_hoy > 0:
                                self.player.logic.cruz_usos_hoy -= 1
                                self.player.logic.cruz_ultimo_tiempo = dia_actual * segundos_por_dia
                                
                                self.player.logic.vida = self.player.logic.max_vida
                                self.player.logic.mana = self.player.logic.max_mana
                                
                                self.log.add_message(f"[CRUZ] Rezas con devoción. Tu cuerpo y mente se restauran. (Usos restantes: {self.player.logic.cruz_usos_hoy})")
                                self.spawn_floating_text("¡Vida y Maná al Máx!", self.player.rect.centerx, self.player.rect.top - 20, CYAN)
                            else:
                                self.log.add_message("[CRUZ] No tienes más usos de oración en este día de juego.")
                        elif self.menu_index == 2:
                            # CUESTIONAR LAS CREENCIAS
                            if self.player.logic.cruz_usos_hoy == 3:
                                self.player.logic.cruz_usos_hoy = 0
                                self.player.logic.cruz_ultimo_tiempo = dia_actual * segundos_por_dia
                                
                                if "cuestionamientos" not in self.player.logic.acciones:
                                    self.player.logic.acciones["cuestionamientos"] = 0
                                self.player.logic.acciones["cuestionamientos"] += 1
                                
                                self.log.add_message("[CRUZ] Cuestionas tu fe. Una profunda duda te invade. Has quedado penalizado y no podrás curarte hoy en la Cruz.")
                                self.spawn_floating_text("¿Fe cuestionada? (Sin curación)", self.player.rect.centerx, self.player.rect.top - 20, RED)
                                
                                self.player.logic.verificar_titulos(self.log)
                            else:
                                self.log.add_message("[CRUZ] Debes tener los 3 usos de oración del día intactos para cuestionar tus creencias.")
                        elif self.menu_index == 3:
                            # SALIR
                            self.state = "PLAYING"

if __name__ == "__main__":
    g = Game()
    while True:
        g.new()
        g.run()
