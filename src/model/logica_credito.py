MONTO_MINIMO = 0
SEMESTRES_MINIMOS = 1
CANTIDAD_CUOTAS_MINIMA = 1
TASA_MINIMA = 0
PERIODO_GRACIA_MINIMO = 0


class MontoInvalido(Exception):
    """ Se dispara cuando el monto del credito por semestre es menor o igual a cero """
    def __init__(self, monto_credito_semestre: float):
        super().__init__(
            f"MontoInvalido: se recibio monto_credito_semestre={monto_credito_semestre}, pero "
            f"el monto del credito debe ser mayor que {MONTO_MINIMO}. Ocurrio en "
            f"validar_monto_credito_semestre(), llamada desde calcular_cuota(). "
            f"Solucion: ingrese un monto de credito positivo."
        )


class SemestresInvalidos(Exception):
    """ Se dispara cuando la cantidad de semestres a financiar es menor que uno """
    def __init__(self, cantidad_semestres: int):
        super().__init__(
            f"SemestresInvalidos: se recibio cantidad_semestres={cantidad_semestres}, pero debe "
            f"ser mayor o igual a {SEMESTRES_MINIMOS}. Ocurrio en validar_cantidad_semestres(), "
            f"llamada desde calcular_cuota(). "
            f"Solucion: ingrese la cantidad de semestres que va a financiar (al menos 1)."
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


class PeriodoGraciaInvalido(Exception):
    """ Se dispara cuando el periodo de gracia ingresado es negativo """
    def __init__(self, periodo_gracia: int):
        super().__init__(
            f"PeriodoGraciaInvalido: se recibio periodo_gracia={periodo_gracia}, pero no puede "
            f"ser menor que {PERIODO_GRACIA_MINIMO}. Ocurrio en validar_periodo_gracia(), "
            f"llamada desde calcular_cuota(). "
            f"Solucion: ingrese 0 si no hay periodo de gracia, o un numero positivo de meses."
        )


class SolicitudCredito:
    """
    Agrupa los datos de entrada necesarios para simular un credito educativo.
    No calcula nada, solo representa la informacion que el usuario ingresa.
    """
    def __init__(
        self,
        monto_credito_semestre: float,
        cantidad_semestres: int,
        tasa_interes_mensual: float,
        cantidad_cuotas: int,
        periodo_gracia: int,
    ):
        self.monto_credito_semestre = monto_credito_semestre
        self.cantidad_semestres = cantidad_semestres
        self.tasa_interes_mensual = tasa_interes_mensual
        self.cantidad_cuotas = cantidad_cuotas
        self.periodo_gracia = periodo_gracia

    def monto_total_credito(self) -> float:
        """ Valor total desembolsado: lo que vale cada semestre por la cantidad de semestres. """
        return self.monto_credito_semestre * self.cantidad_semestres

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SolicitudCredito):
            return NotImplemented
        return (
            self.monto_credito_semestre == other.monto_credito_semestre
            and self.cantidad_semestres == other.cantidad_semestres
            and self.tasa_interes_mensual == other.tasa_interes_mensual
            and self.cantidad_cuotas == other.cantidad_cuotas
            and self.periodo_gracia == other.periodo_gracia
        )


def validar_monto_credito_semestre(monto_credito_semestre: float) -> None:
    """ Verifica que el valor del semestre sea mayor que el minimo permitido. No calcula nada. """
    if monto_credito_semestre <= MONTO_MINIMO:
        raise MontoInvalido(monto_credito_semestre)


def validar_cantidad_semestres(cantidad_semestres: int) -> None:
    """ Verifica que la cantidad de semestres a financiar sea al menos la minima. No calcula nada. """
    if cantidad_semestres < SEMESTRES_MINIMOS:
        raise SemestresInvalidos(cantidad_semestres)


def validar_cantidad_cuotas(cantidad_cuotas: int) -> None:
    """ Verifica que la cantidad de cuotas sea al menos la minima permitida. No calcula nada. """
    if cantidad_cuotas < CANTIDAD_CUOTAS_MINIMA:
        raise PlazoInvalido(cantidad_cuotas)


def validar_tasa_interes(tasa_interes_mensual: float) -> None:
    """ Verifica que la tasa de interes no sea menor que la minima permitida. No calcula nada. """
    if tasa_interes_mensual < TASA_MINIMA:
        raise TasaInvalida(tasa_interes_mensual)


def validar_periodo_gracia(periodo_gracia: int) -> None:
    """ Verifica que el periodo de gracia no sea negativo. No calcula nada. """
    if periodo_gracia < PERIODO_GRACIA_MINIMO:
        raise PeriodoGraciaInvalido(periodo_gracia)


def validar_solicitud_credito(solicitud: SolicitudCredito) -> None:
    """ Orquesta las cinco validaciones individuales sobre la solicitud. No calcula nada. """
    validar_monto_credito_semestre(solicitud.monto_credito_semestre)
    validar_cantidad_semestres(solicitud.cantidad_semestres)
    validar_tasa_interes(solicitud.tasa_interes_mensual)
    validar_cantidad_cuotas(solicitud.cantidad_cuotas)
    validar_periodo_gracia(solicitud.periodo_gracia)


def calcular_saldo_despues_de_gracia(solicitud: SolicitudCredito) -> float:
    """
    Calcula el saldo de la deuda una vez termina el periodo de gracia.
    Durante el periodo de gracia el estudiante no paga, pero los intereses se
    siguen generando y se capitalizan mes a mes sobre el monto total del credito.
    """
    monto_total = solicitud.monto_total_credito()

    if solicitud.periodo_gracia == PERIODO_GRACIA_MINIMO:
        return monto_total

    return monto_total * (1 + solicitud.tasa_interes_mensual) ** solicitud.periodo_gracia


def calcular_cuota(solicitud: SolicitudCredito) -> float:
    """
    Calcula la cuota mensual fija a pagar por un credito educativo, una vez
    terminado el periodo de gracia, usando el sistema de amortizacion francesa
    sobre el saldo ya capitalizado.

    El resultado no esta redondeado
    """
    validar_solicitud_credito(solicitud)

    saldo_a_financiar = calcular_saldo_despues_de_gracia(solicitud)
    tasa = solicitud.tasa_interes_mensual
    cuotas = solicitud.cantidad_cuotas

    if tasa == TASA_MINIMA:
        """
        Cuando la tasa sea la minima (cero), la cuota es el saldo dividido entre
        las cuotas, para evitar error de division por cero
        """
        return saldo_a_financiar / cuotas
    else:
        return (saldo_a_financiar * tasa) / (1 - (1 + tasa) ** (-cuotas))


def calcular_total_pagado(solicitud: SolicitudCredito) -> float:
    cuota = calcular_cuota(solicitud)
    return cuota * solicitud.cantidad_cuotas


def calcular_total_intereses(solicitud: SolicitudCredito) -> float:
    total_pagado = calcular_total_pagado(solicitud)
    return total_pagado - solicitud.monto_total_credito()