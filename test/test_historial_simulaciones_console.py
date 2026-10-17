import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

sys.path.append("src")

from view.console import historial_simulaciones
from model.logica_credito import MontoInvalido


class HistorialSimulacionesConsoleTest(unittest.TestCase):
    @patch("builtins.input", side_effect=["1000000", "2", "1.5", "12", "3"])
    @patch.object(
        historial_simulaciones.SimulacionesCreditoController,
        "guardar",
        return_value=17,
    )
    def test_guardar_solicitud_calculada(self, guardar, input_mock):
        output = StringIO()
        with redirect_stdout(output):
            historial_simulaciones._guardar_simulacion()

        solicitud = guardar.call_args.args[0]
        self.assertEqual(1_000_000, solicitud.monto_credito_semestre)
        self.assertEqual(2, solicitud.cantidad_semestres)
        self.assertEqual(0.015, solicitud.tasa_interes_mensual)
        self.assertEqual(12, solicitud.cantidad_cuotas)
        self.assertEqual(3, solicitud.periodo_gracia)
        self.assertIn("Simulacion guardada con ID: 17", output.getvalue())
        self.assertEqual(5, input_mock.call_count)

    @patch("builtins.input", return_value="no-es-numero")
    @patch.object(historial_simulaciones.SimulacionesCreditoController, "guardar")
    def test_no_intenta_guardar_entradas_no_numericas(self, guardar, input_mock):
        output = StringIO()
        with redirect_stdout(output):
            historial_simulaciones._guardar_simulacion()

        guardar.assert_not_called()
        self.assertIn("Entrada invalida", output.getvalue())

    @patch("builtins.input", side_effect=["0", "2", "1.5", "12", "3"])
    @patch.object(
        historial_simulaciones.SimulacionesCreditoController,
        "guardar",
        side_effect=MontoInvalido(0),
    )
    def test_muestra_error_si_la_solicitud_es_invalida(self, guardar, input_mock):
        output = StringIO()
        with redirect_stdout(output):
            historial_simulaciones._guardar_simulacion()

        guardar.assert_called_once()
        self.assertIn("No se pudo guardar la simulacion", output.getvalue())

    @patch("builtins.input", return_value="17")
    @patch.object(
        historial_simulaciones.SimulacionesCreditoController,
        "buscar",
        return_value=None,
    )
    def test_informa_si_no_existe_la_simulacion(self, buscar, input_mock):
        output = StringIO()
        with redirect_stdout(output):
            historial_simulaciones._buscar_simulacion()

        buscar.assert_called_once_with(17)
        self.assertIn("No existe una simulacion con ID 17", output.getvalue())

    @patch("builtins.input", return_value="no-es-numero")
    @patch.object(historial_simulaciones.SimulacionesCreditoController, "buscar")
    def test_no_busca_un_id_no_numerico(self, buscar, input_mock):
        output = StringIO()
        with redirect_stdout(output):
            historial_simulaciones._buscar_simulacion()

        buscar.assert_not_called()
        self.assertIn("El ID debe ser un numero entero", output.getvalue())


if __name__ == "__main__":
    unittest.main()
