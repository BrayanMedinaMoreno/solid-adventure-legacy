
class Pocion:
    def __init__(self, nombre="Poción de Vida", curacion=30):
        self.nombre = nombre
        self.curacion = curacion

    def usar(self, personaje, log):
        personaje.curar(self.curacion)
        log.add_message(f"[TÚ] Usas {self.nombre} (+{self.curacion} HP)")
