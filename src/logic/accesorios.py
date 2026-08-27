# src/logic/accesorios.py

class Accesorio:
    def __init__(self, nombre, bono_stats=None):
        self.nombre = nombre
        self.bono_stats = bono_stats or {}
        
        self.descripcion = "[ACCESORIO] Mejora atributos pasivamente."
        
        # Generar descripción dinámica basada en las estadísticas
        for stat, valor in self.bono_stats.items():
            if valor > 0:
                self.descripcion += f" +{valor} {stat.capitalize()}"
            elif valor < 0:
                self.descripcion += f" {valor} {stat.capitalize()}"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "bono_stats": self.bono_stats
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nombre"], data.get("bono_stats", {}))

    def __str__(self):
        return self.nombre
