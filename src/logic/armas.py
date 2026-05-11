class Arma:
    def __init__(self, nombre, daño, tipo_daño="fisico"):
        self.nombre = nombre
        self.daño = daño
        self.tipo_daño = tipo_daño # "fisico" (melee) o "distancia" (proyectiles)
        
        tipo_str = "[MELEE]" if tipo_daño == "fisico" else "[DISTANCIA]"
        self.descripcion = f"{tipo_str} Un arma de ataque. Daño base: {daño}."

    def calcular_daño(self, fuerza):
        return self.daño + fuerza

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "daño": self.daño,
            "tipo_daño": self.tipo_daño
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nombre"], data["daño"], data.get("tipo_daño", "fisico"))

    def __str__(self):
        return f"{self.nombre} ({self.tipo_daño.upper()}: {self.daño})"
