# src/logic/titulos_enemigos.py
import random
from settings import *

# --- TÍTULOS DEL REY SLIME (SEPARADOS) ---
def cuerpo_escurridizo_pre_dano(enemy, dmg, tipo="fisico"):
    prob = 0.10
    if tipo == "magico": prob = 0.20
    
    if random.random() < prob:
        enemy.game.spawn_floating_text(f"ESQUIVADO ({tipo})", enemy.rect.centerx, enemy.rect.top, CYAN)
        return False # Falló
    return dmg # Pasa el daño sin modificar

def nucleo_persistente_post_dano(enemy):
    if enemy.vida <= 20 and enemy.vida > 0 and not getattr(enemy, 'last_stand_used', False):
        enemy.vida = enemy.max_vida // 2
        enemy.last_stand_used = True
        enemy.game.log.add_message(f"[NÚCLEO] ¡El Rey Slime sobrevive y se regenera!")
        enemy.game.spawn_floating_text("LAST STAND", enemy.rect.centerx, enemy.rect.centery, GREEN)

def soberano_viscosidad_act(enemy):
    if random.random() < 0.05:
        curacion = enemy.max_vida // 2
        enemy.vida = min(enemy.max_vida, enemy.vida + curacion)
        enemy.game.log.add_message(f"[SOBERANO] Absorbe esencia (+50% HP)")
        enemy.game.spawn_floating_text(f"+{curacion}", enemy.rect.centerx, enemy.rect.top, GREEN)

# --- OTROS TÍTULOS ---
def acolito_pre_dano(enemy, dmg, tipo="fisico"):
    dano_real = max(1, dmg // 2)
    return dano_real

def guardia_spawn(enemy):
    enemy.max_vida *= 2
    enemy.vida = enemy.max_vida
    enemy.fuerza = int(enemy.fuerza * 1.2)

def arquitecto_act(enemy):
    buff_turns = getattr(enemy, 'arquitecto_buff', 0)
    if buff_turns == 0:
        if random.random() < 0.25:
            enemy.defensa += 5
            enemy.arquitecto_buff = 3
            enemy.game.log.add_message(f"[ARQUITECTO] Muros de piedra (+5 DEF)")
            enemy.game.spawn_floating_text("+DEFENSA", enemy.rect.centerx, enemy.rect.top, (150, 150, 150))
    else:
        enemy.arquitecto_buff -= 1
        if enemy.arquitecto_buff <= 0:
            enemy.defensa -= 5
            enemy.arquitecto_buff = 0
            enemy.game.log.add_message(f"[ARQUITECTO] El muro cae (-5 DEF)")

TITULOS_ENEMIGOS = {
    "Cuerpo Escurridizo": {
        "descripcion": "10% probabilidad de esquivar ataques, 20% mágicos.",
        "on_recibir_daño": cuerpo_escurridizo_pre_dano
    },
    "Núcleo Persistente": {
        "descripcion": "Si baja a 20 de HP, se cura 50% (1 vez).",
        "on_post_daño": nucleo_persistente_post_dano
    },
    "Soberano de la Viscosidad": {
        "descripcion": "5% de probabilidad por turno de curarse 50% HP.",
        "on_turno": soberano_viscosidad_act
    },
    "Acolito de la Viscosidad": {
        "descripcion": "Mitiga el 50% de todo el daño recibido.",
        "on_recibir_daño": acolito_pre_dano
    },
    "Guardia Real": {
        "descripcion": "Vida duplicada y fuerza aumentada.",
        "on_spawn": guardia_spawn
    },
    "Cazador Nocturno": {
        "descripcion": "Aumenta la fuerza en la oscuridad.",
        "on_spawn": lambda enemy: setattr(enemy, 'fuerza', enemy.fuerza + 5)
    },
    "El Arquitecto de la mazmorra": {
        "descripcion": "Probabilidad de alzar un muro (+5 Def por 3 turnos).",
        "on_turno": arquitecto_act
    }
}
