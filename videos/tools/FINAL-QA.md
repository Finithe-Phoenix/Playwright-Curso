# Cerrar la revisión del curso

Desde la carpeta `videos`, con Python 3.12 y FFprobe disponibles:

```powershell
# Solo leer y comprobar evidencia; no genera informes.
py -3.12 tools/finalize_course.py --dry-run

# Cuando los 12 MP4 y sus revisiones estén listos: preparar biblioteca y paleta.
node tools/build-library.mjs --strict
py -3.12 tools/audit_course_palette.py
py -3.12 tools/finalize_course.py --create

# Incorporar el enlace al informe y firmar esa versión definitiva de index.html.
node tools/build-library.mjs --strict
py -3.12 tools/audit_course_palette.py
py -3.12 tools/finalize_course.py --create

# Conservar index.html sin regenerarlo después de la segunda auditoría.
py -3.12 tools/package-full-course.py --dry-run
```

`--ffprobe` permite indicar la ruta del ejecutable. El finalizador devuelve 0
cuando están los doce episodios verificados, 2 cuando quedan requisitos
pendientes y 1 ante un error. El modo predeterminado es `--dry-run`.

Se reutilizan las comprobaciones de `package-full-course.py` para las fuentes,
la procedencia, los subtítulos y los formatos de video. La paleta firma también
`index.html`. Como la biblioteca incluye su fecha de generación y el enlace al QA
vigente, cualquier regeneración posterior requiere repetir la auditoría de paleta
y el finalizador; no necesita repetir renders.

Se exige por episodio:

- Checkpoint de producción `rendered`, MP4 con su SHA correcto e inputs vigentes.
- Video real de 360–480 segundos, H.264, 1920×1080, 24 fps y audio AAC.
- Informe de exportación con decodificación completa del audio aprobada, ligado
  al mismo MP4 mediante SHA-256.
- Doce escenas y subtítulos que coincidan con las fuentes actuales.
- Observaciones visuales con `visualReviewPerformedByAgent: true`, SHA del MP4
  actual, los doce identificadores de escena e `issues: []`.
- Manifiesto de muestras con timeline y MP4 vigentes, doce cuadros en sus puntos
  medios y SHA-256 correcto para cada imagen y hoja de contacto.
- Auditoría final de paleta aprobada: todas las fuentes visuales activas limpias,
  144 cuadros de los doce MP4 con cero regiones verdes/teal de al menos 16 píxeles
  candidatos conectados en ocho direcciones, revisión visual vigente y hashes
  vigentes de cada input. Conserva los conteos de píxeles y componentes menores;
  no exige ni afirma cero píxeles con valores verdes. Un informe `sources-only`
  no es suficiente. Los criterios y el diagnóstico del rasterizado están en
  [PALETTE-AUDIT.md](PALETTE-AUDIT.md).

También exige doce episodios aprobados en `qa/audio-validation.json`, y 22 pruebas
locales: diez esperadas en las estadísticas del runner distribuido, más doce en
los cinco XML primarios del laboratorio mainframe. Comprueba los XML, las sumas y
los casos duplicados para no contabilizar repeticiones como cobertura adicional.
No ejecuta nuevamente pruebas, voz, renders o revisiones visuales.

`--create` solo escribe `qa/VIDEO-REVIEW.md` y `qa/final-validation.json`. Prepara
ambos archivos, vuelve a contrastar los hashes de toda la evidencia y promueve
cada archivo de forma atómica. El JSON se promueve al final y contiene el SHA-256
del Markdown para identificar el par. Las fuentes, audio, observaciones y progreso
de producción permanecen intactos. Si existe un temporal `.building`, hay que
inspeccionarlo antes de repetir una publicación.

El informe distingue controles técnicos y muestreo visual por un agente. No
afirma reproducción completa, escucha humana, sincronización entre todas las
muestras, CI alojada ni ensayo completo del taller. Conserva la limitación del
mainframe simulado y de la idempotencia secuencial.
