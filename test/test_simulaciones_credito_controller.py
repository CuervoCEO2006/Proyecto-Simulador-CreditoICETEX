import sys
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

    def test_connect_usa_credenciales_de_secret_config(self):
        secret_config = SimpleNamespace(
            PG_HOST="db.example.test",
            PG_DATABASE="credito_test",
            PG_USER="tester",
            PG_PASSWORD="local-only",
            PG_PORT=5433,
        )
        postgres = SimpleNamespace(connect=MagicMock(return_value=self.connection))
        with patch.dict(
            sys.modules,
            {"secret_config": secret_config, "psycopg2": postgres},
        ):
            connection = SimulacionesCreditoController._connect()

        self.assertIs(self.connection, connection)
        postgres.connect.assert_called_once_with(
            host="db.example.test",
            dbname="credito_test",
            user="tester",
            password="local-only",
            port=5433,
        )

    def test_connect_informa_si_secret_config_no_tiene_credenciales(self):
        secret_config = SimpleNamespace(
            PG_HOST="",
            PG_DATABASE="",
            PG_USER="",
            PG_PASSWORD="",
            PG_PORT=5432,
        )
        with patch.dict(sys.modules, {"secret_config": secret_config}):
            with self.assertRaisesRegex(RuntimeError, "secret_config.py"):
                SimulacionesCreditoController._connect()

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
        solicitud_reconstruida = SolicitudCredito(
            monto_credito_semestre=float(result["monto_credito_semestre"]),
            cantidad_semestres=result["cantidad_semestres"],
            tasa_interes_mensual=float(result["tasa_interes_mensual"]),
            cantidad_cuotas=result["cantidad_cuotas"],
            periodo_gracia=result["periodo_gracia"],
        )
        self.assertEqual(self.solicitud, solicitud_reconstruida)
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

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_limpieza_rechaza_una_base_que_no_es_de_pruebas(self, connect):
        connect.return_value = self.connection
        self.cursor.fetchone.return_value = ("simulador_credito",)

        with self.assertRaisesRegex(RuntimeError, "termine en '_test'"):
            SimulacionesCreditoController._limpiar_tabla_para_pruebas()

        self.cursor.execute.assert_called_once_with("SELECT current_database()")

    @patch.object(SimulacionesCreditoController, "_connect")
    def test_limpieza_vacia_la_tabla_solo_en_base_de_pruebas(self, connect):
        connect.return_value = self.connection
        self.cursor.fetchone.return_value = ("simulador_credito_test",)

        SimulacionesCreditoController._limpiar_tabla_para_pruebas()

        self.cursor.execute.assert_any_call("DELETE FROM simulaciones_credito")


if __name__ == "__main__":
    unittest.main()
