# Paquete completo para compartir

Ejecuta desde `videos`, con Python 3.12, FFmpeg y FFprobe disponibles:

```powershell
# Diagnóstico: no escribe archivos. Es el modo predeterminado.
py -3.12 tools/package-full-course.py --dry-run

# Solo después de exportar los 12 episodios y actualizar la biblioteca estricta.
py -3.12 tools/package-full-course.py --create

# Permitir reemplazar exclusivamente el ZIP de entrega indicado abajo.
py -3.12 tools/package-full-course.py --create --overwrite
```

El destino fijo es `delivery/Playwright-IA-curso-completo.zip`; su carpeta raíz es
`playwright-ai-course`. Los argumentos `--ffmpeg` y `--ffprobe` aceptan las rutas
de sus ejecutables si no están en PATH. Los códigos de salida son 0 para una
operación completa, 2 cuando faltan requisitos de entrega y 1 para un error.

El empaquetador reutiliza el selector y las exclusiones de `package-course.py`.
Añade la biblioteca, exactamente 12 MP4 finales, SRT, timelines y los recursos
sintéticos concretos que necesitan las composiciones. Incluye los documentos,
prompts, fuentes de los laboratorios y herramientas para regenerar el curso.
Excluye dependencias instaladas, modelos, pistas WAV/MP3 separadas, calibraciones,
trazas, sesiones y grabaciones de las pruebas. La voz mezclada en los MP4 sí
forma parte del paquete reproducible.

Antes de crear exige biblioteca con 12 disponibles; subtítulos, guiones y marcas
de capítulo vigentes; MP4 H.264 1920×1080 a 24 fps; narración AAC; duración real
de 360–480 segundos; y correspondencia de cada MP4 con su checkpoint y sus hashes
de fuentes. Decodifica todo el audio y comprueba que tenga señal. Estos controles
son técnicos, sin afirmar escucha humana ni reconocimiento de voz.

También exige el QA final vigente, incluida la auditoría de paleta de 144 cuadros
aprobada y su JSON presente: fuentes limpias, revisión visual vigente y cero
regiones verdes/teal de al menos 16 píxeles conectados en ocho direcciones. Los
conteos de píxeles menores se conservan; no se afirma ausencia absoluta de
valores verdes por el rasterizado o la compresión. El paquete incluye el informe
de paleta y el diagnóstico JSON de los 144 pares nativos/decodificados, sin
incluir esas imágenes de QA. Los hashes del informe, Markdown y evidencia deben
coincidir. Sigue el orden de [FINAL-QA.md](FINAL-QA.md) antes de empaquetar; después
del cierre no regeneres `index.html` sin repetir la auditoría y el finalizador.

Cada archivo de contenido tiene SHA-256 en `COURSE-MANIFEST.json`, incluido el
README inicial. Solo el manifiesto excluye su propio hash. Los MP4 usan STORE;
el resto utiliza DEFLATE. Se escribe un `.building`, se comprueba `testzip`, se
verifican de nuevo todos los hashes y se promueve atómicamente. Si algo falla,
el ZIP final anterior permanece intacto; el temporal se conserva para revisión.
Un archivo existente necesita `--overwrite` explícito.

La implementación se comprobó con archivos pequeños en un directorio temporal:
métodos de compresión, SHA/CRC, rechazo de sobrescritura implícita y preservación
del resultado previo ante fuentes modificadas. Los modos `--dry-run` y `--create`
bloquearon el curso incompleto sin crear ZIP. También se verificó la decodificación
completa y señal del MP4 real 01. Estas comprobaciones del empaquetador no equivalen
a haber generado el ZIP completo antes de terminar los doce videos.
