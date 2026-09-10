# Preparación, facilitación y evaluación del curso

**Duración de la sesión:** 120 minutos, incluida una pausa de 5 minutos.  
**Nivel:** avanzado. **Lenguajes:** TypeScript, Java y Python.  
**Organización:** cada participante trabaja en **un lenguaje** durante la sesión; los tres grupos resuelven el mismo caso ficticio, TransferLab.

**Material práctico disponible:** [biblioteca de 12 lecciones y estado de producción](videos/index.html), [instalación y uso de los laboratorios](videos/LEEME-VIDEOS.md) y [prompts distribuidos y TNZ copiables](videos/AI-PROMPTS-REGRESSION.md). Los proyectos de `videos/lab/distributed` y `videos/lab/mainframe` están implementados y registran **22 casos aprobados localmente**: [10 distribuidos](videos/lab/distributed/evidence/VERIFICATION.md) y [12 de protocolo e híbridos](videos/lab/mainframe/evidence/VERIFICATION.md).

Este documento prepara la facilitación de esa entrega. Siguen pendientes el ensayo real de 120 minutos con participantes, la comprobación de instalación en sus estaciones y una ejecución alojada de CI. La biblioteca contiene los 12 MP4 terminados, de 7:03–7:32, con voz de IA y subtítulos en inglés. Los 14 títulos de diapositivas de la sección 5 siguen siendo una propuesta y no una presentación independiente ya creada.

## 1. Resultado que debe poder demostrar cada participante

Al terminar, el participante debe convertir requisitos y evidencia de una aplicación en tres pruebas de regresión; revisar el código propuesto por IA; ejecutar las pruebas en su lenguaje; explicar un fallo con evidencia; y proponer su ejecución en integración continua. La evaluación distingue siempre entre **código generado**, **código revisado**, **prueba ejecutada** y **resultado aprobado**.

El curso requiere experiencia previa con pruebas web, selectores, asincronía en el lenguaje elegido, Git y conceptos básicos de HTTP. No incluye una introducción a programación ni una instalación guiada durante los 120 minutos. La IA sirve para acelerar el análisis y la implementación; las decisiones sobre cobertura y los resultados observados siguen siendo responsabilidad del participante.

### Contrato común del ejercicio

Cada caso comienza con una cuenta ficticia con saldo **1000**, sin comisiones, y un historial vacío para esa cuenta. Se transfiere a un destinatario ficticio definido en los datos iniciales. Los datos se aíslan entre casos y participantes.

| Caso | Acción | Resultado que debe comprobarse |
|---|---|---|
| TR-01: transferencia válida | Transferir 100 | Saldo final 900 y exactamente un registro de transferencia para el caso. |
| TR-02: fondos insuficientes | Intentar transferir 1100 | Operación rechazada, saldo 1000 y cero registros de transferencia para el caso. |
| TR-03: idempotencia | Repetir una solicitud de 100 con la misma clave de idempotencia | Un único débito, saldo final 900 y exactamente un registro de transferencia para el caso. |

La repetición de TR-03 ocurre después de recibir respuesta de la primera solicitud. Las solicitudes simultáneas son una extensión; no se debe afirmar que la prueba secuencial demuestra seguridad frente a concurrencia. El contrato implementado fija primera respuesta `201`, segunda `200` y el mismo identificador de transferencia; los reportes locales de los tres lenguajes documentan ese caso. El instructor debe comprobar su propia configuración antes de impartirlo.

Los nombres reales de controles, direcciones de API, estados y mensajes deben salir del contrato y de la demo preparada. No se deben inventar para completar una prueba. Una observación de la interfaz por sí sola tampoco demuestra que hubo un solo débito en el almacenamiento: la demo necesita una forma autorizada de consultar saldo e historial reales del caso.

## 2. Material disponible y preparación para impartir

**Referencia de esfuerzo del diseño inicial: 18–30 horas para producir un material similar desde cero**, suponiendo experiencia con Playwright, una demo pequeña y sin trámites de infraestructura. No representa tiempo medido en esta entrega ni una estimación pendiente completa: los proyectos, prompts y evidencias ya están disponibles. La preparación restante depende de la instalación de la cohorte, la selección de ejercicios y el ensayo; no incluye accesos corporativos ni una aplicación bancaria real.

La ejecución local ya permite estudiar y practicar con el laboratorio. Antes de anunciar la sesión como ensayada, hay que cerrar la preparación de participantes y medir el recorrido de 120 minutos. Un resultado técnico local no acredita por sí solo la duración pedagógica ni el funcionamiento de cada estación.

| Orden | Prioridad y entregable | Evidencia de terminación | Esfuerzo supuesto |
|---|---|---|---|
| 1 | **P0. Contrato y matriz de riesgos** | Disponibles: reglas y datos; revisar la selección de riesgos con la cohorte. | 2–3 h |
| 2 | **P0. Demo reproducible** | Implementada: arranque, estado autoritativo en memoria y hooks de datos; validar las nuevas estaciones. | 4–7 h |
| 3 | **P0. Rutas de los tres lenguajes** | Implementadas y ejecutadas localmente; completar las instalaciones de participantes. | 4–6 h |
| 4 | **P0. Materiales del taller** | Prompts, guías y 12 videos disponibles; elegir los ejercicios y fragmentos para la cohorte. Las diapositivas independientes siguen como propuesta. | 3–5 h |
| 5 | **P0. Fallo preparado y revisión de CI** | Fallo intencional y evidencia disponibles; receta de CI ilustrativa, sin ejecución alojada acreditada. | 2–4 h |
| 6 | **P0. Ensayo y ajuste** | Pendiente: ensayo de 120 minutos con participantes y tiempos medidos. | 3–5 h |

**Extensiones posteriores:** ejecución en varios navegadores, solicitudes concurrentes para idempotencia, distribución de pruebas, regresión visual, accesibilidad y generación sistemática de datos. Se mantienen fuera del recorrido obligatorio para proteger el tiempo dedicado a revisar y comprobar los tres casos.

### Lista P0 de producción

- [x] Entregar demo local, datos ficticios, contrato y reinicio de su estado en memoria.
- [x] Implementar fixtures propias por caso y limpieza delimitada; los reportes registran ausencia de fixtures al finalizar.
- [x] Entregar y ejecutar los tres casos centrales en las rutas de TypeScript, Python y Java.
- [x] Fijar dependencias directas y documentar versiones y navegador de las ejecuciones medidas.
- [x] Proporcionar comandos de inicio y comprobaciones de disponibilidad.
- [ ] Comprobar la instalación de cada estación y, si la cohorte lo exige, un lock transitivo completo de Python y una instalación limpia de Windows.
- [ ] Preparar una versión inicial incompleta y una solución docente por lenguaje.
- [x] Ejecutar la variante defectuosa y conservar la evidencia de doble débito y doble registro.
- [x] Guardar capturas, reportes y trazas locales de las ejecuciones.
- [ ] Ensayar la regresión en la configuración definitiva del aula y revisar los puntos de recuperación.
- [ ] Si se decide mostrar un pipeline alojado, implementarlo y ejecutarlo; la receta actual solo acredita el diseño propuesto.
- [ ] Hacer un ensayo con alguien que no haya creado los materiales.

## 3. Preparación del participante, fuera de los 120 minutos

Enviar las instrucciones al menos dos días antes. Reservar **45–90 minutos orientativos** para esta preparación; los permisos o descargas corporativas pueden ampliar ese tiempo. El alumno elige TypeScript, Java o Python y conserva esa elección durante el taller.

Las guías por lenguaje están en [04-COMANDOS-Y-CI.md](04-COMANDOS-Y-CI.md) y los README de los laboratorios reales. Documentan runtime, runner, dependencias, navegador, arranque y resultados. La ejecución de la estación de construcción está registrada; una instalación limpia y la preparación de cada alumno siguen por comprobar. No se presupone que los tres lenguajes compartan las mismas opciones de configuración.

La serie de 12 lecciones se utiliza fuera de la sesión como preparación o repaso; durante los 120 minutos solo se seleccionan fragmentos breves según [el mapa de videos](videos/COURSE-VIDEO-MAP.md). Verifica el estado audiovisual individual en la biblioteca antes de asignar una lección.

El participante llega con:

- [ ] El proyecto de su lenguaje abierto y la instalación autorizada terminada.
- [ ] La demo ficticia accesible y la prueba mínima ejecutada.
- [ ] Su identificador o conjunto de datos asignado.
- [ ] La herramienta de IA aprobada disponible, o las respuestas de respaldo descargadas.
- [ ] Acceso local al contrato, prompts, proyecto inicial y traza de ejemplo.
- [ ] Una captura o registro del resultado de preparación, sin credenciales ni datos reales.

El facilitador recoge previamente los fallos de preparación y los resuelve antes de la sesión. Si un alumno no puede instalar herramientas, se le asigna una estación aprobada o una pareja con el mismo lenguaje. Observar una ejecución del docente puede permitir trabajar el razonamiento, pero debe registrarse como observación: no equivale a haber ejecutado la regresión personalmente.

**Comprobación del respaldo sin conexión:** confirmar que la estación tiene las dependencias y navegadores necesarios disponibles y que la demo funciona sin servicios externos. Un archivo comprimido con código no garantiza por sí solo una ejecución sin red.

## 4. Guion del facilitador y puntos de control

| Minutos | Intervención del facilitador | Trabajo y evidencia del participante |
|---|---|---|
| 0–10 | Presentar el contrato, una prueba que parece correcta pero omite comprobar el saldo y los límites del trabajo con IA. | Identificar qué afirmación de negocio falta y elegir su lenguaje. |
| 10–25 | Modelar la relación requisito → riesgo → evidencia → aserción. Mostrar cómo un prompt debe pedir evidencia faltante. | Completar la matriz de TR-01/02/03; cada resultado tiene una fuente observable. |
| 25–45 | Mostrar la preparación y el aislamiento de datos, la autenticación y la limpieza. Usar un lenguaje en pantalla y señalar los archivos equivalentes de los otros dos. | Preparar su caso con datos propios; explicar dónde se inicia el estado y cómo se evita compartirlo. |
| 45–65 | Dar el prompt de generación y revisar una propuesta de IA en voz alta. Detenerse ante selectores, respuestas o métodos inventados. | Generar, revisar y ejecutar los tres casos. Registrar estado por caso y evidencia del resultado. |
| 65–70 | Pausa de cinco minutos. | Pausa. |
| 70–85 | Preparar una respuesta 503 simulada y preguntar qué parte del sistema demuestra el ejercicio. | Probar el comportamiento visible de la interfaz ante ese 503; etiquetar la evidencia como prueba de UI con respuesta simulada. |
| 85–100 | Abrir el fallo controlado y conducir el diagnóstico: observación, hipótesis, comprobación, corrección y nueva ejecución. | Explicar una causa apoyada en la traza; proponer o aplicar una corrección que conserve las aserciones de negocio. |
| 100–112 | Presentar la receta de CI y los artefactos de ejecución local existentes. Señalar qué falta para ejecutarla en un proveedor alojado. | Identificar arranque, comando y artefactos; marcar lo ejecutado localmente frente al diseño o configuración de CI. |
| 112–120 | Usar ocho minutos para revisión entre pares y valoración. Recoger los entregables. | Puntuar la evidencia de una pareja, responder una pregunta de límites y entregar su registro final. |

**Control al minuto 25:** ninguna fila crítica carece de resultado esperado o fuente de evidencia. **Al minuto 45:** los datos de cada caso se pueden preparar sin depender de una prueba anterior. **Al minuto 65:** se dispone del estado explícito de los tres casos, incluso si alguno sigue fallando. **Al minuto 100:** el diagnóstico señala observaciones concretas. **Al minuto 120:** el participante entrega su código y evidencia, con sus limitaciones.

La demostración no debe convertirse en tres explicaciones consecutivas del mismo concepto. El docente enseña el concepto una vez y mantiene visibles las equivalencias del material. Con grupos grandes, conviene contar con apoyo por lenguaje o trabajar en parejas; esa dotación debe resolverse en la preparación.

## 5. Propuesta de 14 diapositivas

| N.º | Título propuesto | Momento |
|---|---|---|
| 1 | Qué podremos demostrar en dos horas | 0–10 |
| 2 | Una prueba verde también puede omitir el riesgo | 0–10 |
| 3 | TransferLab: contrato de los tres casos | 10–25 |
| 4 | Del requisito a la evidencia y la aserción | 10–25 |
| 5 | Datos aislados y estado inicial reproducible | 25–45 |
| 6 | Autenticación y preparación en los tres lenguajes | 25–45 |
| 7 | Anatomía del prompt de generación | 45–65 |
| 8 | Revisar y ejecutar: tres casos, tres resultados | 45–65 |
| 9 | Pausa y estado del laboratorio | 65–70 |
| 10 | Respuesta 503 simulada: alcance de la evidencia | 70–85 |
| 11 | Leer la traza antes de modificar la prueba | 85–100 |
| 12 | Corregir la causa y conservar el resultado esperado | 85–100 |
| 13 | Regresión en CI y evidencias de un fallo | 100–112 |
| 14 | Revisión entre pares y próximo incremento | 112–120 |

Las diapositivas sostienen la explicación; los pasos extensos y los prompts completos pertenecen a la guía copiable. Preparar notas docentes con el archivo o evidencia que debe abrirse en cada momento.

## 6. Rúbrica de evaluación

Puntuar cinco criterios de 0 a 2. **Referencia de logro: al menos 8/10 y cumplimiento de todas las condiciones obligatorias.** Una limitación ambiental se documenta y da lugar a completar la evidencia después; no debe convertirse en un aprobado ficticio.

| Criterio | 0 puntos | 1 punto | 2 puntos |
|---|---|---|---|
| Cobertura y resultados esperados | Omite casos o inventa requisitos. | Incluye los tres casos, con alguna comprobación incompleta. | Los tres casos verifican rechazo o aceptación, saldo y número de registros según el contrato. |
| Aislamiento y reproducibilidad | Depende del orden o comparte estado sin control. | Explica el aislamiento, pero su evidencia es parcial. | Prepara datos propios y demuestra ejecuciones independientes. |
| Revisión de la propuesta de IA | Acepta código sin comprobarlo. | Revisa algunas suposiciones y deja otras identificadas. | Resuelve las suposiciones con evidencia y puede explicar las aserciones y decisiones adoptadas. |
| Ejecución y diagnóstico | No entrega resultados o elimina comprobaciones para aprobar. | Entrega resultados parciales y una hipótesis razonable. | Entrega ejecución de los tres casos y diagnóstico del fallo controlado apoyado en evidencia. |
| CI y comunicación de límites | Afirma ejecución o cobertura sin evidencia. | Diseña el flujo y declara qué falta ejecutar. | Revisa evidencia real de CI y distingue configuración, ejecución, simulación y cobertura de negocio. |

Condiciones obligatorias:

1. No presentar una prueba como aprobada sin evidencia de ejecución.
2. No incluir secretos, credenciales ni datos reales en prompts, entregas o artefactos compartidos.
3. No debilitar las aserciones de negocio para conseguir un resultado verde; no ocultar fallos mediante omisiones o reintentos sin diagnóstico.
4. Entregar evidencia de los tres casos principales para acreditar la parte práctica. Si falta, registrar **pendiente de completar**, aunque el análisis obtenga una buena puntuación.

## 7. Hoja del participante y respuestas del docente

**Registro de entrega:** nombre o identificador, lenguaje elegido, versión del proyecto inicial, estado de TR-01/02/03, referencia a evidencia por caso, diagnóstico del fallo preparado y estado de CI. Estados permitidos: no iniciado, generado, revisado, ejecutado con fallo, ejecutado y aprobado, bloqueado con causa. Anotar la razón de cada bloqueo.

Preguntas reutilizables para revisión entre pares o evaluación posterior. Durante el cierre de ocho minutos, seleccionar dos; no intentar resolverlas todas:

1. La interfaz muestra «Transferencia realizada». ¿Qué falta para dar TR-01 por aprobado?
2. La IA propone comprobar únicamente el mensaje de fondos insuficientes. ¿Qué cambios necesita TR-02?
3. Dos solicitudes consecutivas con la misma clave producen saldo 900 y un registro. ¿Qué demuestra y qué queda fuera de TR-03?
4. Una respuesta 503 interceptada produce un aviso correcto. ¿Demuestra que el backend maneja una caída real?
5. Una prueba falla y la IA propone quitar la comprobación del saldo. ¿Cómo conduces el diagnóstico?
6. Existe un archivo de CI, pero nunca se ejecutó. ¿Qué estado debe constar en la entrega?

**Clave docente:**

1. Comprobar el saldo 900 y exactamente un registro mediante las fuentes acordadas; confirmar que el caso empezó en 1000 y sin registros.
2. Comprobar también saldo 1000 y cero registros. El rechazo visual no demuestra ausencia de débito.
3. Demuestra idempotencia para esa repetición secuencial y esas condiciones. No demuestra comportamiento concurrente ni persistencia ante cualquier reinicio.
4. Demuestra el comportamiento de UI frente a la respuesta simulada. No valida el backend, su recuperación ni la ausencia real de efectos financieros.
5. Mantener el resultado esperado, leer la evidencia, contrastar datos iniciales y comportamiento observado, corregir la causa y volver a ejecutar.
6. Configurado o pendiente de ejecución; para declarar aprobación se necesita un resultado real y accesible.

## 8. Contingencias y revisión antes de impartir

**IA lenta o sin acceso:** proporcionar salidas previamente preparadas, identificadas como material de respaldo. El alumno las revisa con el mismo contrato; no se atribuyen a una ejecución en vivo.

**Fallo de red:** usar la demo aprobada, proyectos y artefactos locales previamente comprobados. Si únicamente están disponibles capturas o una traza, continuar el análisis y registrar pendiente la ejecución práctica.

**Restricciones de instalación:** usar una estación o entorno ya autorizado y preparado. No consumir el taller intentando eludir controles del equipo ni cambiar a un sitio bancario externo.

**Grupo atrasado:** usar los puntos de recuperación de los proyectos iniciales y recortar discusión de extensiones. Mantener la pausa, el diagnóstico y los ocho minutos finales. Documentar qué parte completó cada alumno por sí mismo.

La revisión final del facilitador debe confirmar la configuración de la cohorte, el acceso a evidencias locales, material de respaldo legible y un ensayo dentro de 120 minutos. Una ejecución alojada de CI solo se presenta como realizada si existe su run verificable. El estado actual es **laboratorios implementados y verificados localmente; preparación de la cohorte y ensayo pendientes**. Las 12 lecciones audiovisuales están exportadas; la biblioteca permite reproducirlas, consultar sus guiones y saltar entre capítulos.
