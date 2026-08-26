class MontoInvalido(Exception):
    """ Excepcion que se dispara cuando el monto del credito es cero o negativo """

class PlazoInvalido(Exception):
    """ Excepcion que se dispara cuando el numero de cuotas es menor que uno """

class TasaInvalida(Exception):
    """ Se dispara cuando la tasa de interes ingresada es negativa """

# Exepcion personalizada que se usa en un caso de error particular
def calcular_cuota(monto_credito: float, tasa_interes_mensual: float, cantidad_cuotas: int) -> float:
    """
    Calcula la cuota mensual fija a pagar por un credito educativo
    monto_credito : Valor total desembolsado del credito
    tasa_interes_mensual : Tasa de interes mensual en decimal (ej. 0.015 = 1.5%)
    cantidad_cuotas : numero de cuotas mensuales para pagar el credito

    El resultado no esta redondeado
    """
    if monto_credito <= 0:
        #### RETORNAR UN ERROR
        raise MontoInvalido("El monto del credito debe ser mayor que cero")

    if cantidad_cuotas < 1:
        raise PlazoInvalido("El numero de cuotas debe ser mayor a cero")

    if tasa_interes_mensual < 0:
        raise TasaInvalida(f"La tasa de interes ingresada {tasa_interes_mensual * 100}% no puede ser negativa")

    if tasa_interes_mensual == 0:
        """
        Cuando la tasa sea cero, la cuota es el monto dividido entre las cuotas
        para evitar error de division por cero
        """
        return monto_credito / cantidad_cuotas
    else:
        return (monto_credito * tasa_interes_mensual) / (1 - (1 + tasa_interes_mensual) ** (-cantidad_cuotas))


def calcular_total_abonos(monto_credito: float, tasa_interes_mensual: float, cantidad_cuotas: int) -> float:
    cuota = calcular_cuota(monto_credito, tasa_interes_mensual, cantidad_cuotas)
    return cuota * cantidad_cuotas


def calcular_total_intereses(monto_credito: float, tasa_interes_mensual: float, cantidad_cuotas: int) -> float:
    total_abonos = calcular_total_abonos(monto_credito, tasa_interes_mensual, cantidad_cuotas)
    return total_abonos - monto_credito