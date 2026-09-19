"""
screens/help_screen.py
Pantalla del manual de aventuras y guía de combate.
"""
import pygame
from settings import WIDTH, HEIGHT, YELLOW, CYAN, LIGHT_GREY, WHITE, RED, GREEN

def draw_help_screen(game):
    game.virtual_surface.fill((12, 12, 22))
    
    # Marco exterior
    pygame.draw.rect(game.virtual_surface, (50, 60, 90), pygame.Rect(20, 20, WIDTH - 40, HEIGHT - 40), 2)
    
    header_font = pygame.font.SysFont("Consolas", 26, bold=True)
    tab_font = pygame.font.SysFont("Consolas", 16, bold=True)
    sec_title_font = pygame.font.SysFont("Consolas", 19, bold=True)
    text_font = pygame.font.SysFont("Consolas", 16)
    code_font = pygame.font.SysFont("Consolas", 15)
    small_hint_font = pygame.font.SysFont("Consolas", 14)
    
    # Título superior
    title_surf = header_font.render("★ MANUAL DE AVENTURAS Y GUÍA DE COMBATE ★", True, YELLOW)
    game.virtual_surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 35))
    
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
        is_active = game.help_page == idx
        bg_col = (45, 45, 80) if is_active else (20, 20, 30)
        brd_col = YELLOW if is_active else (60, 60, 80)
        txt_col = YELLOW if is_active else LIGHT_GREY
        
        pygame.draw.rect(game.virtual_surface, bg_col, t_rect)
        pygame.draw.rect(game.virtual_surface, brd_col, t_rect, 2)
        
        t_surf = tab_font.render(name, True, txt_col)
        game.virtual_surface.blit(t_surf, (t_rect.x + (t_rect.width - t_surf.get_width()) // 2, t_rect.y + 7))

    # Contenedor central
    content_rect = pygame.Rect(40, 125, WIDTH - 80, HEIGHT - 200)
    pygame.draw.rect(game.virtual_surface, (18, 18, 28), content_rect)
    pygame.draw.rect(game.virtual_surface, (40, 45, 65), content_rect, 1)

    if game.help_page == 0:
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
            
            game.virtual_surface.blit(sec_title_font.render(sec_title, True, CYAN), (col_x, col_y))
            pygame.draw.line(game.virtual_surface, (60, 80, 110), (col_x, col_y + 24), (col_x + col_w - 20, col_y + 24), 1)
            
            row_y = col_y + 34
            for key_tag, desc_text in items:
                game.virtual_surface.blit(code_font.render(key_tag, True, YELLOW), (col_x + 5, row_y))
                game.virtual_surface.blit(text_font.render(desc_text, True, WHITE), (col_x + 5, row_y + 18))
                row_y += 38

    elif game.help_page == 1:
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
            game.virtual_surface.blit(sec_title_font.render(sec_title, True, title_col), (content_rect.x + 30, y_sec))
            pygame.draw.line(game.virtual_surface, (50, 60, 85), (content_rect.x + 30, y_sec + 22), (content_rect.right - 30, y_sec + 22), 1)
            y_sec += 30
            for line in lines:
                col = WHITE if not line.startswith("• ¡GRAN VENTAJA!:") else (120, 255, 180)
                game.virtual_surface.blit(text_font.render(line, True, col), (content_rect.x + 40, y_sec))
                y_sec += 21
            y_sec += 14

    elif game.help_page == 2:
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
            game.virtual_surface.blit(sec_title_font.render(p_title, True, p_col), (content_rect.x + 30, y_p))
            pygame.draw.line(game.virtual_surface, (50, 60, 85), (content_rect.x + 30, y_p + 22), (content_rect.right - 30, y_p + 22), 1)
            y_p += 30
            for pline in p_lines:
                game.virtual_surface.blit(text_font.render(pline, True, WHITE), (content_rect.x + 40, y_p))
                y_p += 22
            y_p += 12

    elif game.help_page == 3:
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
            game.virtual_surface.blit(sec_title_font.render(b_title, True, b_col), (content_rect.x + 30, y_b))
            pygame.draw.line(game.virtual_surface, (50, 60, 85), (content_rect.x + 30, y_b + 22), (content_rect.right - 30, y_b + 22), 1)
            y_b += 30
            for bline in b_lines:
                game.virtual_surface.blit(text_font.render(bline, True, WHITE), (content_rect.x + 40, y_b))
                y_b += 22
            y_b += 14

    footer_y = HEIGHT - 65
    footer_text = "[← / →] o [TAB] Cambiar Página   |   [1 - 4] Salto Directo   |   [ESC / ENTER] Volver al Menú"
    f_surf = text_font.render(footer_text, True, (180, 190, 210))
    game.virtual_surface.blit(f_surf, (WIDTH // 2 - f_surf.get_width() // 2, footer_y))
