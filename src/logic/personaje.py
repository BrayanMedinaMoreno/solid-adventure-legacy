# src/logic/personaje.py
from logic.armas import Arma

class Personaje:
    def __init__(self, nombre, fuerza, fe, defensa, vida):
        self.nombre = nombre
        self.fuerza = fuerza
        self.fe = fe
        self.defensa = defensa
        self.vida = vida
        self.max_vida = vida
        self.nivel = 1
        self.xp = 0
        self.xp_necesaria = 100
        
        # Sistema de Dinero
        self.cobre = 0
        self.plata = 0
        self.oro = 0
        self.platino = 0
        self.banco_cobre = 0
        self.banco_plata = 0
        self.banco_oro = 0
        self.banco_platino = 0  

    def vivo(self):
        return self.vida > 0

    def morir(self, log=None):
        self.vida = 0
        if log:
            log.add_message(f"[SISTEMA] {self.nombre} se fue con diocito")

    def daño(self, oponente):
        ataque_total = self.fuerza - oponente.defensa
        if ataque_total <= 0:
            return 0
        return ataque_total

    def atacar(self, oponente, log):
        dmg = self.daño(oponente)
        oponente.vida -= dmg
        log.add_message(f"[{self.nombre}] Ataca -> {dmg} DMG")
        if not oponente.vivo():
            oponente.morir(log)

    def curar(self, cantidad):
        self.vida = min(self.max_vida, self.vida + cantidad)

    def subir_de_nivel(self, fuerza, fe, defensa, log=None):
        self.fuerza += fuerza
        self.fe += fe
        self.defensa += defensa
        self.max_vida += 20
        self.vida = self.max_vida
        self.nivel += 1
        self.xp_necesaria = int(self.xp_necesaria * 1.5)
        if log:
            log.add_message(f"[SISTEMA] ¡NIVEL UP! Lvl {self.nivel}")

    def ganar_xp(self, cantidad, log):
        self.xp += cantidad
        log.add_message(f"[SISTEMA] +{cantidad} XP")
        while self.xp >= self.xp_necesaria:
            self.xp -= self.xp_necesaria
            self.subir_de_nivel(3, 2, 1, log)

    def añadir_monedas(self, cantidad):
        self.cobre += cantidad
        if self.cobre >= 100:
            self.plata += self.cobre // 100
            self.cobre = self.cobre % 100
        if self.plata >= 100:
            self.oro += self.plata // 100
            self.plata = self.plata % 100
        if self.oro >= 100:
            self.platino += self.oro // 100
            self.oro = self.oro % 100

    def gastar_monedas(self, cantidad_cobre):
        total_cobre = self.cobre + (self.plata * 100) + (self.oro * 10000) + (self.platino * 1000000)
        if total_cobre >= cantidad_cobre:
            total_cobre -= cantidad_cobre
            self.platino = total_cobre // 1000000
            total_cobre %= 1000000
            self.oro = total_cobre // 10000
            total_cobre %= 10000
            self.plata = total_cobre // 100
            self.cobre = total_cobre % 100
            return True
        return False

class Tirador(Personaje):
    def __init__(self, nombre, fuerza, fe, defensa, vida, arma):
        super().__init__(nombre, fuerza, fe, defensa, vida)
        self.arma = arma

    def daño(self, oponente):
        ataque_total = self.arma.calcular_daño(self.fuerza)
        if ataque_total <= oponente.defensa:
            return 0
        return ataque_total - oponente.defensa

class Guerrero(Personaje):
    def __init__(self, nombre, fuerza, fe, defensa, vida, espada):
        super().__init__(nombre, fuerza, fe, defensa, vida)
        self.espada = espada

    def daño(self, oponente):
        ataque_total = self.espada.calcular_daño(self.fuerza)
        if ataque_total <= oponente.defensa:
            return 0
        return ataque_total - oponente.defensa

