import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.append("src")

from controller.simulaciones_credito_controller import SimulacionesCreditoController
from model.logica_credito import MontoInvalido, SolicitudCredito


class SimulacionesCreditoControllerTest(unittest.TestCase):
    def setUp(self):
        self.solicitud = SolicitudCredito(
            monto_credito_semestre=1_500_000,
            cantidad_semestres=4,
            tasa_interes_mensual=0.01,
            cantidad_cuotas=24,
            periodo_gracia=4,
        )
        self.connection = MagicMock()
        self.cursor = MagicMock()
        self.connection.cursor.return_value.__enter__.return_value = self.cursor

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_guardar_persist_credito_educativo_y_devuelve_id(self, connect):
        connect.return_value = self.connection
        self.cursor.fetchone.return_value = (42,)

        id_simulacion = SimulacionesCreditoController.guardar(self.solicitud)

        self.assertEqual(42, id_simulacion)
        query, values = self.cursor.execute.call_args.args
        self.assertIn("INSERT INTO simulaciones_credito", query)
        self.assertEqual(
            (
                1_500_000,
                4,
                6_000_000,
                0.01,
                24,
                4,
                293_909.06,
                7_053_817.53,
                1_053_817.53,
            ),
            values,
        )
        self.connection.close.assert_called_once()

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_no_guarda_una_solicitud_invalida(self, connect):
        solicitud_invalida = SolicitudCredito(0, 4, 0.01, 24, 4)

        with self.assertRaises(MontoInvalido):
            SimulacionesCreditoController.guardar(solicitud_invalida)

        connect.assert_not_called()

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_buscar_devuelve_simulacion_por_id(self, connect):
        connect.return_value = self.connection
        row = (
            42,
            "2026-10-06",
            1_500_000,
            4,
            6_000_000,
            0.01,
            24,
            4,
            293_909.06,
            7_053_817.53,
            1_053_817.53,
        )
        columns = (
            "id",
            "fecha_simulacion",
            "monto_credito_semestre",
            "cantidad_semestres",
            "monto_total_credito",
            "tasa_interes_mensual",
            "cantidad_cuotas",
            "periodo_gracia",
            "cuota_mensual",
            "total_pagado",
            "total_intereses",
        )
        self.cursor.description = [SimpleNamespace(name=name) for name in columns]
        self.cursor.fetchone.return_value = row

        result = SimulacionesCreditoController.buscar(42)

        self.assertEqual(42, result["id"])
        self.assertEqual(1_500_000, result["monto_credito_semestre"])
        self.assertEqual(4, result["periodo_gracia"])
        self.cursor.execute.assert_called_once_with(unittest.mock.ANY, (42,))

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_buscar_inexistente_devuelve_none(self, connect):
        connect.return_value = self.connection
        self.cursor.fetchone.return_value = None

        self.assertIsNone(SimulacionesCreditoController.buscar(999))

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_listar_devuelve_historial(self, connect):
        connect.return_value = self.connection
        row = (
            42,
            "2026-10-06",
            1_500_000,
            4,
            6_000_000,
            0.01,
            24,
            4,
            293_909.06,
            7_053_817.53,
            1_053_817.53,
        )
        columns = (
            "id",
            "fecha_simulacion",
            "monto_credito_semestre",
            "cantidad_semestres",
            "monto_total_credito",
            "tasa_interes_mensual",
            "cantidad_cuotas",
            "periodo_gracia",
            "cuota_mensual",
            "total_pagado",
            "total_intereses",
        )
        self.cursor.description = [SimpleNamespace(name=name) for name in columns]
        self.cursor.fetchall.return_value = [row]

        result = SimulacionesCreditoController.listar()

        self.assertEqual(1, len(result))
        self.assertEqual(42, result[0]["id"])
        self.assertEqual(6_000_000, result[0]["monto_total_credito"])

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_eliminar_indica_si_encontro_el_registro(self, connect):
        connect.return_value = self.connection
        self.cursor.rowcount = 1

        self.assertTrue(SimulacionesCreditoController.eliminar(42))
        self.cursor.execute.assert_called_once_with(
            "DELETE FROM simulaciones_credito WHERE id = %s",
            (42,),
        )


if __name__ == "__main__":
    unittest.main()
