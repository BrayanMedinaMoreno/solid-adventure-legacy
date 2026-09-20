import pygame

def handle(game, event):
    if event.key == pygame.K_ESCAPE:
        game.prev_state = "PLAYING"
        game.state = "CONFIRM_EXIT"
        game.menu_index = 0
    # Movimiento
    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        game.player.move(dx=-1)
    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        game.player.move(dx=1)
    elif event.key == pygame.K_UP or event.key == pygame.K_w:
        game.player.move(dy=-1)
    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        game.player.move(dy=1)
    
    if event.key in [pygame.K_i, pygame.K_TAB]:
        game.inventory_tab = "INVENTARIO"
        game.state = "INVENTORY"
        game.menu_index = 0
    elif event.key == pygame.K_t:
        game.inventory_tab = "TITULOS"
        game.state = "INVENTORY"
        game.menu_index = 0
