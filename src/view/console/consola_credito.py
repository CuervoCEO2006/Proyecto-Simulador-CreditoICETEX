import sys
sys.path.append('src')

from model import logica_credito


try:
    print("Este programa le permite calcular la cuota a pagar por un credito educativo")
    monto_credito = float(input("Monto del credito: "))
    tasa_mensual = float(input("Tasa de interes mensual del credito: ")) / 100
    plazo = int(input("Numero de cuotas en que va a pagar el credito: "))

    cuota = round(logica_credito.calcular_cuota(monto_credito, tasa_mensual, plazo), 2)
    total_abonos = round(logica_credito.calcular_total_abonos(monto_credito, tasa_mensual, plazo), 2)
    total_intereses = round(logica_credito.calcular_total_intereses(monto_credito, tasa_mensual, plazo), 2)

    print(f"La cuota mensual a pagar es de: {cuota}")
    print(f"El total pagado al final del credito es de: {total_abonos}")
    print(f"El total de intereses pagados es de: {total_intereses}")
except Exception as err:
    print("No se pudo calcular la cuota")
    print(str(err))
