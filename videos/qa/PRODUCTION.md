# Producción de los doce videos

La narración de producción usa Edge TTS, voz inglesa `en-US-JennyNeural`, velocidad `+0%`. `tools/synthesize_edge.py` conserva los tiempos reales de la voz y genera el audio, los subtítulos y `audio/NN/timeline.json`. Kokoro permanece como alternativa local; fue demasiado lento para esta producción. Cada episodio debe durar entre 360 y 480 segundos. Las narraciones completas deben existir antes de producir su episodio.

Ejecutar estos ejemplos desde la carpeta `work\videos`, con las dependencias instaladas. El orquestador ejecuta procesos ocultos y un único episodio a la vez.

```powershell
# Consultar narraciones listas, sin crear archivos ni iniciar renders.
.\.venv\Scripts\python.exe tools\render_course.py --plan

# Producir un episodio completo.
.\.venv\Scripts\python.exe tools\render_course.py --episode 02

# Continuar desde el segundo episodio; esperar hasta 30 minutos acumulados
# cuando todavía falten narraciones. Los renders tienen su propio límite.
.\.venv\Scripts\python.exe tools\render_course.py --from 02 --wait 1800

# Producir los doce o reanudar un lote interrumpido.
.\.venv\Scripts\python.exe tools\render_course.py --all --wait 1800

# Validar un MP4 que se produjo manualmente. Esta consulta no lo adopta
# ni afirma que se haya aprobado su diseño o la procedencia de sus fuentes.
.\.venv\Scripts\python.exe tools\render_course.py --episode 01 --verify-only

# Después de revisar las fuentes de un MP4 manual: repetir controles y
# capturas, validar el archivo existente y registrarlo sin volver a renderizar.
.\.venv\Scripts\python.exe tools\render_course.py --episode 01 --adopt-existing
```

`--wait` limita la espera acumulada por audio pendiente. Sin esa opción se procesan las narraciones disponibles y se devuelve código 2 si faltan episodios. Un fallo devuelve 1; una interrupción devuelve 130. El código 0 confirma los controles técnicos de los episodios seleccionados; la revisión visual sigue siendo un paso separado y documentado. `--plan` y `--verify-only` no escriben un manifiesto de producción.

## Perfil y controles

Hyperframes está fijado a **0.8.33**. La ejecución usa Chrome de `C:\Program Files\Google\Chrome\Application\chrome.exe`, modificable mediante `--browser`. FFprobe y FFmpeg se buscan en `PATH`; se pueden indicar mediante `--ffprobe` y `--ffmpeg`. El perfil conserva H.264, 1920×1080, 24 fps, calidad alta, un trabajador, GPU y modo de memoria reducida. No ejecutar dos productores al mismo tiempo ni arrancar un lote mientras otro render manual consume los mismos recursos.

1. Validar doce escenas consecutivas, duración de 6–8 minutos, audio completo y subtítulos SRT coherentes con los tiempos reales. Todos los subtítulos deben tener texto, duración positiva y límites válidos.
2. Calcular SHA-256 de la línea de tiempo, narración, subtítulos, constructor, tipografías, GSAP y las imágenes de evidencia utilizadas por cada episodio.
3. Construir la composición y ejecutar `hyperframes check --json` en el punto medio de cada escena. Se exige `ok: true`; el límite externo es de 300 segundos.
4. Obtener doce capturas y una hoja de contacto en `qa/episodes/NN/<hash>/`. Estos archivos permiten revisar cada escena antes de considerar final el curso.
5. Renderizar un MP4 en `renders/.staging/`, con límite de 1.800 segundos por episodio. El archivo definitivo anterior permanece disponible durante la nueva ejecución.
6. Comprobar H.264, resolución, 24 fps, audio presente y duración del contenedor/audio a menos de 0,3 segundos de la narración. FFmpeg decodifica todo el audio y debe terminar sin errores. `--audio-metrics` añade niveles de pico y RMS; `--skip-audio-check` omite únicamente la decodificación completa y queda registrado en las opciones del operador.
7. Volver a calcular las fuentes. Si cambiaron durante el proceso, conservar el render temporal para revisión y detener la promoción. Si coinciden y los controles pasan, promover el MP4 de forma atómica y guardar `qa/episodes/NN/validation.json`.

El curso incorpora subtítulos visibles dentro de la composición. La biblioteca ofrece una pista adicional opcional, desactivada por defecto para evitar texto duplicado.

## Ajuste acotado del tiempo de verificación

La versión instalada limita a 15 segundos la comprobación de imágenes estáticas. En el primer episodio esta ventana agotó su tiempo antes de revisar todos los segmentos candidatos. `tools/configure_hyperframes.py` cambia **una única asignación**, exclusivamente en Hyperframes 0.8.33:

```javascript
STATIC_VERIFY_MAX_MS = Number(process.env.HF_COURSE_STATIC_VERIFY_MAX_MS ?? "15000");
```

El valor original se mantiene si no se define la variable. El orquestador utiliza 90.000 ms por defecto; `--verification-budget-ms` acepta entre 15.000 y 300.000. El ajuste concede más tiempo a las comparaciones de píxeles antes de recurrir a capturar todos los cuadros. **Las comparaciones permanecen activadas**: `HF_STATIC_DEDUP_VERIFY=true`. No cambia las muestras, el algoritmo de comparación, la resolución, la frecuencia de cuadros ni el códec. Su efecto en el rendimiento depende de las escenas y del equipo; el ahorro del lote completo debe medirse en los registros reales.

El helper exige una sola coincidencia conocida, verifica la versión y conserva una copia con SHA-256 en `.tools/hyperframes-backups/`. Registra el archivo original, el modificado y el ajuste en `qa/hyperframes-performance.json`. Repetirlo es idempotente; ante una versión o asignación desconocida se detiene sin modificar el CLI. `npm ci` reinstala la versión original y la siguiente ejecución del orquestador vuelve a aplicar el ajuste controlado.

```powershell
.\.venv\Scripts\python.exe tools\configure_hyperframes.py --dry-run
.\.venv\Scripts\python.exe tools\configure_hyperframes.py --verification-budget-ms 90000
```

El entorno también configura `HF_STATIC_DEDUP=true`, `PRODUCER_LOW_MEMORY_MODE=true`, `PRODUCER_MAX_WORKERS=1`, `PRODUCER_ENABLE_STREAMING_ENCODE=true` y `PRODUCER_STREAMING_ENCODE_MAX_DURATION_SECONDS=600`. La activación explícita de streaming evita que el ajuste automático de Windows lo deshabilite al combinar memoria reducida y un trabajador. Conserva las comparaciones de imágenes y permite solapar captura y codificación; el ahorro se mide en los registros. Los episodios 01 y 02 usan H.264 NVENC, aunque 02 completó captura y codificación como fases separadas antes de aplicar esta configuración.

## Reanudación y evidencia

`production-progress.json` se actualiza atómicamente por etapa y conserva los hashes, registros y datos del MP4. Un archivo que coincide con su hash de fuentes y su SHA registrado se vuelve a validar y se reutiliza. Un MP4 existente sin procedencia registrada se conserva y exige `--adopt-existing` para adoptarlo explícitamente. Un render incompleto permanece en `.staging`; una nueva tentativa usa un nombre separado si ese archivo no pasa la validación.

`.production.lock` impide dos lotes simultáneos. Ante una interrupción se detiene solamente el árbol del proceso hijo que lanzó el orquestador. No se cierran navegadores ni procesos del usuario. Un bloqueo cuyo propietario ya terminó puede recuperarse automáticamente.

Los registros por episodio están en `logs/NN-build.log`, `NN-check.json`, `NN-check.stderr.log`, `NN-snapshots.log`, `NN-render.log` y `NN-audio-integrity.log`. La consola informa la etapa y un latido cada 30 segundos durante las operaciones largas. Las capturas requieren revisión visual; el manifiesto las marca `visualReview: pending` hasta que esa revisión se documente por separado.

La validación del orquestador durante su implementación comprobó sintaxis, planificación con audio real, metadatos del piloto de 12 segundos y rechazo de duraciones cortas, subtítulos fuera de rango y escenas superpuestas. Estas comprobaciones no equivalen a doce videos terminados. El avance real se consulta en los MP4, los registros y el manifiesto de producción.

## Revisión visual de los MP4 exportados

El [muestreador de exportaciones](../tools/review_exports.py) utiliza FFprobe, FFmpeg y [Pillow 11.3.0](../tools/requirements-render-qa.txt). Ejecutar desde `work\videos`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r tools\requirements-render-qa.txt
.\.venv\Scripts\python.exe tools\review_exports.py --episode 01 --require-final
# Cuando los doce registros y archivos correspondan a sus fuentes vigentes:
.\.venv\Scripts\python.exe tools\review_exports.py --available --require-final
```

`--require-final` exige la etapa `rendered`, el SHA-256 del timeline vigente y el SHA-256 del MP4 registrado en producción. Así evita aprobar una exportación anterior mientras se produce su corrección. El muestreador excluye calibraciones, extrae un PNG de 1920×1080 en el punto medio real de cada una de las doce escenas y crea dos hojas de contacto de seis muestras en `qa/export-review/NN/`. `manifest.json` conserva los tiempos, hashes, metadatos y nombres de archivo. Repetir la ejecución con los mismos hashes reutiliza las imágenes verificadas.

La extracción automática deja `visualReviewPerformedByAgent: false`. Después de inspeccionar las imágenes, el agente puede registrar `observations.json`, su SHA del MP4 y las doce escenas revisadas, y actualizar ese campo a `true`. Una revisión anterior solo corresponde al SHA que identifica. La revisión de cuadros muestreados no equivale a reproducción completa, escucha del audio, evaluación de transiciones ni validación perceptual de sincronización. Esas limitaciones se conservan explícitas en cada observación; los problemas detectados se registran sin convertirlos automáticamente en aprobaciones.
