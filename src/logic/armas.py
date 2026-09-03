class Arma:
    def __init__(self, nombre, daño, tipo_daño="fisico", sprite_path=None):
        self.nombre = nombre
        self.daño = daño
        self.tipo_daño = tipo_daño # "fisico" (melee) o "distancia" (proyectiles)
        self.sprite_path = sprite_path or self.determinar_sprite()
        
        tipo_str = "[MELEE]" if tipo_daño == "fisico" else "[DISTANCIA]"
        self.descripcion = f"{tipo_str} Un arma de ataque. Daño base: {daño}."

    def determinar_sprite(self):
        n_lower = self.nombre.lower()
        if "hacha" in n_lower:
            return "assets/sprites/hacha_32x32.png"
        elif "oxidada" in n_lower:
            return "assets/sprites/espada_oxidada.png"
        elif self.tipo_daño == "fisico" or "espada" in n_lower:
            return "assets/sprites/espada_1.png"
        return None

    def calcular_daño(self, fuerza):
        return self.daño + fuerza

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "daño": self.daño,
            "tipo_daño": self.tipo_daño,
            "sprite_path": self.sprite_path
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nombre"], data["daño"], data.get("tipo_daño", "fisico"), data.get("sprite_path"))

    def __str__(self):
        return f"{self.nombre} ({self.tipo_daño.upper()}: {self.daño})"
