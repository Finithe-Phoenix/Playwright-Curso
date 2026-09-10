# Empezar: Playwright avanzado con IA

Este paquete contiene los 12 videos MP4 finales con imagen 1080p y narración
sintética en inglés, subtítulos, guiones, prompts y código del curso de dos horas.
La serie completa sirve como preparación y repaso; el plan del taller indica
los fragmentos y ejercicios que se utilizan durante los 120 minutos de clase.

## Ver los videos

1. Extrae TODO el ZIP y conserva la carpeta playwright-ai-course y su estructura.
2. Abre videos/index.html en Edge u otro navegador actual. También puedes abrir
   directamente cualquiera de los 12 archivos en videos/renders.
3. Si el navegador limita archivos locales o quieres saltar entre capítulos,
   instala Node.js 22 o posterior. Desde la carpeta extraída playwright-ai-course,
   ejecuta en PowerShell:

   node videos/tools/serve-course.mjs

   Abre http://127.0.0.1:8766/videos/index.html. El servidor admite HTTP Range;
   mantén esa terminal abierta y usa Ctrl+C en ella para detenerlo.
   Si 8766 está ocupado: node videos/tools/serve-course.mjs --port 8768

Los MP4 incluyen la voz y subtítulos visibles. Los SRT separados y los tiempos de
escena están en videos/audio/01 a videos/audio/12. La biblioteca permite copiar
guiones y código. No necesita descargar los videos ni utilizar un servicio de IA
para reproducirlos después de extraer este ZIP.

## Preparar los laboratorios

Lee primero 01-PLAN-DEL-CURSO.md, 02-PROMPTS-COPIAR-PEGAR.md y los README de
videos/lab/distributed y videos/lab/mainframe. Instala Node.js, Python 3.12 y,
si eliges Java, JDK y Maven, según esas instrucciones. La instalación inicial de
paquetes y navegadores necesita internet. Este ZIP no instala esas herramientas
ni demuestra que ya funcionen en el equipo de quien lo recibe.

Cada participante ejecuta la aplicación distribuida y el simulador TN3270
localmente. IBM tnz es un cliente real; el servidor TN3270 es un simulador de
formación que consulta los mismos datos en memoria de TransferLab. No incluye
z/OS, CICS, DB2 ni acceso a un mainframe real. Los datos y capturas son sintéticos.
Los resúmenes de validación describen la estación de producción; ejecuta las
pruebas en tu equipo para obtener tus propios resultados.

## Editar y regenerar

Se incluyen fuentes Hyperframes, guiones, scripts de producción, recursos visuales
y dependencias fijadas en los manifiestos. No se incluyen paquetes instalados,
modelos de IA, cachés, trazas ni las pistas de voz WAV/MP3 separadas. La voz ya
mezclada en los MP4 sí está incluida para reproducción.

Para regenerar, instala las dependencias de videos/package-lock.json y
videos/tools/requirements-voice.txt y sigue videos/tools/AUDIO-ENGINE.md y
videos/qa/PRODUCTION.md. Regenera primero la narración con el motor configurado;
su servicio en línea recibe los guiones que elijas enviar. Los modelos Kokoro
son una alternativa opcional y se descargan por separado. Las composiciones
editables requieren que vuelvas a generar sus WAV antes de renderizar.
Las rutas absolutas de ejemplos de la estación original deben adaptarse al
lugar donde extrajiste este paquete.

COURSE-MANIFEST.json registra tamaños y SHA-256 de cada archivo de contenido,
incluido este README, y los controles técnicos de los 12 videos. El manifiesto
excluye únicamente su propio hash para evitar una dependencia circular.
Estos controles no sustituyen una revisión humana de la enseñanza o de la voz.
