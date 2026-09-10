# Prompts copiables: regresión avanzada distribuida y Playwright + TNZ

Estos prompts trabajan con **TransferLab, una aplicación local de entrenamiento con datos ficticios**. Se pueden usar con un asistente que tenga acceso a los archivos del proyecto. Si usas una herramienta sin acceso a tu carpeta, adjunta los archivos indicados: escribir una ruta en un prompt no permite al modelo leerla automáticamente.

Elige **un lenguaje por implementación**. Las instrucciones están en español; puedes pedir explicaciones y reportes en inglés cambiando `IDIOMA_SALIDA`. Los selectores y mensajes españoles de la aplicación deben conservarse literalmente en el código.

Los prompts solicitan trabajo y ejecución; **no son resultados de pruebas**. El inventario real de casos ejecutados está en los archivos `evidence/VERIFICATION.md` de cada laboratorio. No deduzcas que una suite existe o fue ejecutada en tres lenguajes porque un ejemplo muestra equivalencias.

## 1. Contexto común: copiar primero

Copia este bloque al comenzar la conversación. Cambia el lenguaje, el idioma de salida y el objetivo si corresponde. Reemplaza `CARPETA_BASE` por la carpeta donde guardaste los laboratorios en tu equipo; la ruta incluida muestra la ubicación de esta entrega.

```text
Actúa como ingeniero senior de automatización con Playwright y asistentes de IA.

LENGUAJE_ELEGIDO: TypeScript
Alternativas permitidas: Python o Java. Implementa solo el lenguaje elegido.
IDIOMA_SALIDA: español
Alternativa: English. Conserva literalmente etiquetas y mensajes de la aplicación.
OBJETIVO: generar, revisar y ejecutar regresión del laboratorio local TransferLab.

CARPETA_BASE:
C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos

FUENTES LOCALES QUE DEBES LEER:
1. lab\distributed\README.md
2. lab\distributed\tests\fixtures.ts
3. lab\distributed\tests\regression.spec.ts
4. lab\distributed\package.json y playwright.config.ts
5. lab\mainframe\README.md
6. lab\mainframe\adapter.py y simulator.py
7. lab\mainframe\test_hybrid_browser.py y test_core_regression.py
8. lab\mainframe\typescript\hybrid.spec.ts y playwright.config.ts
9. lab\mainframe\java\pom.xml
10. lab\mainframe\java\src\test\java\training\HybridTransferTest.java
    y CoreRegressionTest.java en la misma carpeta
11. lab\distributed\evidence\VERIFICATION.md
12. lab\mainframe\evidence\VERIFICATION.md

Las rutas de esta lista son relativas a CARPETA_BASE. Si no puedes leer un archivo,
pide su contenido y marca sus hechos como no verificados. No finjas haberlo leído.

CONTRATO DEL LABORATORIO:
- Gateway http://127.0.0.1:3000; Accounts :3001; Ledger :3002.
- Simulador TN3270 127.0.0.1:2323; cliente real IBM tnz en Python.
- Moneda MXN; importes enteros en centavos: 100000 = MXN 1000.00.
- Crear una fixture propia por caso e intento; saldo inicial 100000, cero registros.
- Autenticar el contexto del navegador con credenciales sintéticas de esa fixture.
- Usar la clave pública local de clase según README, nunca credenciales externas.
- Enviar X-Test-Hook-Key solo a las peticiones de preparación y limpieza.
- TR-01: transferir 10000; saldo 90000 y exactamente un registro correcto.
- TR-02: intentar 110000; rechazo 422 INSUFFICIENT_FUNDS, saldo 100000 y cero registros.
- TR-03: misma clave de idempotencia y mismo cuerpo, dos POST secuenciales:
  201 y luego 200, mismo id, saldo 90000 y un registro.
- GET /api/transfers es canónico e inmediato.
- GET /api/ledger/transfers es una proyección separada y eventualmente consistente.
- GET /__test/lookup consulta los MISMOS datos canónicos de Accounts en memoria.
- La pantalla TN3270 es una presentación simulada de esos datos; no existe z/OS,
  CICS, DB2, reconciliación independiente ni persistencia duradera demostrada.

RUNNERS:
- TypeScript: Playwright Test, configuración y dependencias del proyecto existente.
- Python: pytest + pytest-playwright, API síncrona y .venv del proyecto mainframe.
- Java: JUnit y Maven según el pom.xml existente; lifecycle explícito.
No traslades opciones de CLI ni comportamiento de un runner a otro sin verificarlos.

REGLAS DE TRABAJO:
1. Revisa primero fuentes y estado real. Conserva trabajo y evidencia existentes.
2. No inventes endpoints, selectores, helpers, métodos TNZ, imports o resultados.
3. Los fragmentos nuevos deben integrarse con dependencias y lifecycle reales.
4. Mantén constantes las expectativas de negocio; no uses skip o retries para ocultar fallos.
5. Esperas por condición y con plazo; polling solo de lecturas donde el contrato permite demora.
6. Conserva referencia, cuenta y moneda en cada comparación; no busques el último registro global.
7. Captura evidencia antes de borrar únicamente la fixture propia. No hagas un borrado global.
8. Conserva el fallo original y reporta por separado fallos de limpieza.
9. No pegues secretos ni datos reales en prompts, trazas o reportes compartidos.
10. Distingue generado, revisado, ejecutado, aprobado, fallido, bloqueado y no ejecutado.
11. No publiques, subas cambios ni ejecutes contra sistemas externos por inferencia.

Antes de implementar, devuelve un inventario breve: archivos leídos, casos existentes,
casos realmente ejecutados según evidencia, diferencias entre lenguajes y hechos faltantes.
```

## 2. Plan de regresión por riesgo y evidencia

```text
Usa el contexto TransferLab y los archivos que acabas de leer.

Crea una matriz de regresión para TR-01, TR-02 y TR-03. Añade filas separadas para:
a) límites de importe: cero, negativo y fracción de centavo;
b) misma clave con otro cuerpo: conflicto 409 sin segundo débito;
c) solicitud sin sesión y acceso a cuenta ajena;
d) publicación del mismo transferId en la proyección Ledger;
e) UI frente a POST 503 interceptado;
f) transferencia web seguida de consulta TNZ del mismo transferId;
g) referencia de terminal inexistente.

Para cada fila incluye: riesgo, preparación aislada, acción, endpoint o control observado,
valores esperados, política de espera, limpieza, artefacto necesario y límite de cobertura.
Clasifica obligatorio o extensión. No mezcles estos límites:
- repetir secuencialmente no demuestra protección concurrente;
- un 503 de route.fulfill no demuestra caída real del backend;
- consultar TNZ no verifica la proyección Ledger ni una base de datos independiente.

Indica qué filas ya implementa el proyecto y cuáles requieren código. Nunca marques
una fila aprobada por el simple hecho de existir en la matriz.
```

## 3. Generar los tres casos centrales completos

```text
Implementa TR-01, TR-02 y TR-03 en LENGUAJE_ELEGIDO dentro del proyecto existente.
Reutiliza los helpers observados; si falta uno, impleméntalo y explica su responsabilidad.

Primero produce una fixture completa con creación, login, evidencia y limpieza.
Usa datos nuevos por caso e intento y un contexto nuevo por prueba. Deja la cabecera
de hooks fuera de las cabeceras globales del navegador. Verifica cada respuesta de setup.

TR-01 debe usar la UI real: seleccionar Cuenta origen y Beneficiario, llenar
Importe (MXN) con 100.00, pulsar Transferir y comprobar confirmación y saldo visible.
Consulta la API canónica para demostrar saldo 90000, total 1 y el registro correcto:
sourceAccountId, beneficiaryId, amountMinor 10000, currency MXN y status COMPLETED.

TR-02 usa otra fixture e importe 1100.00. Captura el POST antes del clic, verifica
422, INSUFFICIENT_FUNDS y alerta. Demuestra saldo 100000 y colección vacía.

TR-03 usa otra fixture y dos POST autenticados con una sola clave y un solo cuerpo.
Comprueba 201/200, mismo id, saldo 90000 y un registro. Navega a /transfers antes de
comprobar la UI; no hagas reload sobre una página about:blank esperando ver el saldo.

Entrega archivos completos, imports, cambios mínimos de configuración, instrucciones
de ejecución desde la carpeta correcta y reporte del resultado real. Si puedes ejecutar,
ejecuta primero un caso y después los tres. Si no puedes, marca PENDIENTE DE EJECUCIÓN.
No cambies las expectativas para ajustarlas a un defecto observado.
```

## 4. Regresión distribuida con correlación y espera acotada

```text
Implementa una prueba de transferencia que observe Accounts y la proyección Ledger.
Lee el contrato real y conserva la diferencia entre ambos endpoints.

1. Crea una fixture aislada, autentica y realiza una transferencia de 10000.
2. Captura el transferId real de la operación; conserva sourceAccountId y currency.
3. Comprueba inmediatamente saldo 90000 y un registro en /api/transfers.
4. Consulta /api/ledger/transfers filtrando por sourceAccountId.
5. Repite SOLO esa lectura hasta encontrar el transferId exacto, con plazo máximo
   de5 segundos para este laboratorio. Cada petición también debe tener timeout.
6. Verifica cantidad, amountMinor, currency, sourceAccountId, status e identidad.
7. Si vence el plazo, falla y conserva última respuesta, tiempo transcurrido,
   referencia y observaciones de salud. No inventes una causa raíz.

TypeScript puede usar expect.poll. En Java o Python implementa una estrategia
equivalente compatible con su API y reloj monotónico. No uses un bucle infinito,
un sleep fijo como prueba de finalización ni POST dentro del polling.

Explica que el outbox es una representación en memoria de un proceso local;
esta prueba no demuestra durabilidad, broker real o recuperación tras caída.
Ejecuta y conserva evidencia identificada por caso e intento.
```

## 5. Error 503 de UI con alcance explícito

```text
Implementa TR-05 como prueba de UI con respuesta de navegador controlada.
Prepara y autentica una fixture real antes de instalar la ruta.

Intercepta únicamente POST /api/transfers; permite continuar otros métodos y rutas.
Responde 503 con JSON:
{"code":"SERVICE_UNAVAILABLE","message":"Servicio temporalmente no disponible"}

Envía 100.00 por UI una sola vez. Comprueba alerta exacta y botón Transferir habilitado.
Consulta el backend real para verificar saldo 100000 y cero registros, porque la
interceptación impidió que ese POST llegara al servidor. Retira el handler o cierra
el contexto al finalizar. Conserva limpieza y evidencia propias de esta fixture.

Titula el resultado "UI ante respuesta 503 simulada". No lo presentes como resiliencia
del backend, recuperación de una caída real o ausencia de débito tras cualquier timeout.
Propón por separado qué contrato faltaría para probar una respuesta perdida después
de que el servidor ya hubiera comprometido la transferencia.
```

## 6. Regresión híbrida web → servicios → TNZ

```text
Extiende o crea una prueba híbrida en LENGUAJE_ELEGIDO usando adapter.py existente.
Lee también su implementación TerminalSession y el ejemplo híbrido de ese lenguaje.

Crea una fixture, autentica el navegador, transfiere 100.00 por UI y comprueba su resultado.
Obtén el transferId real desde respuesta observada o colección canónica filtrada;
comprueba que corresponde a un único registro de la cuenta creada.

Invoca adapter.py con argumentos separados, sin construir un comando de shell:
lookup <transferId> --timeout 8 --snapshot <ruta única de evidencia terminal>
Usa el Python de lab/mainframe/.venv. Límite externo de proceso:12 segundos.
- Python: subprocess.run con lista y timeout.
- TypeScript: execFile/promisify con lista y timeout12000 ms.
- Java: ProcessBuilder, waitFor acotado y terminación si excede el plazo.

Comprueba salida y JSON antes de aceptar éxito. Exige referencia exacta,
status COMPLETED, amountMinor 10000, currency MXN, sourceAccountId correcto,
balanceMinor 90000 y simulated true. No sustituyas ningún dato con un valor por defecto.

Verifica la secuencia real del adaptador: conectar, esperar panel y teclado listos,
key_home, key_eraseeof, key_data(reference), enter, esperar referencia+resultado,
leer scrstr y cerrar con shutdown. No inventes métodos o campos de otra aplicación.

Guarda screenshot, trace, snapshot terminal y JSON con nombres únicos antes de limpiar.
Agrega una prueba negativa para referencia inexistente y diferencia NOT FOUND,
BACKEND UNAVAILABLE, timeout y fallo de validación según el contrato CLI real.

El servidor es un simulador TN3270 local que consulta los MISMOS datos Accounts en memoria.
No conectes otro host ni afirmes reconciliación independiente, z/OS, CICS, DB2 o persistencia.
Entrega código integrado y resultados reales separados por lenguaje y caso.
```

## 7. Revisión adversarial del código generado

```text
Revisa el código y el contrato adjuntos como si debieras mantener esta regresión.
Prioriza defectos concretos sobre consejos genéricos. Devuelve como máximo8 hallazgos
accionables con archivo, línea, escenario que falla, impacto y cambio mínimo propuesto.

Busca: cuentas o sesiones compartidas; fixtures repetidas entre intentos; key nueva
en el segundo POST idempotente; selectores inventados; métodos TNZ inexistentes;
consultas sin filtrar; ausencia de count/currency/source; polling que escribe;
timeouts ilimitados; hook header global; trace iniciado por dos propietarios;
cleanup que oculta el fallo original; artefactos sobrescritos entre pruebas.

Verifica que las APIs existen en las versiones instaladas y que cada fragmento
está integrado con imports y lifecycle reales. Distingue error confirmado de sospecha.
Incluye "Qué está bien" para decisiones respaldadas. No modifiques automáticamente
oráculos monetarios ni reduzcas cobertura para simplificar la implementación.
```

## 8. Diagnóstico de un fallo real sin debilitar la prueba

```text
Diagnostica el fallo adjunto usando contrato, requests/responses, trace y estado final.
No tienes autorización para cambiar el resultado esperado por conveniencia.

Devuelve:
1. Hechos observados con su archivo o artefacto.
2. Hasta3 hipótesis, indicando evidencia a favor y qué falta comprobar.
3. La siguiente comprobación más pequeña que discrimine entre ellas.
4. Una corrección mínima, solo si la evidencia la justifica.
5. El comando y criterio para verificar esa corrección.

Para el defecto de idempotencia, saldo 80000 y dos registros son evidencia de fallo;
el oráculo sigue siendo 90000 y un registro. Compara clave, cuerpo e identidad de
ambas respuestas. No añadas skip, retries o esperas mayores para ocultar el problema.

Conserva los artefactos del fallo en su directorio. Al volver al servidor sano,
cambia BASE_URL a http://127.0.0.1:3000 Y ARTIFACT_DIR a evidence/healthy-recheck,
de modo que la nueva ejecución no sobrescriba evidence/defect.
Si la causa no está demostrada, dilo explícitamente.
```

## 9. CI y reporte final con estados verificables

```text
Prepara la ejecución de regresión en CI para LENGUAJE_ELEGIDO usando el proyecto real.
Antes de escribir configuración, identifica runner, runtime, dependencias fijadas,
browser/channel, servicios locales y rutas reales de reportes.

El job debe instalar lo necesario, arrancar los servicios del laboratorio, verificar
la salud de cada dependencia, ejecutar casos seleccionados y detener sus procesos.
El híbrido requiere además TNZ y el simulador 2323. No conectes sistemas externos.
Conserva resultados, traces y correlación también cuando falle el comando de pruebas.
No publiques ni dispares servicios remotos sin autorización explícita de esa acción.

Genera un reporte SOLO a partir de comandos y artefactos realmente disponibles:
- ubicación de ejecución: local o CI;
- versión/variante, lenguaje, browser y casos seleccionados;
- cantidades reales de aprobadas, fallidas, omitidas y no ejecutadas;
- rutas verificadas de artifacts o enlace real del run;
- preparación bloqueada, errores de limpieza y cobertura faltante;
- límites: idempotencia secuencial, mockUI y terminal con datos locales compartidos.

No equipares compilar con ejecutar, configurar CI con ejecutar CI, ni archivo existente
con prueba aprobada. Si no se ejecutó el pipeline, escribe "CI configurado; ejecución
en su entorno pendiente". Da el próximo paso concreto y la evidencia necesaria.
```

## Uso durante el taller

Una secuencia práctica es **contexto → matriz → tres casos → revisión → ejecución → diagnóstico → reporte**. Distribuida, mock y TNZ amplían esa base con riesgos distintos. Para copiar una instrucción específica, pega primero el contexto común y adjunta sus fuentes; después utiliza el prompt elegido.

Consulta [las fuentes y límites técnicos](scripts/SOURCES.md) y los README de ambos laboratorios para confirmar comandos y configuración. Las opciones de navegador y la captura de trace deben tener un propietario claro en cada proyecto.
