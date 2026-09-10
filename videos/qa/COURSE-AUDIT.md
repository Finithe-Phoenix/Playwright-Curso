# Auditoría del curso y de la portabilidad del laboratorio

Revisión del 9 de septiembre de 2026. Alcance: los cinco documentos del curso original, su entrada LEEME, los 12 episodios y 144 escenas, los proyectos TypeScript/Java/Python, el adaptador TNZ, las instrucciones de Windows y los resúmenes de ejecución. Esta revisión no sustituye la inspección audiovisual de los MP4 ni un ensayo de 120 minutos con participantes.

La arquitectura técnica de los guiones es consistente: Playwright observa navegador y HTTP; IBM tnz controla TN3270; el terminal simulado consulta la misma fuente autoritativa en memoria; la proyección del ledger se verifica por separado. Los problemas relevantes encontrados se concentran en comandos, ciclo de vida, coherencia de ejemplos y orientación hacia las carpetas realmente entregadas.

## Hallazgos prioritarios y correcciones

| Prioridad | Hallazgo concreto y efecto | Corrección o estado |
|---|---|---|
| P1 | El README TypeScript indicaba `npm ci` y Edge ya instalado, pero la configuración tiene `video: 'on'`. Un Windows sin la caché de Playwright necesita también el FFmpeg de Playwright; el FFmpeg del sistema de producción no lo reemplaza. | Corregido en `lab/distributed/README.md` y `LEEME-VIDEOS.md`: `npx playwright install ffmpeg`. El CLI 1.63.0 aceptó `install ffmpeg --dry-run`, salida 0, e identificó FFmpeg 1011 y Winldd 1007. Se solicitó la misma adición al panel 01-04. No se simuló una instalación limpia de Windows. |
| P1 | La escena 02-09 recargaba una página recién creada después de dos POST por API. Sin navegación previa, `reload()` recarga `about:blank` y la aserción de saldo no encuentra la UI. | Corregido en el guion: `await page.goto('/transfers');` antes de `reload()`. La suite ejecutada ya utilizaba `goto`. |
| P1 | La escena 03-10 recomienda `--tracing=retain-on-failure`, mientras que el primer híbrido Python iniciaba/detenía una traza manual sobre el contexto administrado por el plugin. Además, una excepción al finalizar la traza podía impedir borrar la fixture. | Corregido por el propietario del laboratorio: respetar la propiedad de la traza del plugin; iniciar la traza manual solo con tracing `off`; finalización anidada para intentar la limpieza aunque falle la traza. El comando con tracing del plugin se ejecutó con tres casos aprobados, según `lab/mainframe/evidence/VERIFICATION.md`. También se corrigió la finalización Java. |
| P1 | Los videos 03/04 presentan los tres casos de negocio, pero inicialmente Java y Python solo incluían un caso híbrido exitoso. Un alumno no podía ejecutar TR-02/TR-03 en esas rutas sin implementarlos. | Resuelto con `test_core_regression.py` y `java/src/test/java/training/CoreRegressionTest.java`. Los reportes posteriores incluyen tres casos Python y tres Java: éxito híbrido, fondos insuficientes e idempotencia. |
| P2 | Los fragmentos Python usan rutas relativas como `/api/session`, pero el proyecto inicial no configuraba una URL base para el contexto del plugin. | Corregido en `lab/mainframe/pytest.ini`: `base_url = http://127.0.0.1:3000`. El código ejecutable utiliza también su variable `BASE_URL` para peticiones explícitas. Si se cambia de host, revisar ambas configuraciones al reutilizar fragmentos relativos. |
| P2 | El Maven de Java excluye el paquete opcional de Node. Un `mvn test` aislado no explica `PLAYWRIGHT_NODEJS_PATH`, el navegador ni la clave de preparación. | La escena 01-06 ya incluye Node, clave sintética, canal Edge y la condición de tener los servicios listos. El README Java contiene la instalación de Chromium y el uso de Node. Añadir al capítulo 04 una referencia visible al procedimiento previo; `mvn test` presupone ese entorno. |
| P2 | Después del defecto, la variable `ARTIFACT_DIR=evidence/defect` persiste en la terminal. Cambiar solo BASE_URL y repetir TR-03 puede sobrescribir el artefacto fallido que la lección pide conservar. | Corregido en la escena 08-08: restaurar BASE_URL y escribir el nuevo resultado en `evidence/healthy-recheck`. |
| P2 | La primera versión de 10-11 mencionaba una prueba de backend no disponible que no estaba entre las cuatro pruebas del protocolo. | Resuelto con una quinta prueba TN3270 real y una narración que enumera los cinco casos: éxito, referencia desconocida, entrada inválida, plazo de pantalla agotado y backend no disponible. Los cinco están declarados y reportados como aprobados. |

## Puntos que deben cerrarse antes de la distribución final

### 1. Orientar la guía original hacia el laboratorio que sí existe

Los documentos originales conservan su estado de planificación y rutas `work/starter/...` que no existen. Ejemplos concretos:

- `../LEEME.md:26`: afirma que aún no hay aplicación ejecutable ni suites validadas.
- `../03-LABORATORIO-Y-LENGUAJES.md:3` y `:9`: presentan la aplicación y el starter como futuros.
- `../04-COMANDOS-Y-CI.md:3`, `:31`, `:34`, `:51`, `:82` y `:109`: comandos de carpetas futuras y Maven wrapper aún inexistente.
- `../05-PREPARACION-Y-EVALUACION.md:7`: indica que la demo y las ejecuciones están pendientes.

No basta con ocultar esas diferencias dentro del ZIP. Propuesta para la cabecera de los documentos originales y la portada HTML:

> **Actualización del material práctico:** el laboratorio ejecutable y sus resultados se encuentran en `videos/lab/distributed` y `videos/lab/mainframe`. Para instalar y ejecutar esta entrega, utilizar sus README y `videos/LEEME-VIDEOS.md`. Las rutas `starter` de este documento pertenecen al diseño inicial. La biblioteca de 12 videos complementa el taller de 120 minutos.

Mantener explícitos los entregables que continúen como propuesta, por ejemplo un ensayo externo del taller o un pipeline alojado que no se haya ejecutado. La generación de archivos y una ejecución local no acreditan esos puntos.

### 2. Mantener el mismo importe en el ejemplo TR-02

El curso, las narraciones y TypeScript usan 1100.00 MXN como intento contra un saldo de 1000.00. Los nuevos casos Python y Java inicialmente usaron 1000.01. Ambos verifican fondos insuficientes, pero no son exactamente el mismo experimento descrito en las lecciones.

Se solicitó al propietario alinear el importe a `1100.00` y repetir los casos afectados, o declarar expresamente la variante de límite de un centavo. Comprobar el valor final en los archivos y sus reportes antes de afirmar equivalencia exacta entre las tres rutas.

### 3. Separar versión fijada de instalación limpia comprobada

La ejecución local utilizó dependencias fijadas de los proyectos y Edge 152.0.4191.66. No se ejecutó una instalación en un Windows vacío. Los alumnos necesitan Node, Python 3.12 y, si eligen Java, JDK y Maven. La alternativa Chromium descarga navegadores distintos según la versión de Playwright de cada lenguaje. No compartir una ruta de navegador basada únicamente en que las versiones de la librería se parezcan.

Los requirements de Python fijan dependencias directas. El plan original exige además un lock completo de transitivas; mantener esa distinción o generar un lock del entorno elegido antes de congelar el paquete para una cohorte. La caché `.venv`, Maven `.tools` y `node_modules` de la estación se excluye deliberadamente del ZIP de fuentes; por ello ese ZIP no debe anunciarse como instalable sin red.

### 4. Usar “estado autoritativo” para el laboratorio en memoria

`../01-PLAN-DEL-CURSO.md:26` habla de estado persistido. En esta aplicación, cuenta, registro y outbox están en memoria y desaparecen al reiniciar. Propuesta: “Verificar una transferencia en la interfaz y en el estado autoritativo del laboratorio; comprobar idempotencia por API”. Los episodios 06, 09 y 11 ya explican correctamente este límite.

## Snippets de preparación recomendados

Desde la carpeta real `videos/lab/distributed`, antes de clase:

```powershell
npm ci
npx playwright install ffmpeg
$env:TEST_HOOK_KEY = 'classroom-demo-only'
npm run start:lab
```

Desde `videos/lab/mainframe/java`, con el simulador y los servicios ya iniciados y Edge instalado:

```powershell
$env:TEST_HOOK_KEY = 'classroom-demo-only'
$env:PLAYWRIGHT_NODEJS_PATH = (Get-Command node).Source
$env:PW_BROWSER_CHANNEL = 'msedge'
mvn test
```

Desde `videos/lab/mainframe`, con el entorno Python preparado y la misma condición de servicios:

```powershell
$env:TEST_HOOK_KEY = 'classroom-demo-only'
.\.venv\Scripts\python.exe -m pytest test_hybrid_browser.py test_core_regression.py --browser-channel msedge --tracing=retain-on-failure --junitxml=evidence\python-core-plugin-tests.xml
```

Las rutas concretas deben ajustarse al lugar de extracción del paquete. Los comandos de instalación de Chromium y las diferencias entre canal por defecto y canal Edge están en el README de cada proyecto.

## Elementos revisados que están correctamente delimitados

- Las cantidades de API son enteros en centavos y la moneda se comprueba por separado.
- La idempotencia demostrada es secuencial: misma clave, mismo cuerpo, misma identidad y un solo efecto. No se atribuye seguridad frente a concurrencia a esa prueba.
- La colección canónica y la proyección del ledger tienen endpoints diferentes. El sondeo consulta estado y no vuelve a enviar transferencias.
- El mock 503 se identifica como recuperación de UI y no como una interrupción real de servicio.
- La integración TNZ utiliza una conexión real al simulador local; no se presenta como z/OS, CICS, DB2 ni conciliación de una fuente independiente.
- Java, Python y TypeScript conservan sus propios runners, aserciones y reportes. Los fragmentos ilustrativos tienen esa identificación y no se presentan como archivos completos.
- CI se describe como diseño hasta que exista una ejecución alojada verificable.
- El catálogo y mapa separan los 72–96 minutos previstos de la serie y los 120 minutos de taller.

## Fuentes primarias comprobadas

La revisión contrastó comandos y propiedad de fixtures con la [referencia oficial del plugin pytest](https://playwright.dev/python/docs/test-runners), el arranque Java con la [documentación de instalación de Playwright Java](https://playwright.dev/java/docs/intro), la distinción configuración/ejecución CI con la [guía oficial de CI](https://playwright.dev/docs/ci-intro), y los nombres públicos de TNZ con la [referencia de IBM](https://ibm.github.io/tnz/tnz/). Los detalles específicos de TransferLab se verificaron contra su código y sus reportes locales.

## Preparación del paquete de fuentes

Se creó `tools/package-course.py`. Su modo predeterminado es `--dry-run`: inventaría y comprueba las fuentes sin crear un ZIP. La primera revisión incluyó 80 archivos y aproximadamente 2.56 MB antes de incorporar el resto de composiciones y subtítulos; ese tamaño no es el tamaño final de distribución.

El generador excluye entornos instalados, modelos, Maven descargado, compilados, cachés, grabaciones, audio binario, trazas y reportes pesados. Conserva resúmenes de verificación en Markdown, código, lockfiles, requirements, guiones, prompts, fuentes y licencias de tipografía, y opcionalmente subtítulos/timelines. Detecta formas comunes de claves privadas y tokens antes de escribir; no imprime coincidencias.

El `videos/index.html` generado se excluye del ZIP de fuentes, porque sus MP4 no se empaquetan allí. Se incorpora un README interno que explica cómo instalar dependencias y regenerar la biblioteca usando el conjunto completo de medios. De esa forma el ZIP no marca videos ausentes como disponibles.

Comando final, únicamente cuando la producción y las ediciones estén cerradas:

```powershell
py -3.12 tools\package-course.py --create
```

El ZIP incluye un manifiesto SHA-256 por fuente y se comprueba con `ZipFile.testzip()` antes de completar la escritura. Durante esta auditoría se ejecutaron análisis de sintaxis, exclusiones y modo de inventario; **no se creó el ZIP**, según la instrucción de esperar a la producción final.
