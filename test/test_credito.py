import sys
sys.path.append('src')

import unittest
from model.logica_credito import (
    SolicitudCredito,
    calcular_cuota,
    calcular_total_pagado,
    calcular_total_intereses,
    MontoInvalido,
    SemestresInvalidos,
    TasaInvalida,
    PlazoInvalido,
    PeriodoGraciaInvalido,
)

class CreditoEducativoTest(unittest.TestCase):

    def test_solicitudes_con_los_mismos_datos_son_iguales(self):
        solicitud = SolicitudCredito(1_500_000, 4, 0.01, 24, 4)
        solicitud_reconstruida = SolicitudCredito(1_500_000, 4, 0.01, 24, 4)

        self.assertEqual(solicitud, solicitud_reconstruida)

    def test_solicitudes_con_datos_diferentes_no_son_iguales(self):
        solicitud = SolicitudCredito(1_500_000, 4, 0.01, 24, 4)
        solicitud_diferente = SolicitudCredito(1_500_000, 4, 0.01, 24, 5)

        self.assertNotEqual(solicitud, solicitud_diferente)

    # --- CASOS NORMALES ---

    def test_normal_1(self):
        # ENTRADAS
        solicitud = SolicitudCredito(
            monto_credito_semestre=2_000_000,
            cantidad_semestres=5,
            tasa_interes_mensual=1.5 / 100,
            cantidad_cuotas=36,
            periodo_gracia=6,
        )
        # SALIDAS ESPERADAS
        cuota = 395_305.93
        total_pagado = 14_231_013.61
        total_intereses = 4_231_013.61

        self.assertAlmostEqual(cuota, calcular_cuota(solicitud), 2)
        self.assertAlmostEqual(total_pagado, calcular_total_pagado(solicitud), 2)
        self.assertAlmostEqual(total_intereses, calcular_total_intereses(solicitud), 2)

    def test_normal_2(self):
        solicitud = SolicitudCredito(
            monto_credito_semestre=1_500_000,
            cantidad_semestres=4,
            tasa_interes_mensual=1 / 100,
            cantidad_cuotas=24,
            periodo_gracia=4,
        )
        cuota = 293_909.06
        total_pagado = 7_053_817.53
        total_intereses = 1_053_817.53

        self.assertAlmostEqual(cuota, calcular_cuota(solicitud), 2)
        self.assertAlmostEqual(total_pagado, calcular_total_pagado(solicitud), 2)
        self.assertAlmostEqual(total_intereses, calcular_total_intereses(solicitud), 2)

    def test_normal_3(self):
        solicitud = SolicitudCredito(
            monto_credito_semestre=3_000_000,
            cantidad_semestres=6,
            tasa_interes_mensual=1.25 / 100,
            cantidad_cuotas=48,
            periodo_gracia=12,
        )
        cuota = 581_484.0

        self.assertEqual(cuota, round(calcular_cuota(solicitud), 2))

    # --- CASOS EXTRAORDINARIOS ---

    def test_tasa_cero(self):
        solicitud = SolicitudCredito(
            monto_credito_semestre=1_000_000,
            cantidad_semestres=2,
            tasa_interes_mensual=0,
            cantidad_cuotas=12,
            periodo_gracia=6,
        )
        cuota_esperada = 166_666.67
        total_pagado = 2_000_000.0
        total_intereses = 0.0

        self.assertAlmostEqual(cuota_esperada, calcular_cuota(solicitud), 2)
        self.assertAlmostEqual(total_pagado, calcular_total_pagado(solicitud), 2)
        self.assertAlmostEqual(total_intereses, calcular_total_intereses(solicitud), 2)

    def test_sin_periodo_de_gracia(self):
        solicitud = SolicitudCredito(
            monto_credito_semestre=800_000,
            cantidad_semestres=1,
            tasa_interes_mensual=1 / 100,
            cantidad_cuotas=6,
            periodo_gracia=0,
        )
        cuota_esperada = 138_038.69
        total_pagado = 828_232.16
        total_intereses = 28_232.16

        self.assertAlmostEqual(cuota_esperada, calcular_cuota(solicitud), 2)
        self.assertAlmostEqual(total_pagado, calcular_total_pagado(solicitud), 2)
        self.assertAlmostEqual(total_intereses, calcular_total_intereses(solicitud), 2)

    def test_cuota_unica(self):
        solicitud = SolicitudCredito(
            monto_credito_semestre=500_000,
            cantidad_semestres=1,
            tasa_interes_mensual=1 / 100,
            cantidad_cuotas=1,
            periodo_gracia=0,
        )
        cuota_esperada = 505_000.0
        total_pagado = 505_000.0
        total_intereses = 5_000.0

        self.assertAlmostEqual(cuota_esperada, calcular_cuota(solicitud), 2)
        self.assertAlmostEqual(total_pagado, calcular_total_pagado(solicitud), 2)
        self.assertAlmostEqual(total_intereses, calcular_total_intereses(solicitud), 2)

    # --- CASOS DE ERROR ---

    def test_monto_semestre_cero(self):
        solicitud = SolicitudCredito(0, 5, 1.5 / 100, 24, 6)
        with self.assertRaises(MontoInvalido):
            calcular_cuota(solicitud)

    def test_cantidad_semestres_invalida(self):
        solicitud = SolicitudCredito(2_000_000, 0, 1.5 / 100, 24, 6)
        with self.assertRaises(SemestresInvalidos):
            calcular_cuota(solicitud)

    def test_tasa_negativa(self):
        solicitud = SolicitudCredito(2_000_000, 5, -1 / 100, 24, 6)
        with self.assertRaises(TasaInvalida):
            calcular_cuota(solicitud)

    def test_plazo_cero(self):
        solicitud = SolicitudCredito(2_000_000, 5, 1.5 / 100, 0, 6)
        with self.assertRaises(PlazoInvalido):
            calcular_cuota(solicitud)

    def test_periodo_gracia_negativo(self):
        solicitud = SolicitudCredito(2_000_000, 5, 1.5 / 100, 24, -1)
        with self.assertRaises(PeriodoGraciaInvalido):
            calcular_cuota(solicitud)


if __name__ == '__main__':
    unittest.main()