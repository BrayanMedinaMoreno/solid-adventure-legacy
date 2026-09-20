import pygame
from logic.save_manager import SaveManager
import os
import sys

def handle(game, event):
    if game.state == "TITLE_SCREEN":
        if event.key == pygame.K_ESCAPE:
            game.quit_game()
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(4, game.menu_index + 1)
        elif event.key == pygame.K_RETURN:
            if game.menu_index == 0:
                game.state = "NAME_INPUT"
                game.character_name = ""
            elif game.menu_index == 1:
                game.save_files = SaveManager.get_save_files()
                if game.save_files:
                    game.state = "LOAD_SELECTION"
                    game.menu_index = 0
            elif game.menu_index == 2:
                game.state = "OPTIONS_SCREEN"
                game.options_return_state = "TITLE_SCREEN"
                game.options_menu_index = 0
            elif game.menu_index == 3:
                game.state = "HELP_SCREEN"
            elif game.menu_index == 4:
                game.quit_game()

    elif game.state == "OPTIONS_SCREEN":
        if event.key in [pygame.K_UP, pygame.K_w]:
            game.options_menu_index = max(0, game.options_menu_index - 1)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            game.options_menu_index = min(2, game.options_menu_index + 1)
        elif event.key in [pygame.K_LEFT, pygame.K_a]:
            if game.options_menu_index == 0:
                game.change_music_volume(-0.05)
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            if game.options_menu_index == 0:
                game.change_music_volume(0.05)
        elif event.key == pygame.K_RETURN:
            if game.options_menu_index == 0:
                game.change_music_volume(0.10)
            elif game.options_menu_index == 1:
                if game.music_volume > 0:
                    game.pre_mute_volume = game.music_volume
                    game.set_music_volume(0.0)
                else:
                    game.set_music_volume(getattr(game, 'pre_mute_volume', 0.35))
            elif game.options_menu_index == 2:
                game.state = getattr(game, 'options_return_state', 'TITLE_SCREEN')
        elif event.key == pygame.K_ESCAPE:
            game.state = getattr(game, 'options_return_state', 'TITLE_SCREEN')

    elif game.state == "HELP_SCREEN":
        if event.key in [pygame.K_LEFT, pygame.K_a]:
            game.help_page = (game.help_page - 1) % 4
        elif event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_TAB]:
            game.help_page = (game.help_page + 1) % 4
        elif event.key == pygame.K_1:
            game.help_page = 0
        elif event.key == pygame.K_2:
            game.help_page = 1
        elif event.key == pygame.K_3:
            game.help_page = 2
        elif event.key == pygame.K_4:
            game.help_page = 3
        elif event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
            game.state = "TITLE_SCREEN"
            game.menu_index = 3

    elif game.state == "LOAD_SELECTION":
        if event.key == pygame.K_ESCAPE:
            game.state = "TITLE_SCREEN"
            game.menu_index = 1
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(len(game.save_files) - 1, game.menu_index + 1)
        elif event.key == pygame.K_RETURN:
            if game.save_files:
                filename = game.save_files[game.menu_index]
                save_data = SaveManager.load_game(filename)
                if save_data:
                    game.start_saved_game(save_data, filename)
        elif event.key == pygame.K_d or event.key == pygame.K_DELETE:
            if game.save_files and 0 <= game.menu_index < len(game.save_files):
                filename = game.save_files[game.menu_index]
                filepath = os.path.join("saves", filename)
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        game.save_files = SaveManager.get_save_files()
                        game.menu_index = max(0, min(game.menu_index, len(game.save_files) - 1))
                except Exception as e:
                    print("Error al borrar guardado:", e)

    elif game.state == "NAME_INPUT":
        if event.key == pygame.K_ESCAPE:
            game.state = "TITLE_SCREEN"
            game.menu_index = 0
        elif event.key == pygame.K_BACKSPACE:
            game.character_name = game.character_name[:-1]
        elif event.key == pygame.K_RETURN:
            if len(game.character_name.strip()) > 0:
                game.state = "DIFFICULTY_SELECTION"
                game.menu_index = 0
        elif hasattr(event, 'unicode') and (event.unicode.isalnum() or event.key == pygame.K_SPACE):
            if len(game.character_name) < 15:
                game.character_name += event.unicode
                
    elif game.state == "DIFFICULTY_SELECTION":
        if event.key == pygame.K_ESCAPE:
            game.state = "NAME_INPUT"
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(1, game.menu_index + 1)
        elif event.key == pygame.K_RETURN:
            dificultad = "facil" if game.menu_index == 0 else "normal"
            game.start_game("aventurero", game.character_name.strip(), dificultad)
            
    elif game.state == "SAVE_SELECTION":
        options = []
        if len(game.save_files) < 5:
            options.append("NUEVO GUARDADO")
        for f in game.save_files:
            options.append(f"Sobrescribir: {f}")
        if getattr(game, 'save_return_state', 'QUIT') in ['QUIT', 'TITLE_SCREEN']:
            options.append("SALIR SIN GUARDAR")
        options.append("CANCELAR")
        
        options_count = len(options)
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            game.menu_index = max(0, game.menu_index - 1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            game.menu_index = min(options_count - 1, game.menu_index + 1)
        elif event.key == pygame.K_ESCAPE:
            if getattr(game, 'save_return_state', 'QUIT') in ['QUIT', 'TITLE_SCREEN']:
                game.state = "CONFIRM_EXIT"
            else:
                game.state = game.save_return_state
            game.menu_index = 0
        elif event.key == pygame.K_RETURN:
            selected_option = options[game.menu_index]
            ret_target = getattr(game, 'save_return_state', 'QUIT')
            if selected_option == "NUEVO GUARDADO":
                if ret_target == 'QUIT':
                    game.quit_game(None)
                elif ret_target == 'TITLE_SCREEN':
                    SaveManager.save_game(game, None)
                    game.return_to_title_screen()
                else:
                    save_success = SaveManager.save_game(game, None)
                    if save_success:
                        game.log.add_message("[SISTEMA] Partida guardada en nuevo archivo.")
                        from settings import GREEN
                        import core.combat as combat
                        combat.spawn_floating_text(game, "¡Partida Guardada!", game.player.rect.centerx, game.player.rect.top - 20, GREEN)
                    else:
                        game.log.add_message("[SISTEMA] No se pudo guardar la partida.")
                    game.state = game.save_return_state
            elif selected_option.startswith("Sobrescribir: "):
                filename = selected_option[len("Sobrescribir: "):]
                if ret_target == 'QUIT':
                    game.quit_game(filename)
                elif ret_target == 'TITLE_SCREEN':
                    SaveManager.save_game(game, filename)
                    game.return_to_title_screen()
                else:
                    save_success = SaveManager.save_game(game, filename)
                    if save_success:
                        game.log.add_message(f"[SISTEMA] Partida sobrescrita en {filename}.")
                        from settings import GREEN
                        import core.combat as combat
                        combat.spawn_floating_text(game, "¡Partida Sobrescrita!", game.player.rect.centerx, game.player.rect.top - 20, GREEN)
                    else:
                        game.log.add_message("[SISTEMA] No se pudo guardar la partida.")
                    game.state = game.save_return_state
            elif selected_option == "SALIR SIN GUARDAR":
                if ret_target == 'TITLE_SCREEN':
                    game.return_to_title_screen()
                else:
                    pygame.quit()
                    sys.exit()
            elif selected_option == "CANCELAR":
                if ret_target in ['QUIT', 'TITLE_SCREEN']:
                    game.state = "CONFIRM_EXIT"
                else:
                    game.state = game.save_return_state
                game.menu_index = 0
        elif event.key == pygame.K_d or event.key == pygame.K_DELETE:
            selected_option = options[game.menu_index]
            if selected_option.startswith("Sobrescribir: "):
                filename = selected_option[len("Sobrescribir: "):]
                filepath = os.path.join("saves", filename)
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        game.save_files = SaveManager.get_save_files()
                        game.menu_index = 0
                except Exception as e:
                    print("Error al borrar guardado:", e)
