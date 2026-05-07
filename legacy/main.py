from personaje import Tirador, Guerrero
from armas import Arma
from utils import mostrar_menu_acciones

def crear_personaje():
    # Pedir nombre del jugador
    nombre = input("Introduce el nombre de tu personaje: ")

    # Menú de selección de clase
    print("Elige una clase:")
    print("  1. Tirador")
    print("  2. Guerrero")
    clase = input("Selecciona una clase (1/2): ")

    if clase == "1":
        # Crear un Tirador con un arma inicial
        arma = Arma("Pistola", 20)
        personaje = Tirador(nombre, 8, 0, 10, 100, arma)
    elif clase == "2":
        # Crear un Guerrero con un arma inicial
        espada = Arma("Espada", 25)
        personaje = Guerrero(nombre, 10, 0, 15, 120, espada)
    else:
        print("Opción no válida. Se creará un Guerrero por defecto.")
        espada = Arma("Espada", 25)
        personaje = Guerrero(nombre, 10, 0, 15, 120, espada)

    return personaje

def combate_interactivo(player_1, player_2):
    turno = 1
    while player_1.vivo() and player_2.vivo():
        print(f"\n>>> Turno {turno}")

        # Turno del Jugador 1
        print(f">>> Turno de {player_1.nombre}")
        accion_1 = player_1.elegir_accion()
        player_1.realizar_accion(accion_1, player_2)

        # Mostrar puntos de vida después del turno del Jugador 1
        print(f">>> {player_1.nombre} tiene {player_1.vida} puntos de vida.")
        print(f">>> {player_2.nombre} tiene {player_2.vida} puntos de vida.\n")

        if not player_2.vivo():
            break

        # Turno del Jugador 2
        print(f">>> Turno de {player_2.nombre}")
        accion_2 = player_2.elegir_accion()
        player_2.realizar_accion(accion_2, player_1)

        # Mostrar puntos de vida después del turno del Jugador 2
        print(f">>> {player_1.nombre} tiene {player_1.vida} puntos de vida.")
        print(f">>> {player_2.nombre} tiene {player_2.vida} puntos de vida.\n")

        turno += 1

    # Determinar el ganador
    if player_1.vivo():
        print(f"\n>>> {player_1.nombre} ha ganado el combate!\n")
    elif player_2.vivo():
        print(f"\n>>> {player_2.nombre} ha ganado el combate!\n")
    else:
        print("\n>>> ¡Es un empate!\n")

if __name__ == "__main__":
    print("Creación del Jugador 1:")
    player_1 = crear_personaje()

    print("\nCreación del Jugador 2:")
    player_2 = crear_personaje()

    combate_interactivo(player_1, player_2)
