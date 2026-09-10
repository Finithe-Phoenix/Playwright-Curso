# Revisión final de los videos

Fecha UTC: 2026-09-10T04:13:37.534733+00:00

Los doce MP4 coinciden con sus fuentes finales y sus hashes de producción. Cada archivo contiene imagen Full HD 1920×1080, H.264 a 24 fps y voz sintética en inglés. Todos duran entre 6 y 8 minutos.

Duración total: 87.33 minutos. Se revisaron visualmente por un agente 144 cuadros, doce por episodio. Las observaciones vigentes no contienen incidencias pendientes en esas muestras.

| Episodio | Duración | Voz | Imagen | Cuadros revisados |
|---|---:|---|---|---:|
| 01 · Build the Local Test Architecture | 7:03.000 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 02 · TypeScript: Reliable UI and API Regression | 7:10.417 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 03 · Python: Fixtures That Own Their Data | 7:23.292 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 04 · Java: JUnit Lifecycle and Evidence | 7:18.583 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 05 · Isolation, Authentication and Test Data | 7:19.625 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 06 · Distributed Workflows: Correlation and Polling | 7:14.500 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 07 · Mocks and Real End-to-End Evidence | 7:04.500 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 08 · Traces, CI and Evidence-Based Debugging | 7:14.917 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 09 · Local 3270 Architecture and TNZ Setup | 7:19.792 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 10 · TNZ Sessions: Fields, Waits and Cleanup | 7:14.417 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 11 · Hybrid Regression: One Correlation Across Interfaces | 7:24.625 | en-US-JennyNeural | 1080p · 24 fps | 12 |
| 12 · AI-Assisted Regression Capstone | 7:32.000 | en-US-JennyNeural | 1080p · 24 fps | 12 |

## Evidencia técnica

La auditoría de paleta vigente revisó 162 fuentes visuales y los 144 cuadros medios (298,598,400 píxeles). Encontró cero literales verdes/teal y cero regiones de al menos 16 píxeles conectados en ocho direcciones. Conserva el conteo de 4,196 píxeles candidatos, agrupados en componentes de hasta 8 píxeles: no afirma cero píxeles verdes. El detector usa hue exacto 60–180°, saturación HSV ≥20%, valor ≥20/255 y diferencia de canales ≥16/255. La investigación de 144 pares nativos/comprimidos identifica pequeñas franjas de rasterizado y compresión. El resultado se limita a esas fuentes y cuadros muestreados; no certifica todos los cuadros ni todos los estados de la interfaz. Consulta [blue-palette-validation.json](blue-palette-validation.json) y [palette-mask-investigation.json](palette-mask-investigation.json) para hashes, conteos y criterios.

Las doce narraciones pasan los controles registrados de duración, formato, señal finita, límites de pico y subtítulos. La decodificación completa de la pista de audio de cada MP4 está confirmada por el informe de exportación y ligada al SHA-256 vigente. Esto no equivale a una evaluación humana de pronunciación o claridad.

Las pruebas locales suman **22 casos aprobados, cero fallos y cero omitidos**: 10 regresiones TypeScript del laboratorio distribuido y 12 casos entre TN3270, Python, Java y TypeScript. Se contrastaron los cinco XML primarios con el resumen del laboratorio mainframe; las repeticiones de casos no se suman como cobertura adicional.

Los SHA-256, rutas de resultados y observaciones por episodio están en [final-validation.json](final-validation.json). Las pruebas son ejecuciones previas verificadas, no se vuelven a ejecutar al generar este informe.

## Alcance y pendientes

- Revisión visual por un agente de 12 cuadros muestreados por video, uno en el punto medio de cada escena; no reproducción visual completa.
- No se realizó escucha humana completa ni reconocimiento automático de la narración. Los controles de audio son técnicos.
- El muestreo no certifica todas las transiciones, continuidad de animaciones o sincronización de subtítulos entre muestras.
- La auditoría de paleta analiza literales hex/RGB y 144 cuadros medios con umbrales explícitos de hue, saturación, valor y diferencia de canales; excluye colores casi grises o muy oscuros y no cubre todos los cuadros.
- Las 22 pruebas corresponden a ejecuciones locales documentadas; no equivalen a una matriz completa de navegadores o sistemas operativos.
- El servidor TN3270 es un simulador local con cliente IBM tnz real; no hay validación contra z/OS, CICS o DB2.
- La comprobación de idempotencia es secuencial; concurrencia y recuperación real siguen fuera de la cobertura ejecutada.
- CI alojada y ensayo completo del taller de 120 minutos: no ejecutados.
