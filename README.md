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
│   ├── controller/
│   │   └── simulaciones_credito_controller.py
│   ├── model/
│   │   └── logica_credito.py
│   └── view/
│       └── console/
│           └── consola_credito.py
├── test/
│   ├── test_simulaciones_credito_controller.py
│   └── test_credito.py
├── sql/
│   ├── crear_simulaciones_credito.sql
│   ├── insertar_simulacion_credito.sql
│   └── buscar_simulaciones_credito.sql
├── doc/
│   ├── Casos de prueba credito educativo.xlsx
│   └── Entrevista parte 1 y 2 (audio)
└── README.md
```

---

## Pruebas Unitarias

Las pruebas automatizadas usan `unittest`: `test/test_credito.py` cubre los
cálculos del crédito educativo y `test/test_simulaciones_credito_controller.py`
verifica el guardado, consulta y eliminación del historial con una conexión
simulada, sin necesitar una base de datos activa.

Desde la raíz del proyecto, ejecute:

```
python -m unittest test.test_credito test.test_simulaciones_credito_controller
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

---

## Historial de simulaciones ICETEX

El controlador guarda el valor de matrícula por semestre, la cantidad de
semestres, la tasa mensual, el plazo, el periodo de gracia y los resultados de
la simulación. No almacena datos de tarjetas de crédito. Los métodos disponibles
son `guardar(solicitud)`, `listar()`, `buscar(id_simulacion)` y
`eliminar(id_simulacion)`.

Para habilitar PostgreSQL:

1. Instale el controlador de base de datos con `pip install -r requirements.txt`.
2. Configure la variable de entorno `DATABASE_URL` con la cadena de conexión
   de su base PostgreSQL (`postgresql://usuario:contraseña@host:5432/base`).
   No incluya credenciales directamente en el código.
3. Ejecute `sql/crear_simulaciones_credito.sql` contra esa base de datos.
4. Corra las pruebas con `python -m unittest test.test_credito test.test_simulaciones_credito_controller`.

El historial puede usarse desde Python construyendo una instancia de
`SolicitudCredito` del modelo y pasándola a
`SimulacionesCreditoController.guardar()`. Los scripts restantes permiten
insertar una simulación de ejemplo y consultar el historial directamente desde
PostgreSQL.