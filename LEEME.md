# Curso avanzado de Playwright con IA

Taller de **dos horas**, en español, para **Java, TypeScript y Python**, con laboratorios locales ejecutables. Cada participante elige una ruta y trabaja sobre el mismo caso de transferencias ficticias.

**Entrada al material práctico:** abre la [biblioteca de 12 videos terminados](videos/index.html) y sigue [LEEME-VIDEOS.md](videos/LEEME-VIDEOS.md) para instalar y ejecutar los proyectos entregados. Los MP4 se generaron con Hyperframes, en Full HD, con voz de IA y subtítulos en inglés. Duran de **7:03 a 7:32**, **87:20 en total**, como preparación y repaso del taller. Los guiones y proyectos son editables.

**Verificación local:** 22 casos aprobados: [10 del laboratorio distribuido](videos/lab/distributed/evidence/VERIFICATION.md) y [12 de protocolo y regresión híbrida](videos/lab/mainframe/evidence/VERIFICATION.md). El fallo intencional de idempotencia se conserva por separado. No se ha acreditado una ejecución alojada de CI ni un ensayo de clase de 120 minutos con participantes.

## Empezar aquí

Abre [CURSO-PLAYWRIGHT-IA.html](CURSO-PLAYWRIGHT-IA.html) para consultar el plan, la guía y los prompts originales. Su contenido se puede leer sin conexión; las fuentes enlazadas necesitan internet. Los archivos Markdown son las versiones editables. La instalación inicial de dependencias y navegadores requiere las descargas indicadas en cada README; la carpeta de fuentes no equivale a una instalación sin red.

La guía HTML refleja esta entrega. Los cambios posteriores en los archivos Markdown requieren regenerarla para mantener ambas versiones sincronizadas. Desde `work`, ejecuta `node videos/tools/build-course-guide.mjs`; el convertidor Marked 17.0.5 y su licencia se incluyen en `videos/assets`.

| Archivo | Contenido |
|---|---|
| [01-PLAN-DEL-CURSO.md](01-PLAN-DEL-CURSO.md) | Objetivos, agenda exacta de 120 minutos, alcance y pasos para crear el curso |
| [02-PROMPTS-COPIAR-PEGAR.md](02-PROMPTS-COPIAR-PEGAR.md) | Prompt maestro y prompts para diseñar, generar, diagnosticar y revisar regresiones |
| [03-LABORATORIO-Y-LENGUAJES.md](03-LABORATORIO-Y-LENGUAJES.md) | Contrato de TransferLab y equivalencias Java / TypeScript / Python |
| [04-COMANDOS-Y-CI.md](04-COMANDOS-Y-CI.md) | Comandos por ruta y condiciones para utilizarlos en CI |
| [05-PREPARACION-Y-EVALUACION.md](05-PREPARACION-Y-EVALUACION.md) | Producción del curso, trabajo previo, guion y evaluación |
| [videos/AI-PROMPTS-REGRESSION.md](videos/AI-PROMPTS-REGRESSION.md) | Contexto y 9 prompts copiables para los proyectos reales, regresión distribuida, TNZ, diagnóstico y CI |
| [videos/lab/distributed/README.md](videos/lab/distributed/README.md) | Arranque de gateway, Accounts, Ledger y suite TypeScript |
| [videos/lab/mainframe/README.md](videos/lab/mainframe/README.md) | Instalación TNZ y regresiones Python, Java y TypeScript con terminal local |

## Cómo utilizarlo

1. Revisa el plan y elige la ruta del instructor y de cada participante.
2. Instala y ejecuta los proyectos en `videos/lab/distributed` y `videos/lab/mainframe` siguiendo sus README. Usa los documentos 03 y 05 para comprender el contrato y preparar el ensayo con tu grupo.
3. Completa el contexto del catálogo de prompts. En clase, usa sus etapas; el prompt maestro sirve para aplicar el método completo a otros proyectos.
4. Conserva los resultados reales del runner junto con el código para evaluar lo realizado.

**Alcance de esta entrega:** TransferLab y el servidor TN3270 son simuladores locales con datos sintéticos. Accounts, las transferencias y el outbox viven en memoria y desaparecen al reiniciar. El terminal muestra la misma fuente autoritativa; no es una conciliación independiente con z/OS, CICS o DB2. Los proyectos no representan sistemas de HSBC.

Fecha: 9 de septiembre de 2026. Las referencias técnicas se consultaron en la documentación oficial de Playwright. Las estimaciones de tiempo y la rúbrica son propuestas de diseño del taller.
