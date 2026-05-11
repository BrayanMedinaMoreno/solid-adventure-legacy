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

TITULOS_ENEMIGOS = {
    "Soberano de la Viscosidad": {
        "descripcion": "El Rey de todos los slimes. Posee regeneración y esquiva.",
        "on_recibir_daño": slime_boss_recibir_daño,
        "on_turno": slime_boss_act
    },
    "Cazador Nocturno": {
        "descripcion": "Aumenta la fuerza en la oscuridad.",
        "on_spawn": lambda enemy: setattr(enemy, 'fuerza', enemy.fuerza + 5)
    }
}
