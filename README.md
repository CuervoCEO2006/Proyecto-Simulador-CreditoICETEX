# Simulador de Crédito Educativo

---

## Integrantes

- Juan José Camargo Chaverra
- Juan José Cuervo Osorio
- Thomas Leon Torres
- Juan Esteban Correa Guzman

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
│   ├── controller/
│   │   └── simulaciones_credito_controller.py
│   ├── model/
│   │   └── logica_credito.py
│   └── view/
│       ├── console/
│       │   └── consola_credito.py
│       └── gui/
│           └── creditoicetex_gui.py
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

---

## Instrucciones para ejecutar la interfaz Gráfica (GUI)
 
La interfaz gráfica está en `src/view/gui/creditoicetex_gui.py`. Usa la
librería `kivy` y reutiliza las mismas funciones de `src/model/logica_credito.py`
que usa la consola, así que produce siempre los mismos resultados.
 
### Requisitos
 
Instale kivy si no lo tiene:
 
```
pip install kivy
```
 
### Cómo ejecutarla
 
Ubíquese en la raíz del proyecto y ejecute:
 
```
python src/view/gui/creditoicetex_gui.py
```
 
### Uso
 
1. Ingrese el monto del crédito, la tasa de interés mensual (como número,
   ej. `1.5`) y el número de cuotas. Cada campo muestra un texto de ejemplo
   (`hint_text`) y solo acepta caracteres numéricos.
2. Dé clic en el botón **Calcular**.
3. Si los datos son válidos, se muestran en **verde** la cuota mensual, el
   total pagado y el total de intereses, con formato de moneda
   (separador de miles).
4. Si algún dato es inválido (monto en cero, tasa negativa, plazo menor a 1,
   o un campo vacío), se muestra en **rojo** un mensaje de error amigable,
   sin detalles técnicos, en vez de un resultado numérico.
5. Dé clic en el botón **Ver Tabla** para abrir una ventana emergente con la
   tabla de amortización completa. La tabla muestra, para cada mes:
   - **Mes:** número de la cuota.
   - **Cuota:** valor total de la cuota (interés + abono a capital).
   - **Interés:** porción de la cuota destinada a intereses.
   - **Capital:** porción de la cuota que abona al saldo del crédito.
   - **Saldo:** saldo restante del crédito después del abono.
6. El botón **Limpiar** borra los tres campos y el resultado, para hacer
   una nueva simulación sin cerrar la aplicación.
### Funcionalidades destacadas de la GUI
 
- **Validación en el teclado:** los campos de monto y tasa solo aceptan
  números decimales, y el campo de cuotas solo acepta números enteros
  (`input_filter`), evitando errores de digitación antes de calcular.
- **Retroalimentación visual:** el resultado cambia de color según si el
  cálculo fue exitoso (verde) o hubo un error (rojo).
- **Tabla de amortización:** ventana emergente con scroll que detalla
  mes a mes la composición de cada cuota (interés, capital y saldo).
- **Botón Limpiar:** funcionalidad adicional para reiniciar el formulario
  sin reiniciar la aplicación.
- **Manejo de excepciones:** cada excepción del modelo (`MontoInvalido`,
  `TasaInvalida`, `PlazoInvalido`) se traduce a un mensaje de error simple
  y comprensible para el usuario final.
### Ejemplo de ejecución
 
Con los valores:
 
```
Monto del credito: 10000000
Tasa de interes mensual del credito: 1.5
Numero de cuotas: 24
```
 
Al dar clic en **Calcular**, se muestra en verde:
 
```
Cuota mensual: $ 499,241.02
Total pagado: $ 11,981,784.47
Total intereses: $ 1,981,784.47
```

Al dar clic en **Ver Tabla**, se abre una ventana con la tabla de amortización:

```
Mes  |  Cuota        |  Interés      |  Capital      |  Saldo
1    |  $499,241.02  |  $150,000.00  |  $349,241.02  |  $9,650,758.98
2    |  $499,241.02  |  $144,761.38  |  $354,479.64  |  $9,296,279.35
...  |  ...          |  ...          |  ...          |  ...
24   |  $499,241.02  |  $7,362.06    |  $491,878.96  |  $0.00
```
