MONTO_MINIMO = 0
CANTIDAD_CUOTAS_MINIMA = 1
TASA_MINIMA = 0


class MontoInvalido(Exception):
    """ Se dispara cuando el monto del credito es menor o igual a cero """
    def __init__(self, monto_credito: float):
        super().__init__(
            f"MontoInvalido: se recibio monto_credito={monto_credito}, pero el monto del "
            f"credito debe ser mayor que {MONTO_MINIMO}. Ocurrio en validar_monto_credito(), "
            f"llamada desde calcular_cuota(). Solucion: ingrese un monto de credito positivo."
        )


class PlazoInvalido(Exception):
    """ Se dispara cuando la cantidad de cuotas es menor que uno """
    def __init__(self, cantidad_cuotas: int):
        super().__init__(
            f"PlazoInvalido: se recibio cantidad_cuotas={cantidad_cuotas}, pero el numero de "
            f"cuotas debe ser mayor o igual a {CANTIDAD_CUOTAS_MINIMA}. Ocurrio en "
            f"validar_cantidad_cuotas(), llamada desde calcular_cuota(). "
            f"Solucion: ingrese un plazo de al menos {CANTIDAD_CUOTAS_MINIMA} mes."
        )


class TasaInvalida(Exception):
    """ Se dispara cuando la tasa de interes mensual ingresada es negativa """
    def __init__(self, tasa_interes_mensual: float):
        super().__init__(
            f"TasaInvalida: se recibio tasa_interes_mensual={tasa_interes_mensual} "
            f"({tasa_interes_mensual * 100}%), pero la tasa de interes no puede ser menor que "
            f"{TASA_MINIMA}. Ocurrio en validar_tasa_interes(), llamada desde calcular_cuota(). "
            f"Solucion: ingrese una tasa mayor o igual a {TASA_MINIMA}."
        )


def validar_monto_credito(monto_credito: float) -> None:
    """ Verifica que el monto del credito sea mayor que el minimo permitido. No calcula nada. """
    if monto_credito <= MONTO_MINIMO:
        raise MontoInvalido(monto_credito)


def validar_cantidad_cuotas(cantidad_cuotas: int) -> None:
    """ Verifica que la cantidad de cuotas sea al menos la minima permitida. No calcula nada. """
    if cantidad_cuotas < CANTIDAD_CUOTAS_MINIMA:
        raise PlazoInvalido(cantidad_cuotas)


def validar_tasa_interes(tasa_interes_mensual: float) -> None:
    """ Verifica que la tasa de interes no sea menor que la minima permitida. No calcula nada. """
    if tasa_interes_mensual < TASA_MINIMA:
        raise TasaInvalida(tasa_interes_mensual)


def validar_parametros_credito(monto_credito: float, tasa_interes_mensual: float, cantidad_cuotas: int) -> None:
    """ Orquesta las tres validaciones individuales. No calcula nada. """
    validar_monto_credito(monto_credito)
    validar_cantidad_cuotas(cantidad_cuotas)
    validar_tasa_interes(tasa_interes_mensual)


def calcular_cuota(monto_credito: float, tasa_interes_mensual: float, cantidad_cuotas: int) -> float:
    """
    Calcula la cuota mensual fija a pagar por un credito educativo
    monto_credito : Valor total desembolsado del credito
    tasa_interes_mensual : Tasa de interes mensual en decimal (ej. 0.015 = 1.5%)
    cantidad_cuotas : numero de cuotas mensuales para pagar el credito

    El resultado no esta redondeado
    """
    validar_parametros_credito(monto_credito, tasa_interes_mensual, cantidad_cuotas)

    if tasa_interes_mensual == TASA_MINIMA:
        """
        Cuando la tasa sea la minima (cero), la cuota es el monto dividido entre las cuotas
        para evitar error de division por cero
        """
        return monto_credito / cantidad_cuotas
    else:
        return (monto_credito * tasa_interes_mensual) / (1 - (1 + tasa_interes_mensual) ** (-cantidad_cuotas))


def calcular_total_pagado(monto_credito: float, tasa_interes_mensual: float, cantidad_cuotas: int) -> float:
    cuota = calcular_cuota(monto_credito, tasa_interes_mensual, cantidad_cuotas)
    return cuota * cantidad_cuotas


def calcular_total_intereses(monto_credito: float, tasa_interes_mensual: float, cantidad_cuotas: int) -> float:
    total_pagado = calcular_total_pagado(monto_credito, tasa_interes_mensual, cantidad_cuotas)
    return total_pagado - monto_credito