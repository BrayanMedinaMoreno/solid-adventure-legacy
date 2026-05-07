from armas import Arma
from utils import mostrar_menu_acciones
import random

class Personaje:
    def __init__(self, nombre, fuerza, fe, defensa, vida):
        self.nombre = nombre
        self.fuerza = fuerza
        self.fe = fe
        self.defensa = defensa
        self.vida = vida

    def __str__(self):
        return f"{self.nombre}: Fuerza: {self.fuerza}, Fe: {self.fe}, Defensa: {self.defensa}, Vida: {self.vida}"

    def subir_de_nivel(self, fuerza, fe, defensa):
        self.fuerza += fuerza
        self.fe += fe
        self.defensa += defensa

    def vivo(self):
        return self.vida > 0

    def morir(self):
        self.vida = 0
        print(f">>> {self.nombre} Se fue con diocito\n")

    def daño(self, oponente):
        ataque_total = self.fuerza - oponente.defensa
        if ataque_total <= 0:
            print(">>> No hiciste daño")
            return 0
        return ataque_total

    def atacar(self, oponente):
        daño = self.daño(oponente)
        oponente.vida -= daño
        print(f">>> {self.nombre} Atacó e hizo {daño} puntos de daño a {oponente.nombre}")
        if not oponente.vivo():
            oponente.morir()

    def elegir_accion(self):
        print(f"\n>>> Turno de {self.nombre}")
        acciones = ["Atacar", "Subir de nivel", "Mostrar atributos"]
        return mostrar_menu_acciones(acciones)

    def realizar_accion(self, accion, oponente):
        if accion == 1:
            self.atacar(oponente)
        elif accion == 2:
            self.subir_de_nivel(3, 2, 1)
            print(f"{self.nombre} ha subido de nivel.")
        elif accion == 3:
            print(self)
        else:
            print("Acción no válida.")

class Tirador(Personaje):
    def __init__(self, nombre, fuerza, fe, defensa, vida, arma):
        super().__init__(nombre, fuerza, fe, defensa, vida)
        self.arma = arma

    def __str__(self):
        # Mostrar los atributos del tirador y su arma
        return super().__str__() + f", Arma: {self.arma.nombre} (daño: {self.arma.daño})"

    def daño(self, oponente):
        ataque_total = self.arma.calcular_daño(self.fuerza)
        if ataque_total <= oponente.defensa:
            print(">>> No hiciste daño")
            return 0
        return ataque_total - oponente.defensa

    def elegir_accion(self):
        print(f"\n>>> Turno de {self.nombre}")
        acciones = ["Atacar", "Subir de nivel", "Mostrar atributos", "Cambiar arma"]
        return mostrar_menu_acciones(acciones)

    def realizar_accion(self, accion, oponente):
        if accion == 4:
            self.cambiar_arma()
        else:
            super().realizar_accion(accion, oponente)

    def cambiar_arma(self):
        # Cambiar el arma del tirador
        self.arma = Arma("Nueva Arma", random.randint(10, 30) * 2)
        print(f">>> {self.nombre} ha cambiado de arma. Nuevo arma: {self.arma}")

class Guerrero(Personaje):
    def __init__(self, nombre, fuerza, fe, defensa, vida, espada):
        super().__init__(nombre, fuerza, fe, defensa, vida)
        self.espada = espada

    def __str__(self):
        # Mostrar los atributos del guerrero y su espada
        return super().__str__() + f", Espada: {self.espada.nombre} (daño: {self.espada.daño})"

    def daño(self, oponente):
        ataque_total = self.espada.calcular_daño(self.fuerza)
        if ataque_total <= oponente.defensa:
            print(">>> No hiciste daño")
            return 0
        return ataque_total - oponente.defensa

    def elegir_accion(self):
        print(f"\n>>> Turno de {self.nombre}")
        acciones = ["Atacar", "Subir de nivel", "Mostrar atributos"]
        return mostrar_menu_acciones(acciones)
