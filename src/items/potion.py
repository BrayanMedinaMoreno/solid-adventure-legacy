class Pocion:
    def __init__(self, tipo="media"):
        self.tipo = tipo # "pequeña", "media", "grande"
        if tipo == "pequeña":
            self.nombre = "Pocion Pequeña"
            self.porcentaje = 0.20
            self.descripcion = "Recupera el 20% de tu salud máxima."
        elif tipo == "grande":
            self.nombre = "Pocion Grande"
            self.porcentaje = 1.0
            self.descripcion = "Recupera TODA tu salud máxima."
        else:
            self.nombre = "Pocion Media"
            self.porcentaje = 0.50
            self.descripcion = "Recupera el 50% de tu salud máxima."

    def usar(self, personaje, log):
        curacion = int(personaje.max_vida * self.porcentaje)
        personaje.curar(curacion)
        log.add_message(f"[TÚ] Usas {self.nombre} (+{curacion} HP)")

class PocionRegreso:
    def __init__(self):
        self.nombre = "Pocion de Regreso"
        self.descripcion = "Te teletransporta al pueblo. Pierdes 10% XP."

    def usar(self, personaje, log):
        # Penalidad del 10% de la XP actual
        penalidad = int(personaje.xp * 0.10)
        personaje.xp -= penalidad
        log.add_message(f"[TÚ] Usas {self.nombre}. (-{penalidad} XP)")
        log.add_message("[SISTEMA] Teletransportado al Pueblo.")
        
        # Activar teletransporte en el juego
        personaje.game.profundidad = 0
        personaje.game.load_level()
