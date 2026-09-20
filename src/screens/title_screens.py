import pygame

import random

import math

from settings import WIDTH, HEIGHT, BLACK, CYAN, YELLOW, WHITE, DARK_GREY, LIGHT_GREY, RED, GREEN, MAP_WIDTH

from logic.save_manager import SaveManager





def draw_title_screen(game):

    title_font = pygame.font.SysFont('Consolas', 50, bold=True)

    font = pygame.font.SysFont('Consolas', 24)

    small_font = pygame.font.SysFont('Consolas', 14)

    

    # Fondo oscuro

    game.virtual_surface.fill((10, 10, 20))

    

    # Inicializar particulas si no existen

    if not game.title_particles:

        for _ in range(60):

            game.title_particles.append({

                'x': random.randint(0, WIDTH),

                'y': random.randint(0, HEIGHT),

                'speed_y': random.uniform(15, 45),

                'size': random.randint(1, 3),

                'color': random.choice([(70, 70, 110), (100, 100, 160), (45, 60, 95)])

            })

            

    # Dibujar y actualizar particulas

    for p in game.title_particles:

        p['y'] += p['speed_y'] * game.dt

        if p['y'] > HEIGHT:

            p['y'] = 0

            p['x'] = random.randint(0, WIDTH)

        pygame.draw.circle(game.virtual_surface, p['color'], (int(p['x']), int(p['y'])), p['size'])



    # Efecto de pulso en sombra de titulo

    pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) / 2

    shadow_color = (int(30 + pulse * 25), int(30 + pulse * 25), int(55 + pulse * 35))

    

    title_text = "SOLID ADVENTURE LEGACY"

    shadow = title_font.render(title_text, True, shadow_color)

    game.virtual_surface.blit(shadow, (WIDTH//2 - 295, HEIGHT//3 - 45))

    game.virtual_surface.blit(title_font.render(title_text, True, CYAN), (WIDTH//2 - 300, HEIGHT//3 - 50))

    

    menu_box = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 30, 360, 275)

    menu_bg = pygame.Surface((menu_box.width, menu_box.height), pygame.SRCALPHA)

    menu_bg.fill((15, 15, 25, 200))

    game.virtual_surface.blit(menu_bg, (menu_box.x, menu_box.y))

    pygame.draw.rect(game.virtual_surface, CYAN, menu_box, 2)

    

    options = ["NUEVA PARTIDA", "CONTINUAR", "OPCIONES", "AYUDA", "SALIR"]

    game.save_files = SaveManager.get_save_files()

    save_exists = len(game.save_files) > 0

    

    for i, option in enumerate(options):

        if i == 1 and not save_exists:

            color = DARK_GREY

            text = option + " (Sin guardado)"

        else:

            color = YELLOW if i == game.menu_index else WHITE

            text = option

            

        prefix = "> " if i == game.menu_index else "  "

        game.virtual_surface.blit(font.render(prefix + text, True, color), (menu_box.x + 40, menu_box.y + 25 + i * 48))

        

    game.virtual_surface.blit(small_font.render("V1.2.0 - Brayan Medina Moreno", True, (100, 100, 120)), (20, HEIGHT - 40))

    game.virtual_surface.blit(small_font.render("Desarrollado con Pygame", True, (100, 100, 120)), (WIDTH - 200, HEIGHT - 40))





def draw_options_screen(game):

    w, h = 520, 320

    rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)

    pygame.draw.rect(game.virtual_surface, (15, 15, 25), rect)

    pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)

    

    title_font = pygame.font.SysFont('Consolas', 26, bold=True)

    font = pygame.font.SysFont('Consolas', 20)

    small_font = pygame.font.SysFont('Consolas', 14)

    

    game.virtual_surface.blit(title_font.render("AJUSTES Y OPCIONES", True, YELLOW), (rect.x + 120, rect.y + 30))

    pygame.draw.line(game.virtual_surface, (50, 70, 90), (rect.x + 30, rect.y + 70), (rect.right - 30, rect.y + 70), 2)

    

    col_vol = YELLOW if game.options_menu_index == 0 else WHITE

    col_mute = YELLOW if game.options_menu_index == 1 else WHITE

    col_back = YELLOW if game.options_menu_index == 2 else WHITE

    

    pref_vol = "> " if game.options_menu_index == 0 else "  "

    pref_mute = "> " if game.options_menu_index == 1 else "  "

    pref_back = "> " if game.options_menu_index == 2 else "  "

    

    vol_pct = int(game.music_volume * 100)

    bar_w = 160

    bar_h = 16

    bar_x = rect.x + 270

    bar_y = rect.y + 112

    

    game.virtual_surface.blit(font.render(f"{pref_vol}Volumen Musica:", True, col_vol), (rect.x + 40, rect.y + 110))

    pygame.draw.rect(game.virtual_surface, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))

    fill_w = int(bar_w * game.music_volume)

    if fill_w > 0:

        pygame.draw.rect(game.virtual_surface, CYAN if game.options_menu_index == 0 else (70, 160, 180), (bar_x, bar_y, fill_w, bar_h))

    pygame.draw.rect(game.virtual_surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)

    game.virtual_surface.blit(small_font.render(f"{vol_pct}%", True, WHITE), (bar_x + bar_w + 12, bar_y))

    

    is_muted = game.music_volume == 0.0

    mute_str = "SÍ (Mudo)" if is_muted else "NO"

    game.virtual_surface.blit(font.render(f"{pref_mute}Silenciar: [{mute_str}]", True, col_mute), (rect.x + 40, rect.y + 165))

    

    game.virtual_surface.blit(font.render(f"{pref_back}VOLVER", True, col_back), (rect.x + 40, rect.y + 220))

    game.virtual_surface.blit(small_font.render("Usa [FLECHAS] o [A/D] para ajustar volumen | [ENTER] seleccionar | [ESC] volver", True, (130, 130, 150)), (rect.x + 20, rect.y + 280))





def draw_level_selection(game):

    w, h = 500, 250

    rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)

    pygame.draw.rect(game.virtual_surface, (10, 20, 30), rect)

    pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)

    

    title_font = pygame.font.SysFont('Consolas', 24, bold=True)

    font = pygame.font.SysFont('Consolas', 20)

    

    game.virtual_surface.blit(title_font.render("¿A DÓNDE QUIERES IR?", True, YELLOW), (rect.x + 100, rect.y + 30))

    

    options = [

        f"Entrar al Piso 1",

        f"Saltar al Piso {game.max_profundidad}",

        "Cancelar"

    ]

    

    for i, option in enumerate(options):

        color = CYAN if i == game.menu_index else WHITE

        prefix = "> " if i == game.menu_index else "  "

        game.virtual_surface.blit(font.render(prefix + option, True, color), (rect.x + 50, rect.y + 80 + i * 40))





def draw_name_input_screen(game):

    game.virtual_surface.fill((10, 10, 20))

    title_font = pygame.font.SysFont('Consolas', 40, bold=True)

    font = pygame.font.SysFont('Consolas', 30)

    

    game.virtual_surface.blit(title_font.render("NOMBRE DE TU HÉROE", True, CYAN), (WIDTH//2 - 200, HEIGHT//2 - 100))

    

    box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2, 400, 50)

    pygame.draw.rect(game.virtual_surface, (30, 30, 40), box_rect)

    pygame.draw.rect(game.virtual_surface, YELLOW, box_rect, 2)

    

    name_surface = font.render(game.character_name, True, WHITE)

    game.virtual_surface.blit(name_surface, (box_rect.x + 10, box_rect.y + 10))

    

    if len(game.character_name) < 15:

        if (pygame.time.get_ticks() // 500) % 2 == 0:

            cursor_x = box_rect.x + 10 + font.size(game.character_name)[0]

            pygame.draw.line(game.virtual_surface, WHITE, (cursor_x, box_rect.y + 10), (cursor_x, box_rect.y + 40), 2)



    game.virtual_surface.blit(pygame.font.SysFont('Consolas', 20).render("Pulsa ENTER para confirmar", True, LIGHT_GREY), (WIDTH//2 - 130, HEIGHT//2 + 100))





def draw_difficulty_selection_screen(game):

    game.virtual_surface.fill((10, 10, 20))

    title_font = pygame.font.SysFont('Consolas', 40, bold=True)

    font = pygame.font.SysFont('Consolas', 30)

    

    game.virtual_surface.blit(title_font.render("SELECCIONA LA DIFICULTAD", True, YELLOW), (WIDTH//2 - 250, HEIGHT//2 - 150))

    

    options = ["La vida es fácil", "La vida es normal"]

    descriptions = [

        "Dificultad pensada para facilitar la partida.",

        "Dificultad pensada como la dificultad normal del juego."

    ]

    

    for i, option in enumerate(options):

        color = CYAN if i == game.menu_index else WHITE

        prefix = "> " if i == game.menu_index else "  "

        game.virtual_surface.blit(font.render(prefix + option, True, color), (WIDTH//2 - 200, HEIGHT//2 - 50 + i * 50))

        

    desc_font = pygame.font.SysFont('Consolas', 18)

    desc_surf = desc_font.render(descriptions[game.menu_index], True, LIGHT_GREY)

    game.virtual_surface.blit(desc_surf, (WIDTH // 2 - desc_surf.get_width() // 2, HEIGHT // 2 + 100))





def draw_load_selection(game):

    game.virtual_surface.fill((10, 10, 20))

    title_font = pygame.font.SysFont('Consolas', 40, bold=True)

    font = pygame.font.SysFont('Consolas', 24)

    small_font = pygame.font.SysFont('Consolas', 18)

    

    game.virtual_surface.blit(title_font.render("CARGAR PARTIDA", True, CYAN), (WIDTH//2 - 150, HEIGHT//2 - 200))

    

    if not game.save_files:

        game.virtual_surface.blit(font.render("No hay archivos de guardado.", True, RED), (WIDTH//2 - 180, HEIGHT//2))

        game.virtual_surface.blit(font.render("Pulsa ESC para volver", True, WHITE), (WIDTH//2 - 130, HEIGHT//2 + 50))

        return



    max_visible = 6

    if not hasattr(game, 'load_scroll'): game.load_scroll = 0

    if game.menu_index < game.load_scroll: game.load_scroll = game.menu_index

    elif game.menu_index >= game.load_scroll + max_visible: game.load_scroll = game.menu_index - max_visible + 1



    for i in range(game.load_scroll, min(len(game.save_files), game.load_scroll + max_visible)):

        filename = game.save_files[i]

        color = YELLOW if i == game.menu_index else WHITE

        prefix = "> " if i == game.menu_index else "  "

        game.virtual_surface.blit(font.render(prefix + filename, True, color), (WIDTH//2 - 200, HEIGHT//2 - 100 + (i - game.load_scroll) * 40))



    game.virtual_surface.blit(small_font.render("[ENTER] Cargar   [D / SUPR] Borrar Guardado", True, YELLOW), (WIDTH//2 - 200, HEIGHT//2 + 180))

    game.virtual_surface.blit(font.render("ESC para Volver", True, LIGHT_GREY), (WIDTH//2 - 100, HEIGHT//2 + 220))





def draw_save_selection(game):

    w, h = 540, 420

    rect = pygame.Rect(WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)

    pygame.draw.rect(game.virtual_surface, (10, 10, 20), rect)

    pygame.draw.rect(game.virtual_surface, YELLOW, rect, 2)

    

    title_font = pygame.font.SysFont('Consolas', 24, bold=True)

    font = pygame.font.SysFont('Consolas', 20)

    small_font = pygame.font.SysFont('Consolas', 14)

    

    game.virtual_surface.blit(title_font.render("¿DÓNDE QUIERES GUARDAR?", True, CYAN), (rect.x + 110, rect.y + 20))

    

    options = []

    if len(game.save_files) < 5:

        options.append("NUEVO GUARDADO")

    for f in game.save_files:

        options.append(f"Sobrescribir: {f}")

    if getattr(game, 'save_return_state', 'QUIT') == 'QUIT':

        options.append("SALIR SIN GUARDAR")

    options.append("CANCELAR")



    max_visible = 8

    if not hasattr(game, 'save_scroll'): game.save_scroll = 0

    if game.menu_index < game.save_scroll: game.save_scroll = game.menu_index

    elif game.menu_index >= game.save_scroll + max_visible: game.save_scroll = game.menu_index - max_visible + 1



    for i in range(game.save_scroll, min(len(options), game.save_scroll + max_visible)):

        color = YELLOW if i == game.menu_index else WHITE

        prefix = "> " if i == game.menu_index else "  "

        text = options[i]

        if len(text) > 42: text = text[:39] + "..."

        game.virtual_surface.blit(font.render(prefix + text, True, color), (rect.x + 30, rect.y + 60 + (i - game.save_scroll) * 35))



    info_text = "[ENTER] Seleccionar  [D] Borrar partida  [ESC] Cancelar"

    game.virtual_surface.blit(small_font.render(info_text, True, YELLOW), (rect.x + 30, rect.y + h - 35))





def draw_title_menu(game):

    w, h = 500, 450

    rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2, w, h)

    pygame.draw.rect(game.virtual_surface, (20, 20, 35), rect)

    pygame.draw.rect(game.virtual_surface, CYAN, rect, 2)

    

    font = pygame.font.SysFont('Consolas', 18)

    title_font = pygame.font.SysFont('Consolas', 22, bold=True)

    game.virtual_surface.blit(title_font.render("CONTRATOS DE IDENTIDAD (titulos)", True, YELLOW), (rect.x + 20, rect.y + 20))

    

    from logic.personaje import TITULOS_DATA

    titulos = game.player.logic.titulos_desbloqueados

    

    for i, t_name in enumerate(titulos):

        t_data = TITULOS_DATA.get(t_name, {})

        is_passive = t_data.get("tipo") == "pasivo"

        is_active = t_name in getattr(game.player.logic, "titulos_activos", [])

        

        color = YELLOW if i == game.menu_index else (GREEN if is_active else (CYAN if is_passive else WHITE))

        prefix = "> " if i == game.menu_index else ("* " if is_active else ("+ " if is_passive else "  "))

        suffix = " (PASIVO)" if is_passive else ""

        

        game.virtual_surface.blit(font.render(f"{prefix}{t_name}{suffix}", True, color), (rect.x + 30, rect.y + 70 + i * 35))

        

    exit_idx = len(titulos)

    color = YELLOW if exit_idx == game.menu_index else WHITE

    game.virtual_surface.blit(font.render(f"{'> ' if exit_idx == game.menu_index else '  '}SALIR AL MENU PRINCIPAL", True, color), (rect.x + 30, rect.y + 70 + exit_idx * 35))

    

    sel_idx = game.menu_index

    if sel_idx < len(titulos):

        t_name = titulos[sel_idx]

        t_data = TITULOS_DATA.get(t_name, {})

        desc_font = pygame.font.SysFont('Consolas', 15)

        

        desc_box = pygame.Rect(rect.x + 20, rect.y + 320, rect.width - 40, 110)

        pygame.draw.rect(game.virtual_surface, (10, 10, 20), desc_box)

        pygame.draw.rect(game.virtual_surface, YELLOW, desc_box, 1)

        

        game.virtual_surface.blit(desc_font.render(f"Efecto de {t_name}:", True, CYAN), (desc_box.x + 10, desc_box.y + 10))

        

        detalles = []

        if "fuerza" in t_data: detalles.append(f"+{t_data['fuerza']} Fuerza")

        if "defensa" in t_data: detalles.append(f"+{t_data['defensa']} Defensa")

        if "max_vida" in t_data: detalles.append(f"+{t_data['max_vida']} Vida")

        if "bono_monedas" in t_data: detalles.append(f"+{int(t_data['bono_monedas']*100)}% Cobre")

        if "bono_xp" in t_data: detalles.append(f"+{int(t_data['bono_xp']*100)}% XP")

        

        y_offset = 35

        for d in detalles:

            game.virtual_surface.blit(desc_font.render(d, True, WHITE), (desc_box.x + 20, desc_box.y + y_offset))

            y_offset += 20

            if y_offset > 90: break

