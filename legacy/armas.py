class Arma:
    def __init__(self, nombre, daño):
        self.nombre = nombre
        self.daño = daño

    def calcular_daño(self, fuerza):
        return self.daño + fuerza

    def __str__(self):
        return f"{self.nombre} (daño: {self.daño})"
