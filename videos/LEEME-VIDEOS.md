# Biblioteca de videos: Playwright avanzado con IA

Abre [index.html](index.html) para recorrer las doce lecciones, reproducir los videos, leer los subtítulos en inglés, saltar a cada paso y copiar la narración y el código. La interfaz de la biblioteca está en español; la voz sintética, los subtítulos y las explicaciones de los videos están en inglés.

La entrega contiene **12 MP4 de 7:03–7:32**, **87:20 en total**, producidos con Hyperframes a **1920 × 1080 y 24 fps**. La voz de IA es JennyNeural en inglés y cada MP4 incorpora sus subtítulos visibles. La biblioteca muestra la duración real de cada lección. Es material de preparación y repaso del [taller de 120 minutos](../01-PLAN-DEL-CURSO.md). La serie completa se ve fuera de esas dos horas; en clase se utilizan fragmentos breves y se practica con el laboratorio.

## Abrir y utilizar

1. Conserva la carpeta `videos` completa: la biblioteca utiliza rutas relativas para los MP4, subtítulos, guiones y laboratorios.
2. Inicia el servidor local indicado abajo y abre la biblioteca en Edge u otro navegador actual. Selecciona una lección y utiliza los controles del video. `Abrir MP4` permite abrir el archivo directamente.
3. En **Pasos**, selecciona una marca de tiempo para ir a esa explicación. En **Guion y código**, puedes copiar el texto completo o seleccionar un fragmento. **Fuentes** enlaza la documentación original.
4. Los MP4 ya tienen subtítulos visibles en inglés; también está disponible el archivo SRT y una pista adicional opcional, desactivada inicialmente para evitar texto duplicado. Las preferencias de avance se guardan solamente en el navegador local, cuando este lo permite.

Para reproducir y saltar a cualquier capítulo, sirve la carpeta localmente desde PowerShell. Requiere Node.js y admite solicitudes parciales de video:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos'
node tools\serve-course.mjs
```

Abre [la biblioteca local](http://127.0.0.1:8766/videos/index.html). Se sirve la carpeta `work` para que también funcionen los enlaces a la guía original del curso. Mantén esa terminal abierta mientras ves los videos; pulsa **Ctrl+C en esa misma terminal** para detener únicamente el servidor de la biblioteca. Si el puerto 8766 está ocupado, utiliza `node tools\serve-course.mjs --port 8768` y cambia ese número en la dirección. El servidor escucha únicamente en `127.0.0.1`. Los capítulos pueden avanzar hacia partes que todavía no se han descargado gracias al soporte HTTP Range.

## Qué significa el estado de cada video

- **Disponible:** el archivo MP4 existe, FFprobe detectó imagen y audio, y su duración está dentro del objetivo de 6–8 minutos. Esto verifica su estructura; la revisión pedagógica, visual y de la voz se documenta por separado.
- **En preparación:** todavía no existe el MP4 final. Los guiones presentes pueden consultarse mientras se produce el video.
- **Actualizándose:** existe una exportación anterior y se está produciendo la versión que corresponde a las fuentes actuales.
- **Archivo sin verificar**, **Render incompleto**, **Voz pendiente** o **Revisar duración:** el archivo requiere una comprobación adicional. La biblioteca no lo cuenta como una lección terminada.

El estado se fija al generar la biblioteca. Para incorporar videos nuevos, el instructor vuelve a ejecutar el generador descrito al final de este documento. Si existe un informe final de revisión, la biblioteca ofrece su enlace en el pie de página.

## Material incluido

La [revisión final](qa/VIDEO-REVIEW.md) reúne las duraciones, formatos, validación técnica de audio, pruebas de laboratorio y revisión visual de doce cuadros por episodio.

| Carpeta o archivo | Uso |
|---|---|
| `renders/` | Videos MP4 terminados, uno por episodio. |
| `audio/01/` … `audio/12/` | Narración, subtítulos SRT y tiempos de escenas de cada episodio. |
| `compositions/` | Proyectos editables de Hyperframes y guiones `SCRIPT.md`. |
| [scripts/episodes.json](scripts/episodes.json) | Guiones, código mostrado, objetivos y fuentes de todas las lecciones. |
| [lab/distributed/README.md](lab/distributed/README.md) | TransferLab: navegador, gateway, cuentas, proyección de ledger y pruebas TypeScript. |
| [lab/mainframe/README.md](lab/mainframe/README.md) | Simulador TN3270, cliente IBM tnz y ejercicios híbridos por lenguaje. |
| [COURSE-VIDEO-MAP.md](COURSE-VIDEO-MAP.md) | Qué ver antes de clase, qué fragmentos usar y qué entregar. |
| [FRAGMENTOS-PARA-LA-CLASE.md](FRAGMENTOS-PARA-LA-CLASE.md) | Marcas exactas para los fragmentos dentro del taller. |
| [Prompts del curso](../02-PROMPTS-COPIAR-PEGAR.md) | Prompts reutilizables para diseñar, generar, diagnosticar y revisar regresiones. |

Los MP4 narrados son las lecciones. Los videos breves guardados por los runners dentro de `lab/**/evidence` son evidencia de ejecución; cumplen otra función y no sustituyen los tutoriales narrados.

## Ejecutar el laboratorio distribuido

Instala las dependencias antes de la clase. La ruta TypeScript requiere Node.js 22 o posterior. El proyecto fija sus paquetes en `package-lock.json`; la configuración predeterminada utiliza Microsoft Edge en un contexto de pruebas nuevo. La alternativa Chromium se explica en su README.

**Terminal 1 — aplicación de entrenamiento:**

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\distributed'
npm ci
npx playwright install ffmpeg
$env:TEST_HOOK_KEY = 'classroom-demo-only'
npm run start:lab
```

La grabación de las pruebas necesita el FFmpeg de Playwright incluso cuando se utiliza Edge ya instalado. El comando anterior instala esa dependencia; es distinta del FFmpeg del sistema utilizado para producir los tutoriales. La instalación de Playwright Chromium también incluye este componente.

La aplicación se abre en [TransferLab local](http://127.0.0.1:3000/transfers). El arranque crea tres procesos propios, ligados a `127.0.0.1`, en los puertos 3000, 3001 y 3002. Las pruebas crean su propio acceso sintético mediante una fixture y autentican su navegador. La página de acceso manual requiere las credenciales de una fixture vigente.

**Terminal 2 — regresiones TypeScript:**

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\distributed'
$env:TEST_HOOK_KEY = 'classroom-demo-only'
npm test
npm run report
```

`classroom-demo-only` es un valor público de entrenamiento. No corresponde a una credencial bancaria o empresarial. La misma variable debe estar configurada en la aplicación y en la terminal de pruebas.

## Añadir el terminal TN3270

El laboratorio utiliza el cliente real **IBM tnz** contra un **servidor TN3270 simulado localmente**. Playwright controla navegador y HTTP; tnz escribe la referencia en un campo del terminal y lee su resultado. El simulador consulta los datos en memoria de TransferLab. Esto demuestra coordinación entre protocolos; no demuestra conciliación independiente contra z/OS, CICS o DB2.

Con Python 3.12 instalado, prepara el entorno antes de la clase y deja corriendo la aplicación de la terminal 1.

**Terminal 3 — preparación y arranque del simulador:**

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\mainframe'
.\setup.ps1 -Browser
.\start.ps1
```

El simulador escucha en `127.0.0.1:2323`. En otra terminal, comprueba la pantalla mediante una sesión real de tnz y ejecuta la integración Python:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\mainframe'
.\.venv\Scripts\python.exe adapter.py health --timeout 5
$env:TEST_HOOK_KEY = 'classroom-demo-only'
.\.venv\Scripts\python.exe -m pytest test_hybrid_browser.py -q --junitxml=evidence\hybrid-python-tests.xml
```

La ruta Java requiere JDK y Maven; los comandos y las variantes TypeScript/Python están en el [README del laboratorio TNZ](lab/mainframe/README.md). Cada participante trabaja con un lenguaje. No copies flags de Playwright Test a Maven o pytest: cada runner tiene sus propias opciones y gestión de artefactos.

Para terminar, pulsa **Ctrl+C en la terminal del simulador** y después **Ctrl+C en la terminal de la aplicación distribuida**. El coordinador de la aplicación detiene sus tres procesos. Cierra también el servidor de reportes o de la biblioteca si lo iniciaste. Reiniciar la aplicación elimina sus datos en memoria.

## Cómo practicar con la IA

Abre primero el contrato y el código del laboratorio elegido. Usa los prompts del curso con ese contexto y pide una prueba pequeña. Revisa preparación, autenticación, aserciones de negocio y limpieza antes de ejecutarla. Registra el comando y el resultado real. Cuando algo falle, entrega a la IA el error y la evidencia pertinente; conserva el resultado de negocio esperado durante la corrección.

En aplicaciones distribuidas, verifica el estado autoritativo y consulta la proyección con una referencia exacta y un plazo máximo. En el terminal, verifica la pantalla esperada y el teclado disponible antes de introducir datos. Evita transformar una espera arbitraria en una supuesta garantía de negocio.

Los resultados ya medidos se encuentran en las carpetas de evidencia y en los documentos de verificación de cada laboratorio. Distingue siempre una ejecución local verificada, un defecto deliberado, un fragmento ilustrativo y una adaptación pendiente a un sistema real.

## Actualizar la biblioteca — instructor

El generador utiliza Node.js y FFprobe. Busca FFprobe en `PATH`, admite `FFPROBE_PATH` y dispone de una alternativa para la instalación local de WinGet. También puede recibir una ruta explícita:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos'
node tools\build-library.mjs

# Revisión final: exige los 12 videos, subtítulos, guiones y escenas.
node tools\build-library.mjs --strict

# Alternativa si FFprobe no está en PATH:
node tools\build-library.mjs --ffprobe 'C:\Users\daedg\AppData\Local\Microsoft\WinGet\Links\ffprobe.exe' --strict
```

El primer comando regenera `index.html` y muestra el estado real de cada episodio. `--strict` devuelve un código distinto de cero si falta algún componente requerido; no convierte archivos ausentes en videos disponibles. El reproductor convierte los SRT a pistas WebVTT en memoria, sin depender de un servicio externo ni de una CDN.
