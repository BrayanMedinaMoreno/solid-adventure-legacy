# src/logic/armaduras.py

class Armadura:
    def __init__(self, nombre, defensa, slot="pechera", clase_permitida=None, durabilidad=None, max_durabilidad=None):
        import random
        self.nombre = nombre
        self.defensa = defensa
        self.slot = slot
        self.clase_permitida = clase_permitida
        clase_str = f"[{clase_permitida.upper()}]" if clase_permitida else "[TODAS LAS CLASES]"
        self.max_durabilidad = max_durabilidad if max_durabilidad is not None else random.randint(150, 300)
        self.durabilidad = durabilidad if durabilidad is not None else self.max_durabilidad
        self.descripcion = f"{clase_str} Proteccion defensiva. Defensa: {defensa}."

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "defensa": self.defensa,
            "slot": self.slot,
            "clase_permitida": self.clase_permitida,
            "durabilidad": self.durabilidad,
            "max_durabilidad": self.max_durabilidad
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nombre"], data["defensa"], data.get("slot", "pechera"), data.get("clase_permitida"), data.get("durabilidad"), data.get("max_durabilidad"))

    def __str__(self):
        return f"{self.nombre} (Defensa: {self.defensa})"
