class Pocion:
    def __init__(self, tipo="media"):
        self.tipo = tipo # "pequeña", "media", "grande"
        if tipo == "pequeña":
            self.nombre = "Pocion Pequeña (20%)"
            self.porcentaje = 0.20
        elif tipo == "grande":
            self.nombre = "Pocion Grande (100%)"
            self.porcentaje = 1.0
        else:
            self.nombre = "Pocion Media (50%)"
            self.porcentaje = 0.50

    def usar(self, personaje, log):
        curacion = int(personaje.max_vida * self.porcentaje)
        personaje.curar(curacion)
        log.add_message(f"[TÚ] Usas {self.nombre} (+{curacion} HP)")

class PocionRegreso:
    def __init__(self):
        self.nombre = "Pocion de Regreso"

    def usar(self, personaje, log):
        # Penalidad del 10% de la XP actual
        penalidad = int(personaje.xp * 0.10)
        personaje.xp -= penalidad
        log.add_message(f"[TÚ] Usas {self.nombre}. (-{penalidad} XP)")
        log.add_message("[SISTEMA] Teletransportado al Pueblo.")
        
        # Activar teletransporte en el juego
        personaje.game.profundidad = 0
        personaje.game.load_level()
