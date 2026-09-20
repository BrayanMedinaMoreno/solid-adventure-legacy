import random
from settings import WHITE, RED, GREEN, YELLOW, BLUE
from ui.floating_text import FloatingText
from logic.armas import Arma
from items.potion import Pocion, PocionRegreso


# ---------------------------------------------------------------------------
# Helpers de consulta al mapa
# ---------------------------------------------------------------------------

def get_chest_at(game, x, y):
    for chest in game.chests:
        if chest.x == x and chest.y == y:
            return chest
    return None


def get_enemy_at(game, x, y):
    for enemy in game.enemies:
        if enemy.x == x and enemy.y == y:
            return enemy
    return None


def get_npc_at(game, x, y):
    for npc in game.npcs:
        if npc.x == x and npc.y == y:
            return npc
    return None


def get_trap_at(game, x, y):
    for trap in game.traps:
        if trap.x == x and trap.y == y:
            return trap
    return None


# ---------------------------------------------------------------------------
# Texto flotante
# ---------------------------------------------------------------------------

def spawn_floating_text(game, text, x, y, color=WHITE):
    FloatingText(game.floating_texts, text, x, y, color)


# ---------------------------------------------------------------------------
# Opciones de combate del jugador
# ---------------------------------------------------------------------------

def get_combat_options(game):
    options = ["Ataque Básico"]
    titulos_activos = game.player.logic.titulos_activos
    cd_h = game.player.logic.cooldowns.get("habilidad", 0)
    cd_d = game.player.logic.cooldowns.get("distancia", 0)

    has_sword = any("Espada" in t or "Hoja" in t for t in titulos_activos)
    has_bow = any("Proyectil" in t or "Arquero" in t or "Halcón" in t for t in titulos_activos)

    if has_sword:
        options.append(f"Golpe Habilidad{' (CD: ' + str(cd_h) + ')' if cd_h > 0 else ''}")
    if has_bow:
        options.append(f"Ataque Distancia{' (CD: ' + str(cd_d) + ')' if cd_d > 0 else ''}")

    if getattr(game.player.logic, 'magia_desbloqueada', False):
        costo_mp = 15
        if game.player.logic.mana >= costo_mp:
            options.append(f"Ataque Mágico (-{costo_mp} MP)")
        else:
            options.append(f"Ataque Mágico (Sin MP)")

    options.extend(["Huir", "Inventario"])
    return options


# ---------------------------------------------------------------------------
# Inicio de combate
# ---------------------------------------------------------------------------

def start_combat(game, enemy):
    game.state = "COMBAT"
    game.current_enemy = enemy
    game.menu_index = 0
    game.combat_intro_timer = 0.8
    game.player.logic.aliento_usado_combate = False
    game.player.logic.min_porcentaje_vida_combate = (
        game.player.logic.vida / game.player.logic.max_vida
    ) * 100
    game.log.add_message(f"--- COMBATE: {enemy.name.upper()} ---")


# ---------------------------------------------------------------------------
# Resolución de turno del jugador
# ---------------------------------------------------------------------------

def resolve_combat_action(game):
    game.player.logic.ejecutar_regen_turno(game.log)

    options = get_combat_options(game)
    game.menu_index = max(0, min(game.menu_index, len(options) - 1))
    action = options[game.menu_index]

    should_end_turn = False

    if action == "Ataque Básico":
        arma_p = getattr(game.player.logic, 'arma', None) or getattr(game.player.logic, 'espada', None)
        if arma_p and "hacha" in arma_p.nombre.lower():
            game.play_sfx("hacha")
        else:
            game.play_sfx("espada")
        game.player.logic.atacar(game.current_enemy, game.log, tipo_forzado="fisico")
        should_end_turn = True

    elif action.startswith("Golpe Habilidad"):
        if game.player.logic.cooldowns.get("habilidad", 0) > 0:
            game.log.add_message("[SISTEMA] Habilidad ¡EN ENFRIAMIENTO!.")
            spawn_floating_text(game, "¡EN ENFRIAMIENTO!", game.player.rect.centerx, game.player.rect.top - 20, YELLOW)
            return
        game.player.logic.cooldowns["habilidad"] = 3
        arma_p = getattr(game.player.logic, 'arma', None) or getattr(game.player.logic, 'espada', None)
        if arma_p and "hacha" in arma_p.nombre.lower():
            game.play_sfx("hacha")
        else:
            game.play_sfx("espada")
        game.player.logic.atacar(game.current_enemy, game.log, tipo_forzado="habilidad")
        should_end_turn = True

    elif action.startswith("Ataque Distancia"):
        if game.player.logic.cooldowns.get("distancia", 0) > 0:
            game.log.add_message("[SISTEMA] Habilidad ¡EN ENFRIAMIENTO!.")
            spawn_floating_text(game, "¡EN ENFRIAMIENTO!", game.player.rect.centerx, game.player.rect.top - 20, YELLOW)
            return
        game.player.logic.cooldowns["distancia"] = 3
        game.play_sfx("ballesta")
        game.player.logic.atacar(game.current_enemy, game.log, tipo_forzado="distancia")
        should_end_turn = True

    elif action.startswith("Ataque Mágico"):
        if game.player.logic.gastar_mana(15):
            game.play_sfx("espada")
            game.player.logic.atacar(game.current_enemy, game.log, tipo_forzado="magico")
            should_end_turn = True
        else:
            game.log.add_message("[SISTEMA] No tienes suficiente mana.")
            spawn_floating_text(game, "¡SIN MANÁ!", game.player.rect.centerx, game.player.rect.top - 20, BLUE)
            return

    elif action == "Huir":
        if random.random() < 0.7:
            game.log.add_message("[SISTEMA] Has escapado del combate!")
            spawn_floating_text(game, "¡ESCAPASTE!", game.player.rect.centerx, game.player.rect.top - 20, GREEN)
            game.state = "PLAYING"
            game.current_enemy = None
            game.menu_index = 0
            return
        else:
            game.log.add_message("[SISTEMA] No pudiste escapar!")
            spawn_floating_text(game, "¡FALLASTE!", game.player.rect.centerx, game.player.rect.top - 20, RED)
            should_end_turn = True

    elif action == "Inventario":
        game.state = "INVENTORY"
        game.menu_index = 0
        return

    if game.current_enemy and game.current_enemy.vida <= 0:
        game.play_sfx("muerte")
        game.log.add_message(f"[SISTEMA] {game.current_enemy.name} muere.")
        game.player.logic.ganar_xp(game.current_enemy.xp_recompensa, game.log)
        spawn_floating_text(game, f"+{game.current_enemy.xp_recompensa} XP",
                            game.player.rect.centerx, game.player.rect.top, YELLOW)

        min_hp = game.player.logic.min_porcentaje_vida_combate
        if min_hp < 25: game.player.logic.acciones["combates_bajo_25hp"] += 1
        if min_hp < 20: game.player.logic.acciones["combates_bajo_20hp"] += 1
        if min_hp < 15: game.player.logic.acciones["combates_bajo_15hp"] += 1
        game.player.logic.verificar_titulos(game.log)

        monedas = int(random.randint(
            game.current_enemy.xp_recompensa // 2,
            game.current_enemy.xp_recompensa
        ) * (1 + (game.profundidad * 0.5)))
        game.player.logic.añadir_monedas(monedas)
        game.play_sfx("coins")
        game.log.add_message(f"[LOOT] +{monedas} Cobre")
        spawn_floating_text(game, f"+{monedas} Cob",
                            game.player.rect.centerx, game.player.rect.centery, (205, 127, 50))
                            
        if hasattr(game.current_enemy, "loot_extra") and game.current_enemy.loot_extra:
            for loot_entry in game.current_enemy.loot_extra:
                # Podría ser (item, prob) o solo item si algún otro código lo agregó así
                if isinstance(loot_entry, tuple):
                    item, prob = loot_entry
                else:
                    item, prob = loot_entry, 1.0 # Si no tiene probabilidad, drop 100%
                    
                if random.random() <= prob:
                    game.player.add_to_inventory(item)
                    game.log.add_message(f"[LOOT] Has despojado: {item.nombre}!")
                    spawn_floating_text(game, f"+ {item.nombre}",
                                        game.player.rect.centerx, game.player.rect.top - 20, (0, 255, 0))

        game.state = "PLAYING"
        game.current_enemy.kill()
        game.current_enemy = None

        if len(game.enemies) == 0:
            game.log.add_message("[SISTEMA] ¡¡ZONA DESPEJADA! Las escaleras están abiertas.")
            spawn_floating_text(game, "¡ZONA DESPEJADA!", game.player.rect.centerx, game.player.rect.top - 40, GREEN)

    elif should_end_turn and game.current_enemy:
        resolve_enemy_turn(game)


# ---------------------------------------------------------------------------
# Resolución del turno del enemigo
# ---------------------------------------------------------------------------

def resolve_enemy_turn(game):
    if not game.current_enemy or game.current_enemy.vida <= 0:
        return

    game.current_enemy.act()

    damage_type = "fisico"
    enemy_name = game.current_enemy.__class__.__name__

    chance = random.random()
    if enemy_name == "Goblin" and chance < 0.25:
        damage_type = "distancia"
        game.log.add_message("[GOBLIN] Lanza una flecha!")
    elif enemy_name == "Orco" and chance < 0.15:
        damage_type = "habilidad"
        game.log.add_message("[ORCO] Golpe de habilidad pesado!")
    elif enemy_name == "SlimeBoss" and chance < 0.20:
        damage_type = "magico"
        game.log.add_message("[REY SLIME] Explosion magica viscosa!")

    if damage_type == "distancia":
        game.play_sfx("ballesta")
    elif "Goblin" in enemy_name:
        game.play_sfx("goblin")
    elif "Orco" in enemy_name:
        game.play_sfx("hacha")
    elif "Slime" in enemy_name:
        game.play_sfx("slime")
    else:
        game.play_sfx("espada")

    enemy_dmg = max(1, game.current_enemy.fuerza - game.player.logic.defensa)
    if game.player.logic.recibir_daño(enemy_dmg, tipo=damage_type, log=game.log):
        spawn_floating_text(game, f"-{enemy_dmg}", game.player.rect.centerx, game.player.rect.top, RED)
        if not hasattr(game, 'screen_shake'):
            game.screen_shake = 0
        game.screen_shake = min(8, game.screen_shake + 2 + enemy_dmg // 5)

    if game.player.logic.vida <= 0:
        game.play_sfx("muerte")
        game.log.add_message("[SISTEMA] ¡HAS MUERTO!")

        xp_perdida = int(game.player.logic.xp * 0.20)
        game.player.logic.xp -= xp_perdida

        dificultad = getattr(game, "dificultad", "normal")

        if dificultad == "facil":
            game.player.logic.cobre //= 2
            game.player.logic.plata //= 2
            game.player.logic.oro //= 2
            game.player.logic.platino //= 2
            game.log.add_message(f"[SISTEMA] Perdiste {xp_perdida} XP y la mitad de tu dinero, pero conservas tus objetos.")
        else:
            game.player.logic.cobre = 0
            game.player.logic.plata = 0
            game.player.logic.oro = 0
            game.player.logic.platino = 0

            regreso_items = [item for item in game.player.inventory if isinstance(item, PocionRegreso)]
            arma_basica = Arma("Espada de Madera", 8, "fisico")
            game.player.inventory = [arma_basica] + regreso_items
            game.player.logic.arma = arma_basica
            game.player.logic.armadura = None
            if hasattr(game.player.logic, 'casco'):    game.player.logic.casco = None
            if hasattr(game.player.logic, 'pechera'):  game.player.logic.pechera = None
            if hasattr(game.player.logic, 'botas'):    game.player.logic.botas = None
            if hasattr(game.player.logic, 'accesorio'): game.player.logic.accesorio = None
            game.log.add_message(f"[SISTEMA] Perdiste {xp_perdida} XP, tu dinero y tu equipo. Solo conservas Pociones de Regreso.")

        game.player.logic.vida = game.player.logic.max_vida
        game.profundidad = 0
        game.load_level()


# ---------------------------------------------------------------------------
# Uso de items desde inventario
# ---------------------------------------------------------------------------

def use_item(game, item):
    from items.potion import Pocion, PocionRegreso, PocionMana, LibroMagia
    from logic.accesorios import Accesorio
    
    if isinstance(item, Pocion) or isinstance(item, PocionRegreso) or isinstance(item, PocionMana) or isinstance(item, LibroMagia):
        item.usar(game.player.logic, game.log)
        if hasattr(item, 'cantidad'):
            item.cantidad -= 1
            if item.cantidad <= 0 and item in game.player.inventory:
                game.player.inventory.remove(item)
        if game.current_enemy:
            game.state = "COMBAT"
            resolve_enemy_turn(game)
        else:
            game.state = "PLAYING"
            
    elif hasattr(item, 'tipo_daño') or hasattr(item, 'tipo_dano'):
        if item in game.player.inventory:
            game.player.inventory.remove(item)
        old_arma = getattr(game.player.logic, 'arma', None)
        if old_arma:
            game.player.inventory.append(old_arma)
        game.player.logic.arma = item
        game.log.add_message(f"[Tú] Equipas {item.nombre}.")
        
        if game.current_enemy:
            game.state = "COMBAT"
            resolve_enemy_turn(game)
        else:
            game.state = "PLAYING"
            
    elif hasattr(item, 'defensa') and not hasattr(item, 'bono'):
        slot = getattr(item, 'slot', 'pechera')
        if item in game.player.inventory:
            game.player.inventory.remove(item)
        old_armor = getattr(game.player.logic, slot, None)
        if old_armor:
            game.player.inventory.append(old_armor)
        setattr(game.player.logic, slot, item)
        game.log.add_message(f"[Tú] Equipas {item.nombre} en {slot.upper()}.")
        
        if game.current_enemy:
            game.state = "COMBAT"
            resolve_enemy_turn(game)
        else:
            game.state = "PLAYING"
            
    elif isinstance(item, Accesorio):
        if item in game.player.inventory:
            game.player.inventory.remove(item)
        old_acc = game.player.logic.accesorio
        if old_acc:
            game.player.inventory.append(old_acc)
        game.player.logic.accesorio = item
        game.log.add_message(f"[Tú] Equipas {item.nombre}.")
        
        if game.current_enemy:
            game.state = "COMBAT"
            resolve_enemy_turn(game)
        else:
            game.state = "PLAYING"
