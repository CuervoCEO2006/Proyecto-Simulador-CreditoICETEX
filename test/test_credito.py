import sys
sys.path.append('src')

import unittest
from model import logica_credito

class CreditoEducativoTest(unittest.TestCase):

    # --- CASOS NORMALES ---

    def test_normal_1(self):
        # ENTRADAS
        monto_credito = 10_000_000
        interes = 1.5 / 100
        plazo = 24
        cuota = 499_241.02
        # SALIDAS ESPERADAS
        total_pagado = 11_981_784.47
        total_intereses = 1_981_784.47

        cuota_calculada = logica_credito.calcular_cuota(monto_credito, interes, plazo)
        total_pagado_calculado = logica_credito.calcular_total_pagado(monto_credito, interes, plazo)
        total_intereses_calculado = logica_credito.calcular_total_intereses(monto_credito, interes, plazo)

        # Prueba que dos variables sean iguales
        self.assertAlmostEqual(cuota, cuota_calculada, 2)
        self.assertAlmostEqual(total_pagado, total_pagado_calculado, 2)
        self.assertAlmostEqual(total_intereses, total_intereses_calculado, 2)

    def test_normal_2(self):
        # ENTRADAS
        monto_credito = 5_000_000
        interes = 1 / 100
        plazo = 12
        cuota = 444_243.94
        # SALIDAS ESPERADAS
        total_pagado = 5_330_927.32
        total_intereses = 330_927.32

        cuota_calculada = logica_credito.calcular_cuota(monto_credito, interes, plazo)
        total_pagado_calculado = logica_credito.calcular_total_pagado(monto_credito, interes, plazo)
        total_intereses_calculado = logica_credito.calcular_total_intereses(monto_credito, interes, plazo)

        self.assertAlmostEqual(cuota, cuota_calculada, 2)
        self.assertAlmostEqual(total_pagado, total_pagado_calculado, 2)
        self.assertAlmostEqual(total_intereses, total_intereses_calculado, 2)

    def test_normal_3(self):
        # ENTRADAS
        monto_credito = 20_000_000
        tasa = 1.25 / 100
        plazo = 36
        cuota = 693_306.57

        resultado = logica_credito.calcular_cuota(monto_credito, tasa, plazo)
        self.assertEqual(cuota, round(resultado, 2))

    # --- CASOS EXTRAORDINARIOS ---

    def test_tasa_cero(self):
        # ENTRADAS
        monto_credito = 3_000_000
        interes = 0 / 100
        plazo = 6
        # SALIDAS ESPERADAS
        cuota_esperada = 500_000
        total_pagado = 3_000_000
        total_intereses = 0

        cuota_calculada = logica_credito.calcular_cuota(monto_credito, interes, plazo)
        total_pagado_calculado = logica_credito.calcular_total_pagado(monto_credito, interes, plazo)
        total_intereses_calculado = logica_credito.calcular_total_intereses(monto_credito, interes, plazo)

        self.assertAlmostEqual(cuota_esperada, cuota_calculada, 2)
        self.assertAlmostEqual(total_pagado, total_pagado_calculado, 2)
        self.assertAlmostEqual(total_intereses, total_intereses_calculado, 2)

    def test_cuota_unica(self):
        # ENTRADAS
        monto_credito = 500_000
        interes = 1 / 100
        plazo = 1
        # SALIDAS ESPERADAS
        cuota_esperada = 505_000
        total_pagado = 505_000
        total_intereses = 5_000

        cuota_calculada = logica_credito.calcular_cuota(monto_credito, interes, plazo)
        total_pagado_calculado = logica_credito.calcular_total_pagado(monto_credito, interes, plazo)
        total_intereses_calculado = logica_credito.calcular_total_intereses(monto_credito, interes, plazo)

        self.assertAlmostEqual(cuota_esperada, cuota_calculada, 2)
        self.assertAlmostEqual(total_pagado, total_pagado_calculado, 2)
        self.assertAlmostEqual(total_intereses, total_intereses_calculado, 2)

    def test_credito_alto_plazo_largo(self):
        # ENTRADAS
        monto_credito = 25_000_000
        interes = 1.5 / 100
        plazo = 60
        # SALIDAS ESPERADAS
        cuota_esperada = 634_835.69
        total_pagado = 38_090_141.14
        total_intereses = 13_090_141.14

        cuota_calculada = logica_credito.calcular_cuota(monto_credito, interes, plazo)
        total_pagado_calculado = logica_credito.calcular_total_pagado(monto_credito, interes, plazo)
        total_intereses_calculado = logica_credito.calcular_total_intereses(monto_credito, interes, plazo)

        self.assertAlmostEqual(cuota_esperada, cuota_calculada, 2)
        self.assertAlmostEqual(total_pagado, total_pagado_calculado, 2)
        self.assertAlmostEqual(total_intereses, total_intereses_calculado, 2)

    # --- CASOS DE ERROR ---

    def test_monto_cero(self):
        # ENTRADAS
        monto_credito = 0
        interes = 1.5 / 100
        plazo = 24

        # Verifica que si se genere una excepcion adentro del bloque with
        with self.assertRaises(logica_credito.MontoInvalido):
            logica_credito.calcular_cuota(monto_credito, interes, plazo)

    def test_tasa_negativa(self):
        # ENTRADAS
        monto_credito = 10_000_000
        interes = -1 / 100
        plazo = 24

        with self.assertRaises(logica_credito.TasaInvalida):
            logica_credito.calcular_cuota(monto_credito, interes, plazo)

    def test_plazo_cero(self):
        # ENTRADAS
        monto_credito = 10_000_000
        interes = 1.5 / 100
        plazo = 0

        with self.assertRaises(logica_credito.PlazoInvalido):
            logica_credito.calcular_cuota(monto_credito, interes, plazo)

    def test_plazo_negativo(self):
        # ENTRADAS
        monto_credito = 10_000_000
        interes = 1.5 / 100
        plazo = -12

        with self.assertRaises(logica_credito.PlazoInvalido):
            logica_credito.calcular_cuota(monto_credito, interes, plazo)


if __name__ == '__main__':
    unittest.main()