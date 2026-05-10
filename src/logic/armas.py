# src/logic/armas.py

class Arma:
    def __init__(self, nombre, daño, clase_permitida=None):
        self.nombre = nombre
        self.daño = daño
        self.clase_permitida = clase_permitida # "guerrero", "tirador" o None
        self.descripcion = f"Un arma de {clase_permitida if clase_permitida else 'cualquier clase'}. Daño base: {daño}."

    def calcular_daño(self, fuerza):
        return self.daño + fuerza

    def __str__(self):
        return f"{self.nombre} (Daño: {self.daño})"
