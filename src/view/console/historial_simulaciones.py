import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from controller.simulaciones_credito_controller import SimulacionesCreditoController
from model.logica_credito import (
    MontoInvalido,
    PeriodoGraciaInvalido,
    PlazoInvalido,
    SemestresInvalidos,
    SolicitudCredito,
    TasaInvalida,
    calcular_cuota,
    calcular_total_intereses,
    calcular_total_pagado,
)


def _guardar_simulacion() -> None:
    try:
        monto_semestre = float(input("Valor del semestre a financiar: "))
        semestres = int(input("Cantidad de semestres a financiar: "))
        tasa_mensual = float(input("Tasa de interes mensual (%): ")) / 100
        cuotas = int(input("Numero de cuotas: "))
        periodo_gracia = int(input("Periodo de gracia en meses: "))
    except ValueError:
        print("Entrada invalida: ingresa numeros validos.")
        return

    solicitud = SolicitudCredito(
        monto_semestre,
        semestres,
        tasa_mensual,
        cuotas,
        periodo_gracia,
    )
    try:
        id_simulacion = SimulacionesCreditoController.guardar(solicitud)
    except (
        MontoInvalido,
        SemestresInvalidos,
        TasaInvalida,
        PlazoInvalido,
        PeriodoGraciaInvalido,
        RuntimeError,
    ) as error:
        print(f"No se pudo guardar la simulacion: {error}")
        return

    print(f"Simulacion guardada con ID: {id_simulacion}")
    print(f"Cuota mensual: {calcular_cuota(solicitud):,.2f}")
    print(f"Total pagado: {calcular_total_pagado(solicitud):,.2f}")
    print(f"Total intereses: {calcular_total_intereses(solicitud):,.2f}")


def _buscar_simulacion() -> None:
    try:
        id_simulacion = int(input("ID de la simulacion: "))
    except ValueError:
        print("El ID debe ser un numero entero.")
        return

    try:
        simulacion = SimulacionesCreditoController.buscar(id_simulacion)
    except RuntimeError as error:
        print(f"No se pudo buscar la simulacion: {error}")
        return

    if simulacion is None:
        print(f"No existe una simulacion con ID {id_simulacion}.")
        return

    print(f"ID: {simulacion['id']}")
    print(f"Fecha: {simulacion['fecha_simulacion']}")
    print(f"Valor por semestre: {simulacion['monto_credito_semestre']:,.2f}")
    print(f"Semestres: {simulacion['cantidad_semestres']}")
    print(f"Total desembolsado: {simulacion['monto_total_credito']:,.2f}")
    print(f"Tasa mensual: {simulacion['tasa_interes_mensual'] * 100:.2f}%")
    print(f"Cuotas: {simulacion['cantidad_cuotas']}")
    print(f"Periodo de gracia: {simulacion['periodo_gracia']} meses")
    print(f"Cuota mensual: {simulacion['cuota_mensual']:,.2f}")
    print(f"Total pagado: {simulacion['total_pagado']:,.2f}")
    print(f"Total intereses: {simulacion['total_intereses']:,.2f}")


def main() -> None:
    while True:
        print("\nHistorial de simulaciones de credito ICETEX")
        print("1. Guardar una simulacion")
        print("2. Buscar una simulacion por ID")
        print("0. Salir")
        opcion = input("Selecciona una opcion: ").strip()

        if opcion == "1":
            _guardar_simulacion()
        elif opcion == "2":
            _buscar_simulacion()
        elif opcion == "0":
            print("Hasta luego.")
            return
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
