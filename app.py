import sys
from threading import Lock
from pathlib import Path

from flask import Flask, render_template, request

project_root = Path(__file__).resolve().parent
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


app = Flask(__name__)
_database_initialization_lock = Lock()


@app.before_request
def inicializar_base_de_datos():
    if app.extensions.get("simulaciones_credito_inicializadas"):
        return

    with _database_initialization_lock:
        if app.extensions.get("simulaciones_credito_inicializadas"):
            return
        SimulacionesCreditoController.inicializar_tabla()
        app.extensions["simulaciones_credito_inicializadas"] = True


@app.get("/")
def inicio():
    return render_template("inicio.html")


@app.get("/simular")
def mostrar_formulario():
    return render_template(
        "simulador_credito.html",
        formulario={},
        resultado=None,
        error=None,
    )


@app.get("/calcular")
def calcular():
    formulario = {
        "monto_credito_semestre": request.args.get("monto_credito_semestre", ""),
        "cantidad_semestres": request.args.get("cantidad_semestres", ""),
        "tasa_interes_mensual": request.args.get("tasa_interes_mensual", ""),
        "cantidad_cuotas": request.args.get("cantidad_cuotas", ""),
        "periodo_gracia": request.args.get("periodo_gracia", ""),
    }

    if any(value == "" for value in formulario.values()):
        return render_template(
            "simulador_credito.html",
            formulario=formulario,
            resultado=None,
            error="Completa todos los campos para calcular el crédito.",
        )

    try:
        solicitud = SolicitudCredito(
            monto_credito_semestre=float(formulario["monto_credito_semestre"]),
            cantidad_semestres=int(formulario["cantidad_semestres"]),
            tasa_interes_mensual=(
                float(formulario["tasa_interes_mensual"]) / 100
            ),
            cantidad_cuotas=int(formulario["cantidad_cuotas"]),
            periodo_gracia=int(formulario["periodo_gracia"]),
        )
        resultado = {
            "monto_total_credito": solicitud.monto_total_credito(),
            "cuota_mensual": calcular_cuota(solicitud),
            "total_pagado": calcular_total_pagado(solicitud),
            "total_intereses": calcular_total_intereses(solicitud),
        }
        id_simulacion = SimulacionesCreditoController.guardar(solicitud)
    except ValueError:
        return render_template(
            "simulador_credito.html",
            formulario=formulario,
            resultado=None,
            error="Ingresa valores numéricos válidos en todos los campos.",
        )
    except (
        MontoInvalido,
        SemestresInvalidos,
        TasaInvalida,
        PlazoInvalido,
        PeriodoGraciaInvalido,
    ) as error:
        return render_template(
            "simulador_credito.html",
            formulario=formulario,
            resultado=None,
            error=str(error),
        )
    except RuntimeError as error:
        return render_template(
            "simulador_credito.html",
            formulario=formulario,
            resultado=None,
            error=f"No se pudo guardar la simulación: {error}",
        )

    return render_template(
        "simulacion_guardada.html",
        solicitud=solicitud,
        resultado=resultado,
        id_simulacion=id_simulacion,
    )


@app.get("/buscar")
def buscar_simulacion():
    id_solicitado = request.args.get("id_simulacion", "").strip()
    if not id_solicitado:
        return render_template(
            "simulacion_buscada.html",
            simulacion=None,
            error="Ingresa el ID de la simulación que quieres buscar.",
        )

    try:
        id_simulacion = int(id_solicitado)
    except ValueError:
        return render_template(
            "simulacion_buscada.html",
            simulacion=None,
            error="El ID de la simulación debe ser un número entero positivo.",
        )

    if id_simulacion < 1:
        return render_template(
            "simulacion_buscada.html",
            simulacion=None,
            error="El ID de la simulación debe ser un número entero positivo.",
        )

    try:
        simulacion = SimulacionesCreditoController.buscar(id_simulacion)
    except RuntimeError as error:
        return render_template(
            "simulacion_buscada.html",
            simulacion=None,
            error=f"No se pudo buscar la simulación: {error}",
        )

    if simulacion is None:
        return render_template(
            "simulacion_buscada.html",
            simulacion=None,
            error=f"No existe una simulación con el ID {id_simulacion}.",
        )

    return render_template(
        "simulacion_buscada.html",
        simulacion=simulacion,
        error=None,
    )


if __name__ == "__main__":
    app.run(debug=False)
