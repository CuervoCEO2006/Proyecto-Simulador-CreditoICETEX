import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from model.logica_credito import SolicitudCredito
from app import app


class SimuladorCreditoWebTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_inicio_muestra_enlace_al_formulario(self):
        response = self.client.get("/")

        self.assertEqual(200, response.status_code)
        self.assertIn(b'href="/simular"', response.data)

    def test_formulario_muestra_campos_del_modelo(self):
        response = self.client.get("/simular")

        self.assertEqual(200, response.status_code)
        self.assertIn(b'name="monto_credito_semestre"', response.data)
        self.assertIn(b'name="cantidad_semestres"', response.data)
        self.assertIn(b'name="tasa_interes_mensual"', response.data)
        self.assertIn(b'name="cantidad_cuotas"', response.data)
        self.assertIn(b'name="periodo_gracia"', response.data)

    @patch("app.SimulacionesCreditoController.guardar", return_value=42)
    def test_calcular_guarda_y_muestra_los_resultados(self, guardar):
        datos = {
            "monto_credito_semestre": "1500000",
            "cantidad_semestres": "4",
            "tasa_interes_mensual": "1",
            "cantidad_cuotas": "24",
            "periodo_gracia": "4",
        }
        response = self.client.get("/calcular", query_string=datos)

        self.assertEqual(200, response.status_code)
        self.assertIn(b"La simulaci\xc3\xb3n se guard\xc3\xb3 con el ID 42", response.data)
        self.assertIn(b"$293,909.06", response.data)
        self.assertIn(b"$7,053,817.53", response.data)
        self.assertIn(b"$1,053,817.53", response.data)
        guardar.assert_called_once()
        solicitud = guardar.call_args.args[0]
        self.assertIsInstance(solicitud, SolicitudCredito)
        self.assertEqual(0.01, solicitud.tasa_interes_mensual)
        self.assertEqual(1500000, solicitud.monto_credito_semestre)

    def test_calcular_informa_si_faltan_parametros(self):
        response = self.client.get("/calcular")

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Completa todos los campos", response.data)

    def test_calcular_rechaza_valores_no_numericos(self):
        response = self.client.get(
            "/calcular",
            query_string={
                "monto_credito_semestre": "abc",
                "cantidad_semestres": "4",
                "tasa_interes_mensual": "1",
                "cantidad_cuotas": "24",
                "periodo_gracia": "4",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Ingresa valores num", response.data)

    def test_calcular_muestra_error_para_un_monto_invalido(self):
        response = self.client.get(
            "/calcular",
            query_string={
                "monto_credito_semestre": "0",
                "cantidad_semestres": "4",
                "tasa_interes_mensual": "1",
                "cantidad_cuotas": "24",
                "periodo_gracia": "4",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"No se pudo calcular", response.data)
        self.assertNotIn(b"Cuota mensual:", response.data)

    @patch(
        "app.SimulacionesCreditoController.guardar",
        side_effect=RuntimeError("Falta secret_config.py."),
    )
    def test_calcular_muestra_error_si_no_puede_guardar(self, guardar):
        response = self.client.get(
            "/calcular",
            query_string={
                "monto_credito_semestre": "1500000",
                "cantidad_semestres": "4",
                "tasa_interes_mensual": "1",
                "cantidad_cuotas": "24",
                "periodo_gracia": "4",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"No se pudo guardar la simulaci\xc3\xb3n", response.data)
        self.assertIn(b"Falta secret_config.py.", response.data)
        guardar.assert_called_once()


if __name__ == "__main__":
    unittest.main()
