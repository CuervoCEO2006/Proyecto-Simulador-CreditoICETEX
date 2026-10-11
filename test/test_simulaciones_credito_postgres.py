import os
import sys
import unittest
from unittest.mock import patch

sys.path.append("src")

from controller.simulaciones_credito_controller import SimulacionesCreditoController
from model.logica_credito import SolicitudCredito


@unittest.skipUnless(
    os.environ.get("RUN_POSTGRES_TESTS") == "1",
    "Define RUN_POSTGRES_TESTS=1 para ejecutar pruebas con PostgreSQL.",
)
class SimulacionesCreditoPostgresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import secret_config

        database_name = secret_config.PG_DATABASE
        if not database_name:
            raise RuntimeError("Configura PG_DATABASE en secret_config.py.")
        if not database_name.endswith("_test"):
            database_name = f"{database_name}_test"
        cls.database_config = patch.object(
            secret_config, "PG_DATABASE", database_name
        )
        cls.database_config.start()

    @classmethod
    def tearDownClass(cls):
        cls.database_config.stop()

    def setUp(self):
        SimulacionesCreditoController._limpiar_tabla_para_pruebas()
        self.solicitud = SolicitudCredito(
            monto_credito_semestre=1_500_000,
            cantidad_semestres=4,
            tasa_interes_mensual=0.01,
            cantidad_cuotas=24,
            periodo_gracia=4,
        )

    def tearDown(self):
        SimulacionesCreditoController._limpiar_tabla_para_pruebas()

    def test_guardar_y_buscar_reconstruyen_la_solicitud(self):
        id_simulacion = SimulacionesCreditoController.guardar(self.solicitud)

        resultado = SimulacionesCreditoController.buscar(id_simulacion)

        self.assertIsNotNone(resultado)
        solicitud_recuperada = SolicitudCredito(
            monto_credito_semestre=float(resultado["monto_credito_semestre"]),
            cantidad_semestres=resultado["cantidad_semestres"],
            tasa_interes_mensual=float(resultado["tasa_interes_mensual"]),
            cantidad_cuotas=resultado["cantidad_cuotas"],
            periodo_gracia=resultado["periodo_gracia"],
        )
        self.assertEqual(self.solicitud, solicitud_recuperada)

    def test_buscar_devuelve_none_si_no_existe(self):
        self.assertIsNone(SimulacionesCreditoController.buscar(-1))

    def test_listar_devuelve_las_simulaciones_guardadas(self):
        id_simulacion = SimulacionesCreditoController.guardar(self.solicitud)

        resultados = SimulacionesCreditoController.listar()

        self.assertEqual(1, len(resultados))
        self.assertEqual(id_simulacion, resultados[0]["id"])

    def test_eliminar_quita_la_simulacion(self):
        id_simulacion = SimulacionesCreditoController.guardar(self.solicitud)

        self.assertTrue(SimulacionesCreditoController.eliminar(id_simulacion))
        self.assertIsNone(SimulacionesCreditoController.buscar(id_simulacion))


if __name__ == "__main__":
    unittest.main()
