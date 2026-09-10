# Cómo integrar los videos en el curso de dos horas

Las doce lecciones terminadas constituyen **87:20 de preparación y repaso**. Cada video dura **7:03–7:32**, dentro del objetivo de 6–8 minutos. No se suman íntegramente a la sesión en vivo. La duración individual y sus capítulos se consultan en la [biblioteca](index.html).

En el taller se mantienen **120 minutos, incluida una pausa de 5 minutos**. Cada participante elige TypeScript, Python o Java. Los videos permiten estudiar las otras rutas después, sin tener que construir tres frameworks durante la misma clase.

Para usar los saltos a capítulos, abre PowerShell en `work\videos`, ejecuta `node tools\serve-course.mjs` y visita [la biblioteca local](http://127.0.0.1:8766/videos/index.html). El servidor entrega segmentos de video mediante HTTP Range. Si el puerto está ocupado, usa `node tools\serve-course.mjs --port 8768` y actualiza el puerto de la dirección. Mantén la terminal abierta durante la clase; Ctrl+C detiene ese servidor.

## Ruta de episodios

| Nº | Lección | Objetivo práctico | Momento recomendado |
|---:|---|---|---|
| 01 | Build the Local Test Architecture | Arrancar el sistema, identificar navegador, servicios y terminal y fijar resultados observables. | Preparación común. |
| 02 | TypeScript: Reliable UI and API Regression | Verificar una transferencia con UI y API usando Playwright Test. | Preparación de la ruta TypeScript. |
| 03 | Python: Fixtures That Own Their Data | Administrar datos, contexto y limpieza mediante pytest. | Preparación de la ruta Python. |
| 04 | Java: JUnit Lifecycle and Evidence | Separar el ciclo de vida de Playwright, JUnit y sus artefactos. | Preparación de la ruta Java. |
| 05 | Isolation, Authentication and Test Data | Aislar el estado mutable del servidor y compartir la sesión correcta con la página. | Preparación común; consulta durante el bloque de fixtures. |
| 06 | Distributed Workflows: Correlation and Polling | Distinguir el estado autoritativo de una proyección eventual y consultar una referencia exacta. | Preparación o extensión posterior al núcleo de regresiones. |
| 07 | Mocks and Real End-to-End Evidence | Separar recuperación visual con un mock de la ejecución real entre servicios. | Fragmento durante el bloque de error 503; repaso posterior. |
| 08 | Traces, CI and Evidence-Based Debugging | Diagnosticar un fallo y conservar resultados y artefactos sin ocultarlo con reintentos. | Fragmentos de diagnóstico y CI; repaso posterior. |
| 09 | Local 3270 Architecture and TNZ Setup | Preparar el cliente IBM tnz y el simulador local y reconocer sus límites. | Preparación de la ampliación mainframe. |
| 10 | TNZ Sessions: Fields, Waits and Cleanup | Navegar por campos y condiciones de pantalla con plazos definidos y cierre garantizado. | Práctica de terminal antes del ejercicio híbrido. |
| 11 | Hybrid Regression: One Correlation Across Interfaces | Seguir la misma transferencia desde el navegador hasta el terminal y comprobar sus valores. | Ejercicio híbrido de ampliación. |
| 12 | AI-Assisted Regression Capstone | Usar contexto, código, ejecución y evidencia para revisar una regresión generada con IA. | Preparación de la evaluación y cierre. |

Los títulos se corresponden con los guiones de [episodes.json](scripts/episodes.json). Los pasos de cada video se pueden localizar desde la pestaña **Pasos** de la biblioteca cuando están disponibles sus tiempos de narración.

## Trabajo previo por participante

**Base común:** ver 01 y 05, más el video de su lenguaje: 02, 03 o 04. Son **aproximadamente 22 minutos**. Descargar e instalar previamente sus dependencias, iniciar TransferLab y ejecutar el caso de conectividad o regresión indicado en el README. Reservar el tiempo de instalación por separado: una descarga no forma parte de esos minutos de video.

**Ruta distribuida:** añadir 06, otros **6–8 minutos**, y escribir qué consulta usa estado inmediato y cuál observa una proyección con demora. Guardar la referencia real devuelta por una transferencia.

**Ruta de terminal:** después de la base, ver 09, 10 y 11, otros **18–24 minutos**, instalar las dependencias de tnz y ejecutar la comprobación de pantalla. Esta ampliación puede impartirse como trabajo previo o posterior; no es un prerrequisito del núcleo original de tres regresiones UI/API.

Antes de entrar a clase, cada persona debe contar con una ruta instalada y un arranque local comprobado. No es necesario terminar las doce lecciones antes del taller. El resto de la serie queda disponible para profundizar y comparar lenguajes.

## Agenda en vivo: 120 minutos

La [ficha de fragmentos](FRAGMENTOS-PARA-LA-CLASE.md) proporciona marcas de tiempo exactas para siete segmentos, unos diez minutos audiovisuales en total.

Los fragmentos de video señalados están **incluidos dentro del bloque**, no se añaden a su duración. Elegir el paso por su título y por la marca de tiempo real de la biblioteca.

| Minutos | Actividad del taller | Apoyo en video | Entrega observable |
|---|---|---|---|
| 00–10 | Definir riesgo y resultado de negocio. | 01: mapa del sistema; hasta 90 s. | Diferenciar confirmación visible, débito y registro. |
| 10–25 | Completar contexto y matriz de regresión con IA. | 12: contexto y criterio de aceptación; hasta 90 s. | Tres escenarios priorizados y sus expectativas. |
| 25–45 | Revisar fixtures, autenticación y datos propios. | 05, más consulta individual de 02/03/04; hasta 2 min comunes. | Fixture aislada y limpieza delimitada. |
| 45–65 | Completar y ejecutar TR-01, TR-02 y TR-03. | 02/03/04 como consulta; 06 para una extensión si el grupo ya terminó. | Resultado real de tres regresiones y evidencia de sus efectos. |
| 65–70 | Pausa. | Sin video obligatorio. | Recuperar el punto común. |
| 70–85 | Simular un error 503 y verificar la recuperación de UI. | 07: alcance de la interceptación; hasta 2 min. | Caso identificado como UI con mock, con cero efectos de backend. |
| 85–100 | Diagnosticar el defecto de idempotencia con una traza. | 08: leer la evidencia; hasta 2 min. | Explicación sustentada del fallo y corrección o defecto documentado. |
| 100–112 | Revisar selección, CI y conservación de artefactos. | 08: runner y artefactos; hasta 90 s. | Comando de su lenguaje y plan de resultados/trazas. |
| 112–120 | Revisión por pares y evaluación. | 12: revisión final; hasta 60 s si aporta valor. | Rúbrica y pendientes explícitos. |

No reproducir episodios completos de 6–8 minutos durante todos los bloques: los participantes necesitan ese tiempo para ejecutar y diagnosticar. El instructor puede usar una captura de evidencia o un fragmento concreto cuando resuelva una duda mejor que una explicación adicional.

## Ejercicio de ampliación: navegador → servicios → terminal

Usar 09–11 para una práctica posterior o una sesión adicional. Mantener el mismo contrato de negocio:

1. Crear una fixture nueva con saldo de 100000 centavos sintéticos.
2. Autenticar el contexto de navegador con sus propias credenciales.
3. Transferir 10000 centavos desde la UI y capturar la referencia devuelta.
4. Comprobar saldo autoritativo 90000 y exactamente un registro.
5. Consultar la proyección de ledger usando la referencia exacta y un plazo máximo.
6. Abrir una sesión de tnz contra el simulador local, introducir esa referencia y comprobar estado, importe, moneda, cuenta y saldo.
7. Guardar evidencia de navegador y terminal, cerrar sesiones y eliminar únicamente la fixture propia.

La pantalla del simulador consulta los mismos datos autoritativos de TransferLab. La práctica verifica coordinación de UI, HTTP y TN3270, y una proyección independiente del laboratorio; no verifica un mainframe empresarial ni un libro contable externo. Una futura adaptación necesita el contrato real de pantallas, autenticación, transacciones, tiempos y fuentes de verdad del entorno autorizado.

## Evaluación y uso responsable de la evidencia

Cada equipo entrega el comando ejecutado, el resultado del runner y la evidencia mínima que demuestra su afirmación. Debe explicar qué es dato aislado, qué fue simulado y qué valor observó en cada interfaz.

La versión defectuosa de TransferLab está diseñada para que TR-03 falle al repetir un débito. Un diagnóstico correcto conserva la expectativa de un solo débito y documenta el fallo. No se otorga un resultado aprobado a partir de un video, una respuesta de la IA o una prueba omitida.

Utiliza la [rúbrica del curso](../05-PREPARACION-Y-EVALUACION.md) y los [prompts copiables](../02-PROMPTS-COPIAR-PEGAR.md). Los README y documentos de verificación de los laboratorios distinguen las pruebas realmente ejecutadas de los ejemplos y las adaptaciones pendientes.
