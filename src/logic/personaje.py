# src/logic/personaje.py
from settings import *
from logic.armas import Arma

TITULOS_DATA = {
    "Hoja en Blanco": {
        "descripcion": "Una tabla rasa. El mundo aún no sabe quién eres.",
        "req": {},
        "bono": {}
    },
    # SENDA DEL ACERO (ESPADAS)
    "Aprendiz de Espada": {
        "descripcion": "Has empezado a entender el peso del acero. +5 Atk, +2 Daño Melee.",
        "req": {"usos_espada": 200},
        "bono": {"fuerza": 5, "daño_melee": 2}
    },
    "Espadachín de Grado III": {
        "descripcion": "Tu técnica es fluida. +15 Atk, +5 Def, +8 Daño Melee.",
        "req": {"usos_espada": 1000, "muertes_goblin": 100, "titulos": ["Aprendiz de Espada"]},
        "bono": {"fuerza": 15, "defensa": 5, "daño_melee": 8}
    },
    "Maestro de la Hoja": {
        "descripcion": "Inalcanzable con el filo. +40 Atk, +15 Def, +15 Daño Melee.",
        "req": {"usos_espada": 5000, "muertes_orco": 200, "titulos": ["Espadachín de Grado III"]},
        "bono": {"fuerza": 40, "defensa": 15, "daño_melee": 15}
    },
    # SENDA DEL OJO DE ÁGUILA (PROYECTILES)
    "Iniciado en Proyectiles": {
        "descripcion": "Tus ojos siguen la trayectoria. +6 Atk, +2 Daño Distancia.",
        "req": {"usos_proyectil": 200},
        "bono": {"fuerza": 6, "daño_distancia": 2}
    },
    "Arquero de Élite": {
        "descripcion": "Nunca fallas el blanco. +18 Atk, +8 Daño Distancia.",
        "req": {"usos_proyectil": 1000, "muertes_slime": 100, "titulos": ["Iniciado en Proyectiles"]},
        "bono": {"fuerza": 18, "daño_distancia": 8},
        "bono_pasivo_oculto": {"esquiva_basica": 0.10}
    },
    "Halcón del Abismo": {
        "descripcion": "Tus flechas cruzan dimensiones. +45 Atk, +15 Daño Distancia.",
        "req": {"usos_proyectil": 5000, "muertes_totales": 300, "titulos": ["Arquero de Élite"]},
        "bono": {"fuerza": 45, "daño_distancia": 15},
        "bono_pasivo_oculto": {"esquiva_basica": 0.20}
    },
    # SENDA DE LO ARCANO (MAGIA)
    "Aprendiz de lo Arcano": {
        "descripcion": "La chispa de la magia nace en ti. +10 Max Mana, +2 Magia.",
        "req": {"magia_desbloqueada": 1},
        "bono": {"max_mana": 10, "magia": 2}
    },
    "Mago de Batalla": {
        "descripcion": "Conjuras en medio del caos. +30 Max Mana, +8 Magia.",
        "req": {"usos_magia": 100, "titulos": ["Aprendiz de lo Arcano"]},
        "bono": {"max_mana": 30, "magia": 8}
    },
    "Archimago": {
        "descripcion": "El tejido de la realidad se dobla ante ti. +100 Max Mana, +20 Magia.",
        "req": {"usos_magia": 500, "titulos": ["Mago de Batalla"]},
        "bono": {"max_mana": 100, "magia": 20}
    },
    # SENDA DEL EXTERMINADOR (MONSTRUOS)
    "Cazador de Slimes": {
        "descripcion": "Esas masas ya no son un reto. +4 Defensa. (Req: 100 muertes)",
        "req": {"muertes_slime": 100},
        "bono": {"defensa": 4}
    },
    "Azote de Goblins": {
        "descripcion": "Los Goblins temen tu nombre. +10 Defensa, +10 Fuerza. (Req: 250 Goblins, Titulo: Cazador)",
        "req": {"muertes_goblin": 250, "titulos": ["Cazador de Slimes"]},
        "bono": {"defensa": 10, "fuerza": 10}
    },
    "Leyenda del Calabozo": {
        "descripcion": "El terror de las profundidades. +30 Defensa, +30 Fuerza, +100 Vida.",
        "req": {"muertes_totales": 10000, "titulos": ["Azote de Goblins"]},
        "bono": {"defensa": 30, "fuerza": 30, "max_vida": 100}
    },
    # SENDA DEL CONQUISTADOR (PROGRESO)
    "Aventurero del Pueblo": {
        "descripcion": "Reconocido por los lugareños. +30 Vida Máx.",
        "req": {"nivel": 10},
        "bono": {"max_vida": 30}
    },
    "Explorador del Abismo": {
        "descripcion": "Conoces cada rincón oscuro. +100 Vida, +5 Fuerza.",
        "req": {"piso_maximo": 20, "titulos": ["Aventurero del Pueblo"]},
        "bono": {"max_vida": 100, "fuerza": 5}
    },
    "Soberano de las Profundidades": {
        "descripcion": "El calabozo se inclina ante ti. +300 Vida, +20 Atk, +20 Def.",
        "req": {"nivel": 50, "cofres_abiertos": 100, "titulos": ["Explorador del Abismo"]},
        "bono": {"max_vida": 300, "fuerza": 20, "defensa": 20}
    },
    "Cuestionar": {
        "descripcion": "Has dudado de la divinidad. Tu fe flaquea pero tu mente se expande. +15 Magia, +10 Max Mana. (Req: Cuestionar creencias 5 veces)",
        "req": {"cuestionamientos": 5},
        "bono": {"magia": 15, "max_mana": 10}
    },
    # LINEA DE ESQUIVA (PASIVOS)
    "Esquiva de Novato": {
        "tipo": "pasivo",
        "descripcion": "Has aprendido a moverte entre los golpes. 2% esquiva básica.",
        "req": {"golpes_bajo_15hp": 100},
        "bono_pasivo": {"esquiva_basica": 0.02}
    },
    "Esquiva de Iniciado": {
        "tipo": "pasivo",
        "descripcion": "Tus reflejos mejoran. 4% esquiva básica, 10% trampas.",
        "req": {"golpes_bajo_25hp": 200, "esquivas_novato": 60, "titulos": ["Esquiva de Novato"]},
        "bono_pasivo": {"esquiva_basica": 0.04, "esquiva_trampa": 0.10}
    },
    "Esquiva Intermedio": {
        "tipo": "pasivo",
        "descripcion": "El peligro es predecible. 6% básica, 20% trampa, 2% otros.",
        "req": {"golpes_bajo_25hp": 200, "trampas_esquivadas": 15, "esquivas_iniciado": 60, "titulos": ["Esquiva de Iniciado"]},
        "bono_pasivo": {"esquiva_basica": 0.06, "esquiva_trampa": 0.20, "esquiva_distancia": 0.02, "esquiva_magica": 0.02, "esquiva_habilidad": 0.02}
    },
    "Esquiva de Veterano": {
        "tipo": "pasivo",
        "descripcion": "Casi intocable. 8% básica, 30% trampa, 4% otros.",
        "req": {"golpes_bajo_20hp": 200, "trampas_esquivadas": 30, "esquivas_intermedio": 80, "titulos": ["Esquiva Intermedio"]},
        "bono_pasivo": {"esquiva_basica": 0.08, "esquiva_trampa": 0.30, "esquiva_distancia": 0.04, "esquiva_magica": 0.04, "esquiva_habilidad": 0.04}
    },
    "Esquiva de Experto": {
        "tipo": "pasivo",
        "descripcion": "El aire es tu aliado. 9% básica, 35% trampa, 6% otros.",
        "req": {"golpes_bajo_18hp": 200, "trampas_esquivadas": 40, "esquivas_veterano": 80, "titulos": ["Esquiva de Veterano"]},
        "bono_pasivo": {"esquiva_basica": 0.09, "esquiva_trampa": 0.35, "esquiva_distancia": 0.06, "esquiva_magica": 0.06, "esquiva_habilidad": 0.06}
    },
    "Esquiva de Maestro": {
        "tipo": "pasivo",
        "descripcion": "Inalcanzable. 12% esquiva general absoluta.",
        "req": {"golpes_bajo_16hp": 300, "trampas_esquivadas": 50, "esquivas_experto": 80, "titulos": ["Esquiva de Experto"]},
        "bono_pasivo": {"esquiva_general": 0.12}
    },
    # LINEA DE ULTIMO ALIENTO (PASIVOS)
    "Último Aliento Novato": {
        "tipo": "pasivo",
        "descripcion": "El destino te da una segunda oportunidad. Al bajar de 10 HP, cura 30% Max HP.",
        "req": {"combates_bajo_15hp": 50},
        "bono_pasivo": {"aliento_trigger": 10, "aliento_heal": 0.30}
    },
    "Último Aliento Iniciado": {
        "tipo": "pasivo",
        "descripcion": "Tu voluntad es férrea. Al bajar de 12 HP, cura 40% Max HP.",
        "req": {"combates_bajo_20hp": 100, "aliento_activaciones_novato": 60, "titulos": ["Último Aliento Novato"]},
        "bono_pasivo": {"aliento_trigger": 12, "aliento_heal": 0.40}
    },
    "Último Aliento Intermedio": {
        "tipo": "pasivo",
        "descripcion": "La muerte te teme. Al bajar de 15 HP, cura 50% Max HP.",
        "req": {"combates_bajo_25hp": 150, "aliento_activaciones_iniciado": 60, "titulos": ["Último Aliento Iniciado"]},
        "bono_pasivo": {"aliento_trigger": 15, "aliento_heal": 0.50}
    },
    "Último Aliento Veterano": {
        "tipo": "pasivo",
        "descripcion": "Un guerrero nunca se rinde. Al bajar de 18 HP, cura 60% Max HP.",
        "req": {"combates_bajo_25hp": 200, "aliento_activaciones_intermedio": 80, "titulos": ["Último Aliento Intermedio"]},
        "bono_pasivo": {"aliento_trigger": 18, "aliento_heal": 0.60}
    },
    "Último Aliento Experto": {
        "tipo": "pasivo",
        "descripcion": "Has trascendido el umbral. Al bajar de 20 HP, cura 70% Max HP.",
        "req": {"combates_bajo_25hp": 250, "aliento_activaciones_veterano": 80, "titulos": ["Último Aliento Veterano"]},
        "bono_pasivo": {"aliento_trigger": 20, "aliento_heal": 0.70}
    },
    "Último Aliento de Maestro": {
        "tipo": "pasivo",
        "descripcion": "Inmortal en espíritu. Al bajar de 20 HP, cura 80% Max HP.",
        "req": {"combates_bajo_25hp": 350, "aliento_activaciones_experto": 100, "titulos": ["Último Aliento Experto"]},
        "bono_pasivo": {"aliento_trigger": 20, "aliento_heal": 0.80}
    },
    # LINEA DE REGENERACION (PASIVOS)
    "Regeneración Pasiva Baja": {
        "tipo": "pasivo",
        "descripcion": "Tu cuerpo sana rápido. 5% chance curar 2% Max HP por turno. +2 HP/seg.",
        "req": {"hp_regenerada_total": 2000},
        "bono_pasivo": {"regen_chance": 0.05, "regen_pct": 0.02, "regen_flat": 2}
    },
    "Regeneración Pasiva Intermedia": {
        "tipo": "pasivo",
        "descripcion": "La esencia fluye en ti. 5% chance curar 5% Max HP por turno. +4 HP/seg.",
        "req": {"hp_regenerada_total": 10000, "regen_activaciones_baja": 100, "titulos": ["Regeneración Pasiva Baja"]},
        "bono_pasivo": {"regen_chance": 0.05, "regen_pct": 0.05, "regen_flat": 4}
    },
    "Regeneración Pasiva Media": {
        "tipo": "pasivo",
        "descripcion": "Vigor inagotable. 5% chance curar 8% Max HP por turno. +6 HP/seg.",
        "req": {"hp_regenerada_total": 25000, "regen_activaciones_intermedia": 150, "titulos": ["Regeneración Pasiva Intermedia"]},
        "bono_pasivo": {"regen_chance": 0.05, "regen_pct": 0.08, "regen_flat": 6}
    },
    "Regeneración Pasiva Alta": {
        "tipo": "pasivo",
        "descripcion": "Vitalidad legendaria. 5% chance curar 12% Max HP por turno. +10 HP/seg.",
        "req": {"hp_regenerada_total": 60000, "regen_activaciones_media": 200, "titulos": ["Regeneración Pasiva Media"]},
        "bono_pasivo": {"regen_chance": 0.05, "regen_pct": 0.12, "regen_flat": 10}
    },
    "Regeneración Pasiva Superior": {
        "tipo": "pasivo",
        "descripcion": "Casi divino. 5% chance curar 50% Max HP por turno. +20 HP/seg.",
        "req": {"hp_regenerada_total": 150000, "regen_activaciones_alta": 300, "titulos": ["Regeneración Pasiva Alta"]},
        "bono_pasivo": {"regen_chance": 0.05, "regen_pct": 0.50, "regen_flat": 20}
    }
}

class Personaje:
    def __init__(self, nombre, fuerza, fe, defensa, vida, arma=None):
        self.nombre = nombre
        self.fuerza_base = fuerza
        self.fe_base = fe
        self.magia_base = 0 # Estadistica mágica
        self.defensa_base = defensa
        self.defensa_magica_base = 0
        self.vida = vida
        self.max_vida_base = vida
        
        # Sistema de Maná
        self.mana = 50
        self.max_mana_base = 50
        self.magia_desbloqueada = False
        
        # Cruz Sagrada
        self.cruz_usos_hoy = 3
        self.cruz_ultimo_dia = ""
        
        self.nivel = 1
        self.xp = 0
        self.xp_necesaria = 250
        
        # Sistema de Dinero
        self.cobre = 0
        self.plata = 0
        self.oro = 0
        self.platino = 0
        self.banco_cobre = 0
        
        self.arma = arma
        self.casco = None
        self.pechera = None
        self.botas = None
        self.accesorio = None
        self.baul = []
        
        self.cooldowns = {"habilidad": 0, "distancia": 0}
        
        # Sistema de Títulos
        self.titulo_actual = "Hoja en Blanco"
        self.titulos_desbloqueados = ["Hoja en Blanco"]
        
        # Contadores de acciones (Huella de Identidad)
        self.acciones = {
            "usos_espada": 0,
            "usos_proyectil": 0,
            "muertes_slime": 0,
            "muertes_goblin": 0,
            "muertes_orco": 0,
            "muertes_totales": 0,
            "cofres_abiertos": 0,
            "piso_maximo": 0,
            # Contadores para Esquiva
            "golpes_bajo_25hp": 0,
            "golpes_bajo_20hp": 0,
            "golpes_bajo_18hp": 0,
            "golpes_bajo_16hp": 0,
            "golpes_bajo_15hp": 0,
            "trampas_esquivadas": 0,
            "esquivas_novato": 0,
            "esquivas_iniciado": 0,
            "esquivas_intermedio": 0,
            "esquivas_veterano": 0,
            "esquivas_experto": 0,
            # Contadores para Último Aliento
            "combates_bajo_15hp": 0,
            "combates_bajo_20hp": 0,
            "combates_bajo_25hp": 0,
            "aliento_activaciones_novato": 0,
            "aliento_activaciones_iniciado": 0,
            "aliento_activaciones_intermedio": 0,
            "aliento_activaciones_veterano": 0,
            "aliento_activaciones_experto": 0,
            # Contadores para Regeneración
            "hp_regenerada_total": 0,
            "regen_activaciones_baja": 0,
            "regen_activaciones_intermedia": 0,
            "regen_activaciones_media": 0,
            "regen_activaciones_alta": 0,
            "usos_magia": 0,
            "cuestionamientos": 0
        }
        self.aliento_usado_combate = False
        self.min_porcentaje_vida_combate = 100.0
        self.regen_timer = 0 # Para regen por segundo

    @property
    def fuerza(self):
        bono = TITULOS_DATA[self.titulo_actual]["bono"].get("fuerza", 0)
        bono_acc = self.accesorio.bono_stats.get("fuerza", 0) if self.accesorio else 0
        return self.fuerza_base + bono + bono_acc

    @property
    def defensa(self):
        bono = TITULOS_DATA[self.titulo_actual]["bono"].get("defensa", 0)
        def_equipo = 0
        if self.casco: def_equipo += self.casco.defensa
        if self.pechera: def_equipo += self.pechera.defensa
        if self.botas: def_equipo += self.botas.defensa
        bono_acc = self.accesorio.bono_stats.get("defensa", 0) if self.accesorio else 0
        return self.defensa_base + bono + def_equipo + bono_acc
        
    @property
    def magia(self):
        bono = TITULOS_DATA[self.titulo_actual]["bono"].get("magia", 0)
        bono_acc = self.accesorio.bono_stats.get("magia", 0) if self.accesorio else 0
        return self.magia_base + bono + bono_acc

    @property
    def defensa_magica(self):
        bono = TITULOS_DATA[self.titulo_actual]["bono"].get("defensa_magica", 0)
        def_eq = 0
        if self.casco: def_eq += getattr(self.casco, 'defensa_magica', 0)
        if self.pechera: def_eq += getattr(self.pechera, 'defensa_magica', 0)
        if self.botas: def_eq += getattr(self.botas, 'defensa_magica', 0)
        return self.defensa_magica_base + bono + def_eq

    @property
    def max_vida(self):
        bono = TITULOS_DATA[self.titulo_actual]["bono"].get("max_vida", 0)
        bono_acc = self.accesorio.bono_stats.get("max_vida", 0) if self.accesorio else 0
        bono += bono_acc
        # Añadir bonos pasivos de títulos EQUIPADOS (como los de Arquero/Halcón)
        bono_pasivo_extra = TITULOS_DATA[self.titulo_actual].get("bono_pasivo_oculto", {})
        # ... podrías aplicar otros aquí ...
        
        # Añadir bonos pasivos reales (líneas de Esquiva/Aliento/Regen)
        for t_name in self.titulos_desbloqueados:
            data = TITULOS_DATA[t_name]
            if data.get("tipo") == "pasivo":
                bono += data.get("bono_pasivo", {}).get("max_vida", 0)
        return self.max_vida_base + bono
        
    @property
    def max_mana(self):
        bono = TITULOS_DATA[self.titulo_actual]["bono"].get("max_mana", 0)
        bono_acc = self.accesorio.bono_stats.get("max_mana", 0) if self.accesorio else 0
        return self.max_mana_base + bono + bono_acc

    def get_bono_pasivo(self, stat_name):
        total = 0
        for t_name in self.titulos_desbloqueados:
            data = TITULOS_DATA[t_name]
            if data.get("tipo") == "pasivo":
                total += data.get("bono_pasivo", {}).get(stat_name, 0)
        return total

    def vivo(self):
        return self.vida > 0

    def recibir_daño(self, dmg, tipo="fisico", log=None):
        import random
        
        # Calcular esquiva basada en pasivos
        prob_esquiva = 0
        if tipo == "fisico":
            prob_esquiva = self.get_bono_pasivo("esquiva_basica")
        elif tipo == "trampa":
            prob_esquiva = self.get_bono_pasivo("esquiva_trampa")
        elif tipo == "distancia":
            prob_esquiva = self.get_bono_pasivo("esquiva_distancia")
        elif tipo == "magico":
            prob_esquiva = self.get_bono_pasivo("esquiva_magica")
        elif tipo == "habilidad":
            prob_esquiva = self.get_bono_pasivo("esquiva_habilidad")
        
        # Esquiva general (Maestro)
        prob_esquiva += self.get_bono_pasivo("esquiva_general")
        
        # Bono especial si el título EQUIPADO tiene esquiva extra (ej: Arquero/Halcón)
        bono_equipado = TITULOS_DATA[self.titulo_actual].get("bono_pasivo_oculto", {}).get("esquiva_basica", 0)
        if tipo == "fisico" or tipo == "distancia":
            prob_esquiva += bono_equipado
        
        if random.random() < prob_esquiva:
            if log: log.add_message(f"[{self.nombre}] ¡ESQUIVADO!")
            if self.game: self.game.spawn_floating_text("ESQUIVA", self.game.player.rect.centerx, self.game.player.rect.top, (100, 255, 255))
            
            # Incrementar contadores de activación para evolución
            if "Esquiva de Novato" in self.titulos_desbloqueados: self.acciones["esquivas_novato"] += 1
            if "Esquiva de Iniciado" in self.titulos_desbloqueados: self.acciones["esquivas_iniciado"] += 1
            if "Esquiva Intermedio" in self.titulos_desbloqueados: self.acciones["esquivas_intermedio"] += 1
            if "Esquiva de Veterano" in self.titulos_desbloqueados: self.acciones["esquivas_veterano"] += 1
            if "Esquiva de Experto" in self.titulos_desbloqueados: self.acciones["esquivas_experto"] += 1
            
            if tipo == "trampa": self.acciones["trampas_esquivadas"] += 1
            
            self.verificar_titulos(log)
            return False # No recibió daño

        # Si no esquivó, aplicar daño
        self.vida -= dmg
        if self.vida < 0: self.vida = 0
        
        # Registrar golpe recibido a baja vida
        porcentaje_vida = (self.vida / self.max_vida) * 100
        self.min_porcentaje_vida_combate = min(self.min_porcentaje_vida_combate, porcentaje_vida)
        
        if porcentaje_vida < 25: self.acciones["golpes_bajo_25hp"] += 1
        if porcentaje_vida < 20: self.acciones["golpes_bajo_20hp"] += 1
        if porcentaje_vida < 18: self.acciones["golpes_bajo_18hp"] += 1
        if porcentaje_vida < 16: self.acciones["golpes_bajo_16hp"] += 1
        if porcentaje_vida < 15: self.acciones["golpes_bajo_15hp"] += 1
        
        # Lógica de ÚLTIMO ALIENTO (PASIVOS)
        if not self.aliento_usado_combate and self.vida > 0:
            # Obtener el mejor bono de aliento disponible
            mejor_trigger = self.get_max_pasivo("aliento_trigger")
            if self.vida <= mejor_trigger:
                mejor_heal_pct = self.get_max_pasivo("aliento_heal")
                curacion = int(self.max_vida * mejor_heal_pct)
                self.curar(curacion)
                self.aliento_usado_combate = True
                if log: log.add_message(f"[TITULO] ¡ÚLTIMO ALIENTO! +{curacion} HP")
                if self.game: self.game.spawn_floating_text("LAST STAND", self.game.player.rect.centerx, self.game.player.rect.top, (0, 255, 0))
                
                # Incrementar activaciones para evolución
                if "Último Aliento Novato" in self.titulos_desbloqueados: self.acciones["aliento_activaciones_novato"] += 1
                if "Último Aliento Iniciado" in self.titulos_desbloqueados: self.acciones["aliento_activaciones_iniciado"] += 1
                if "Último Aliento Intermedio" in self.titulos_desbloqueados: self.acciones["aliento_activaciones_intermedio"] += 1
                if "Último Aliento Veterano" in self.titulos_desbloqueados: self.acciones["aliento_activaciones_veterano"] += 1
                if "Último Aliento Experto" in self.titulos_desbloqueados: self.acciones["aliento_activaciones_experto"] += 1
        
        self.verificar_titulos(log)
        return True

    def get_max_pasivo(self, stat_name):
        # Para triggers o efectos no acumulativos, buscamos el valor máximo
        val_max = 0
        for t_name in self.titulos_desbloqueados:
            data = TITULOS_DATA[t_name]
            if data.get("tipo") == "pasivo":
                val_max = max(val_max, data.get("bono_pasivo", {}).get(stat_name, 0))
        return val_max

    def morir(self, log=None):
        self.vida = 0
        if log:
            log.add_message(f"[SISTEMA] {self.nombre} ha caído en combate.")

    def daño(self, oponente, tipo="fisico"):
        if tipo == "magico":
            self.acciones["usos_magia"] += 1
            ataque_total = self.magia
            titulo_data = TITULOS_DATA[self.titulo_actual]
            ataque_total += titulo_data.get("bono", {}).get("daño_magico", 0)
            
            defensa_oponente = oponente.defensa_magica if hasattr(oponente, 'defensa_magica') else 0
            if ataque_total <= defensa_oponente:
                return 0
            return ataque_total - defensa_oponente

        if self.arma:
            ataque_total = self.arma.calcular_daño(self.fuerza)
        else:
            ataque_total = self.fuerza
            
        # Aplicar bonos planos del título equipado
        titulo_data = TITULOS_DATA[self.titulo_actual]
        bonos = titulo_data.get("bono", {})
        
        if tipo == "fisico" or tipo == "habilidad":
            ataque_total += bonos.get("daño_melee", 0)
        elif tipo == "distancia":
            ataque_total += bonos.get("daño_distancia", 0)
            
        defensa_oponente = oponente.defensa
        if ataque_total <= defensa_oponente:
            return 0
        return ataque_total - defensa_oponente

    def atacar(self, oponente, log, tipo_forzado=None):
        # Determinar tipo de daño basado en arma y título
        if tipo_forzado:
            tipo_daño = tipo_forzado
            # Si es un ataque básico pero llevamos arma a distancia, debe ser tipo distancia
            if tipo_forzado == "fisico" and self.arma and self.arma.tipo_daño == "distancia":
                tipo_daño = "distancia"
        else:
            # Por defecto usar el tipo del arma si existe
            tipo_daño = self.arma.tipo_daño if self.arma else "fisico"
            
            if self.titulo_actual != "Hoja en Blanco":
                if "Espada" in self.titulo_actual or "Hoja" in self.titulo_actual:
                    tipo_daño = "habilidad"
                elif "Proyectil" in self.titulo_actual or "Arquero" in self.titulo_actual or "Halcón" in self.titulo_actual:
                    tipo_daño = "distancia"
            
        # Registrar acción para evolución
        if tipo_daño == "distancia":
            self.acciones["usos_proyectil"] += 1
        elif tipo_daño == "habilidad":
            self.acciones["usos_espada"] += 1
        
        dmg = self.daño(oponente, tipo=tipo_daño)
        if oponente.recibir_daño(dmg, tipo=tipo_daño):
            log.add_message(f"[{self.nombre}] {tipo_daño.upper()} -> {dmg} DMG")
        else:
            log.add_message(f"[{self.nombre}] ¡FALLÓ! ({tipo_daño})")
            
        if not oponente.vivo():
            oponente.morir(log)
            # Registrar muerte por tipo
            tipo_enemigo = oponente.__class__.__name__.lower()
            if f"muertes_{tipo_enemigo}" in self.acciones:
                self.acciones[f"muertes_{tipo_enemigo}"] += 1
            self.acciones["muertes_totales"] += 1
            
            # Verificar nuevos títulos tras una acción importante
            self.verificar_titulos(log)

    def verificar_titulos(self, log=None):
        nuevos = []
        for titulo, data in TITULOS_DATA.items():
            if titulo in self.titulos_desbloqueados:
                continue
            
            cumple = True
            for req_key, req_val in data["req"].items():
                if req_key == "nivel":
                    if self.nivel < req_val: cumple = False
                elif req_key == "titulos":
                    for t_req in req_val:
                        if t_req not in self.titulos_desbloqueados:
                            cumple = False
                            break
                elif req_key == "magia_desbloqueada":
                    if not self.magia_desbloqueada: cumple = False
                elif self.acciones.get(req_key, 0) < req_val:
                    cumple = False
            
            if cumple:
                self.titulos_desbloqueados.append(titulo)
                nuevos.append(titulo)
                if log:
                    log.add_message(f"[TITULO] ¡Has desbloqueado: {titulo}!")
                if self.game:
                    self.game.spawn_floating_text(f"¡NUEVA IDENTIDAD: {titulo}!", self.game.player.rect.centerx, self.game.player.rect.top - 20, YELLOW)
                    self.game.spawn_floating_text("¡DESBLOQUEADO!", self.game.player.rect.centerx, self.game.player.rect.top - 50, GREEN)
        return nuevos

    def cambiar_titulo(self, nuevo_titulo):
        if nuevo_titulo in self.titulos_desbloqueados:
            self.titulo_actual = nuevo_titulo
            return True
        return False

    def curar(self, cantidad):
        if self.vida >= self.max_vida: return
        
        curacion_real = min(cantidad, self.max_vida - self.vida)
        self.vida += curacion_real
        self.acciones["hp_regenerada_total"] += curacion_real
        self.verificar_titulos()
        
    def restaurar_mana(self, cantidad):
        self.mana = min(self.max_mana, self.mana + cantidad)
        
    def gastar_mana(self, cantidad):
        if self.mana >= cantidad:
            self.mana -= cantidad
            return True
        return False

    def update_regen(self, dt):
        # Regen por segundo fuera de combate
        regen_flat = self.get_max_pasivo("regen_flat")
        if regen_flat > 0 and self.vida < self.max_vida:
            self.regen_timer += dt
            if self.regen_timer >= 1.0:
                self.curar(regen_flat)
                self.regen_timer = 0

    def ejecutar_regen_turno(self, log=None):
        import random
        # Reducir cooldowns
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= 1
                
        # 1. Regen Flat
        regen_flat = self.get_max_pasivo("regen_flat")
        if regen_flat > 0:
            self.curar(regen_flat)
            if log: log.add_message(f"[TITULO] Regeneración: +{regen_flat} HP")
            if self.game: self.game.spawn_floating_text(f"+{regen_flat}", self.game.player.rect.centerx, self.game.player.rect.top, (0, 255, 0))

        # 2. Regen Porcentual (5% chance)
        regen_chance = self.get_max_pasivo("regen_chance")
        if random.random() < regen_chance:
            regen_pct = self.get_max_pasivo("regen_pct")
            curacion = int(self.max_vida * regen_pct)
            self.curar(curacion)
            if log: log.add_message(f"[TITULO] ¡ABSORCIÓN DE ESENCIA! +{curacion} HP")
            if self.game: self.game.spawn_floating_text("ESENCIA", self.game.player.rect.centerx, self.game.player.rect.centery, (100, 255, 100))
            
            # Incrementar activaciones para evolución
            if "Regeneración Pasiva Baja" in self.titulos_desbloqueados: self.acciones["regen_activaciones_baja"] += 1
            if "Regeneración Pasiva Intermedia" in self.titulos_desbloqueados: self.acciones["regen_activaciones_intermedia"] += 1
            if "Regeneración Pasiva Media" in self.titulos_desbloqueados: self.acciones["regen_activaciones_media"] += 1
            if "Regeneración Pasiva Alta" in self.titulos_desbloqueados: self.acciones["regen_activaciones_alta"] += 1
            
            self.verificar_titulos(log)

    def subir_de_nivel(self, fuerza, fe, defensa, log=None):
        self.fuerza_base += fuerza
        self.fe_base += fe
        self.magia_base += 1 # Escala mágica básica por nivel
        self.defensa_base += defensa
        self.max_vida_base += 20
        self.max_mana_base += 10 # Crece el Maná por nivel
        self.vida = self.max_vida
        self.mana = self.max_mana
        self.nivel += 1
        self.xp_necesaria = int(self.xp_necesaria * 2.0)
        if log:
            log.add_message(f"[SISTEMA] ¡NIVEL UP! Lvl {self.nivel}")
        self.verificar_titulos(log)

    def ganar_xp(self, cantidad, log):
        self.xp += cantidad
        log.add_message(f"[SISTEMA] +{cantidad} XP")
        while self.xp >= self.xp_necesaria:
            self.xp -= self.xp_necesaria
            self.subir_de_nivel(1, 0, 1, log)

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

    def to_dict(self):
        baul_serialized = []
        for item in self.baul:
            if hasattr(item, "to_dict"):
                item_data = item.to_dict()
                if not "type" in item_data:
                    item_data["type"] = item.__class__.__name__
                baul_serialized.append(item_data)

        return {
            "nombre": self.nombre,
            "fuerza_base": self.fuerza_base,
            "fe_base": self.fe_base,
            "defensa_base": self.defensa_base,
            "vida": self.vida,
            "max_vida_base": self.max_vida_base,
            "mana": self.mana,
            "max_mana_base": self.max_mana_base,
            "magia_base": self.magia_base,
            "magia_desbloqueada": self.magia_desbloqueada,
            "cruz_usos_hoy": self.cruz_usos_hoy,
            "cruz_ultimo_dia": self.cruz_ultimo_dia,
            "nivel": self.nivel,
            "xp": self.xp,
            "xp_necesaria": self.xp_necesaria,
            "cobre": self.cobre,
            "plata": self.plata,
            "oro": self.oro,
            "platino": self.platino,
            "banco_cobre": self.banco_cobre,
            "casco": self.casco.to_dict() if self.casco else None,
            "pechera": self.pechera.to_dict() if self.pechera else None,
            "botas": self.botas.to_dict() if self.botas else None,
            "accesorio": self.accesorio.to_dict() if self.accesorio else None,
            "arma": self.arma.to_dict() if self.arma else None,
            "baul": baul_serialized,
            "titulo_actual": self.titulo_actual,
            "titulos_desbloqueados": self.titulos_desbloqueados,
            "acciones": self.acciones,
            "cooldowns": self.cooldowns
        }

    def load_base_stats(self, data):
        self.fuerza_base = data.get("fuerza_base", data.get("fuerza", 10))
        self.fe_base = data.get("fe_base", data.get("fe", 0))
        self.magia_base = data.get("magia_base", 0)
        self.defensa_base = data.get("defensa_base", data.get("defensa", 5))
        self.vida = data["vida"]
        self.max_vida_base = data.get("max_vida_base", data.get("max_vida", 100))
        self.mana = data.get("mana", 50)
        self.max_mana_base = data.get("max_mana_base", 50)
        self.magia_desbloqueada = data.get("magia_desbloqueada", False)
        self.cruz_usos_hoy = data.get("cruz_usos_hoy", 3)
        self.cruz_ultimo_dia = data.get("cruz_ultimo_dia", "")
        self.cooldowns = data.get("cooldowns", {"habilidad": 0, "distancia": 0})
        self.nivel = data["nivel"]
        self.xp = data["xp"]
        self.xp_necesaria = data["xp_necesaria"]
        self.cobre = data["cobre"]
        self.plata = data["plata"]
        self.oro = data["oro"]
        self.platino = data["platino"]
        self.banco_cobre = data["banco_cobre"]
        self.defensa_magica_base = data.get("defensa_magica_base", 0)
        
        self.titulo_actual = data.get("titulo_actual", "Hoja en Blanco")
        self.titulos_desbloqueados = data.get("titulos_desbloqueados", ["Hoja en Blanco"])
        self.acciones = data.get("acciones", self.acciones)
        
        from logic.armaduras import Armadura
        from logic.accesorios import Accesorio
        
        if data.get("casco"): self.casco = Armadura.from_dict(data["casco"])
        if data.get("pechera"): self.pechera = Armadura.from_dict(data["pechera"])
        if data.get("botas"): self.botas = Armadura.from_dict(data["botas"])
        if data.get("armadura"): self.pechera = Armadura.from_dict(data["armadura"]) # Compatibilidad
        if data.get("accesorio"): self.accesorio = Accesorio.from_dict(data["accesorio"])
        
        if data.get("arma"):
            self.arma = Arma.from_dict(data["arma"])
        elif data.get("espada"): # Migración de guardados viejos
            self.arma = Arma.from_dict(data["espada"])

