class Arma:
    def __init__(
        self,
        nombre,
        daño,
        tipo_daño="fisico",
        sprite_path=None,
    ):
        self.nombre = nombre
        self.daño = daño
        self.tipo_daño = tipo_daño  # "fisico" (melee), "distancia" (proyectiles), "contundente" (mazos), "magico" (varitas)
        self.sprite_path = sprite_path or self.determinar_sprite()

        n_lower = self.nombre.lower()
        self.stat_escalado = "fuerza"
        if (
            "hacha" in n_lower
            or "oxidada" in n_lower
            or "mazo" in n_lower
            or "martillo" in n_lower
            or self.tipo_daño == "fisico"
            or "espada" in n_lower
        ):
            self.stat_escalado = "fuerza"
        elif "varita" in n_lower:
            self.stat_escalado = "magia"

        self.coef_escalado = 1.1
        n_lower = self.nombre.lower()

        if "oxidada" in n_lower or "mazo" in n_lower or "martillo" in n_lower:
            self.crit_chance = 0.08
        elif "hacha" in n_lower or "espada" in n_lower:
            self.crit_chance = 0.1
        elif "varita" in n_lower:
            self.crit_chance = 0.09
        else:
            self.crit_chance = 0.05

        self.crit_mult = 2.0

        self.durabilidad: int = 100
        self.durabilidad_max: int = 100

        if self.tipo_daño == "fisico":
            tipo_str = "[MELEE]"
        elif self.tipo_daño == "contundente":
            tipo_str = "[CONTUNDENTE]"
        elif self.tipo_daño == "magico":
            tipo_str = "[MAGICO]"
        else:
            tipo_str = "[DISTANCIA]" if tipo_daño == "fisico" else "[DISTANCIA]"

        self.descripcion = f"{tipo_str} Un arma de ataque. Daño base: {daño}."

    def determinar_sprite(self):
        n_lower = self.nombre.lower()

        if "hacha" in n_lower:
            return "assets/sprites/hacha_32x32.png"
        elif "oxidada" in n_lower:
            return "assets/sprites/espada_oxidada.png"
        elif "mazo" in n_lower or "martillo" in n_lower:
            return "assets/sprites/mazo.png"
        elif "varita" in n_lower or "báculo" in n_lower or "cetro" in n_lower:
            return "assets/sprites/varita.png"
        elif self.tipo_daño == "fisico" or "espada" in n_lower:
            return "assets/sprites/espada_1.png"
        return None

    def calcular_daño(self, personaje):
        valor_stat = 0
        if self.stat_escalado == "fuerza":
            valor_stat = personaje.fuerza
        elif self.stat_escalado == "magia":
            valor_stat = personaje.magia
        return self.daño + int(valor_stat * self.coef_escalado)

    def mejorar_daño(self, mejora):
        self.daño += mejora

    def mejorar_durabilidad(self, mejora):
        self.durabilidad_max += mejora
        self.durabilidad = self.durabilidad_max

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "daño": self.daño,
            "tipo_daño": self.tipo_daño,
            "sprite_path": self.sprite_path,
            "crit_chance": self.crit_chance,
            "crit_mult": self.crit_mult,
            "stat_escalado": self.stat_escalado,
            "coef_escalado": self.coef_escalado,
            "durabilidad": self.durabilidad,
            "durabilidad_max": self.durabilidad_max,
        }

    @classmethod
    def from_dict(cls, data):
        arma = cls(
            data["nombre"],
            data["daño"],
            data.get("tipo_daño", "fisico"),
            data.get("sprite_path"),
        )
        arma.crit_chance = data.get("crit_chance", arma.crit_chance)
        arma.crit_mult = data.get("crit_mult", arma.crit_mult)
        arma.stat_escalado = data.get("stat_escalado", arma.stat_escalado)
        arma.coef_escalado = data.get("coef_escalado", arma.coef_escalado)
        arma.durabilidad_max = data.get("durabilidad_max", arma.durabilidad_max)
        arma.durabilidad = data.get("durabilidad", arma.durabilidad_max)
        return arma

    def __str__(self):
        return f"{self.nombre} ({self.tipo_daño.upper()}: {self.daño})"
