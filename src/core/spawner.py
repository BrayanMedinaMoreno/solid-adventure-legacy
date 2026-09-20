import random
from entities.enemy_types import Goblin, Orco, Slime, SlimeBoss, SlimeMutante, SlimeRosa, SlimeArcano
from items.chest import Chest
from entities.trap import Trap
from entities.npc import Mercader, Banquero, CruzInteractiva


def populate_level(game, occupied_tiles):
    """Llena el nivel con enemigos, cofres y trampas (mazmorra) o NPCs (pueblo)."""
    if game.profundidad > 0:
        _spawn_dungeon(game, occupied_tiles)
    else:
        _spawn_town(game)


def _spawn_dungeon(game, occupied_tiles):
    profundidad = game.profundidad
    num_enemies = 4 + profundidad * 2

    if profundidad % 5 == 0:
        # Nivel de jefe: Rey Slime escalado
        game.log.add_message("[ALERTA] HAS LLEGADO AL REINO DEL REY SLIME!")
        available_tiles = [t for t in game.level.floor_tiles if t not in occupied_tiles]
        if available_tiles:
            tile = random.choice(available_tiles)
            multiplicador = profundidad // 5
            boss = SlimeBoss(game, tile[0], tile[1])
            boss.max_vida += multiplicador * 500
            boss.vida = boss.max_vida
            boss.fuerza += multiplicador * 20
            boss.defensa += multiplicador * 10
            boss.xp_recompensa += multiplicador * 1000
            occupied_tiles.add(tile)
            available_tiles.remove(tile)
            
        # Generar Secuaces (Goblins Campeones y Slimes Arcanos)
        for _ in range(num_enemies):
            if not available_tiles: break
            tile = random.choice(available_tiles)
            
            tipo = random.choice(["Goblin Campeon", "Slime Arcano"])
            if tipo == "Goblin Campeon":
                enemy = Goblin(game, tile[0], tile[1])
                
                # Equipar accesorio forzado
                from logic.accesorios import Accesorio
                bono = random.randint(5 + game.player.logic.nivel, 15 + game.player.logic.nivel*2)
                bono = int(bono * 0.95)
                stat = random.choice(["fuerza", "defensa", "magia", "max_vida", "max_mana"])
                val = bono * 5 if stat in ["max_vida", "max_mana"] else bono
                acc = Accesorio("Talismán de Élite", {stat: val}, 10, 100)
                if stat == "max_vida":
                    enemy.max_vida += val
                    enemy.vida += val
                elif stat == "fuerza":
                    enemy.fuerza += val
                elif stat == "defensa":
                    enemy.defensa += val
                
                # NO DROPEA NADA (Prob 0.0)
                enemy.loot_extra.append((acc, 0.0))
                enemy.titulo = "Guardia Real"
                enemy.name = "Goblin Campeón (Guardia)"
                enemy.xp_recompensa += 30
            else:
                enemy = SlimeArcano(game, tile[0], tile[1])
                enemy.titulo = "Acolito de la Viscosidad"
                enemy.name = "Slime Arcano (Élite)"
                enemy.max_vida += 50
                enemy.vida = enemy.max_vida
                enemy.xp_recompensa += 30
                
            occupied_tiles.add(tile)
            available_tiles.remove(tile)
            
    else:
        for _ in range(num_enemies):
            available_tiles = [t for t in game.level.floor_tiles if t not in occupied_tiles]
            if not available_tiles:
                break
            tile = random.choice(available_tiles)

            if profundidad <= 2:
                tipo_enemigo = random.choice([Slime, Slime, Slime, Goblin, SlimeMutante])
            elif profundidad <= 4:
                tipo_enemigo = random.choice([Slime, SlimeMutante, SlimeMutante, SlimeArcano, SlimeArcano, Goblin, Orco, SlimeRosa])
            else:
                tipo_enemigo = random.choice([Goblin, Orco, Orco, SlimeArcano, SlimeRosa, SlimeRosa])

            enemy = tipo_enemigo(game, tile[0], tile[1])
            if profundidad <= 4 and random.random() < 0.15: # 15% prob
                enemy.titulo = "El Arquitecto de la mazmorra"
            enemy.max_vida += profundidad * 20
            enemy.vida = enemy.max_vida
            enemy.fuerza += profundidad * 5
            enemy.defensa += profundidad * 2
            enemy.xp_recompensa += profundidad * 15
            occupied_tiles.add(tile)

    # Cofres
    for _ in range(3):
        available_tiles = [t for t in game.level.floor_tiles if t not in occupied_tiles]
        if not available_tiles:
            break
        tile = random.choice(available_tiles)
        Chest(game, tile[0], tile[1])
        occupied_tiles.add(tile)

    # Trampas
    num_traps = random.randint(1, 3)
    for _ in range(num_traps):
        available_tiles = [t for t in game.level.floor_tiles if t not in occupied_tiles]
        if not available_tiles:
            break
        tile = random.choice(available_tiles)
        Trap(game, tile[0], tile[1])
        occupied_tiles.add(tile)


def _spawn_town(game):
    mid_x = game.level.width_tiles // 2
    mid_y = game.level.height_tiles // 2
    game.log.add_message("[PUEBLO] Estas a salvo aqui.")
    Mercader(game, mid_x - 2, mid_y)
    Banquero(game, mid_x + 2, mid_y)
    CruzInteractiva(game, mid_x, mid_y - 3)
