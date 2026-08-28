# Simulador de Crédito Educativo

---

## Integrantes

- Juan José Camargo Chaverra
- Juan José Cuervo Osorio

---

## Descripción

Aplicación en Python que calcula la cuota mensual fija que debe pagar un estudiante
para cancelar un crédito educativo en un plazo determinado, usando el sistema de
amortización francesa (cuota fija). Además del valor de la cuota, calcula el total
de intereses pagados y el total pagado al finalizar el crédito.

---

## Arquitectura del Proyecto

El proyecto separa la lógica de negocio, la interfaz de usuario y las pruebas en
capas independientes:

```
Proyecto-Simulador-CreditoICETEX/
├── src/
│   ├── model/
│   │   └── logica_credito.py
│   └── view/
│       └── console/
│           └── consola_credito.py
├── test/
│   └── test_credito.py
├── doc/
│   ├── Casos de prueba credito educativo.xlsx
│   └── Entrevista parte 1 y 2 (audio)
└── README.md
```



---

## Entradas

| Entrada | Tipo | Descripción |
|---|---|---|
| `monto_credito_semestre` | float | Valor de matricula del semestre a financiar |
| `tasa_interes` | float | Tasa de interés mensual en decimal (ej. `0.015` = 1.5%) |
| `plazo` | int | Número de cuotas mensuales para pagar el crédito |
| `periodo_gracia` | int | Tiempo de espera para comenzar a pagar. Empieza al terminar la carrera. |

---

## Proceso

El sistema calcula la cuota mensual fija usando el sistema de amortización francesa:

```
Cuota = (Monto * i) / (1 - (1 + i) ** (-n))
```

Donde `Monto` es el valor del crédito, `i` es la tasa de interés mensual y `n` es el plazo en meses.
Si la tasa es 0%, se usa: **Cuota = Monto / n**.

Pasos:

1. **Validación:** se verifica que el monto y el plazo sean mayores que cero y que la tasa no sea negativa. Si algo falla, se lanza una excepción personalizada (`MontoInvalido`, `PlazoInvalido` o `TasaInvalida`) con un mensaje explicando el error.
2. **Cálculo de la cuota:** se aplica la fórmula de amortización francesa.
3. **Cálculo del total pagado:** se multiplica la cuota por el número de meses.
4. **Cálculo de intereses:** se resta el monto del crédito al total pagado.

---

## Salidas

- **Cuota mensual:** valor fijo que el estudiante debe pagar cada mes.
- **Total de intereses:** dinero adicional pagado por encima del monto del crédito.
- **Total pagado:** suma de todas las cuotas pagadas durante el plazo.

En caso de datos inválidos, el sistema muestra un mensaje de error indicando qué dato causó el problema.