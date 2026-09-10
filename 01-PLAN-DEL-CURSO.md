# Playwright avanzado con IA: de riesgos a regresiones confiables

Plan para crear e impartir un taller de **120 minutos**, en español, con rutas de **TypeScript, Java y Python**. Preparado el 9 de septiembre de 2026.

**Material práctico entregado:** [biblioteca de 12 videos terminados](videos/index.html), [instalación y uso](videos/LEEME-VIDEOS.md) y [prompts de regresión distribuida y TNZ](videos/AI-PROMPTS-REGRESSION.md). Los proyectos reales están en `videos/lab/distributed` y `videos/lab/mainframe`; registran **22 casos aprobados localmente** en sus [evidencias distribuidas](videos/lab/distributed/evidence/VERIFICATION.md) y [evidencias de protocolo e híbridos](videos/lab/mainframe/evidence/VERIFICATION.md). Los 12 MP4 están exportados en Full HD con voz de IA y subtítulos en inglés; duran 7:03–7:32 y suman 87:20. El ensayo con participantes y una ejecución alojada de CI tienen estados independientes.

## Propuesta

Los participantes usarán IA para analizar un flujo, generar pruebas, ejecutarlas y revisar sus resultados. Trabajarán sobre **TransferLab**, un laboratorio local implementado con transferencias y datos sintéticos. No describe sistemas ni reglas reales de HSBC.

El resultado esperado por participante es una pequeña suite de regresión con tres escenarios relevantes, datos aislados, comprobaciones del resultado de negocio y evidencias de ejecución. Se añade una prueba de interfaz con un fallo simulado y un diagnóstico de una prueba fallida. Estos son objetivos del taller, no resultados ya obtenidos.

**Decisión para hacerlo viable:** cada persona elige un lenguaje antes de la sesión. El instructor explica una solución común y muestra TypeScript como referencia; Java y Python tienen material equivalente preparado. Los conceptos se comparten, las implementaciones se resuelven por ruta. Una demostración completa de los tres proyectos desde cero necesitaría sesiones adicionales.

## A quién va dirigido

QA automation, SDET y desarrolladores que ya escriben pruebas básicas. Deben conocer selectores, aserciones, HTTP/JSON, Git y el lenguaje elegido. La ruta TypeScript requiere manejar `async/await`; la ruta Java, JUnit; la ruta Python, pytest y sus fixtures. Un ejercicio de diagnóstico previo comprueba esas bases.

El taller se concentra en decisiones avanzadas: qué riesgo cubrir, cómo aislar estado del servidor, cómo verificar una operación y cómo distinguir un error del producto de un error de la prueba. No reserva tiempo de clase para instalar herramientas ni enseñar sintaxis inicial.

## Objetivos observables

Al terminar, el participante podrá:

1. Convertir reglas de negocio en una matriz de riesgos con prioridades y resultados esperados verificables.
2. Proporcionar a la IA un contrato, evidencia de la aplicación y restricciones suficientes para generar pruebas revisables.
3. Preparar y limpiar datos propios de cada prueba sin depender del orden de ejecución.
4. Verificar una transferencia en la interfaz y en el estado autoritativo del laboratorio; comprobar idempotencia por API. El estado de esta implementación vive en memoria.
5. Reproducir un fallo, analizar su traza y conservar el resultado esperado durante la corrección.
6. Proponer una ejecución en CI y reportar con precisión pruebas aprobadas, fallidas, omitidas y no ejecutadas.

## Agenda de 120 minutos

| Minutos | Duración | Actividad | Acción del participante | Evidencia de aprendizaje |
|---|---:|---|---|---|
| 00–10 | 10 min | Riesgo, regresión e IA | Comparar una prueba superficial con otra que comprueba el débito y el registro | Explicar qué defecto detecta cada una |
| 10–25 | 15 min | Contexto y diseño de cobertura | Completar el contexto de P00 y usar P01 para priorizar escenarios | Matriz con tres casos y sus resultados esperados |
| 25–45 | 20 min | Arquitectura, autenticación y datos | Revisar el proyecto inicial preparado; aplicar P02/P03 para completar una fixture | Datos exclusivos, autenticación y limpieza delimitada |
| 45–65 | 20 min | Generación de regresiones | Usar P04, revisar y ejecutar TR-01, TR-02 y TR-03 | Tres casos con aserciones de negocio y resultado real de la ejecución |
| 65–70 | 5 min | Pausa | Descanso y recuperación del punto común | Grupo listo para continuar |
| 70–85 | 15 min | Fallo controlado de red | Usar P05 para simular un 503 y comprobar la respuesta de la interfaz | Caso etiquetado como prueba de interfaz con mock |
| 85–100 | 15 min | Diagnóstico con trazas | Usar P06 sobre el fallo preparado; proponer una corrección basada en evidencia | Causa sustentada y nueva ejecución, o defecto del producto documentado |
| 100–112 | 12 min | CI, selección y evidencia | Revisar la plantilla de su ruta con P07 | Comando, selección de pruebas y artefactos que se conservarán |
| 112–120 | 8 min | Revisión y cierre | Aplicar P08/P09 a lo realizado y responder la evaluación | Resultado con rúbrica y pendientes explícitos |

**Total: 120 minutos, incluida una pausa de cinco minutos.** El proyecto inicial, las dependencias y las trazas de ejemplo deben estar disponibles desde el inicio. En el bloque de generación se completan puntos concretos del proyecto preparado; construir toda la infraestructura ahí haría inviable el horario.

## Caso práctico y alcance

Cada escenario comienza con una cuenta nueva de **MXN 1,000.00**. Los importes en API se representan en centavos enteros.

| Caso | Riesgo | Operación | Resultado esperado | Capa |
|---|---|---|---|---|
| TR-01 | Débito o registro incorrecto | Transferir MXN 100.00 | Saldo MXN 900.00, un registro, confirmación visible | UI + API real del laboratorio |
| TR-02 | Transferencia sin fondos | Intentar MXN 1,100.00 | Rechazo, saldo MXN 1,000.00, cero registros | UI + API real del laboratorio |
| TR-03 | Débito duplicado al reintentar | Enviar dos veces MXN 100.00 con la misma clave de idempotencia | Mismo identificador de transferencia, un débito, un registro | API real + consulta posterior de UI |
| Extensión de clase | Mala respuesta visual a un servicio caído | Simular una respuesta 503 | Mensaje de error y posibilidad de recuperación según contrato | UI con respuesta simulada |

TR-03 no equivale a pulsar dos veces un botón: comprueba el contrato de idempotencia del servicio. El aislamiento del navegador tampoco demuestra aislamiento de saldos; cada prueba necesita datos propios del servidor. Playwright documenta el aislamiento mediante contextos de navegador y estrategias distintas de autenticación para pruebas que modifican estado compartido. [Aislamiento](https://playwright.dev/docs/browser-contexts), [autenticación](https://playwright.dev/docs/auth).

El contrato didáctico completo, la ubicación de las implementaciones y las equivalencias de código están en [03-LABORATORIO-Y-LENGUAJES.md](03-LABORATORIO-Y-LENGUAJES.md). Las pruebas locales ya ejecutadas sirven como referencia; cada participante debe preparar y comprobar su propia estación antes de la sesión.

La [biblioteca de 12 lecciones](videos/index.html) amplía el material con proyección de Ledger y terminal TNZ local. La serie completa se utiliza fuera del taller, como preparación o repaso; en clase se seleccionan fragmentos breves. No se suma su duración a la agenda de 120 minutos ni se intenta ejecutar todas las extensiones dentro de ella.

## Cómo encajan los tres lenguajes

| Ruta | Base del proyecto | Qué comparte con las otras rutas | Qué requiere adaptación |
|---|---|---|---|
| TypeScript | Playwright Test | Riesgos, casos, contrato, datos, resultados esperados | Configuración, fixtures, proyectos y reportes del runner |
| Java | Playwright Java + JUnit 5 + Maven | Los mismos escenarios y criterios | Ciclo de vida JUnit, dependencias Maven y captura de evidencia |
| Python | Playwright Python + pytest-playwright, API síncrona | Los mismos escenarios y criterios | Fixtures pytest, markers y configuración de plugins |

Playwright Test es el runner de la ruta Node.js. Java y Python se integran con sus respectivos runners; sus opciones de ejecución no son intercambiables. [Lenguajes soportados](https://playwright.dev/docs/languages), [JUnit](https://playwright.dev/java/docs/test-runners), [pytest](https://playwright.dev/python/docs/test-runners).

Si hay un solo instructor, conviene trabajar en parejas del mismo lenguaje y resolver incidencias de instalación antes del taller. Se recomienda un apoyo técnico para atender las tres rutas en un grupo grande; es una decisión de facilitación, no un requisito de Playwright.

## Uso de IA durante el taller

El ciclo de trabajo será **contexto → riesgos → código → ejecución → evidencia → revisión**. El catálogo de prompts incluye un prompt maestro reutilizable y prompts por etapa. Para aprender, usar las etapas; para transferir el método a otro proyecto después del curso, usar el maestro con información real del proyecto.

El participante proporciona contratos y evidencia sanitizada; la IA propone casos y cambios; el participante revisa el resultado de negocio y comprueba la ejecución. Una respuesta de la IA que dice “todo pasó” no sustituye un reporte del runner.

Los prompts pueden usarse con un asistente de texto o con un agente que tenga acceso al proyecto. En modo texto, la persona copia los archivos y ejecuta los comandos. En modo agente, este puede hacerlo si dispone de esas herramientas. El material exige distinguir ambos modos.

Como ampliación, Playwright ofrece agentes planner, generator y healer. Se puede mostrar su flujo si el entorno del instructor ya está configurado. Esta integración específica queda como demostración opcional de TypeScript; no es una dependencia del curso ni una capacidad idéntica de JUnit y pytest. Toda reparación debe preservar el criterio de aceptación. [Playwright Test Agents](https://playwright.dev/docs/test-agents).

## Qué preparar para impartir esta entrega

1. **Revisar el contrato entregado:** utilizar TransferLab o adaptar los casos a otra aplicación autorizada, verificando sus reglas.
2. **Preparar la estación del grupo:** instalar dependencias y arrancar los proyectos entregados; los resultados de esta estación no sustituyen una instalación comprobada en cada equipo.
3. **Elegir los puntos a completar:** conservar la solución funcional y preparar una copia de trabajo por participante. Una variante inicial deliberadamente incompleta queda como preparación docente.
4. **Revisar la evidencia existente:** comprobar los tres casos por lenguaje, la limpieza y el fallo intencional; repetir solo lo necesario para validar la configuración de la cohorte.
5. **Preparar la facilitación:** seleccionar los [fragmentos con tiempos exactos](videos/FRAGMENTOS-PARA-LA-CLASE.md) de las 12 lecciones; la propuesta de 14 diapositivas del documento 05 es material de planificación, no una presentación independiente ya terminada.
6. **Hacer un ensayo de 120 minutos:** sigue pendiente un ensayo con participantes ajenos a la construcción. Ajustar la práctica al tiempo medido y cerrar la configuración antes de impartir.

La lista de producción, el trabajo previo y la evaluación están en [05-PREPARACION-Y-EVALUACION.md](05-PREPARACION-Y-EVALUACION.md). Los comandos y requisitos de CI están en [04-COMANDOS-Y-CI.md](04-COMANDOS-Y-CI.md).

## Criterio de éxito y límites

Objetivo de evaluación: **8/10 puntos** en la rúbrica, además de sus criterios obligatorios. Si hay un defecto intencional del producto, documentarlo correctamente cuenta como evidencia de diagnóstico; no se transforma en prueba aprobada eliminando una aserción.

La sesión introduce cómo trasladar la suite a CI mediante una plantilla preparada. Ejecutar una matriz completa de tres lenguajes por tres navegadores, crear infraestructura CI corporativa, enseñar pruebas de carga y cubrir regresión visual quedan como ampliaciones. Los 120 minutos se dedican a completar y evaluar el mismo flujo de regresión.

**Estado de esta entrega:** plan y prompts disponibles, laboratorios ejecutables y 22 casos aprobados localmente. El [estado audiovisual de cada lección](videos/index.html) se verifica durante su producción; esta guía no afirma que los 12 MP4 estén listos. El ensayo real de 120 minutos, la presentación independiente de 14 diapositivas y una ejecución alojada de CI siguen pendientes de preparación o comprobación.
