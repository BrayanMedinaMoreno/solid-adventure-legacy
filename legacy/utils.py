# utils.py
def mostrar_menu_acciones(acciones):
    print("Acciones disponibles:")
    for idx, accion in enumerate(acciones, 1):
        print(f"  {idx}. {accion}")

    while True:
        try:
            opcion = int(input("Elige una acción: "))
            if 1 <= opcion <= len(acciones):
                return opcion
            else:
                print("Elige una opción válida.")
        except ValueError:
            print("Por favor, ingresa un número válido.")
