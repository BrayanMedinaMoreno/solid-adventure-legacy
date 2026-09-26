from items.potion import PocionMana
import pygame
import random
import os
import copy
from items.potion import Pocion, PocionRegreso, PocionMana
from logic.armas import Arma
from logic.armaduras import Armadura
from logic.save_manager import SaveManager
import core.combat as combat
from settings import CYAN, YELLOW, GREEN, RED


def handle(game, event):
    if game.state == "CHEST_REWARD":
        if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_e]:
            game.state = "PLAYING"
            game.chest_reward_item = None

    elif game.state == "DIALOG":
        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            game.state = game.next_state
            if game.state in ["SHOP", "BANK"]:
                game.menu_index = 0

    elif game.state == "INVENTORY":
        if event.key in [pygame.K_TAB, pygame.K_e]:
            tabs = ["INVENTARIO", "EQUIPO", "TITULOS"]
            current = (
                tabs.index(game.inventory_tab)
                if hasattr(game, "inventory_tab") and game.inventory_tab in tabs
                else 0
            )
            game.inventory_tab = tabs[(current + 1) % 3]
            game.menu_index = 0
        elif event.key == pygame.K_q:
            tabs = ["INVENTARIO", "EQUIPO", "TITULOS"]
            current = (
                tabs.index(game.inventory_tab)
                if hasattr(game, "inventory_tab") and game.inventory_tab in tabs
                else 0
            )
            game.inventory_tab = tabs[(current - 1) % 3]
            game.menu_index = 0
        elif event.key == pygame.K_1:
            game.inventory_tab = "INVENTARIO"
            game.menu_index = 0
        elif event.key == pygame.K_2:
            game.inventory_tab = "EQUIPO"
            game.menu_index = 0
        elif event.key == pygame.K_3:
            game.inventory_tab = "TITULOS"
            game.menu_index = 0
        elif event.key in [pygame.K_ESCAPE, pygame.K_i]:
            game.state = "COMBAT" if game.current_enemy else "PLAYING"
        else:
            if getattr(game, "inventory_tab", "INVENTARIO") == "INVENTARIO":
                inv = game.player.inventory
                if event.key in [pygame.K_UP, pygame.K_w]:
                    game.menu_index = max(0, game.menu_index - 1)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    game.menu_index = min(len(inv), game.menu_index + 1)
                elif event.key == pygame.K_RETURN:
                    if game.menu_index < len(inv):
                        item = inv[game.menu_index]
                        combat.use_item(game, item)
                    else:
                        game.state = "COMBAT" if game.current_enemy else "PLAYING"
            elif game.inventory_tab == "EQUIPO":
                if event.key in [pygame.K_UP, pygame.K_w]:
                    game.menu_index = max(0, game.menu_index - 1)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    game.menu_index = min(4, game.menu_index + 1)
                elif event.key == pygame.K_RETURN:
                    if game.menu_index < 5:
                        slots = ["arma", "casco", "pechera", "botas", "accesorio"]
                        slot = slots[game.menu_index]
                        item = getattr(game.player.logic, slot, None)
                        if item:
                            setattr(game.player.logic, slot, None)
                            game.player.add_to_inventory(item)
                            game.log.add_message(
                                f"[EQUIPO] Te has quitado: {item.nombre}."
                            )
                            game.play_sfx("equip")
                    else:
                        game.state = "COMBAT" if game.current_enemy else "PLAYING"
            else:
                titulos = game.player.logic.titulos_desbloqueados
                if event.key in [pygame.K_UP, pygame.K_w]:
                    game.menu_index = max(0, game.menu_index - 1)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    game.menu_index = min(len(titulos), game.menu_index + 1)
                elif event.key == pygame.K_RETURN:
                    if game.menu_index < len(titulos):
                        nuevo = titulos[game.menu_index]
                        from logic.personaje import TITULOS_DATA

                        t_data = TITULOS_DATA.get(nuevo, {})
                        if t_data.get("tipo") == "pasivo":
                            game.log.add_message(
                                "[SISTEMA] Este titulo es pasivo y ya esta activo."
                            )
                            combat.spawn_floating_text(
                                game,
                                "¡PASIVO YA ACTIVO!",
                                game.player.rect.centerx,
                                game.player.rect.top - 20,
                                CYAN,
                            )
                        elif game.player.logic.cambiar_titulo(nuevo):
                            game.play_sfx("coins")
                            game.log.add_message(f"[TITULO] Equipado: {nuevo}")
                            combat.spawn_floating_text(
                                game,
                                f"★ {nuevo} ★",
                                game.player.rect.centerx,
                                game.player.rect.top - 20,
                                GREEN,
                            )
                    else:
                        game.state = "COMBAT" if game.current_enemy else "PLAYING"

    elif game.state == "SHOP":
        category = getattr(game, "shop_category", "MAIN")
        if category == "MAIN":
            if event.key == pygame.K_ESCAPE:
                game.state = "PLAYING"
                game.menu_index = 0
            elif event.key in [pygame.K_UP, pygame.K_w]:
                game.menu_index = max(0, game.menu_index - 1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                game.menu_index = min(4, game.menu_index + 1)
            elif event.key == pygame.K_RETURN:
                if game.menu_index == 0:
                    game.shop_category = "POTIONS"
                    game.menu_index = 0
                elif game.menu_index == 1:
                    game.shop_category = "WEAPONS"
                    game.menu_index = 0
                elif game.menu_index == 2:
                    game.shop_category = "ARMORS"
                    game.menu_index = 0
                elif game.menu_index == 3:
                    game.state = "SELL"
                    game.menu_index = 0
                elif game.menu_index == 4:
                    game.state = "PLAYING"

        elif category == "POTIONS":
            if event.key == pygame.K_ESCAPE:
                game.shop_category = "MAIN"
                game.menu_index = 0
            elif event.key in [pygame.K_UP, pygame.K_w]:
                game.menu_index = max(0, game.menu_index - 1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                game.menu_index = min(5, game.menu_index + 1)
            elif event.key == pygame.K_RETURN:
                if game.menu_index == 0:
                    game.open_quantity_buy(
                        "Pocion Vida Media", 100, lambda: Pocion("media")
                    )
                elif game.menu_index == 1:
                    game.open_quantity_buy(
                        "Pocion Vida Grande", 300, lambda: Pocion("grande")
                    )
                elif game.menu_index == 2:
                    game.open_quantity_buy(
                        "Pocion Mana Media", 150, lambda: PocionMana("media")
                    )
                elif game.menu_index == 3:
                    game.open_quantity_buy(
                        "Pocion Regreso", 50, lambda: PocionRegreso()
                    )
                elif game.menu_index == 4:
                    if game.player.logic.gastar_monedas(10000):
                        game.play_sfx("coins")
                        from items.potion import LibroMagia

                        item = LibroMagia()
                        game.player.add_to_inventory(item)
                        game.log.add_message("[MERCADER] El conocimiento es poder.")
                        combat.spawn_floating_text(
                            game,
                            f"+{item.nombre}",
                            game.player.rect.centerx,
                            game.player.rect.top,
                            YELLOW,
                        )
                    else:
                        game.log.add_message(
                            "[MERCADER] Ese libro es muy caro para ti."
                        )
                elif game.menu_index == 5:
                    game.shop_category = "MAIN"
                    game.menu_index = 0

        elif category == "WEAPONS":
            if event.key == pygame.K_ESCAPE:
                game.shop_category = "MAIN"
                game.menu_index = 1
            elif event.key in [pygame.K_UP, pygame.K_w]:
                game.menu_index = max(0, game.menu_index - 1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                game.menu_index = min(4, game.menu_index + 1)
            elif event.key == pygame.K_RETURN:
                if game.menu_index == 4:
                    game.shop_category = "MAIN"
                    game.menu_index = 1
                    return
                precio = 500
                if game.player.logic.gastar_monedas(precio):
                    game.play_sfx("coins")
                    dmg = random.randint(
                        8 + game.player.logic.nivel,
                        12 + int(game.player.logic.nivel * 1.5),
                    )
                    if game.menu_index == 0:
                        item = Arma(
                            f"Espada lvl {game.player.logic.nivel}", dmg, "fisico"
                        )
                    elif game.menu_index == 1:
                        item = Arma(
                            f"Arco lvl {game.player.logic.nivel}", dmg, "distancia"
                        )
                    elif game.menu_index == 2:
                        item = Arma(
                            f"Mazo lvl {game.player.logic.nivel}",
                            dmg + 10,
                            "contundente",
                        )
                    elif game.menu_index == 3:
                        item = Arma(
                            f"Varita lvl {game.player.logic.nivel}", dmg - 5, "magico"
                        )
                    game.player.add_to_inventory(item)
                    game.log.add_message("[MERCADER] !Excelente eleccion!")
                    combat.spawn_floating_text(
                        game,
                        f"+{item.nombre}",
                        game.player.rect.centerx,
                        game.player.rect.top,
                        YELLOW,
                    )
                else:
                    game.log.add_message("[MERCADER] No tienes dinero suficiente.")
                if game.menu_index == 4:
                    game.shop_category = "MAIN"
                    game.menu_index = 1

        elif category == "ARMORS":
            if event.key == pygame.K_ESCAPE:
                game.shop_category = "MAIN"
                game.menu_index = 2
            elif event.key in [pygame.K_UP, pygame.K_w]:
                game.menu_index = max(0, game.menu_index - 1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                game.menu_index = min(3, game.menu_index + 1)
            elif event.key == pygame.K_RETURN:
                if game.menu_index == 3:
                    game.shop_category = "MAIN"
                    game.menu_index = 2
                    return
                precio = 600
                if game.player.logic.gastar_monedas(precio):
                    game.play_sfx("coins")
                    defensa = random.randint(1, 10)
                    if random.random() < 0.08:  # 8% chance
                        defensa += game.player.logic.nivel
                        game.log.add_message(
                            "[!] Tu suerte despertó: +Nivel aplicado a la armadura!"
                        )
                    if game.menu_index == 0:
                        item = Armadura(
                            f"Casco lvl {game.player.logic.nivel}",
                            defensa,
                            slot="casco",
                        )
                    elif game.menu_index == 1:
                        item = Armadura(
                            f"Pechera lvl {game.player.logic.nivel}",
                            defensa + 5,
                            slot="pechera",
                        )
                    elif game.menu_index == 2:
                        item = Armadura(
                            f"Botas lvl {game.player.logic.nivel}",
                            defensa - 2,
                            slot="botas",
                        )
                    game.player.add_to_inventory(item)
                    game.log.add_message("[MERCADER] !Que te proteja bien!")
                    combat.spawn_floating_text(
                        game,
                        f"+{item.nombre}",
                        game.player.rect.centerx,
                        game.player.rect.top,
                        YELLOW,
                    )
                else:
                    game.log.add_message("[MERCADER] No tienes dinero suficiente.")
                if game.menu_index == 3:
                    game.shop_category = "MAIN"
                    game.menu_index = 2

        elif category == "ACCESSORIES":
            if event.key == pygame.K_ESCAPE:
                game.shop_category = "MAIN"
                game.menu_index = 3
            elif event.key in [pygame.K_UP, pygame.K_w]:
                game.menu_index = max(0, game.menu_index - 1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                game.menu_index = min(4, game.menu_index + 1)
            elif event.key == pygame.K_RETURN:
                if game.menu_index == 4:
                    game.shop_category = "MAIN"
                    game.menu_index = 3
                    return
                precio = 1000
                if game.player.logic.gastar_monedas(precio):
                    game.play_sfx("coins")
                    from logic.accesorios import Accesorio

                    bono = random.randint(
                        5 + game.player.logic.nivel, 15 + game.player.logic.nivel * 2
                    )
                    if game.menu_index == 0:
                        item = Accesorio(
                            f"Anillo de Vida lvl {game.player.logic.nivel}",
                            {"vida": bono * 5},
                        )
                    elif game.menu_index == 1:
                        item = Accesorio(
                            f"Amuleto de Mana lvl {game.player.logic.nivel}",
                            {"mana": bono * 5},
                        )
                    elif game.menu_index == 2:
                        item = Accesorio(
                            f"Collar de Defensa lvl {game.player.logic.nivel}",
                            {"defensa": bono},
                        )
                    elif game.menu_index == 3:
                        item = Accesorio(
                            f"Anillo de Poder lvl {game.player.logic.nivel}",
                            {"daño": bono},
                        )
                    game.player.add_to_inventory(item)
                    game.log.add_message("[MERCADER] !Un accesorio util!")
                    combat.spawn_floating_text(
                        game,
                        f"+{item.nombre}",
                        game.player.rect.centerx,
                        game.player.rect.top,
                        YELLOW,
                    )
                else:
                    game.log.add_message("[MERCADER] No tienes dinero suficiente.")
                if game.menu_index == 4:
                    game.shop_category = "MAIN"
                    game.menu_index = 3
    elif game.state == "SELL":
        inv = game.player.inventory
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(len(inv), game.menu_index + 1)
        if event.key == pygame.K_ESCAPE:
            game.state = "SHOP"
            game.shop_category = "MAIN"
            game.menu_index = 4
        if event.key == pygame.K_RETURN:
            if game.menu_index < len(inv):
                item = inv[game.menu_index]
                valor = 50
                if isinstance(item, Arma):
                    valor = 200
                elif isinstance(item, Armadura):
                    valor = 150

                if hasattr(item, "cantidad") and item.cantidad > 1:
                    game.open_quantity_sell(game.menu_index, item, valor)
                else:
                    game.player.logic.añadir_monedas(valor)
                    game.play_sfx("coins")
                    game.log.add_message(
                        f"[MERCADER] Te doy {valor} Cob por {item.nombre}."
                    )
                    inv.pop(game.menu_index)
                    game.menu_index = max(0, min(game.menu_index, len(inv) - 1))
            else:
                game.state = "SHOP"
                game.shop_category = "MAIN"
                game.menu_index = 4

    elif game.state == "SHOP_QUANTITY_BUY":
        if event.key in [pygame.K_LEFT, pygame.K_a]:
            game.qty_current = max(1, game.qty_current - 1)
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            game.qty_current = min(game.qty_max, game.qty_current + 1)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            game.qty_current = max(1, game.qty_current - 10)
        elif event.key in [pygame.K_UP, pygame.K_w]:
            game.qty_current = min(game.qty_max, game.qty_current + 10)
        elif event.key in [pygame.K_m, pygame.K_t]:
            game.qty_current = game.qty_max
        elif event.key == pygame.K_ESCAPE:
            game.state = "SHOP"
        elif event.key == pygame.K_RETURN:
            costo = game.qty_current * game.qty_unit_price
            if game.player.logic.gastar_monedas(costo):
                game.play_sfx("coins")
                item = game.qty_item_factory()
                game.player.add_to_inventory(item, cantidad=game.qty_current)
                game.log.add_message(
                    f"[MERCADER] ¡Compraste {game.qty_current}x {game.qty_item_name}!"
                )
                combat.spawn_floating_text(
                    game,
                    f"+{game.qty_current} {game.qty_item_name}",
                    game.player.rect.centerx,
                    game.player.rect.top,
                    YELLOW,
                )
            else:
                game.log.add_message("[MERCADER] No tienes suficiente dinero.")
            game.state = "SHOP"

    elif game.state == "SHOP_QUANTITY_SELL":
        if event.key in [pygame.K_LEFT, pygame.K_a]:
            game.qty_current = max(1, game.qty_current - 1)
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            game.qty_current = min(game.qty_max, game.qty_current + 1)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            game.qty_current = max(1, game.qty_current - 10)
        elif event.key in [pygame.K_UP, pygame.K_w]:
            game.qty_current = min(game.qty_max, game.qty_current + 10)
        elif event.key in [pygame.K_m, pygame.K_t]:
            game.qty_current = game.qty_max
        elif event.key == pygame.K_ESCAPE:
            game.state = "SELL"
        elif event.key == pygame.K_RETURN:
            ganancia = game.qty_current * game.qty_unit_price
            game.player.logic.añadir_monedas(ganancia)
            game.play_sfx("coins")
            game.log.add_message(
                f"[MERCADER] Vendiste {game.qty_current}x {game.qty_item_name} por {ganancia} Cob."
            )
            combat.spawn_floating_text(
                game,
                f"+{ganancia} Cob",
                game.player.rect.centerx,
                game.player.rect.top,
                (205, 127, 50),
            )

            inv = game.player.inventory
            if game.qty_inv_index < len(inv):
                target_item = inv[game.qty_inv_index]
                if hasattr(target_item, "cantidad"):
                    if game.qty_current >= target_item.cantidad:
                        inv.pop(game.qty_inv_index)
                        game.menu_index = max(0, min(game.menu_index, len(inv) - 1))
                    else:
                        target_item.cantidad -= game.qty_current
                else:
                    inv.pop(game.qty_inv_index)
                    game.menu_index = max(0, min(game.menu_index, len(inv) - 1))
            game.state = "SELL"

    elif game.state == "BANK":
        if event.key == pygame.K_ESCAPE:
            game.state = "PLAYING"
            game.menu_index = 0
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(4, game.menu_index + 1)
        if event.key == pygame.K_RETURN:
            l = game.player.logic
            total_cobre = l.cobre + l.plata * 100 + l.oro * 10000 + l.platino * 1000000
            if game.menu_index == 0:
                if total_cobre > 0:
                    l.banco_cobre += total_cobre
                    l.gastar_monedas(total_cobre)
                    game.play_sfx("coins")
                    game.log.add_message("[BANQUERO] Protegido.")
            elif game.menu_index == 1:
                if l.banco_cobre > 0:
                    l.añadir_monedas(l.banco_cobre)
                    l.banco_cobre = 0
                    game.play_sfx("coins")
                    game.log.add_message("[BANQUERO] Dinero retirado.")
            elif game.menu_index == 2:
                game.state = "BANK_STORE"
                game.menu_index = 0
            elif game.menu_index == 3:
                game.state = "BANK_RETRIEVE"
                game.menu_index = 0
            elif game.menu_index == 4:
                game.state = "PLAYING"

    elif game.state == "BANK_STORE":
        inv = game.player.inventory
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(len(inv), game.menu_index + 1)
        if event.key == pygame.K_ESCAPE:
            game.state = "BANK"
            game.menu_index = 2
        if event.key == pygame.K_RETURN:
            if game.menu_index < len(inv):
                item = inv[game.menu_index]
                found = False
                if isinstance(item, (Pocion, PocionRegreso)):
                    for b_item in game.player.logic.baul:
                        if type(b_item) == type(item):
                            if isinstance(item, Pocion):
                                if b_item.tipo == item.tipo:
                                    b_item.cantidad += 1
                                    found = True
                                    break
                            else:
                                b_item.cantidad += 1
                                found = True
                                break

                if not found:
                    if hasattr(item, "cantidad") and item.cantidad > 1:
                        new_item = copy.copy(item)
                        new_item.cantidad = 1
                        game.player.logic.baul.append(new_item)
                    else:
                        game.player.logic.baul.append(inv.pop(game.menu_index))
                        game.menu_index = max(0, game.menu_index - 1)
                else:
                    if hasattr(item, "cantidad") and item.cantidad > 1:
                        item.cantidad -= 1
                    else:
                        inv.pop(game.menu_index)
                        game.menu_index = max(0, game.menu_index - 1)

                game.log.add_message(f"[BANQUERO] {item.nombre} guardado.")
            else:
                game.state = "BANK"
                game.menu_index = 2

    elif game.state == "BANK_RETRIEVE":
        baul = game.player.logic.baul
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(len(baul), game.menu_index + 1)
        if event.key == pygame.K_ESCAPE:
            game.state = "BANK"
            game.menu_index = 3
        if event.key == pygame.K_RETURN:
            if game.menu_index < len(baul):
                item = baul[game.menu_index]
                game.player.add_to_inventory(item)

                if hasattr(item, "cantidad") and item.cantidad > 1:
                    item.cantidad -= 1
                else:
                    baul.pop(game.menu_index)
                    game.menu_index = max(0, game.menu_index - 1)

                game.log.add_message(f"[BANQUERO] {item.nombre} retirado.")
            else:
                game.state = "BANK"
                game.menu_index = 3

    elif game.state == "HERRERO":
        armas = getattr(game, "herrero_armas", [])
        if event.key == pygame.K_ESCAPE:
            game.state = "PLAYING"
            game.menu_index = 0
        elif event.key in [pygame.K_UP, pygame.K_w]:
            game.menu_index = max(0, game.menu_index - 1)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            game.menu_index = min(len(armas), game.menu_index + 1)  # len=salir
        elif event.key == pygame.K_RETURN:
            if game.menu_index < len(armas):
                game.herrero_arma_idx = game.menu_index
                game.state = "HERRERO_ACTION"
                game.menu_index = 0
            else:
                game.state = "PLAYING"
                game.menu_index = 0

    elif game.state == "HERRERO_ACTION":
        arma, _origen = game.herrero_armas[game.herrero_arma_idx]
        l = game.player.logic

        # Construir opciones dinámicamente (igual que get_combat_options)
        opciones = ["Reparar", "Mejorar Durabilidad", "Mejorar Daño", "Volver"]

        if event.key == pygame.K_ESCAPE:
            game.state = "HERRERO"
            game.menu_index = game.herrero_arma_idx
        elif event.key in [pygame.K_UP, pygame.K_w]:
            game.menu_index = max(0, game.menu_index - 1)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            game.menu_index = min(len(opciones) - 1, game.menu_index + 1)
        elif event.key == pygame.K_RETURN:
            idx = game.menu_index
            if idx == 3:  # Volver
                game.state = "HERRERO"
                game.menu_index = game.herrero_arma_idx
            elif idx == 0:  # Reparar
                if arma.esta_al_maximo():
                    game.log.add_message(f"[HERRERO] {arma.nombre} ya está al 100%.")
                else:
                    costo = (arma.durabilidad_max - arma.durabilidad) * 2
                    if l.gastar_monedas(costo):
                        arma.reparar()
                        game.play_sfx("coins")
                        game.log.add_message(f"[HERRERO] Reparada por {costo} Cob.")
                    else:
                        game.log.add_message("[HERRERO] No tienes suficiente dinero.")
            elif idx == 1:  # Mejorar Durabilidad
                if not arma.puede_mejorar_durabilidad():
                    game.log.add_message(
                        "[HERRERO] Esta arma ya no admite más mejoras."
                    )
                else:
                    costo = 100 + arma.durabilidad_max  # ajustable
                    if l.gastar_monedas(costo):
                        arma.mejorar_durabilidad(15)
                        arma.mejoras_realizadas_durabilidad += 1
                        game.play_sfx("coins")
                        game.log.add_message(f"[HERRERO] Durabilidad mejorada (+25).")
                    else:
                        game.log.add_message("[HERRERO] No tienes suficiente dinero.")
            elif idx == 2:  # Mejorar Daño
                if not arma.puede_mejorar_daño():
                    game.log.add_message(
                        "[HERRERO] Esta arma ya no admite más mejoras."
                    )
                else:
                    costo = 200 + arma.daño * 15
                    if l.gastar_monedas(costo):
                        mejora = max(1, int(arma.daño * 0.1))
                        arma.mejorar_daño(mejora)
                        arma.mejoras_realizadas_daño += 1
                        arma.reparar()
                        game.play_sfx("coins")
                        game.log.add_message(f"[HERRERO] Daño mejorado (+{mejora}).")
                    else:
                        game.log.add_message("[HERRERO] No tienes suficiente dinero.")

    elif game.state == "CONFIRM_EXIT":
        if event.key in [pygame.K_UP, pygame.K_w]:
            game.menu_index = (game.menu_index - 1) % 4
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            game.menu_index = (game.menu_index + 1) % 4
        elif event.key in [pygame.K_LEFT, pygame.K_a]:
            if game.menu_index == 1:
                game.change_music_volume(-0.05)
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            if game.menu_index == 1:
                game.change_music_volume(0.05)
        elif event.key == pygame.K_RETURN:
            if game.menu_index == 0:
                game.state = getattr(game, "prev_state", "PLAYING")
            elif game.menu_index == 1:
                game.change_music_volume(0.05)
            elif game.menu_index == 2:
                if game.profundidad == 0:
                    game.save_return_state = "TITLE_SCREEN"
                    game.state = "SAVE_SELECTION"
                    game.save_files = SaveManager.get_save_files()
                    game.menu_index = 0
                else:
                    game.return_to_title_screen()
            elif game.menu_index == 3:
                if game.profundidad == 0:
                    game.save_return_state = "QUIT"
                    game.state = "SAVE_SELECTION"
                    game.save_files = SaveManager.get_save_files()
                    game.menu_index = 0
                else:
                    game.quit_game()
        elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            game.state = getattr(game, "prev_state", "PLAYING")

    elif game.state == "TITLE_MENU":
        game.inventory_tab = "TITULOS"
        game.state = "INVENTORY"
        game.menu_index = 0

    elif game.state == "LEVEL_SELECTION":
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(2, game.menu_index + 1)
        if event.key == pygame.K_RETURN:
            if game.menu_index == 0:
                game.profundidad = 1
                game.went_down = True
                game.load_level()
            elif game.menu_index == 1:
                game.profundidad = game.max_profundidad
                game.went_down = True
                game.load_level()
            else:
                game.state = "PLAYING"
        if event.key == pygame.K_ESCAPE:
            game.state = "PLAYING"

    elif game.state == "CROSS_MENU":
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(3, game.menu_index + 1)
        elif event.key == pygame.K_ESCAPE:
            game.state = "PLAYING"
        elif event.key == pygame.K_RETURN:
            tiempo_actual = game.player.logic.tiempo_juego
            ultimo_tiempo = game.player.logic.cruz_ultimo_tiempo
            segundos_por_dia = 15 * 60

            dia_actual = int(tiempo_actual // segundos_por_dia)
            dia_ultimo = int(ultimo_tiempo // segundos_por_dia)

            if dia_actual > dia_ultimo:
                game.player.logic.cruz_usos_hoy = 3

            if game.menu_index == 0:
                game.save_files = SaveManager.get_save_files()
                if (
                    getattr(game, "current_save_file", None) is None
                    and len(game.save_files) >= 5
                ):
                    game.state = "SAVE_SELECTION"
                    game.save_return_state = "CROSS_MENU"
                    game.menu_index = 0
                    game.log.add_message(
                        "[SISTEMA] Limite de guardados. Selecciona uno para sobrescribir o 'D' para borrar."
                    )
                else:
                    save_success = SaveManager.save_game(
                        game, getattr(game, "current_save_file", None)
                    )
                    if save_success:
                        game.log.add_message(
                            "[SISTEMA] Partida guardada correctamente."
                        )
                        combat.spawn_floating_text(
                            game,
                            "¡Partida Guardada!",
                            game.player.rect.centerx,
                            game.player.rect.top - 20,
                            GREEN,
                        )
                    else:
                        game.log.add_message("[SISTEMA] No se pudo guardar la partida.")
            elif game.menu_index == 1:
                if game.player.logic.cruz_usos_hoy > 0:
                    game.player.logic.cruz_usos_hoy -= 1
                    game.player.logic.cruz_ultimo_tiempo = dia_actual * segundos_por_dia

                    game.player.logic.vida = game.player.logic.max_vida
                    game.player.logic.mana = game.player.logic.max_mana

                    game.log.add_message(
                        f"[CRUZ] Rezas con devocion. (Usos restantes: {game.player.logic.cruz_usos_hoy})"
                    )
                    combat.spawn_floating_text(
                        game,
                        "¡Vida y Mana al Max!",
                        game.player.rect.centerx,
                        game.player.rect.top - 20,
                        CYAN,
                    )
                else:
                    game.log.add_message(
                        "[CRUZ] No tienes mas usos de oracion en este dia de juego."
                    )
            elif game.menu_index == 2:
                if game.player.logic.cruz_usos_hoy == 3:
                    game.player.logic.cruz_usos_hoy = 0
                    game.player.logic.cruz_ultimo_tiempo = dia_actual * segundos_por_dia

                    if "cuestionamientos" not in game.player.logic.acciones:
                        game.player.logic.acciones["cuestionamientos"] = 0
                    game.player.logic.acciones["cuestionamientos"] += 1

                    game.log.add_message(
                        "[CRUZ] Cuestionas tu fe. Has quedado penalizado y no podras curarte hoy en la Cruz."
                    )
                    combat.spawn_floating_text(
                        game,
                        "¿Fe cuestionada? (Sin curacion)",
                        game.player.rect.centerx,
                        game.player.rect.top - 20,
                        RED,
                    )

                    game.player.logic.verificar_titulos(game.log)
                else:
                    game.log.add_message(
                        "[CRUZ] Debes tener los 3 usos de oracion del dia intactos para cuestionar tus creencias."
                    )
            elif game.menu_index == 3:
                game.state = "PLAYING"
