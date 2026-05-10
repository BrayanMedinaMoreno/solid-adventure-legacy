# src/logic/armaduras.py

class Armadura:
    def __init__(self, nombre, defensa, clase_permitida=None):
        self.nombre = nombre
        self.defensa = defensa
        self.clase_permitida = clase_permitida # "guerrero", "tirador" o None
        self.descripcion = f"Protección para {clase_permitida if clase_permitida else 'cualquier clase'}. Defensa: {defensa}."

    def __str__(self):
        return f"{self.nombre} (Defensa: {self.defensa})"
