# src/logic/accesorios.py

class Accesorio:
    def __init__(self, nombre, bono_stats=None, durabilidad=None, max_durabilidad=None):
        import random
        self.nombre = nombre
        self.bono_stats = bono_stats or {}
        self.max_durabilidad = max_durabilidad if max_durabilidad is not None else random.randint(150, 300)
        self.durabilidad = durabilidad if durabilidad is not None else self.max_durabilidad
        
        self.descripcion = "[ACCESORIO] Mejora atributos pasivamente."
        
        for stat, valor in self.bono_stats.items():
            if valor > 0:
                self.descripcion += f" +{valor} {stat.capitalize()}"
            elif valor < 0:
                self.descripcion += f" {valor} {stat.capitalize()}"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "bono_stats": self.bono_stats,
            "durabilidad": self.durabilidad,
            "max_durabilidad": self.max_durabilidad
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nombre"], data.get("bono_stats", {}), data.get("durabilidad"), data.get("max_durabilidad"))

    def __str__(self):
        return self.nombre