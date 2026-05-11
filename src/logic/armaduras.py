# src/logic/armaduras.py

class Armadura:
    def __init__(self, nombre, defensa, clase_permitida=None):
        self.nombre = nombre
        self.defensa = defensa
        self.clase_permitida = clase_permitida # "guerrero", "tirador" o None
        clase_str = f"[{clase_permitida.upper()}]" if clase_permitida else "[TODAS LAS CLASES]"
        self.descripcion = f"{clase_str} Protección defensiva. Defensa: {defensa}."

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "defensa": self.defensa,
            "clase_permitida": self.clase_permitida
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nombre"], data["defensa"], data["clase_permitida"])

    def __str__(self):
        return f"{self.nombre} (Defensa: {self.defensa})"
