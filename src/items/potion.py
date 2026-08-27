class Pocion:
    def __init__(self, tipo="media"):
        self.cantidad = 1
        self.tipo = tipo # "pequeña", "media", "grande"
        if tipo == "pequeña":
            self.nombre = "Pocion Pequeña"
            self.porcentaje = 0.20
            self.descripcion = "[CONSUMIBLE] Recupera el 20% de tu salud máxima."
        elif tipo == "grande":
            self.nombre = "Pocion Grande"
            self.porcentaje = 1.0
            self.descripcion = "[CONSUMIBLE] Recupera TODA tu salud máxima."
        else:
            self.nombre = "Pocion Media"
            self.porcentaje = 0.50
            self.descripcion = "[CONSUMIBLE] Recupera el 50% de tu salud máxima."

    def usar(self, personaje, log):
        curacion = int(personaje.max_vida * self.porcentaje)
        personaje.curar(curacion)
        log.add_message(f"[TÚ] Usas {self.nombre} (+{curacion} HP)")

    def to_dict(self):
        return {
            "type": "Pocion",
            "tipo": self.tipo,
            "cantidad": self.cantidad
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data["tipo"])
        p.cantidad = data["cantidad"]
        return p

class PocionRegreso:
    def __init__(self):
        self.cantidad = 1
        self.nombre = "Pocion de Regreso"
        self.descripcion = "[CONSUMIBLE] Te teletransporta al pueblo de forma segura. No tiene penalizaciones."

    def usar(self, personaje, log):
        log.add_message(f"[TÚ] Usas {self.nombre}. Teletransportado al Pueblo.")
        
        # Activar teletransporte en el juego
        personaje.game.profundidad = 0
        personaje.game.load_level()

    def to_dict(self):
        return {
            "type": "PocionRegreso",
            "cantidad": self.cantidad
        }

    @classmethod
    def from_dict(cls, data):
        p = cls()
        p.cantidad = data["cantidad"]
        return p

class PocionMana:
    def __init__(self, tipo="media"):
        self.cantidad = 1
        self.tipo = tipo # "pequeña", "media", "grande"
        if tipo == "pequeña":
            self.nombre = "Pocion Maná Pequeña"
            self.porcentaje = 0.20
            self.descripcion = "[CONSUMIBLE] Recupera el 20% de tu maná máximo."
        elif tipo == "grande":
            self.nombre = "Pocion Maná Grande"
            self.porcentaje = 1.0
            self.descripcion = "[CONSUMIBLE] Recupera TODO tu maná máximo."
        else:
            self.nombre = "Pocion Maná Media"
            self.porcentaje = 0.50
            self.descripcion = "[CONSUMIBLE] Recupera el 50% de tu maná máximo."

    def usar(self, personaje, log):
        restauracion = int(personaje.max_mana * self.porcentaje)
        personaje.restaurar_mana(restauracion)
        log.add_message(f"[TÚ] Usas {self.nombre} (+{restauracion} MP)")

    def to_dict(self):
        return {
            "type": "PocionMana",
            "tipo": self.tipo,
            "cantidad": self.cantidad
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data["tipo"])
        p.cantidad = data["cantidad"]
        return p

class LibroMagia:
    def __init__(self):
        self.cantidad = 1
        self.nombre = "Grimorio de Aprendiz"
        self.descripcion = "[CONSUMIBLE] Despierta tu afinidad con la magia. Desbloquea Ataque Mágico."

    def usar(self, personaje, log):
        if getattr(personaje, 'magia_desbloqueada', False):
            log.add_message("[TÚ] Ya conoces los secretos de este libro.")
        else:
            personaje.magia_desbloqueada = True
            log.add_message("[TÚ] Lees el grimorio. La magia fluye en ti.")
            personaje.verificar_titulos(log)

    def to_dict(self):
        return {
            "type": "LibroMagia",
            "cantidad": self.cantidad
        }

    @classmethod
    def from_dict(cls, data):
        p = cls()
        p.cantidad = data["cantidad"]
        return p
