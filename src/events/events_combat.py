"""
events/events_combat.py
Manejo de eventos de combate.
"""
import pygame
import core.combat as combat

def handle(game, event):
    if getattr(game, 'combat_intro_timer', 0) > 0:
        pass
    else:
        if event.key == pygame.K_ESCAPE:
            game.prev_state = "COMBAT"
            game.state = "CONFIRM_EXIT"
            game.menu_index = 0
        else:
            options = combat.get_combat_options(game)
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                game.menu_index = max(0, game.menu_index - 1)
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                game.menu_index = min(len(options) - 1, game.menu_index + 1)
            if event.key == pygame.K_RETURN:
                combat.resolve_combat_action(game)
