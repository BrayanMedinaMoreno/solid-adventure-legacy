import sys
import os
import unittest

# Agregar la carpeta src al path para poder importar los modulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logic.personaje import Personaje

class TestLineaDeEsquiva(unittest.TestCase):
    def setUp(self):
        # Crear un personaje con 100 de vida maxima
        self.p = Personaje(nombre='Heroe', fuerza=10, fe=0, defensa=5, vida=100)

    def test_desbloqueo_esquiva_novato(self):
        # Simular 50 golpes a menos del 80% de vida
        self.p.acciones['golpes_bajo_80hp'] = 50
        nuevos = self.p.verificar_titulos()
        
        self.assertIn('Esquiva de Novato', self.p.titulos_desbloqueados)
        self.assertIn('Esquiva de Novato', nuevos)
        self.assertEqual(self.p.get_max_pasivo('esquiva_basica'), 0.02)

    def test_desbloqueo_esquiva_iniciado(self):
        # Dar el titulo anterior
        self.p.titulos_desbloqueados.append('Esquiva de Novato')
        # Simular los requisitos: 100 golpes < 50% HP y 3 esquivas de novato
        self.p.acciones['golpes_bajo_50hp'] = 100
        self.p.acciones['esquivas_novato'] = 3
        
        self.p.verificar_titulos()
        
        self.assertIn('Esquiva de Iniciado', self.p.titulos_desbloqueados)
        self.assertEqual(self.p.get_max_pasivo('esquiva_basica'), 0.04)
        self.assertEqual(self.p.get_max_pasivo('esquiva_trampa'), 0.10)

    def test_esquiva_maestro_y_multiples_bonos(self):
        # Simular que tiene hasta experto
        self.p.titulos_desbloqueados.extend([
            'Esquiva de Novato', 'Esquiva de Iniciado', 'Esquiva Intermedio', 
            'Esquiva de Veterano', 'Esquiva de Experto'
        ])
        
        # Simular los requisitos para Maestro
        self.p.acciones['golpes_bajo_22hp'] = 300
        self.p.acciones['trampas_esquivadas'] = 50
        self.p.acciones['esquivas_experto'] = 80
        
        self.p.verificar_titulos()
        
        self.assertIn('Esquiva de Maestro', self.p.titulos_desbloqueados)
        self.assertEqual(self.p.get_max_pasivo('esquiva_general'), 0.12)
        self.assertEqual(self.p.get_max_pasivo('esquiva_trampa'), 0.50)

    def test_registro_de_golpes_baja_vida(self):
        # Bajar la vida a 75 (75% HP)
        self.p.vida = 75
        self.p.recibir_daño(10, tipo='fisico')
        
        # Debe haber registrado el golpe en <80%
        self.assertEqual(self.p.acciones.get('golpes_bajo_80hp', 0), 1)
        # Pero no en <50% porque tenia 75
        self.assertEqual(self.p.acciones.get('golpes_bajo_50hp', 0), 0)

if __name__ == '__main__':
    unittest.main()
