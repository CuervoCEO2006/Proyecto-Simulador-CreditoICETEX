from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from model.logica_credito import (
    SolicitudCredito,
    calcular_cuota,
    calcular_total_intereses,
    calcular_total_pagado,
    validar_solicitud_credito,
)


class SimulacionesCreditoController:
    """Persiste y consulta simulaciones de crédito educativo ICETEX."""

    @staticmethod
    def _connect() -> Any:
        try:
            import secret_config
        except ModuleNotFoundError as error:
            if error.name != "secret_config":
                raise
            raise RuntimeError(
                "Falta secret_config.py. Copia secret_config_sample.py como "
                "secret_config.py y configura los datos locales de PostgreSQL."
            ) from error

        configuration = {
            "host": secret_config.PG_HOST,
            "dbname": secret_config.PG_DATABASE,
            "user": secret_config.PG_USER,
            "password": secret_config.PG_PASSWORD,
            "port": secret_config.PG_PORT,
        }
        missing = [
            key for key, value in configuration.items()
            if value == "" or value is None
        ]
        if missing:
            raise RuntimeError(
                "Completa los datos de conexión de PostgreSQL en secret_config.py."
            )

        try:
            import psycopg2
        except ImportError as error:
            raise RuntimeError(
                "Para usar el historial instala el controlador PostgreSQL: "
                "pip install psycopg2-binary."
            ) from error

        return psycopg2.connect(**configuration)

    @staticmethod
    @contextmanager
    def _cursor() -> Iterator[Any]:
        connection = SimulacionesCreditoController._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    yield cursor
        finally:
            connection.close()

    @staticmethod
    def _row_as_dict(cursor: Any, row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            column.name: value
            for column, value in zip(cursor.description, row)
        }

    @staticmethod
    def guardar(solicitud: SolicitudCredito) -> int:
        """Guarda la solicitud y los resultados calculados; devuelve su identificador."""
        validar_solicitud_credito(solicitud)
        with SimulacionesCreditoController._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO simulaciones_credito (
                    monto_credito_semestre,
                    cantidad_semestres,
                    monto_total_credito,
                    tasa_interes_mensual,
                    cantidad_cuotas,
                    periodo_gracia,
                    cuota_mensual,
                    total_pagado,
                    total_intereses
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    solicitud.monto_credito_semestre,
                    solicitud.cantidad_semestres,
                    solicitud.monto_total_credito(),
                    solicitud.tasa_interes_mensual,
                    solicitud.cantidad_cuotas,
                    solicitud.periodo_gracia,
                    round(calcular_cuota(solicitud), 2),
                    round(calcular_total_pagado(solicitud), 2),
                    round(calcular_total_intereses(solicitud), 2),
                ),
            )
            result = cursor.fetchone()
            if result is None:
                raise RuntimeError(
                    "PostgreSQL no devolvió el identificador de la simulación guardada."
                )
            return result[0]

    @staticmethod
    def listar() -> list[dict[str, Any]]:
        """Devuelve el historial de simulaciones, de la más reciente a la más antigua."""
        with SimulacionesCreditoController._cursor() as cursor:
            cursor.execute(
                """
                SELECT id, fecha_simulacion, monto_credito_semestre,
                       cantidad_semestres, monto_total_credito,
                       tasa_interes_mensual, cantidad_cuotas, periodo_gracia,
                       cuota_mensual, total_pagado, total_intereses
                FROM simulaciones_credito
                ORDER BY fecha_simulacion DESC, id DESC
                """
            )
            return [
                SimulacionesCreditoController._row_as_dict(cursor, row)
                for row in cursor.fetchall()
            ]

    @staticmethod
    def buscar(id_simulacion: int) -> dict[str, Any] | None:
        """Busca una simulación por su identificador; devuelve None si no existe."""
        with SimulacionesCreditoController._cursor() as cursor:
            cursor.execute(
                """
                SELECT id, fecha_simulacion, monto_credito_semestre,
                       cantidad_semestres, monto_total_credito,
                       tasa_interes_mensual, cantidad_cuotas, periodo_gracia,
                       cuota_mensual, total_pagado, total_intereses
                FROM simulaciones_credito
                WHERE id = %s
                """,
                (id_simulacion,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return SimulacionesCreditoController._row_as_dict(cursor, row)

    @staticmethod
    def eliminar(id_simulacion: int) -> bool:
        """Elimina una simulación por su identificador e indica si existía."""
        with SimulacionesCreditoController._cursor() as cursor:
            cursor.execute(
                "DELETE FROM simulaciones_credito WHERE id = %s",
                (id_simulacion,),
            )
            return cursor.rowcount > 0

    @staticmethod
    def _limpiar_tabla_para_pruebas() -> None:
        """Vacía la tabla solo si la conexión apunta a una base con sufijo _test."""
        with SimulacionesCreditoController._cursor() as cursor:
            cursor.execute("SELECT current_database()")
            database = cursor.fetchone()
            if database is None or not str(database[0]).endswith("_test"):
                raise RuntimeError(
                    "Se rechazó limpiar simulaciones: las pruebas solo pueden "
                    "vaciar una base cuyo nombre termine en '_test'."
                )
            cursor.execute("DELETE FROM simulaciones_credito")

    @staticmethod
    def _recrear_tabla_para_pruebas() -> None:
        """Recrea la tabla desde el SQL del proyecto únicamente en una base _test."""
        schema_path = (
            Path(__file__).resolve().parents[2]
            / "sql"
            / "crear_simulaciones_credito.sql"
        )
        schema = schema_path.read_text(encoding="utf-8")

        with SimulacionesCreditoController._cursor() as cursor:
            cursor.execute("SELECT current_database()")
            database = cursor.fetchone()
            if database is None or not str(database[0]).endswith("_test"):
                raise RuntimeError(
                    "Se rechazó recrear la tabla: las pruebas solo pueden "
                    "modificar una base cuyo nombre termine en '_test'."
                )
            cursor.execute("DROP TABLE IF EXISTS simulaciones_credito")
            cursor.execute(schema)
