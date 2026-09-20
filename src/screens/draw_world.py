import pygame
import random
from settings import WIDTH, HEIGHT, TILESIZE, MAP_WIDTH, BLACK, DARK_GREY, LIGHT_GREY, YELLOW, CYAN, WHITE

def draw_grid(game, cam_x=0, cam_y=0):
    """Dibuja líneas del grid compensando la cámara."""
    offset_x = cam_x % TILESIZE
    offset_y = cam_y % TILESIZE
    
    for x in range(0, MAP_WIDTH + TILESIZE, TILESIZE):
        pygame.draw.line(game.virtual_surface, DARK_GREY, (x - offset_x, 0), (x - offset_x, HEIGHT))
    for y in range(0, HEIGHT + TILESIZE, TILESIZE):
        pygame.draw.line(game.virtual_surface, DARK_GREY, (0, y - offset_y), (MAP_WIDTH, y - offset_y))


def flip_to_screen(game):
    """Escala la superficie virtual a la ventana real manteniendo el aspecto."""
    window_w, window_h = game.screen.get_size()
    scale_w = window_w / WIDTH
    scale_h = window_h / HEIGHT
    scale = min(scale_w, scale_h)
    
    new_w = int(WIDTH * scale)
    new_h = int(HEIGHT * scale)
    
    scaled_surf = pygame.transform.scale(game.virtual_surface, (new_w, new_h))
    
    # Centrar en la pantalla (barras negras si el aspect ratio es distinto)
    pos_x = (window_w - new_w) // 2
    pos_y = (window_h - new_h) // 2
    
    # Aplicar Screen Shake (temblor aleatorio)
    if hasattr(game, 'screen_shake') and game.screen_shake > 0:
        offset = int(game.screen_shake)
        if offset > 0:
            pos_x += random.randint(-offset, offset)
            pos_y += random.randint(-offset, offset)
    
    game.screen.fill(BLACK)
    game.screen.blit(scaled_surf, (pos_x, pos_y))
    pygame.display.flip()


def draw_description_box(game, text):
    if not text: return
    w = 450
    panel_rect = pygame.Rect(MAP_WIDTH // 2 - w // 2, HEIGHT - 130, w, 110)
    # Sombra
    pygame.draw.rect(game.virtual_surface, (5, 5, 5), (panel_rect.x + 5, panel_rect.y + 5, panel_rect.width, panel_rect.height))
    # Fondo con degradado simulado (bordes más claros)
    pygame.draw.rect(game.virtual_surface, (25, 25, 40), panel_rect)
    pygame.draw.rect(game.virtual_surface, (60, 60, 80), panel_rect, 1) # Borde sutil
    pygame.draw.rect(game.virtual_surface, YELLOW, (panel_rect.x, panel_rect.y, panel_rect.width, 4)) # Línea superior decorativa
    
    font = pygame.font.SysFont('Consolas', 16)
    title_font = pygame.font.SysFont('Consolas', 16, bold=True)
    
    game.virtual_surface.blit(title_font.render("DETALLES DEL OBJETO:", True, YELLOW), (panel_rect.x + 15, panel_rect.y + 12))
    
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
        game.virtual_surface.blit(font.render(line, True, LIGHT_GREY), (panel_rect.x + 15, panel_rect.y + 40 + i * 20))


def draw_volume_hud(game):
    w, h = 230, 46
    x = WIDTH - w - 20
    y = 20
    hud_rect = pygame.Rect(x, y, w, h)
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((15, 15, 25, 220))
    game.virtual_surface.blit(bg, (x, y))
    pygame.draw.rect(game.virtual_surface, CYAN, hud_rect, 1)
    
    font = pygame.font.SysFont('Consolas', 15, bold=True)
    vol_pct = int(game.music_volume * 100)
    game.virtual_surface.blit(font.render(f"MÚSICA: {vol_pct}%", True, YELLOW), (x + 10, y + 6))
    
    bar_w = 210
    bar_h = 8
    bar_x = x + 10
    bar_y = y + 28
    pygame.draw.rect(game.virtual_surface, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
    fill_w = int(bar_w * game.music_volume)
    if fill_w > 0:
        pygame.draw.rect(game.virtual_surface, CYAN, (bar_x, bar_y, fill_w, bar_h))
    pygame.draw.rect(game.virtual_surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
