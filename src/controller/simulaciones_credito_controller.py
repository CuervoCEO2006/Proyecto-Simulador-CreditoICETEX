import os
from typing import Any

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
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "Falta configurar DATABASE_URL con la cadena de conexión de PostgreSQL."
            )

        try:
            import psycopg2
        except ImportError as error:
            raise RuntimeError(
                "Para usar el historial instala el controlador PostgreSQL: "
                "pip install psycopg2-binary."
            ) from error

        return psycopg2.connect(database_url)

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
        connection = SimulacionesCreditoController._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
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
        finally:
            connection.close()

    @staticmethod
    def listar() -> list[dict[str, Any]]:
        """Devuelve el historial de simulaciones, de la más reciente a la más antigua."""
        connection = SimulacionesCreditoController._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
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
        finally:
            connection.close()

    @staticmethod
    def buscar(id_simulacion: int) -> dict[str, Any] | None:
        """Busca una simulación por su identificador; devuelve None si no existe."""
        connection = SimulacionesCreditoController._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
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
        finally:
            connection.close()

    @staticmethod
    def eliminar(id_simulacion: int) -> bool:
        """Elimina una simulación por su identificador e indica si existía."""
        connection = SimulacionesCreditoController._connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM simulaciones_credito WHERE id = %s",
                        (id_simulacion,),
                    )
                    return cursor.rowcount > 0
        finally:
            connection.close()
