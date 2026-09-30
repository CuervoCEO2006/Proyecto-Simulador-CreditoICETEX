# Simulador de Crédito Educativo

---

## Integrantes

- Juan José Camargo Chaverra
- Juan José Cuervo Osorio

---

## Descripción

Aplicación en Python que calcula la cuota mensual fija que debe pagar un estudiante para cancelar un crédito educativo, usando el sistema de amortización francesa (cuota fija).

A diferencia de un crédito tradicional, ICETEX no desembolsa el valor completo de la carrera al inicio: gira el valor de la matrícula semestre a semestre. Cada desembolso empieza a generar intereses desde el momento en que se entrega, y esos intereses se capitalizan durante el resto de la carrera y durante el período de gracia, hasta que el estudiante empieza a pagar cuotas. Solo en ese momento se consolida la deuda total y se calcula la cuota fija mensual.

Además de la cuota, la aplicación calcula el total de intereses pagados y el total pagado al finalizar el crédito
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

## Pruebas Unitarias

Las pruebas unitarias automatizadas se encuentran en `test/test_credito.py`, y usan
la libreria `unittest` de Python para validar las funciones de `src/model/logica_credito.py`.

### Distribución de las pruebas

| Tipo de prueba | Descripción |
|---|---|
| Normal | `test_normal_1`: crédito de $10.000.000, tasa 1.5% mensual, plazo de 24 meses |
| Normal | `test_normal_2`: crédito de $5.000.000, tasa 1% mensual, plazo de 12 meses |
| Normal | `test_normal_3`: crédito de $20.000.000, tasa 1.25% mensual, plazo de 36 meses |
| Excepcional | `test_tasa_cero`: tasa de interés en 0%, la cuota se calcula como monto / plazo |
| Excepcional | `test_cuota_unica`: crédito a pagar en una sola cuota (plazo = 1) |
| Excepcional | `test_credito_alto_plazo_largo`: monto alto ($25.000.000) a un plazo largo (60 meses) |
| Error | `test_monto_cero`: el monto del crédito es cero, debe lanzar `MontoInvalido` |
| Error | `test_tasa_negativa`: la tasa de interés es negativa, debe lanzar `TasaInvalida` |
| Error | `test_plazo_cero`: el plazo es cero, debe lanzar `PlazoInvalido` |
| Error | `test_plazo_negativo`: el plazo es negativo, debe lanzar `PlazoInvalido` |

### Instrucciones para ejecutar las pruebas

Ubíquese en la raíz del proyecto y ejecute:

```
python test/test_credito.py
```

### Resultado esperado

Las 10 pruebas deben pasar sin errores:

```
..........
----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

---

## Entradas

| Entrada | Tipo | Descripción |
|---|---|---|
| `monto_matricula_semestre` | float | Valor de la matrícula de **un** semestre a financiar |
| `numero_semestres` | int | Número de semestres que dura la carrera (número de desembolsos que hace ICETEX) |
| `duracion_semestre_meses` | int | Duración de cada semestre en meses (valor típico: 6) |
| `tasa_interes` | float | Tasa de interés mensual en decimal (ej. `0.015` = 1.5%), aplicada tanto en la fase de estudio/gracia como en la fase de pago |
| `periodo_gracia` | int | Meses de espera adicionales para empezar a pagar, después de terminar la carrera |
| `plazo` | int | Número de cuotas mensuales para pagar el crédito ya consolidado |

---

## Proceso

### 1. Validación
Se verifica que:
- `monto_matricula_semestre` > 0 (si no, `MontoInvalido`)
- `numero_semestres` > 0 (si no, `NumeroSemestresInvalido`)
- `tasa_interes` >= 0 (si no, `TasaInvalida`)
- `plazo` > 0 (si no, `PlazoInvalido`)

Si algo falla, se lanza la excepción correspondiente con un mensaje explicando
el error, igual que en la versión anterior.

### 2. Capitalización de cada desembolso semestral
Por cada semestre `k` (desde `1` hasta `numero_semestres`), el desembolso hecho
en ese semestre queda expuesto a interés desde que se gira hasta que empieza el
pago. Los meses de capitalización de ese desembolso son:

```
meses_capitalizacion_k = (numero_semestres - k) * duracion_semestre_meses + periodo_gracia
```

Y su valor futuro al momento de empezar a pagar es:

```
valor_futuro_k = monto_matricula_semestre * (1 + tasa_interes) ** meses_capitalizacion_k
```

(Si `tasa_interes = 0`, `valor_futuro_k = monto_matricula_semestre` para todo `k`.)

### 3. Monto consolidado
Se suman los valores futuros de todos los desembolsos:

```
monto_consolidado = Σ valor_futuro_k   (k = 1 .. numero_semestres)
```

Este es el monto sobre el que se calcula la cuota fija, **no** la suma nominal
de las matrículas.

### 4. Cálculo de la cuota (sin cambios respecto a la versión anterior)
Se aplica la fórmula de amortización francesa sobre el monto consolidado:

```
Cuota = (monto_consolidado * i) / (1 - (1 + i) ** (-n))
```

Donde `i` es la tasa de interés mensual y `n` es `plazo`. Si `i = 0`, se usa:
**Cuota = monto_consolidado / n**.

### 5. Total pagado e intereses
- `total_pagado = Cuota * plazo`
- `total_matriculas = monto_matricula_semestre * numero_semestres` (suma nominal, sin intereses)
- `total_intereses = total_pagado - total_matriculas`

Así, `total_intereses` refleja tanto los intereses capitalizados durante la
carrera/período de gracia como los intereses de la fase de pago.

---

## Salidas

- **Cuota mensual:** valor fijo que el estudiante debe pagar cada mes.
- **Total de intereses:** dinero adicional pagado por encima de la suma nominal de las matrículas.
- **Total pagado:** suma de todas las cuotas pagadas durante el plazo.

En caso de datos inválidos, el sistema muestra un mensaje de error indicando qué dato causó el problema.

---

## Instrucciones para ejecutar la interfaz de Consola

La interfaz de usuario se encuentra en `src/view/console/consola_credito.py`.
Se encarga de pedir los datos al usuario, llamar a las funciones de
`src/model/logica_credito.py` y mostrar los resultados o el error correspondiente.

### Cómo ejecutarla

Ubíquese en la raíz del proyecto y ejecute:

```
python src/view/console/consola_credito.py
```

### Menú principal (lo que se muestra al iniciar)

Al ejecutar el programa, lo primero que se muestra es un mensaje de bienvenida
seguido de las tres preguntas para ingresar los datos del crédito:

```
Este programa le permite calcular la cuota a pagar por un credito educativo
Monto del credito:
Tasa de interes mensual del credito:
Numero de cuotas en que va a pagar el credito:
```

### Proceso de cálculo

1. El programa pide el monto del crédito, la tasa de interés mensual (se ingresa
   como número entero, ej. `1.5`, y el programa la divide entre 100) y el número
   de cuotas.
2. Con esos datos llama a `calcular_cuota()`, `calcular_total_pagado()` y
   `calcular_total_intereses()` del módulo `logica_credito`.
3. Si algún dato es inválido, el modelo lanza una excepción (`MontoInvalido`,
   `PlazoInvalido` o `TasaInvalida`), que la consola captura y muestra como
   mensaje de error en vez de un resultado numérico.
4. Si los datos son válidos, se muestran los tres resultados en pantalla.

### Ejemplo de ejecución

```
Este programa le permite calcular la cuota a pagar por un credito educativo
Monto del credito: 10000000
Tasa de interes mensual del credito: 1.5
Numero de cuotas en que va a pagar el credito: 24
La cuota mensual a pagar es de: 499241.02
El total pagado al final del credito es de: 11981784.47
El total de intereses pagados es de: 1981784.47
```

Ejemplo con un dato inválido:

```
Este programa le permite calcular la cuota a pagar por un credito educativo
Monto del credito: 0
Tasa de interes mensual del credito: 1.5
Numero de cuotas en que va a pagar el credito: 24
No se pudo calcular la cuota
MontoInvalido: se recibio monto_credito=0.0, pero el monto del credito debe ser mayor que cero. Ocurrio en validar_monto_credito(), llamada desde calcular_cuota(). Solucion: ingrese un monto de credito positivo.
```
