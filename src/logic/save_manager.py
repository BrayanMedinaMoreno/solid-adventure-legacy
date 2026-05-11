# src/logic/save_manager.py
import json
import os
import datetime
from logic.armas import Arma
from logic.armaduras import Armadura
from items.potion import Pocion, PocionRegreso

SAVE_DIR = "saves"

class SaveManager:
    @staticmethod
    def ensure_save_dir():
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    @staticmethod
    def get_save_files():
        SaveManager.ensure_save_dir()
        files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        # Sort by modification time, newest first
        files.sort(key=lambda x: os.path.getmtime(os.path.join(SAVE_DIR, x)), reverse=True)
        return files

    @staticmethod
    def save_game(game, filename=None):
        SaveManager.ensure_save_dir()
        if game.profundidad != 0:
            return False # Solo se guarda en el pueblo

        if not filename:
            # Generar un nombre por defecto si no se proporciona
            nombre_limpio = "".join(x for x in game.player.logic.nombre if x.isalnum())
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{nombre_limpio}_{timestamp}.json"
        
        if not filename.endswith(".json"):
            filename += ".json"

        data = {
            "max_profundidad": game.max_profundidad,
            "player_logic": game.player.logic.to_dict(),
            "inventory": []
        }

        # Serializar inventario del jugador
        for item in game.player.inventory:
            if hasattr(item, "to_dict"):
                item_data = item.to_dict()
                if "type" not in item_data:
                    item_data["type"] = item.__class__.__name__
                data["inventory"].append(item_data)

        try:
            filepath = os.path.join(SAVE_DIR, filename)
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False

    @staticmethod
    def load_game(filename):
        filepath = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar: {e}")
            return None

    @staticmethod
    def reconstruct_item(item_data):
        item_type = item_data.get("type")
        if item_type == "Arma":
            return Arma.from_dict(item_data)
        elif item_type == "Armadura":
            return Armadura.from_dict(item_data)
        elif item_type == "Pocion":
            return Pocion.from_dict(item_data)
        elif item_type == "PocionRegreso":
            return PocionRegreso.from_dict(item_data)
        return None

