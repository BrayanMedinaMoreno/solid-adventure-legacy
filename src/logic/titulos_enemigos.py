# src/logic/titulos_enemigos.py
import random
from settings import *

def slime_boss_recibir_daño(enemy, dmg, tipo="fisico"):
    # 10% probabilidad de esquivar cualquier cosa
    # Pero si es MAGICO, esquiva un 20%
    prob = 0.10
    if tipo == "magico": prob = 0.20
    
    if random.random() < prob:
        enemy.game.spawn_floating_text(f"ESQUIVADO ({tipo})", enemy.rect.centerx, enemy.rect.top, CYAN)
        return False # El ataque falló

    enemy.vida -= dmg
    
    # Habilidad de Last Stand (Curarse cuando está a punto de morir)
    if enemy.vida <= 20 and not getattr(enemy, 'last_stand_used', False):
        enemy.vida = enemy.max_vida // 2
        enemy.last_stand_used = True
        enemy.game.log.add_message(f"[TITULO: {enemy.titulo}] ¡SE REGENERA!")
        enemy.game.spawn_floating_text("LAST STAND", enemy.rect.centerx, enemy.rect.centery, GREEN)

    if enemy.vida < 0: enemy.vida = 0
    return True

def slime_boss_act(enemy):
    # 5% probabilidad de curarse 50% de la vida en su turno
    if random.random() < 0.05:
        curacion = enemy.max_vida // 2
        enemy.vida = min(enemy.max_vida, enemy.vida + curacion)
        enemy.game.log.add_message(f"[TITULO: {enemy.titulo}] Absorbe esencia (+50% HP)")
        enemy.game.spawn_floating_text(f"+{curacion}", enemy.rect.centerx, enemy.rect.top, GREEN)


def acolito_recibir_dano(enemy, dmg, tipo="fisico"):
    # Recibe la mitad del daño
    dano_real = max(1, dmg // 2)
    enemy.vida -= dano_real
    if enemy.vida < 0: enemy.vida = 0
    return True

def guardia_spawn(enemy):
    enemy.max_vida *= 2
    enemy.vida = enemy.max_vida
    enemy.fuerza = int(enemy.fuerza * 1.2)

def arquitecto_act(enemy):
    import random
    buff_turns = getattr(enemy, 'arquitecto_buff', 0)
    if buff_turns == 0:
        if random.random() < 0.25: # 25% prob
            enemy.defensa += 5
            enemy.arquitecto_buff = 3
            enemy.game.log.add_message(f"[TITULO: {enemy.titulo}] Muros de piedra (+5 DEF)")
            enemy.game.spawn_floating_text("+DEFENSA", enemy.rect.centerx, enemy.rect.top, (150, 150, 150))
    else:
        enemy.arquitecto_buff -= 1
        if enemy.arquitecto_buff <= 0:
            enemy.defensa -= 5
            enemy.arquitecto_buff = 0
            enemy.game.log.add_message(f"[TITULO: {enemy.titulo}] El muro cae (-5 DEF)")

TITULOS_ENEMIGOS = {
    "Soberano de la Viscosidad": {
        "descripcion": "El Rey de todos los slimes. Posee regeneración y esquiva.",
        "on_recibir_daño": slime_boss_recibir_daño,
        "on_turno": slime_boss_act
    },
    "Acolito de la Viscosidad": {
        "descripcion": "Sirviente leal del Rey. Mitiga el 50% de todo el daño recibido.",
        "on_recibir_daño": acolito_recibir_dano
    },
    "Guardia Real": {
        "descripcion": "Protector élite del Rey. Tiene vida duplicada y daño aumentado.",
        "on_spawn": guardia_spawn
    },
    "Cazador Nocturno": {
        "descripcion": "Aumenta la fuerza en la oscuridad.",
        "on_spawn": lambda enemy: setattr(enemy, 'fuerza', enemy.fuerza + 5)
    },
    "El Arquitecto de la mazmorra": {
        "descripcion": "Probabilidad del 25% de alzar un muro que otorga +5 de Defensa por 3 turnos.",
        "on_turno": arquitecto_act
    }
}
