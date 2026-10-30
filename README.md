# Simulador de Crédito Educativo ICETEX

## Integrantes

- Juan José Camargo Chaverra
- Juan José Cuervo Osorio
- Thomas Leon Torres
- Juan Esteban Correa Guzman

---

## Descripción

Aplicación en Python para simular un crédito educativo. Calcula la cuota
mensual fija mediante amortización francesa a partir del valor de matrícula por
semestre, la cantidad de semestres, la tasa de interés mensual, el plazo y el
periodo de gracia.

El modelo suma los desembolsos nominales de los semestres, capitaliza ese monto
durante el periodo de gracia y calcula la cuota sobre el saldo resultante.
También presenta el monto total desembolsado, el total pagado y los intereses.

## Aplicación publicada

El simulador está disponible en
[proyecto-simulador-creditoicetex.onrender.com](https://proyecto-simulador-creditoicetex.onrender.com).

---

## Arquitectura del Proyecto

El proyecto separa la lógica de negocio, la interfaz de usuario y las pruebas en
capas independientes:

```
Proyecto-Simulador-CreditoICETEX/
├── app.py
├── templates/
│   ├── inicio.html
│   ├── simulacion_buscada.html
│   ├── simulacion_guardada.html
│   └── simulador_credito.html
├── src/
│   ├── controller/
│   │   └── simulaciones_credito_controller.py
│   ├── model/
│   │   └── logica_credito.py
│   └── view/
│       ├── console/
│       │   ├── consola_credito.py
│       │   └── historial_simulaciones.py
│       ├── gui/
│       │   └── creditoicetex_gui.py
├── test/
│   ├── test_credito.py
│   ├── test_historial_simulaciones_console.py
│   ├── test_simulaciones_credito_controller.py
│   ├── test_simulaciones_credito_postgres.py
│   └── test_web_credito.py
├── sql/
│   ├── crear_simulaciones_credito.sql
│   ├── insertar_simulacion_credito.sql
│   └── buscar_simulaciones_credito.sql
├── requirements.txt
├── secret_config_sample.py
├── doc/
│   ├── Casos de prueba credito educativo.xlsx
│   └── Entrevista parte 1 y 2 (audio)
└── README.md
```
 
---

## Pruebas Unitarias

Las pruebas usan `unittest`. Desde la raíz, ejecute toda la suite:

```powershell
python -m unittest discover -s test -p "test_*.py"
```

Las pruebas que requieren PostgreSQL se omiten, salvo que se habiliten
explícitamente; consulte [Pruebas de integración con PostgreSQL](#pruebas-de-integración-con-postgresql).

---

## Entradas

| Entrada | Tipo | Descripción |
|---|---|---|
| `monto_credito_semestre` | decimal | Valor de matrícula de cada semestre |
| `cantidad_semestres` | entero | Número de semestres financiados |
| `tasa_interes_mensual` | decimal | Tasa mensual en decimal; por ejemplo, `0.01` equivale a 1% |
| `cantidad_cuotas` | entero | Número de cuotas mensuales |
| `periodo_gracia` | entero | Meses de gracia antes de iniciar los pagos |

---

## Proceso

El modelo valida que el monto sea positivo, que haya al menos un semestre y una
cuota, que la tasa no sea negativa y que el periodo de gracia no sea negativo.
Si la tasa mensual es `i`, el monto por semestre es `m`, hay `s` semestres, el
periodo de gracia es `g` meses y el plazo es `n` cuotas, calcula:

```
monto_total_credito = m * s
saldo_despues_de_gracia = monto_total_credito * (1 + i) ** g
```

La cuota fija usa la fórmula de amortización francesa:

```
cuota = saldo_despues_de_gracia * i / (1 - (1 + i) ** (-n))
```

Si `i = 0`, la cuota es `saldo_despues_de_gracia / n`. El total pagado es
`cuota * n`, y el total de intereses es `total_pagado - monto_total_credito`.

---

## Salidas

- **Cuota mensual:** valor fijo que el estudiante debe pagar cada mes.
- **Total de intereses:** diferencia entre el total pagado y el monto total nominal desembolsado.
- **Total pagado:** suma de todas las cuotas pagadas durante el plazo.

En caso de datos inválidos, el sistema muestra un mensaje de error indicando qué dato causó el problema.

---

## Interfaz de consola para calcular

Desde la raíz del proyecto, ejecute:

```powershell
python src/view/console/consola_credito.py
```

La consola solicita el valor de matrícula por semestre, la cantidad de
semestres, la tasa mensual en porcentaje, el número de cuotas y el periodo de
gracia en meses. Convierte la tasa ingresada a decimal antes de llamar al modelo.

---

## Interfaz web con Flask

La aplicación reutiliza el modelo y el controlador de simulaciones. `/` muestra
la página principal, `/simular` presenta los formularios, `/calcular` procesa y
guarda una simulación en PostgreSQL y `/buscar` consulta una simulación por ID.
La tasa se ingresa como porcentaje (por ejemplo, `1.5`) y se convierte a
decimal. En el primer acceso web se crea la tabla si hace falta mediante
`CREATE TABLE IF NOT EXISTS`, sin borrar datos de una tabla existente.

Configure PostgreSQL siguiendo la sección
[Historial de simulaciones ICETEX](#historial-de-simulaciones-icetex). Después,
desde la raíz, ejecute:

```powershell
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`. Para buscar un registro, ingrese el ID devuelto al
guardar una simulación.

---

## Historial de simulaciones ICETEX

El controlador guarda los datos de la solicitud y los resultados en la tabla
`simulaciones_credito`. La tabla tiene un ID y fecha generados por PostgreSQL.
El proyecto no almacena datos de tarjetas de crédito. El controlador permite
guardar, listar, buscar por ID y eliminar simulaciones.

Para usar PostgreSQL localmente:

1. Instale las dependencias con `pip install -r requirements.txt`.
2. Copie `secret_config_sample.py` como `secret_config.py` en la raíz del
   proyecto y complete los datos locales de conexión. `secret_config.py` se
   ignora en Git; no comparta ni suba sus credenciales.
3. La tabla se crea automáticamente en el primer acceso web. También puede
   ejecutarse manualmente `sql/crear_simulaciones_credito.sql`.

### Pruebas de integración con PostgreSQL

Las pruebas de integración recrean la tabla antes de cada caso y limpian sus
datos al terminar. Para proteger otras bases, solo se ejecutan contra una base
cuyo nombre termine en `_test`. Configure las credenciales de esa base en
`secret_config.py` y actívelas en PowerShell:

```powershell
$env:RUN_POSTGRES_TESTS = "1"
python -m unittest test.test_simulaciones_credito_postgres
```

### Guardar y buscar desde la consola

Para registrar una simulación o buscarla por el ID que genera la base de datos:

```powershell
python src/view/console/historial_simulaciones.py
```

La opción de guardar solicita los datos del crédito, calcula la cuota y guarda
la simulación. La opción de búsqueda muestra los datos y resultados persistidos.

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
