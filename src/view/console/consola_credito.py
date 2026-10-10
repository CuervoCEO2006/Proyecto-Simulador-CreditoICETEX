import sys
sys.path.append('src')

from model.logica_credito import SolicitudCredito, calcular_cuota, calcular_total_pagado, calcular_total_intereses


try:
    print("Este programa le permite calcular la cuota a pagar por un credito educativo")
    monto_credito_semestre = float(input("Valor del semestre a financiar: "))
    cantidad_semestres = int(input("Cantidad de semestres a financiar: "))
    tasa_interes_mensual = float(input("Tasa de interes mensual del credito: ")) / 100
    cantidad_cuotas = int(input("Numero de cuotas en que va a pagar el credito: "))
    periodo_gracia = int(input("Periodo de gracia en meses (0 si no aplica): "))

    solicitud = SolicitudCredito(
        monto_credito_semestre,
        cantidad_semestres,
        tasa_interes_mensual,
        cantidad_cuotas,
        periodo_gracia,
    )

    cuota = round(calcular_cuota(solicitud), 2)
    total_pagado = round(calcular_total_pagado(solicitud), 2)
    total_intereses = round(calcular_total_intereses(solicitud), 2)

    print(f"La cuota mensual a pagar es de: {cuota}")
    print(f"El total pagado al final del credito es de: {total_pagado}")
    print(f"El total de intereses pagados es de: {total_intereses}")
except Exception as err:
    print("No se pudo calcular la cuota")
    print(str(err))
