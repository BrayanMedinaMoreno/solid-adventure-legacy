# src/logic/armaduras.py

class Armadura:
    def __init__(self, nombre, defensa, clase_permitida=None):
        self.nombre = nombre
        self.defensa = defensa
        self.clase_permitida = clase_permitida # "guerrero", "tirador" o None

    def __str__(self):
        return f"{self.nombre} (Defensa: {self.defensa})"
