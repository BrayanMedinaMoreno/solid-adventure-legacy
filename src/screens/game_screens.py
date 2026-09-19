"""
screens/game_screens.py
Pantallas de la UI durante la partida: inventario, tiendas, combates, banco, cofres.
"""
import pygame
from settings import MAP_WIDTH, HEIGHT, WIDTH, WHITE, CYAN, YELLOW, GREEN, RED, LIGHT_GREY, DARK_GREY, BLACK
from logic.armas import Arma
from logic.armaduras import Armadura

def draw_combat_menu(game):
    import core.combat as combat
    menu_rect = pygame.Rect(MAP_WIDTH // 2 - 120, HEIGHT // 2 + 80, 240, 180)
    pygame.draw.rect(game.virtual_surface, (20, 20, 20), menu_rect)
    pygame.draw.rect(game.virtual_surface, WHITE, menu_rect, 2)
    
    font = pygame.font.SysFont('Consolas', 20)
    options = combat.get_combat_options(game)
    game.menu_index = max(0, min(game.menu_index, len(options) - 1))
    
    for i, option in enumerate(options):
        color = CYAN if i == game.menu_index else WHITE
        prefix = "> " if i == game.menu_index else "  "
        text_surface = font.render(prefix + option, True, color)
        game.virtual_surface.blit(text_surface, (menu_rect.x + 20, menu_rect.y + 20 + i * 35))


def draw_enemy_info_box(game):
    if not game.current_enemy:
        return
        
    enemy = game.current_enemy
    w, h = 400, 160
    box_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 140, w, h)
    
    pygame.draw.rect(game.virtual_surface, (25, 15, 15), box_rect)
    pygame.draw.rect(game.virtual_surface, RED, box_rect, 2)
    
    title_font = pygame.font.SysFont('Consolas', 14, bold=True)
    game.virtual_surface.blit(title_font.render("ENEMIGO EN COMBATE", True, RED), (box_rect.x + 10, box_rect.y + 8))
    
    if hasattr(enemy, 'image') and enemy.image:
        enemy_img = pygame.transform.scale(enemy.image, (64, 64))
        game.virtual_surface.blit(enemy_img, (box_rect.x + 20, box_rect.y + 45))
    
    font = pygame.font.SysFont('Consolas', 18)
    bold_font = pygame.font.SysFont('Consolas', 18, bold=True)
    small_font = pygame.font.SysFont('Consolas', 14)
    
    game.virtual_surface.blit(bold_font.render(enemy.name, True, YELLOW), (box_rect.x + 100, box_rect.y + 25))
    if hasattr(enemy, 'titulo') and enemy.titulo:
        game.virtual_surface.blit(small_font.render(f"<{enemy.titulo}>", True, (0, 255, 255)), (box_rect.x + 100, box_rect.y + 42))
    
    bar_x = box_rect.x + 100
    bar_y = box_rect.y + 60
    bar_w = 280
    bar_h = 14
    pygame.draw.rect(game.virtual_surface, DARK_GREY, (bar_x, bar_y, bar_w, bar_h))
    fill = (enemy.vida / enemy.max_vida) * bar_w
    pygame.draw.rect(game.virtual_surface, RED, (bar_x, bar_y, fill, bar_h))
    pygame.draw.rect(game.virtual_surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
    
    hp_text = f"HP: {enemy.vida}/{enemy.max_vida}"
    hp_surface = small_font.render(hp_text, True, WHITE)
    game.virtual_surface.blit(hp_surface, (bar_x + bar_w // 2 - hp_surface.get_width() // 2, bar_y - 1))
    
    stats_y = box_rect.y + 85
    game.virtual_surface.blit(small_font.render(f"Fuerza (ATK): {enemy.fuerza}", True, LIGHT_GREY), (box_rect.x + 100, stats_y))
    game.virtual_surface.blit(small_font.render(f"Defensa (DEF): {enemy.defensa}", True, LIGHT_GREY), (box_rect.x + 100, stats_y + 18))
    game.virtual_surface.blit(small_font.render(f"Def. Mag. (MAG): {getattr(enemy, 'defensa_magica', 0)}", True, LIGHT_GREY), (box_rect.x + 100, stats_y + 36))
    
    game.virtual_surface.blit(small_font.render(f"Recompensa: +{enemy.xp_recompensa} XP", True, CYAN), (box_rect.x + 250, stats_y))


def draw_inventory_menu(game):
    w, h = 600, 500
    menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    
    pygame.draw.rect(game.virtual_surface, (15, 15, 25), menu_rect)
    pygame.draw.rect(game.virtual_surface, CYAN, menu_rect, 2)
    
    tab_h = 42
    pygame.draw.rect(game.virtual_surface, (25, 25, 40), (menu_rect.x, menu_rect.y, menu_rect.width, tab_h))
    
    title_font = pygame.font.SysFont('Consolas', 18, bold=True)
    small_hint_font = pygame.font.SysFont('Consolas', 14)
    
    tabs_data = [
        ("INVENTARIO", "[ 1. MOCHILA ]"),
        ("EQUIPO", "[ 2. EQUIPO ]"),
        ("TITULOS", "[ 3. TITULOS ]")
    ]
    for i, (tab_id, tab_label) in enumerate(tabs_data):
        tab_active = getattr(game, 'inventory_tab', 'INVENTARIO') == tab_id
        tab_rect = pygame.Rect(menu_rect.x + 8 + i * 145, menu_rect.y + 6, 140, 30)
        bg_tab = (45, 45, 75) if tab_active else (20, 20, 30)
        border_tab = YELLOW if tab_active else (60, 60, 80)
        color_tab = YELLOW if tab_active else LIGHT_GREY
        pygame.draw.rect(game.virtual_surface, bg_tab, tab_rect)
        pygame.draw.rect(game.virtual_surface, border_tab, tab_rect, 2)
        t_surf = title_font.render(tab_label, True, color_tab)
        game.virtual_surface.blit(t_surf, (tab_rect.x + (tab_rect.width - t_surf.get_width()) // 2, tab_rect.y + 5))

    hint_surf = small_hint_font.render("[TAB/Q/E] Cambiar", True, (170, 170, 200))
    game.virtual_surface.blit(hint_surf, (menu_rect.right - hint_surf.get_width() - 15, menu_rect.y + 13))

    font = pygame.font.SysFont('Consolas', 18)
    small_font = pygame.font.SysFont('Consolas', 14)

    if getattr(game, 'inventory_tab', 'INVENTARIO') == "INVENTARIO":
        inv = game.player.inventory
        game.menu_index = max(0, min(game.menu_index, len(inv)))
        
        list_rect = pygame.Rect(menu_rect.x + 10, menu_rect.y + 50, 350, h - 70)
        pygame.draw.rect(game.virtual_surface, (10, 10, 15), list_rect)
        pygame.draw.rect(game.virtual_surface, (50, 50, 70), list_rect, 1)
        
        eq_rect = pygame.Rect(menu_rect.x + 370, menu_rect.y + 50, 220, h - 70)
        pygame.draw.rect(game.virtual_surface, (20, 20, 35), eq_rect)
        pygame.draw.rect(game.virtual_surface, CYAN, eq_rect, 1)
        
        game.virtual_surface.blit(font.render("EQUIPADO:", True, CYAN), (eq_rect.x + 10, eq_rect.y + 10))
        y_eq = eq_rect.y + 40
        slots = [
            ("ARMA", game.player.logic.arma),
            ("CABEZA", game.player.logic.casco),
            ("PECHO", game.player.logic.pechera),
            ("PIES", game.player.logic.botas),
            ("ACCES.", getattr(game.player.logic, 'accesorio', None))
        ]
        for label, item in slots:
            game.virtual_surface.blit(small_font.render(label, True, LIGHT_GREY), (eq_rect.x + 10, y_eq))
            nombre = item.nombre if item else "---"
            color = YELLOW if item else (100, 100, 100)
            game.virtual_surface.blit(font.render(nombre, True, color), (eq_rect.x + 10, y_eq + 15))
            y_eq += 45

        max_visible = (list_rect.height - 40) // 30
        if not hasattr(game, 'inv_scroll'): game.inv_scroll = 0
        
        if game.menu_index < game.inv_scroll:
            game.inv_scroll = game.menu_index
        elif game.menu_index >= game.inv_scroll + max_visible:
            game.inv_scroll = game.menu_index - max_visible + 1

        for i in range(game.inv_scroll, min(len(inv), game.inv_scroll + max_visible)):
            item = inv[i]
            logic = game.player.logic
            is_equipped = False
            if isinstance(item, Arma):
                if item == logic.arma: is_equipped = True
            elif isinstance(item, Armadura):
                if item in [logic.casco, logic.pechera, logic.botas]: is_equipped = True
            elif item.__class__.__name__ == "Accesorio":
                if item == getattr(logic, 'accesorio', None): is_equipped = True

            color = CYAN if i == game.menu_index else (GREEN if is_equipped else WHITE)
            prefix = "> " if i == game.menu_index else "  "
            eq_tag = " [E]" if is_equipped else ""
            cant_tag = f" x{item.cantidad}" if hasattr(item, 'cantidad') and item.cantidad > 1 else ""
            
            draw_y = menu_rect.y + 50 + (i - game.inv_scroll) * 30
            text_surface = font.render(f"{prefix}{item.nombre}{cant_tag}{eq_tag}", True, color)
            game.virtual_surface.blit(text_surface, (menu_rect.x + 20, draw_y))

        exit_idx = len(inv)
        if exit_idx >= game.inv_scroll and exit_idx < game.inv_scroll + max_visible:
            color = CYAN if exit_idx == game.menu_index else WHITE
            prefix = "> " if exit_idx == game.menu_index else "  "
            draw_y = menu_rect.y + 50 + (exit_idx - game.inv_scroll) * 30
            game.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 20, draw_y))

        if game.menu_index < len(inv):
            item = inv[game.menu_index]
            game.draw_description_box(getattr(item, 'descripcion', "Sin descripción."))
        else:
            game.draw_description_box("Cerrar el inventario y volver al juego.")

    elif getattr(game, 'inventory_tab', 'INVENTARIO') == "EQUIPO":
        list_rect = pygame.Rect(menu_rect.x + 10, menu_rect.y + 50, 580, h - 70)
        pygame.draw.rect(game.virtual_surface, (10, 10, 15), list_rect)
        pygame.draw.rect(game.virtual_surface, (50, 50, 70), list_rect, 1)

        slots = [
            ("ARMA", game.player.logic.arma),
            ("CABEZA", game.player.logic.casco),
            ("PECHO", game.player.logic.pechera),
            ("PIES", game.player.logic.botas),
            ("ACCES.", getattr(game.player.logic, 'accesorio', None))
        ]
        
        game.menu_index = max(0, min(game.menu_index, len(slots)))

        y_eq = menu_rect.y + 70
        for i, (label, item) in enumerate(slots):
            color = CYAN if i == game.menu_index else WHITE
            prefix = "> " if i == game.menu_index else "  "
            
            game.virtual_surface.blit(font.render(f"{prefix}{label}:", True, color), (menu_rect.x + 30, y_eq))
            
            nombre = f"{item.nombre} ({item.durabilidad}/{item.max_durabilidad})" if item and hasattr(item, "durabilidad") else (item.nombre if item else "---")
            item_color = YELLOW if item else (100, 100, 100)
            game.virtual_surface.blit(font.render(nombre, True, item_color), (menu_rect.x + 150, y_eq))
            
            # Show a brief hint of stats if equipped
            if item and i == game.menu_index:
                desc = getattr(item, 'descripcion', "Sin descripcin.")
                game.draw_description_box(f"{desc} (Presiona ENTER para Desequipar)")
            
            y_eq += 50
            
        exit_idx = len(slots)
        color = CYAN if exit_idx == game.menu_index else WHITE
        prefix = "> " if exit_idx == game.menu_index else "  "
        game.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 30, y_eq))
        if game.menu_index == exit_idx:
            game.draw_description_box("Cerrar el inventario y volver al juego.")

    else: # TITULOS
        from logic.personaje import TITULOS_DATA
        titulos = game.player.logic.titulos_desbloqueados
        game.menu_index = max(0, min(game.menu_index, len(titulos)))

        list_rect = pygame.Rect(menu_rect.x + 10, menu_rect.y + 50, 350, h - 70)
        pygame.draw.rect(game.virtual_surface, (10, 10, 15), list_rect)
        pygame.draw.rect(game.virtual_surface, (50, 50, 70), list_rect, 1)

        info_rect = pygame.Rect(menu_rect.x + 370, menu_rect.y + 50, 220, h - 70)
        pygame.draw.rect(game.virtual_surface, (20, 20, 35), info_rect)
        pygame.draw.rect(game.virtual_surface, CYAN, info_rect, 1)

        game.virtual_surface.blit(font.render("CONTRATO ACTIVO:", True, CYAN), (info_rect.x + 10, info_rect.y + 15))
        act_nombre = ", ".join(game.player.logic.titulos_activos) if getattr(game.player.logic, "titulos_activos", []) else "Ninguno"
        if len(act_nombre) > 25: act_nombre = f"{len(game.player.logic.titulos_activos)} Activos"
        game.virtual_surface.blit(title_font.render(act_nombre, True, GREEN), (info_rect.x + 10, info_rect.y + 40))

        game.virtual_surface.blit(small_font.render(f"Desbloqueados: {len(titulos)}/{len(TITULOS_DATA)}", True, YELLOW), (info_rect.x + 10, info_rect.y + 80))
        
        p_count = sum(1 for t in titulos if TITULOS_DATA.get(t, {}).get("tipo") == "pasivo")
        game.virtual_surface.blit(small_font.render(f"Pasivos activos: {p_count}", True, CYAN), (info_rect.x + 10, info_rect.y + 105))

        inst_lines = [
            "Los pasivos (+) siempre",
            "estan activos.",
            "",
            "Presiona [ENTER] para",
            "equipar un titulo",
            "activo (*)."
        ]
        for idx_l, line in enumerate(inst_lines):
            game.virtual_surface.blit(small_font.render(line, True, LIGHT_GREY), (info_rect.x + 10, info_rect.y + 145 + idx_l * 20))

        max_visible = (list_rect.height - 40) // 30
        if not hasattr(game, 'title_scroll'): game.title_scroll = 0
        if game.menu_index < game.title_scroll:
            game.title_scroll = game.menu_index
        elif game.menu_index >= game.title_scroll + max_visible:
            game.title_scroll = game.menu_index - max_visible + 1

        for i in range(game.title_scroll, min(len(titulos), game.title_scroll + max_visible)):
            t_name = titulos[i]
            t_data = TITULOS_DATA.get(t_name, {})
            is_passive = t_data.get("tipo") == "pasivo"
            is_active = t_name in getattr(game.player.logic, "titulos_activos", [])

            color = YELLOW if i == game.menu_index else (GREEN if is_active else (CYAN if is_passive else WHITE))
            prefix = "> " if i == game.menu_index else ("* " if is_active else ("+ " if is_passive else "  "))
            suffix = " [PASIVO]" if is_passive else (" [ACTIVO]" if is_active else "")

            draw_y = menu_rect.y + 50 + (i - game.title_scroll) * 30
            game.virtual_surface.blit(font.render(f"{prefix}{t_name}{suffix}", True, color), (menu_rect.x + 20, draw_y))

        exit_idx = len(titulos)
        if exit_idx >= game.title_scroll and exit_idx < game.title_scroll + max_visible:
            color = CYAN if exit_idx == game.menu_index else WHITE
            prefix = "> " if exit_idx == game.menu_index else "  "
            draw_y = menu_rect.y + 50 + (exit_idx - game.title_scroll) * 30
            game.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 20, draw_y))

        if game.menu_index < len(titulos):
            t_name = titulos[game.menu_index]
            desc = TITULOS_DATA.get(t_name, {}).get("descripcion", "Sin descripcion.")
            game.draw_description_box(desc)
        else:
            game.draw_description_box("Cerrar el menu de titulos y volver al juego.")


def draw_shop_menu(game):
    cat = getattr(game, 'shop_category', 'MAIN')
    if cat == 'POTIONS':
        draw_shop_potions(game)
    elif cat == 'WEAPONS':
        draw_shop_weapons(game)
    elif cat == 'ARMORS':
        draw_shop_armors(game)
    else:
        w, h = 450, 350
        rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
        pygame.draw.rect(game.virtual_surface, (20, 20, 30), rect)
        pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)
        font = pygame.font.SysFont('Consolas', 20, bold=True)
        game.virtual_surface.blit(font.render("TIENDA - SELECCIONA CATEGORIA -", True, YELLOW), (rect.x + 30, rect.y + 20))
        options = ["1. Pociones", "2. Armas", "3. Armaduras", "4. Vender Objeto", "5. Salir"]
        for i, text_opt in enumerate(options):
            color = CYAN if i == game.menu_index else WHITE
            prefix = "> " if i == game.menu_index else "  "
            game.virtual_surface.blit(font.render(prefix + text_opt, True, color), (rect.x + 40, rect.y + 70 + i * 40))
        draw_vault_money(game, rect)

def draw_shop_potions(game):
    w, h = 450, 350
    rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    pygame.draw.rect(game.virtual_surface, (20, 20, 30), rect)
    pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)
    font = pygame.font.SysFont('Consolas', 20, bold=True)
    game.virtual_surface.blit(font.render("TIENDA - POCIONES", True, YELLOW), (rect.x + 30, rect.y + 20))
    options = [
        "Pocion Vida Media (1 Plata)",
        "Pocion Vida Grande (3 Plata)",
        "Pocion Mana Media (1 Pl, 50 Cob)",
        "Pocion Regreso (50 Cob)",
        "Grimorio Aprendiz (1 Oro)"
    ,
        "Volver"
    ]
    for i, text_opt in enumerate(options):
        color = CYAN if i == game.menu_index else WHITE
        prefix = "> " if i == game.menu_index else "  "
        game.virtual_surface.blit(font.render(prefix + text_opt, True, color), (rect.x + 40, rect.y + 70 + i * 40))
    draw_vault_money(game, rect)

def draw_shop_weapons(game):
    w, h = 480, 350
    rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    pygame.draw.rect(game.virtual_surface, (20, 20, 30), rect)
    pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)
    font = pygame.font.SysFont('Consolas', 20, bold=True)
    game.virtual_surface.blit(font.render("TIENDA - ARMAS (5 Plata c/u)", True, YELLOW), (rect.x + 30, rect.y + 20))
    options = [
        f"Espada lvl {game.player.logic.nivel} (Cuerpo a cuerpo)",
        f"Arco lvl {game.player.logic.nivel} (A distancia)",
        f"Mazo lvl {game.player.logic.nivel} (Contundente)",
        f"Varita lvl {game.player.logic.nivel} (Magico)"
    ,
        "Volver"
    ]
    for i, text_opt in enumerate(options):
        color = CYAN if i == game.menu_index else WHITE
        prefix = "> " if i == game.menu_index else "  "
        game.virtual_surface.blit(font.render(prefix + text_opt, True, color), (rect.x + 40, rect.y + 70 + i * 40))
    draw_vault_money(game, rect)

def draw_shop_armors(game):
    w, h = 480, 350
    rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    pygame.draw.rect(game.virtual_surface, (20, 20, 30), rect)
    pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)
    font = pygame.font.SysFont('Consolas', 20, bold=True)
    game.virtual_surface.blit(font.render("TIENDA - ARMADURAS (6 Plata c/u)", True, YELLOW), (rect.x + 30, rect.y + 20))
    options = [
        f"Casco lvl {game.player.logic.nivel} (+Defensa)",
        f"Pechera lvl {game.player.logic.nivel} (++Defensa)",
        f"Botas lvl {game.player.logic.nivel} (+Defensa)"
    ,
        "Volver"
    ]
    for i, text_opt in enumerate(options):
        color = CYAN if i == game.menu_index else WHITE
        prefix = "> " if i == game.menu_index else "  "
        game.virtual_surface.blit(font.render(prefix + text_opt, True, color), (rect.x + 40, rect.y + 70 + i * 40))
    draw_vault_money(game, rect)

def draw_shop_accessories(game):
    w, h = 540, 350
    rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    pygame.draw.rect(game.virtual_surface, (20, 20, 30), rect)
    pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)
    font = pygame.font.SysFont('Consolas', 20, bold=True)
    game.virtual_surface.blit(font.render("TIENDA - ACCESORIOS (10 Plata c/u)", True, YELLOW), (rect.x + 30, rect.y + 20))
    options = [
        f"Anillo de Vida lvl {game.player.logic.nivel} (+HP)",
        f"Amuleto de Mana lvl {game.player.logic.nivel} (+MP)",
        f"Collar de Defensa lvl {game.player.logic.nivel} (+DEF)",
        f"Anillo de Poder lvl {game.player.logic.nivel} (+ATK)"
    ,
        "Volver"
    ]
    for i, text_opt in enumerate(options):
        color = CYAN if i == game.menu_index else WHITE
        prefix = "> " if i == game.menu_index else "  "
        game.virtual_surface.blit(font.render(prefix + text_opt, True, color), (rect.x + 40, rect.y + 70 + i * 40))
    draw_vault_money(game, rect)

def draw_vault_money(game, rect):
    money_font = pygame.font.SysFont('Consolas', 16)
    p = game.player.logic
    total = p.cobre + (p.plata * 100) + (p.oro * 10000) + (p.platino * 1000000)
    banco_str = f"{total // 1000000} Platino, {(total % 1000000) // 10000} Oro, {(total % 10000) // 100} Plata, {total % 100} Cobre" if total >= 1000000 else (f"{total // 10000} Oro, {(total % 10000) // 100} Plata, {total % 100} Cobre" if total >= 10000 else (f"{total // 100} Plata, {total % 100} Cobre" if total >= 100 else f"{total} Cobre"))
    game.virtual_surface.blit(money_font.render(f"Dinero: {banco_str}", True, (205, 127, 50)), (rect.x + 40, rect.y + rect.height - 40))


def draw_sell_menu(game):
    draw_inventory_menu(game)
    title_font = pygame.font.SysFont('Consolas', 22, bold=True)
    game.virtual_surface.blit(title_font.render("VENDER (Enter para 1/2 valor)", True, RED), (MAP_WIDTH // 2 - 130, 60))


def draw_quantity_selector(game):
    if getattr(game, 'qty_mode', 'BUY') == "BUY":
        draw_shop_menu(game)
    else:
        draw_sell_menu(game)

    overlay = pygame.Surface((MAP_WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    game.virtual_surface.blit(overlay, (0, 0))

    w, h = 580, 250
    rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((25, 20, 30, 245))
    game.virtual_surface.blit(bg, (rect.x, rect.y))
    
    border_color = (255, 200, 50) if game.qty_mode == "BUY" else (255, 100, 100)
    pygame.draw.rect(game.virtual_surface, border_color, rect, 3)
    pygame.draw.rect(game.virtual_surface, (100, 80, 40), pygame.Rect(rect.x + 4, rect.y + 4, w - 8, h - 8), 1)

    title_font = pygame.font.SysFont('Consolas', 20, bold=True)
    name_font = pygame.font.SysFont('Consolas', 22, bold=True)
    qty_font = pygame.font.SysFont('Consolas', 32, bold=True)
    info_font = pygame.font.SysFont('Consolas', 17)
    prompt_font = pygame.font.SysFont('Consolas', 15)

    title_text = "- COMPRA DE CONSUMIBLES -" if game.qty_mode == "BUY" else "- VENTA DE CONSUMIBLES -"
    t_surf = title_font.render(title_text, True, YELLOW if game.qty_mode == "BUY" else (255, 120, 120))
    game.virtual_surface.blit(t_surf, (rect.x + (w - t_surf.get_width()) // 2, rect.y + 18))

    n_surf = name_font.render(game.qty_item_name, True, WHITE)
    game.virtual_surface.blit(n_surf, (rect.x + (w - n_surf.get_width()) // 2, rect.y + 48))

    qty_text = f"◄   [  {game.qty_current}  ]   ►"
    q_surf = qty_font.render(qty_text, True, CYAN)
    game.virtual_surface.blit(q_surf, (rect.x + (w - q_surf.get_width()) // 2, rect.y + 85))

    total_val = game.qty_current * game.qty_unit_price
    if game.qty_mode == "BUY":
        info_text = f"Precio: {game.qty_unit_price} Cob c/u  |  Total: {total_val} Cob"
        sub_info = f"(Max posible: {game.qty_max} unidades)"
    else:
        info_text = f"Valor: {game.qty_unit_price} Cob c/u  |  Ganancia: +{total_val} Cob"
        sub_info = f"(Tienes: {game.qty_max}  |  Te quedaran: {game.qty_max - game.qty_current})"

    i_surf = info_font.render(info_text, True, YELLOW)
    game.virtual_surface.blit(i_surf, (rect.x + (w - i_surf.get_width()) // 2, rect.y + 132))

    s_surf = info_font.render(sub_info, True, LIGHT_GREY)
    game.virtual_surface.blit(s_surf, (rect.x + (w - s_surf.get_width()) // 2, rect.y + 156))

    instr_text = "[←/→] -1/+1   [↑/↓] -10/+10   [M] Max   [ENTER] OK   [ESC] Salir"
    instr_surf = prompt_font.render(instr_text, True, (160, 160, 180))
    game.virtual_surface.blit(instr_surf, (rect.x + (w - instr_surf.get_width()) // 2, rect.y + 204))


def draw_bank_menu(game):
    w = 600
    menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 110, w, 220)
    pygame.draw.rect(game.virtual_surface, (20, 30, 30), menu_rect)
    pygame.draw.rect(game.virtual_surface, LIGHT_GREY, menu_rect, 2)
    font = pygame.font.SysFont('Consolas', 18)
    banco = game.player.logic.banco_cobre
    banco_str = f"{banco // 1000000} Platino, {(banco % 1000000) // 10000} Oro, {(banco % 10000) // 100} Plata, {banco % 100} Cobre" if banco >= 1000000 else (f"{banco // 10000} Oro, {(banco % 10000) // 100} Plata, {banco % 100} Cobre" if banco >= 10000 else (f"{banco // 100} Plata, {banco % 100} Cobre" if banco >= 100 else f"{banco} Cobre"))
    game.virtual_surface.blit(font.render(f"BANCO: {banco_str}", True, CYAN), (menu_rect.x + 20, menu_rect.y + 10))
    options = ["Depositar todo", "Retirar todo", "Guardar Objeto", "Retirar Objeto", "Salir"]
    descriptions = [
        "Guarda todo tu dinero actual en la caja fuerte.",
        "Retira todos tus ahorros del banco.",
        "Abre el baul para guardar objetos de tu inventario.",
        "Abre el baul para recuperar objetos guardados.",
        "Cierra el menu del banco."
    ]
    for i, option in enumerate(options):
        color = CYAN if i == game.menu_index else WHITE
        prefix = "> " if i == game.menu_index else "  "
        game.virtual_surface.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 50 + i * 32))
        
    game.draw_description_box(descriptions[game.menu_index])


def draw_vault_menu(game, items, title):
    w = 450
    h = 500
    menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    pygame.draw.rect(game.virtual_surface, (10, 10, 20), menu_rect)
    pygame.draw.rect(game.virtual_surface, CYAN, menu_rect, 2)
    font = pygame.font.SysFont('Consolas', 18)
    game.virtual_surface.blit(font.render(title, True, YELLOW), (menu_rect.x + 10, menu_rect.y + 10))

    max_visible = (h - 100) // 30
    if not hasattr(game, 'vault_scroll'): game.vault_scroll = 0
    
    if game.menu_index < game.vault_scroll:
        game.vault_scroll = game.menu_index
    elif game.menu_index >= game.vault_scroll + max_visible:
        game.vault_scroll = game.menu_index - max_visible + 1

    for i in range(game.vault_scroll, min(len(items), game.vault_scroll + max_visible)):
        item = items[i]
        color = CYAN if i == game.menu_index else WHITE
        prefix = "> " if i == game.menu_index else "  "
        cant_tag = f" x{item.cantidad}" if hasattr(item, 'cantidad') and item.cantidad > 1 else ""
        draw_y = menu_rect.y + 40 + (i - game.vault_scroll) * 30
        game.virtual_surface.blit(font.render(prefix + item.nombre + cant_tag, True, color), (menu_rect.x + 20, draw_y))
        
    exit_idx = len(items)
    if exit_idx >= game.vault_scroll and exit_idx < game.vault_scroll + max_visible:
        color = CYAN if exit_idx == game.menu_index else WHITE
        prefix = "> " if exit_idx == game.menu_index else "  "
        draw_y = menu_rect.y + 40 + (exit_idx - game.vault_scroll) * 30
        game.virtual_surface.blit(font.render(prefix + "VOLVER / SALIR", True, color), (menu_rect.x + 20, draw_y))
    
    if game.menu_index < len(items):
        item = items[game.menu_index]
        game.draw_description_box(getattr(item, 'descripcion', "Sin descripcion."))
    else:
        game.draw_description_box("Cerrar el inventario y volver al juego.")
        

def draw_chest_reward(game):
    w, h = 300, 200
    rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    pygame.draw.rect(game.virtual_surface, (30, 20, 10), rect)
    pygame.draw.rect(game.virtual_surface, YELLOW, rect, 2)
    font = pygame.font.SysFont('Consolas', 18)
    game.virtual_surface.blit(font.render("COFRE ABIERTO", True, YELLOW), (rect.x + 20, rect.y + 10))
    game.virtual_surface.blit(font.render("Has encontrado:", True, WHITE), (rect.x + 20, rect.y + 50))
    if hasattr(game, 'chest_reward_item') and game.chest_reward_item:
        c_item = game.chest_reward_item
        cant = f" x{c_item.cantidad}" if hasattr(c_item, 'cantidad') and c_item.cantidad > 1 else ""
        game.virtual_surface.blit(font.render(f"{c_item.nombre}{cant}", True, CYAN), (rect.x + 20, rect.y + 80))
    else:
        game.virtual_surface.blit(font.render("Nada útil...", True, LIGHT_GREY), (rect.x + 20, rect.y + 80))
    game.virtual_surface.blit(font.render("[ENTER] Continuar", True, YELLOW), (rect.x + 20, rect.y + 140))


def draw_confirm_exit(game):
    w, h = 500, 290
    rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)
    pygame.draw.rect(game.virtual_surface, (20, 18, 25), rect)
    pygame.draw.rect(game.virtual_surface, (70, 80, 110), rect, 2)
    
    title_font = pygame.font.SysFont('Consolas', 24, bold=True)
    font = pygame.font.SysFont('Consolas', 19)
    
    t_surf = title_font.render("PAUSA / MENU", True, YELLOW)
    game.virtual_surface.blit(t_surf, (rect.x + (w - t_surf.get_width()) // 2, rect.y + 20))
    
    vol_str = f"{int(game.music_volume * 100)}%"
    options = [
        "SEGUIR JUGANDO",
        f"VOLUMEN MUSICA: < {vol_str} >",
        "PANTALLA PRINCIPAL (MENU)",
        "SALIR AL ESCRITORIO"
    ]
    
    opt_y = rect.y + 65
    for i, opt in enumerate(options):
        is_sel = game.menu_index == i
        col = YELLOW if is_sel else WHITE
        pref = "> " if is_sel else "  "
        game.virtual_surface.blit(font.render(f"{pref}{opt}", True, col), (rect.x + 50, opt_y))
        opt_y += 36
    
    msg_font = pygame.font.SysFont('Consolas', 14)
    if game.profundidad == 0:
        msg = "En el Pueblo: se guardara tu progreso."
        color = GREEN
    else:
        msg = "¡Atencion! En mazmorra perderas el avance del piso."
        color = (255, 130, 130)
    game.virtual_surface.blit(msg_font.render(msg, True, color), (rect.x + 35, rect.y + 245))


def draw_combat_alert(game):
    if not game.current_enemy: return
    
    alpha = int(abs(pygame.time.get_ticks() % 1000 - 500) / 500 * 150) + 100
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 0, 0, 40 if getattr(game, 'combat_intro_timer', 0) > 0.5 else 0))
    game.virtual_surface.blit(overlay, (0, 0))
    
    font_big = pygame.font.SysFont('Consolas', 80, bold=True)
    font_small = pygame.font.SysFont('Consolas', 30, bold=True)
    
    text_vs = f"{game.character_name.upper()} VS {game.current_enemy.name.upper()}"
    
    shadow = font_big.render("¡COMBATE!", True, (50, 0, 0))
    game.virtual_surface.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 5, HEIGHT//2 - 100 + 5))
    
    text_surf = font_big.render("¡COMBATE!", True, RED)
    game.virtual_surface.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 - 100))
    
    vs_surf = font_small.render(text_vs, True, WHITE)
    game.virtual_surface.blit(vs_surf, (WIDTH//2 - vs_surf.get_width()//2, HEIGHT//2))
    
    timer = getattr(game, 'combat_intro_timer', 0.8)
    line_w = 400 * (timer / 0.8)
    pygame.draw.line(game.virtual_surface, RED, (WIDTH//2 - line_w//2, HEIGHT//2 - 120), (WIDTH//2 + line_w//2, HEIGHT//2 - 120), 4)
    pygame.draw.line(game.virtual_surface, RED, (WIDTH//2 - line_w//2, HEIGHT//2 + 50), (WIDTH//2 + line_w//2, HEIGHT//2 + 50), 4)

def draw_cross_menu(game):
    w = 450
    menu_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - 110, w, 220)
    pygame.draw.rect(game.virtual_surface, (20, 20, 30), menu_rect)
    pygame.draw.rect(game.virtual_surface, (255, 255, 0), menu_rect, 2)
    font = pygame.font.SysFont('Consolas', 18)
    game.virtual_surface.blit(font.render("CRUZ SAGRADA", True, (255, 255, 0)), (menu_rect.x + 20, menu_rect.y + 10))
    
    tiempo_actual = game.player.logic.tiempo_juego
    ultimo_tiempo = game.player.logic.cruz_ultimo_tiempo
    segundos_por_dia = 15 * 60
    
    dia_actual = int(tiempo_actual // segundos_por_dia)
    dia_ultimo = int(ultimo_tiempo // segundos_por_dia)
    
    if dia_actual > dia_ultimo:
        game.player.logic.cruz_usos_hoy = 3
        
    usos = game.player.logic.cruz_usos_hoy
    options = [
        "Guardar Partida",
        f"Rezar ({usos} usos hoy)",
        "Cuestionar las Creencias",
        "Salir"
    ]
    descriptions = [
        "Guarda tu progreso actual en el pueblo.",
        "Recupera toda tu vida y mana.",
        "Cuestiona tu fe. Consume los 3 usos del dia (penalizado para curarte hoy).",
        "Te alejas de la Cruz Sagrada."
    ]
    for i, option in enumerate(options):
        color = (0, 255, 255) if i == game.menu_index else (255, 255, 255)
        prefix = "> " if i == game.menu_index else "  "
        game.virtual_surface.blit(font.render(prefix + option, True, color), (menu_rect.x + 20, menu_rect.y + 50 + i * 32))
        
    game.draw_description_box(descriptions[game.menu_index])
