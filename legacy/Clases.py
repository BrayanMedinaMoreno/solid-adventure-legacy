import random
from typing import Any

def mostrar_menu_acciones():
    print("Acciones disponibles:")
    print("  1. Atacar")
    print("  2. Subir de nivel")
    print("  3. Mostrar atributos")
    print("  4. Cambiar arma")
    
class Personaje:
    def __init__(self, nombre, fuerza, fe, defensa, vida):
        self.nombre = nombre
        self.fuerza = fuerza
        self.fe = fe
        self.defensa = defensa
        self.vida = vida

    def atributos(self):
        print(f"{self.nombre}:")
        print(f"  - Fuerza   : {self.fuerza}")
        print(f"  - Fe       : {self.fe}")
        print(f"  - Defensa  : {self.defensa}")
        print(f"  - Vida     : {self.vida}\n")

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
        if oponente.defensa > self.fuerza:
            print(">>> No hiciste daño")
            return 0  # Devuelve 0 para indicar que no se hizo daño
        elif oponente.defensa < self.fuerza:
            return self.fuerza - oponente.defensa

    def atacar(self, oponente):
        daño = self.daño(oponente)
        oponente.vida = oponente.vida - daño
        print(f">>> {self.nombre} Atacó y ha hecho {daño} puntos de daño a {oponente.nombre}")
        if oponente.vivo():
            print(f">>> La vida de {oponente.nombre} es {oponente.vida}\n")
        else:
            oponente.morir()

    def elegir_accion(self):
        print("\n>>> Acción de", self.nombre + ":")
        mostrar_menu_acciones()
        accion = input("Elige una acción (1/2/3): ")
        return accion

    def realizar_accion(self, accion, oponente):
        if accion == "1":
            self.atacar(oponente)
        elif accion == "2":
            self.subir_de_nivel(random.randint(1, 5), random.randint(1, 5), random.randint(1, 5))
        elif accion == "3":
            self.atributos()

class Tirador(Personaje):
    def __init__(self, nombre, fuerza, fe, defensa, vida, arma_de_fuego):
        super().__init__(nombre, fuerza, fe, defensa, vida)
        self.arma_de_fuego = arma_de_fuego

    def atributos(self):
        super().atributos()
        print(f"  - Arma     : {self.arma_de_fuego}\n")

    def daño(self, oponente):
        ataque_total = self.calcular_ataque_total(oponente)
        if ataque_total < oponente.defensa:
            print(">>> No hiciste daño")
            return 0  # Devuelve 0 para indicar que no se hizo daño
        elif ataque_total > oponente.defensa:
            return ataque_total - oponente.defensa

    def calcular_ataque_total(self, oponente):
        return self.fuerza + self.arma_de_fuego

    def elegir_accion(self):
        accion = super().elegir_accion()
        return accion

    def realizar_accion(self, accion, oponente):
        if accion == "4":
            self.cambiar_arma()
        else:
            super().realizar_accion(accion, oponente)

    def cambiar_arma(self):
        self.arma_de_fuego = random.randint(10, 30) * 2
        print(f">>> Has cambiado tu arma. Nuevo daño: {self.arma_de_fuego}\n")


class Guerrero(Personaje):
    def __init__(self, nombre, fuerza, fe, defensa, vida,espada):
        super().__init__(nombre, fuerza, fe, defensa, vida)
        self.espada = espada
    pass

def combate_interactivo(player_1, player_2):
    turno = 1
    while player_1.vivo() and player_2.vivo():
        print(f"\n>>> Turno {turno}")

        print(f">>> Acción de {player_1.nombre}:")
        accion_1 = player_1.elegir_accion()
        player_1.realizar_accion(accion_1, player_2)

        print(f">>> Acción de {player_2.nombre}:")
        accion_2 = player_2.elegir_accion()
        player_2.realizar_accion(accion_2, player_1)

        turno += 1

    if player_1.vivo():
        print(f"\nHa ganado {player_1.nombre}\n")
    elif player_2.vivo():
        print(f"\nHa ganado {player_2.nombre}\n")
    else:
        print("\nEmpate\n")

# Crear instancias de las clases
Akari = Tirador("Akari", 8, 0, 10, 100, 0)
sebas_low_elo = Personaje("Sebas", 30, 1, 30, 100)

# Iniciar combate interactivo
combate_interactivo(Akari, sebas_low_elo)

"""
print("\nEstadisticas iniciales")
sebas_low_elo.atributos()
print("\nAtacando..")
Akari.atacar(sebas_low_elo)
print("\nEstadisticas finales")
sebas_low_elo.atributos()


Moises = Personaje ("MoisesPH",30,100,30,100)
minita = Personaje("feminismo",20,0,12,100)
combate(minita,Moises)
"""


"""
mi_personaje = Personaje("Akari", 1000,1,5,100)
sebas_low_elo = Personaje("Sebas",30,1,30,100)
mi_personaje.atacar(sebas_low_elo)
sebas_low_elo.atributos()
"""
#print(mi_personaje.daño(sebas_low_elo))
#sebas_low_elo.atributos()
#mi_personaje.atributos()
#mi_personaje.morir()
#mi_personaje.atributos()
#mi_personaje.subir_de_nivel(10,2,5)
#print("el nombre del persona es", mi_personaje.nombre)
#print("La fuerza del personaje es", mi_personaje.fuerza)
        