# Playwright avanzado con IA — Prompts para copiar y pegar

Material para un curso de **120 minutos**. Cada participante elige **un lenguaje**: TypeScript, Java o Python. El curso trabaja la misma estrategia de regresión; no intenta enseñar los tres lenguajes simultáneamente.

**Estado de este material:** son instrucciones para generar y revisar trabajo. No constituyen una suite implementada ni resultados de pruebas. **TransferLab** es una aplicación ficticia para formación; no representa sistemas ni contratos de HSBC. El instructor debe preparar y validar el laboratorio antes de impartirlo mediante P10.

## Cómo utilizar los prompts

1. Completa el bloque CONTEXTO con información comprobable. Escribe `DESCONOCIDO` donde falte algo; nunca inventes una URL, selector o endpoint para poder continuar.
2. En un chat nuevo, pega CONTEXTO y después el prompt elegido. Usa P00 para un flujo completo fuera de la sesión; durante el curso utiliza P01–P09 por etapas.
3. Mantén el mismo contexto en la conversación. Si cambia una condición, pega la corrección antes del siguiente prompt.
4. Revisa la evidencia que entrega la IA. Que el código se vea correcto no demuestra que se haya ejecutado ni que detecte una regresión.

La ruta TypeScript utiliza el runner `@playwright/test` y sus fixtures ([documentación](https://playwright.dev/docs/test-fixtures)). La ruta Java utiliza Playwright con JUnit 5 y Maven ([integración con runners](https://playwright.dev/java/docs/test-runners)); las instancias de Playwright y sus objetos requieren respetar las restricciones de hilos ([multithreading](https://playwright.dev/java/docs/multithreading)). La ruta Python utiliza la API síncrona y `pytest-playwright` ([plugin de pytest](https://playwright.dev/python/docs/test-runners)). Los prompts obligan a comprobar las versiones del proyecto antes de generar sintaxis, opciones o comandos. Referencias consultadas el 9 de septiembre de 2026.

## CONTEXTO — Copiar, completar y conservar

Los importes siguientes son requisitos propuestos para el laboratorio ficticio, en centavos de MXN y sin comisiones: 100000 equivale a MXN 1000.00. El contrato completo, incluidas rutas y UI propuestas, está en [03-LABORATORIO-Y-LENGUAJES.md](03-LABORATORIO-Y-LENGUAJES.md). El instructor debe construir y verificar la demo contra ese contrato **antes** de generar las pruebas. Una ruta propuesta no es evidencia de una API existente.

```text
CONTEXTO DEL PROYECTO

LENGUAJE: [TYPESCRIPT | JAVA | PYTHON; elige exactamente uno]
CAPACIDAD_DEL_ASISTENTE: [CON_ACCESO_AL_REPO_Y_EJECUCION | SOLO_TEXTO]
REPOSITORIO_O_CARPETA: [ruta accesible para el asistente, o DESCONOCIDO]
RAMA_Y_ESTADO_INICIAL: [rama, cambios existentes o DESCONOCIDO]
ALCANCE_AUTORIZADO: [rutas donde puede crear/editar pruebas y ejecutar]
APLICACION: [TransferLab ficticia u otra aplicación de pruebas autorizada]
BASE_URL: [URL verificada del entorno de pruebas, o DESCONOCIDO]
ENTORNO: [local/QA; sistema operativo y shell]
ARRANQUE_Y_HEALTHCHECK: [comando y comprobación observados, o DESCONOCIDO]

TOOLCHAIN_Y_RUNNER:
- TypeScript: Node, gestor de paquetes, versión de @playwright/test,
  archivo de dependencias, lockfile y configuración observados.
- Java: JDK, Maven/wrapper, versión de Playwright, JUnit 5 y Surefire
  observadas en el pom.xml. No utilizar la configuración del runner Node.
- Python: intérprete/venv, gestor, versiones de playwright, pytest,
  pytest-playwright y configuración observadas. Usar API síncrona.
[Rellenar SOLO el lenguaje elegido; desconocidos deben quedar explícitos.]

CONTRATO_FUNCIONAL:
[Adjuntar criterios de aceptación aprobados. Para TransferLab proponemos:]
- Importes en unidades menores enteras; sin comisiones en estos casos.
- TR-01: cuenta aislada con saldo inicial 100000; transferencia de 10000.
  Resultado: aceptada, saldo final 90000 y exactamente un nuevo registro
  de transferencia asociado a la operación. UI y API deben coincidir.
- TR-02: cuenta aislada con saldo inicial 100000; intento de transferir 110000.
  Resultado: rechazada por fondos insuficientes, saldo final 100000 y cero
  nuevos registros de transferencia. El rechazo se muestra en la UI.
- TR-03: cuenta aislada con saldo inicial 100000; enviar dos solicitudes
  equivalentes de transferencia de 10000 con la MISMA clave de idempotencia.
  Resultado: un solo débito de 10000, saldo final 90000 y exactamente un
  nuevo registro de transferencia para esa operación. UI y API coinciden.
  El contrato debe precisar la identidad de la operación y las respuestas
  al reenvío. No dar por hecho que el segundo envío devuelve un HTTP concreto.
- “Registro” significa registro de transferencia de negocio; no cuenta
  intentos ni logs de auditoría. Leer la fuente acordada en el contrato.

API_OBSERVADA:
[Método, ruta, autenticación, esquema de petición/respuesta, estados HTTP,
 rutas de consulta de saldo/operaciones y mecanismo real de idempotencia.
 Incluir extracto OpenAPI, código o respuestas sanitizadas y su procedencia.
 En TransferLab contrastar la implementación con el contrato propuesto en
 03-LABORATORIO-Y-LENGUAJES.md; no copiar sus rutas como si ya se observaron.]
DOM_OBSERVADO:
[Roles, nombres accesibles, labels y test IDs realmente presentes; incluir
 snapshot/HTML relevante o acceso autorizado para inspeccionarlo.]
AUTENTICACION:
[Flujo de pruebas, roles y nombres de variables de entorno; nunca valores
 secretos. Indicar expiración y si existen usuarios aislados por caso/worker.]
DATOS_Y_LIMPIEZA:
[Mecanismo autorizado de crear, consultar y eliminar datos propios; IDs,
 namespaces por ejecución y límites. Si no existe, escribir DESCONOCIDO.]
CONSISTENCIA_Y_TIEMPOS:
[Confirmación síncrona o eventual y límite documentado; o DESCONOCIDO.]

CI:
[Proveedor, archivo existente, SO, secretos por nombre y política actual;
 o SIN_CI_DEFINIDO. No publicar ni activar servicios externos.]
EVIDENCIA_DISPONIBLE:
[Rutas o adjuntos: logs, trace, reportes, capturas y ejecución que los generó.
 Indicar fecha/commit; sanitizar tokens, credenciales y datos personales.]
COMANDOS_Y_RESULTADOS_PREVIOS:
[Comandos reales, directorio, códigos de salida y resumen; o NO_EJECUTADO.]
RESTRICCIONES:
[Navegadores, recursos, tiempo, proxy, política de datos o restricciones reales.]
```

## P00 — Generar una regresión completa con evidencia

**Uso:** flujo reutilizable después del curso. Ejecuta por etapas; no sustituye la revisión humana.

```text
Actúa como ingeniero senior de calidad especializado en Playwright.
Utiliza exclusivamente el CONTEXTO adjunto y el lenguaje elegido.
Tu objetivo es construir una regresión mantenible y demostrar qué se
implementó, qué se ejecutó y qué sigue pendiente.

Primero confirma tu capacidad real. Si tienes acceso al repositorio y
herramientas, inspecciona instrucciones locales, estructura, dependencias,
configuración, contratos, pruebas y cambios existentes. Si solo tienes texto,
analiza los adjuntos y entrega archivos propuestos claramente identificados;
no afirmes haber leído archivos, abierto la aplicación ni ejecutado comandos.

Clasifica los datos de entrada como VERIFICADO, REQUISITO_PROPORCIONADO,
SUPUESTO o FALTANTE. Un requisito proporcionado define lo esperado; una
respuesta observada del producto no sustituye ese requisito. No inventes
selectores, endpoints, mecanismos de autenticación ni versiones.
Cuando falte información indispensable, señala el dato concreto y continúa
con trabajo independiente que sí tenga fundamento. No produzcas una suite
supuestamente ejecutable mientras dependa de contratos inventados.

Trabaja en este orden:
1. Matriz de riesgos y trazabilidad. Prioriza TR-01, TR-02 y TR-03 del contrato.
2. Arquitectura mínima usando el runner real del proyecto. No añadas capas
   que solo renombren métodos ni conviertas código entre lenguajes por sintaxis.
3. Preparación de datos, autenticación y aislamiento de navegador Y backend.
4. Generación de los tres casos con oráculos de negocio independientes.
5. Un caso de fallo de dependencia mediante mock, separado y etiquetado
   como prueba de UI aislada; no contarlo como E2E de la transferencia real.
6. Ejecución y diagnóstico si tienes capacidad. Conserva evidencias.
7. Configuración de CI compatible con el proyecto, sin activarla externamente.
8. Revisión final y reporte de resultados reales.

Reglas obligatorias:
- TypeScript: @playwright/test; Java: Playwright + JUnit 5/Maven;
  Python: API síncrona con pytest-playwright. Verifica APIs y opciones contra
  la versión instalada y documentación oficial cuando sea necesario.
- Locators basados en roles, labels o test IDs observados. Evita índices y
  selectores estructurales frágiles; cualquier excepción necesita fundamento.
- Sin sleeps arbitrarios. Usa assertions con reintento y esperas acotadas a
  un evento/estado verificable. Las esperas de red se registran antes de actuar.
- Cada caso crea datos propios; incorpora ejecución, worker y caso en su
  namespace. Un BrowserContext nuevo no aísla cuentas ni saldos del servidor.
- Conserva IDs creados y limpia solo esos IDs, también si falla la preparación
  parcialmente. Usa try/finally, finalizadores o teardown equivalente.
- En Java no compartas Playwright, Browser, BrowserContext ni Page entre
  hilos concurrentes; define propiedad y cierre en el mismo hilo.
- TR-03 debe demostrar dos envíos con la misma clave y el efecto persistido;
  un botón deshabilitado o un mensaje de éxito no demuestra idempotencia.
- No añadas skip, xfail, force, capturas aprobadas automáticamente, assertions
  débiles o reintentos para hacer desaparecer un fallo. Si el producto incumple
  el contrato, conserva la prueba que lo demuestra y redacta el defecto.
- No uses datos bancarios reales. No incluyas credenciales ni estado de sesión
  en Git, en prompts ni en artefactos compartidos sin sanitizar.

Entrega por etapa: decisión breve, evidencia de entrada, archivos creados o
diff propuesto, comando correspondiente al entorno y resultado observado.
No ejecutes cambios externos fuera del alcance autorizado. En modo SOLO_TEXTO
marca comandos como PROPUESTOS y todos los resultados como NO_EJECUTADO.
Finaliza con una tabla por caso: requisito, archivo, nivel UI/API/E2E, backend
real o simulado, estado de ejecución y evidencia. Cuenta casos únicos aparte
de intentos/retries. Enumera los huecos que impiden declarar la regresión lista.
```

## P01 — Convertir requisitos en una matriz de regresión

**Momento:** minutos 10–25. **Salida:** matriz con prioridad y oráculo medible.

```text
Con el CONTEXTO adjunto, crea una matriz de regresión basada en riesgo.
Todavía no generes código. Distingue requisitos proporcionados de interfaces
observadas y escribe FALTANTE cuando no exista evidencia.

Produce una tabla con: ID, riesgo de negocio, requisito, precondición,
datos propios, acción, resultado observable, fuente del oráculo, nivel
recomendado (API, UI aislada o E2E), prioridad y evidencia necesaria.
Incluye obligatoriamente TR-01, TR-02 y TR-03 sin alterar sus invariantes.
Puedes proponer hasta cinco casos adicionales, marcados FUERA_DEL_NUCLEO.

Prioriza impacto y probabilidad en escalas 1–3, indicando que son estimaciones
del ejercicio. Explica en una frase por qué cada caso esencial merece estar.
No uses porcentaje de cobertura sin definir el universo que estás midiendo.

Para cada caso núcleo precisa qué demostraría una regresión: saldo incorrecto,
registro ausente/extra, rechazo indebido o doble débito. Un toast por sí solo
no demuestra persistencia. Un HTTP 200 por sí solo no demuestra el resultado.
Para TR-03 diferencia reenvío secuencial con la misma clave de concurrencia;
la concurrencia es extensión salvo que el requisito la exija explícitamente.

Termina con los tres huecos de contexto de mayor impacto y el artefacto
concreto que resolvería cada uno: contrato, DOM, respuesta API o mecanismo
de datos. No rellenes esos huecos por imaginación.
```

## P02 — Diseñar la estructura del proyecto

**Momento:** transición hacia minutos 25–45. **Salida:** estructura pequeña y decisiones del lenguaje elegido.

```text
Diseña la estructura mínima de regresión para el CONTEXTO y la matriz P01.
Inspecciona el repositorio si puedes; en modo SOLO_TEXTO usa únicamente los
archivos adjuntos. Reutiliza las convenciones y dependencias existentes.

Selecciona una sola ruta:
- TYPESCRIPT: @playwright/test, fixtures tipadas, configuración del runner.
- JAVA: Playwright, JUnit 5 y Maven; lifecycle de recursos explícito.
- PYTHON: pytest-playwright, API síncrona y fixtures en conftest.py.
No propongas playwright.config.ts para Java/Python ni opciones de Node para
Maven/pytest. No añadas plugins, versiones o flags cuya existencia no verificaste.

Entrega árbol propuesto y responsabilidad de cada archivo: configuración,
preparación de datos, UI reutilizable si aporta valor, tests y evidencias.
Las abstracciones UI representan tareas del usuario; las assertions de negocio
deben permanecer visibles en los casos o helpers claramente identificados.

Explica el alcance de cada recurso: proceso, worker, test y backend. Define
quién crea/cierra browser/context/page/API client y cómo se evitan colisiones.
En Java explica la propiedad por hilo antes de habilitar paralelismo.

Proporciona solo los cambios indispensables para integrar esa estructura.
Si falta una versión, verifica el archivo de dependencias o solicita ese dato;
no selecciones silenciosamente “latest”. Diferencia arquitectura propuesta de
archivos efectivamente creados. No declares que compila sin salida de compilación.
```

## P03 — Crear fixtures, autenticación y datos aislados

**Momento:** minutos 25–45. **Salida:** preparación y limpieza que no dependen del orden de los tests.

```text
Implementa la preparación de TR-01, TR-02 y TR-03 usando CONTEXTO y P02.
Si no puedes editar archivos, entrega el contenido completo propuesto con
rutas sugeridas, imports y dependencias identificadas, sin afirmar ejecución.

Antes de generar código, confirma el mecanismo real de crear cuentas/datos,
obtener sesión, leer saldo/transferencias y limpiar. Si falta uno, delimita
la interfaz pendiente y explica qué bloquea; no inventes endpoints auxiliares.

Cada test debe empezar con estado conocido e independiente. Crea un namespace
por ejecución y datos propios por caso; incorpora worker/attempt cuando aplique.
Guarda los IDs realmente creados. Limpia exclusivamente esos IDs incluso si
falla parte del setup. El fallo de limpieza se reporta sin ocultar el fallo
principal. No borres tablas, cuentas compartidas ni datos ajenos.

Usa contextos de navegador nuevos por caso. Si reutilizas estado de autenticación,
explica su alcance, expiración y archivo por identidad. Nunca compartas una
cuenta mutable entre pruebas paralelas sin aislamiento demostrado en backend.
No guardes contraseñas, tokens ni storage state en archivos versionados.

Adapta el lifecycle al runner: fixtures test/worker para TypeScript; hooks o
extensión JUnit 5 con try/finally para Java; fixtures pytest con finalizadores
que cubran también setup parcialmente fallido para Python. No mezcles async
y sync en Python. En Java, objetos Playwright confinados al hilo propietario.

Entrega: código, mapa de propiedad de recursos y comprobación acotada de que
dos casos usan cuentas distintas y terminan limpiando sus propios IDs. Si puedes
ejecutar, muestra resultados de esa comprobación; si no, da instrucciones y
marca NO_EJECUTADO. No confundas cookies separadas con saldos separados.
```

## P04 — Generar los tres casos núcleo

**Momento:** minutos 45–65. **Salida:** tres casos trazables con efecto de negocio verificable.

```text
Genera TR-01, TR-02 y TR-03 a partir del CONTEXTO, matriz y fixtures acordadas.
Usa exclusivamente el lenguaje elegido y APIs/selectores comprobados.
No escribas una plantilla con TODO y la presentes como lista para ejecutar.

TR-01: iniciar con saldo 100000 y transferir 10000; comprobar aceptación,
saldo persistido 90000 y exactamente un nuevo registro de esa operación.
TR-02: iniciar con saldo 100000 e intentar transferir 110000; comprobar rechazo
por fondos insuficientes, saldo persistido 100000 y cero nuevos registros.
TR-03: iniciar con saldo 100000 y enviar dos solicitudes equivalentes de 10000
usando la MISMA clave; comprobar un solo débito, saldo 90000 y exactamente
un nuevo registro de transferencia. No contar entradas de auditoría como
transferencias ni exigir un código HTTP de reenvío que el contrato no define.
En TransferLab, el contrato 03 sí define primera respuesta 201 y repetición
200 con el mismo id: comprueba los tres valores. Al adaptar a otra aplicación,
usa su contrato explícito. El ejercicio núcleo es secuencial, no concurrente.

Para TR-01/TR-02 conduce el flujo UI y verifica la persistencia por la API
documentada. Para TR-03 elige una de estas rutas según evidencia:
A. Reenvío desde UI si el mecanismo real permite conservar la misma clave.
B. Dos envíos API con la misma clave y posterior comprobación de la UI.
Etiqueta honestamente la ruta B como API + verificación UI; no afirmes que
prueba doble clic en UI. Si no hay mecanismo observado de clave/idempotencia,
TR-03 está BLOQUEADO_POR_CONTRATO; no lo sustituyas por dos clics genéricos.

Compara la API con UI actualizada mediante el flujo real de consulta/recarga.
Si hay consistencia eventual documentada, usa polling acotado y registra el
último estado observado al fallar. No uses sleeps ni networkidle como prueba
de finalización del negocio. Registra esperas de respuesta antes de la acción.

Filtra los registros por cuenta y correlación propias y compara con la línea
base. Comprueba tanto el saldo como la cardinalidad: uno no sustituye al otro.
Usa importes exactos; no derives el esperado de la misma respuesta que validas.
La lista consultada debe cubrir todos los registros relevantes, incluyendo
paginación cuando exista; no concluyas “exactamente uno” desde una vista parcial.

Entrega archivos completos y trazabilidad ID -> assertions -> evidencia.
Ejecuta los casos si tienes herramientas y entorno; separa problemas de
compilación, descubrimiento, setup, test y limpieza. Si no puedes ejecutar,
entrega comandos fundamentados y marca NO_EJECUTADO.
```

## P05 — Simular una dependencia sin falsear cobertura E2E

**Momento:** minutos 70–85. **Salida:** una prueba de UI aislada y su límite explícito.

```text
A partir del CONTEXTO, añade un caso de UI aislada para un fallo de dependencia.
Selecciona una dependencia/ruta observada y un comportamiento esperado
documentado. Si falta el contrato del error o el manejo UI esperado, indica
ese hueco antes de generar assertions o una respuesta ficticia.

Intercepta únicamente la petición concreta por URL y método. Registra la ruta
antes de disparar la acción. Devuelve una respuesta coherente con el contrato
o simula el fallo de transporte acordado. Verifica que el mock fue utilizado
y que el caso no pasó por una ruta alternativa no observada.

Valida el error visible y el estado de la UI que define el requisito; no
inventes un comportamiento de reintento. Si el escenario permite reintentar,
explica qué respuesta corresponde a cada intento y verifica la secuencia.
Elimina el override al terminar. No interceptes globalmente todas las APIs.
Si hay Service Workers y la petición no es interceptable, diagnostica esa
condición y documenta el ajuste del contexto de pruebas cuando esté justificado.

Etiqueta este test UI_AISLADA_MOCK y sepáralo de TR-01/TR-02/TR-03 con backend
real. Explica: este caso demuestra el manejo UI del error simulado; no demuestra
persistencia real, atomicidad ni idempotencia del backend.

Entrega el caso, origen del contrato utilizado, evidencia de interceptación
y resultado real si se ejecutó. Mantén intactos los oráculos de los casos reales.
```

## P06 — Diagnosticar una falla usando evidencia

**Momento:** minutos 85–100. **Salida:** causa sustentada o hipótesis comprobable y corrección mínima.

```text
Analiza el fallo adjunto usando CONTEXTO, código del caso, comando, resultado,
trace/log/captura disponible y contrato esperado. Primero indica qué evidencia
puedes inspeccionar realmente. Si solo tienes un nombre de archivo o no puedes
leer un trace, no afirmes haberlo abierto: pide el extracto relevante o explica
qué debe exportarse, sanitizado.

Reconstruye una línea de tiempo breve: preparación, acción, petición/respuesta,
estado UI, assertion y limpieza. Distingue hechos observados de hipótesis.
Clasifica la causa como PRODUCTO, TEST, DATOS, ENTORNO o INDETERMINADA y explica
la evidencia. Un timeout no prueba automáticamente que exista flakiness.

Identifica la primera divergencia del contrato. Propón como máximo tres
hipótesis ordenadas, cada una con una comprobación que pueda refutarla.
Prioriza el cambio mínimo que resuelva una causa demostrada.

Si es un defecto del test, corrige la causa conservando el oráculo de negocio.
Si es un defecto de producto, conserva la prueba fallida y redacta un reporte
con reproducción, esperado, observado e impacto; no arregles el producto fuera
del alcance autorizado. Si faltan datos, declara INDETERMINADA.

No aumentes sleeps/timeouts/retries ni añadas skip/xfail/catch genérico/force
para obtener verde. Un timeout distinto requiere evidencia del comportamiento
esperado y un límite defendible. No debilites assertions ni actualices snapshots
solo porque fallaron.

Si puedes ejecutar, repite el caso afectado después de la corrección y los casos
que comparten el recurso modificado. Informa cada intento, incluidos fallidos.
Termina con causa, cambio, evidencia posterior y limitación pendiente.
```

## P07 — Preparar CI con resultados verificables

**Momento:** minutos 100–112. **Salida:** cambio de configuración revisable para el proveedor existente.

```text
Prepara la integración CI de esta regresión usando CONTEXTO y las pruebas
generadas. Inspecciona el proveedor, runner, SO y comandos reales existentes.
Si no hay proveedor definido, entrega un diseño neutral con esa decisión
pendiente; no inventes una pipeline corporativa ni actives servicios externos.

Genera la configuración mínima del proveedor confirmado con:
- Instalación reproducible del lenguaje, dependencias y navegadores acordados.
- Arranque o comprobación de salud de la aplicación de pruebas.
- Variables por nombre; secretos provistos por el almacén existente.
- Selección separada de casos núcleo con backend real y UI aislada con mocks.
- Paralelismo acotado al aislamiento disponible y recursos del runner.
- Fallo explícito si no se descubren/ejecutan los casos obligatorios.
- Conservación de reporte y evidencia de fallos aunque la ejecución falle,
  con rutas verificadas, retención indicada y contenido revisado/sanitizado.

Adapta la solución al lenguaje. TypeScript puede usar capacidades nativas del
runner; Java debe configurar JUnit/Maven y captura de traces en el lifecycle;
Python debe usar opciones realmente disponibles en pytest-playwright. No
copies reporters, projects, sharding o flags de Node a otros lenguajes.
Si propones sharding/xdist/plugins, verifica primero que están instalados y
que el aislamiento de datos funciona; no son requisitos de la primera entrega.

La puerta mínima exige TR-01/TR-02/TR-03 ejecutados y aprobados con backend real,
sin casos omitidos ni sustituidos por mocks. Distingue intento limpio de un
resultado recuperado mediante retry. No ocultes inestabilidad tras el total.
La prueba UI_AISLADA_MOCK aporta su resultado separado.

Entrega archivo/diff, comandos y rutas de artefactos. Distingue configuración
validada localmente, pipeline preparada y pipeline efectivamente ejecutada.
Sin una ejecución remota observada, escribe CI_NO_EJECUTADA.
```

## P08 — Revisar lo que generó la IA

**Momento:** minutos 112–120. **Salida:** decisión de revisión sustentada.

```text
Revisa esta regresión como un reviewer independiente usando CONTEXTO,
requisitos, diff y evidencia disponible. No asumas que el autor de los tests
tenía razón. No cambies código durante esta revisión.

Busca defectos que puedan permitir un falso positivo, provocar inestabilidad
o afectar datos ajenos: contratos/selectores inventados, oráculos circulares,
assertions insuficientes, consultas parciales, mocks presentados como E2E,
cuentas compartidas, cleanup incompleto, recursos/hilos compartidos en Java,
esperas sin causa, retries que ocultan fallos y credenciales en artefactos.

Comprueba especialmente TR-03: dos solicitudes con la misma clave y payload
equivalente, una sola transferencia persistida, un solo débito y UI coherente.
Explica si la prueba cubre API + UI, reenvío UI o concurrencia; no confundirlos.

Entrega como máximo cinco hallazgos accionables y priorizados. Cada uno debe
incluir archivo/línea cuando exista, escenario que falla, impacto, evidencia
y corrección propuesta. No inventes ubicaciones en archivos no disponibles.
Añade una breve lista de decisiones correctas que conviene conservar.

Emite una decisión: LISTA_PARA_REVISION_FINAL, REQUIERE_CAMBIOS o
EVIDENCIA_INSUFICIENTE. Código sin ejecución puede recibir revisión estática,
pero no puede declararse regresión validada. Indica exactamente qué falta.
```

## P09 — Reportar únicamente la ejecución observada

**Uso:** cierre del ejercicio o siguiente ejecución. **Salida:** reporte que otra persona puede verificar.

```text
Produce un reporte de regresión con CONTEXTO y resultados adjuntos.
Si tienes permiso y herramientas para ejecutar, usa los comandos comprobados
del proyecto y conserva sus salidas. Si no, reporta únicamente evidencia
proporcionada e identifica su origen; no simules resultados.

Incluye entorno, fecha, commit o estado local conocido, lenguaje, runner,
versiones verificadas, navegador, comando, directorio y código de salida.
Si alguno falta, escribe DESCONOCIDO; no completes números por estimación.

Tabla por caso único: ID, requisito, nivel, backend real/mock, archivo,
estado (APROBADO/FALLIDO/BLOQUEADO/OMITIDO/NO_EJECUTADO), número de intentos,
resultado inicial/final y enlace/ruta de evidencia accesible.
Reporta preparación y limpieza separadamente cuando afecten el resultado.
Una ejecución con cero tests no es aprobada. Un retry aprobado no borra el
intento fallido. No cuentes un mismo caso repetido como cobertura adicional.

Separa tres totales: casos núcleo con backend real, casos con mocks y casos
adicionales. Para cobertura funcional usa solo el universo definido en P01.
No confundas “3 de 3 casos implementados” con “3 de 3 casos aprobados”.

Termina con defectos observados, bloqueos, datos no limpiados si los hubiera
y la siguiente acción concreta para cada pendiente. No declares que el
producto está libre de defectos ni que hay cobertura completa por pasar tres
casos. Si no hubo ejecución, el título debe decir REPORTE SIN EJECUCION.
```

## P10 — Preparar TransferLab antes de impartir el curso

**Uso exclusivo del instructor, fuera de los 120 minutos.** Este prompt permite encargar la construcción del laboratorio; pegarlo no significa que el laboratorio exista.

```text
Prepara un laboratorio ficticio llamado TransferLab para enseñar Playwright
avanzado con IA durante dos horas. Trabaja en la carpeta de laboratorio que
indique el instructor. Antes de crear archivos inspecciona su estado y conserva
el trabajo existente. Si solo puedes producir texto, entrega una propuesta
claramente marcada SIN_IMPLEMENTAR/SIN_EJECUTAR.

El laboratorio debe estar funcionando y comprobado antes de la clase. No uses
marcas, cuentas, credenciales ni datos reales de ninguna entidad financiera.
Construye una aplicación local mínima con UI accesible, backend y persistencia
real durante la ejecución, autenticación ficticia para pruebas y mecanismos
locales de preparación/consulta/limpieza de datos propios. Documenta límites
del demo; no lo presentes como una arquitectura bancaria de producción.

Implementa el contrato propuesto en 03-LABORATORIO-Y-LENGUAJES.md, que incluye
rutas, respuestas y nombres accesibles. Contrasta después cada punto con la
aplicación funcionando. Sus requisitos núcleo son:
- Importes enteros en centavos de MXN y sin comisiones.
- TR-01: saldo 100000, transferencia 10000, saldo final 90000, exactamente una
  nueva transferencia persistida y UI/API coherentes.
- TR-02: saldo 100000, intento 110000, rechazo por insuficiencia, saldo sin cambio
  y ninguna transferencia nueva; el rechazo aparece en UI.
- TR-03: dos solicitudes equivalentes de 10000 con la misma clave idempotente;
  un débito, una transferencia y saldo final 90000 desde 100000. Define scope,
  formato, respuesta de reenvío y comportamiento ante clave reutilizada con
  payload distinto. El núcleo demuestra reenvío secuencial; concurrencia es
  ampliación explícita, salvo que decidas implementarla y verificarla también.
- Consulta verificable de saldo y registros de transferencia, con correlación
  por operación. Distingue transferencias de logs de intento/auditoría.
- Errores con contrato consistente, incluidos los usados por el ejercicio mock.

Implementa UI y API respetando ese contrato. Proporciona roles/labels y test IDs
estables donde sean necesarios. Incorpora namespace por ejecución y limpieza
limitada a IDs propios. No añadas una operación de borrado global accesible
desde fuera del entorno de laboratorio.

Prepara tres carpetas de inicio para participantes: TypeScript/@playwright/test,
Java/Playwright + JUnit 5/Maven y Python síncrono/pytest-playwright. Cada ruta
debe permitir ejecutar el mismo contrato eligiendo solo un lenguaje. Incluye
dependencias verificadas, versiones fijadas, instrucciones para el SO del
instructor y una comprobación de conexión; deja el núcleo de los ejercicios
para que los alumnos lo construyan. Mantén soluciones del instructor aparte.

Prepara también una falla controlada, reversible y aislada del demo para el
ejercicio de diagnóstico, junto con trace/log sanitizado, causa documentada
y pasos para volver a la versión sana. Marca claramente cualquier evidencia
de una falla inducida. No modifiques una aplicación real para generar el fallo.

Valida el arranque real y el contrato de los tres casos. Comprueba por separado
el inicio de cada ruta de lenguaje; una ruta que no fue ejecutada queda
NO_VALIDADA. Conserva resultados, comandos, códigos de salida y evidencias.
Entrega una lista de preparación para el instructor: archivos, arranque/parada,
healthcheck, datos, limpieza, starters, soluciones, evidencia para diagnóstico,
comprobaciones realizadas y pendientes. No declares el laboratorio listo
si falta una aplicación funcionando o alguna ruta prometida está sin validar.
```

## Criterio rápido para aceptar una respuesta de la IA

Antes de incorporar una respuesta al proyecto, comprueba cinco puntos:

- **Fundamento:** selectors, endpoints, versiones y esperados tienen origen identificable.
- **Oráculo:** valida el efecto de negocio y detectaría el error que motiva el caso.
- **Aislamiento:** cuenta, sesión, IDs y limpieza pertenecen a esa ejecución.
- **Evidencia:** diferencia contenido generado, comprobación estática y ejecución real.
- **Cobertura:** declara el nivel UI/API/E2E y si utiliza backend real o mocks.

Si falla uno, vuelve al prompt de la etapa correspondiente y aporta el dato faltante. No intentes resolver una falta de contrato pidiendo a la IA que genere más código.
