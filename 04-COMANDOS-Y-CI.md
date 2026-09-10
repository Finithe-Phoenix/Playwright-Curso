# Comandos del laboratorio entregado y adaptación a CI

**Usa las carpetas existentes, no un directorio futuro de starter.** La [biblioteca de 12 lecciones y su estado de producción](videos/index.html) y [LEEME-VIDEOS.md](videos/LEEME-VIDEOS.md) son las entradas al material práctico. Este documento resume los comandos de los proyectos entregados; el estado de los MP4 se verifica por separado.

Se registraron **22 casos aprobados localmente**: [10 distribuidos](videos/lab/distributed/evidence/VERIFICATION.md) y [12 de protocolo y regresión híbrida](videos/lab/mainframe/evidence/VERIFICATION.md). La receta de CI de la última sección es una adaptación didáctica: no hay una ejecución alojada de ese pipeline acreditada por estos resultados.

## 1. Preparación antes de clase y rutas reales

La instalación se realiza fuera de los 120 minutos. El entorno verificado utilizó Node 24.16.0, Python 3.12.10, JDK 11.0.17, Maven 3.9.11 y Edge 152.0.4191.66. No se hizo una instalación en un Windows vacío. Los requisitos y alternativas actuales están en los README de cada proyecto.

```text
videos/lab/
  distributed/
    package.json, package-lock.json, playwright.config.ts
    start-lab.mjs, tests/, evidence/
  mainframe/
    setup.ps1, start.ps1, adapter.py, simulator.py
    requirements.txt, requirements-browser.txt, pytest.ini
    test_terminal.py, test_hybrid_browser.py, test_core_regression.py
    typescript/hybrid.spec.ts, typescript/playwright.config.ts
    java/pom.xml, java/src/test/java/training/, evidence/
```

TypeScript tiene lockfile npm. Python fija sus dependencias directas en requirements; eso no equivale a un lock completo de transitivas. Java fija las dependencias y plugins del POM y utiliza Maven instalado: **no se incluye un Maven wrapper**. Si la cohorte exige un lock transitivo o validar una máquina limpia, esa preparación sigue pendiente.

La configuración TypeScript predeterminada usa Edge y graba los casos; por eso necesita el **FFmpeg de Playwright**, aunque Edge ya esté instalado. El FFmpeg del sistema utilizado para producir los tutoriales es distinto. Los navegadores descargados corresponden a cada versión de Playwright; no compartir un ejecutable por suponer equivalencia entre versiones. [Navegadores](https://playwright.dev/docs/browsers).

Las variables `TEST_HOOK_KEY`, `BASE_URL`, `ARTIFACT_DIR` y los canales de navegador son opciones de estos proyectos, no una interfaz universal de todos los runners. La clave `classroom-demo-only` es pública y sintética, exclusiva de este laboratorio local.

## 2. Arrancar la aplicación distribuida

En una terminal del laboratorio:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\distributed'
npm ci
npx playwright install ffmpeg
$env:TEST_HOOK_KEY = 'classroom-demo-only'
npm run start:lab
```

El coordinador inicia gateway `3000`, Accounts `3001` y Ledger `3002`, ligados a `127.0.0.1`. Verifica la salud de cada proceso y falla si hay conflictos de puertos. Mantén esa terminal abierta. En otra terminal puedes observar la salud del gateway:

```powershell
$labHealth = Invoke-RestMethod -Uri 'http://127.0.0.1:3000/health'
if ($labHealth.status -ne 'ok' -or $labHealth.environment -ne 'test') {
    throw 'El gateway del laboratorio no está listo.'
}
```

Esa consulta por sí sola confirma el gateway; no sustituye las comprobaciones del coordinador sobre las otras dependencias. La [interfaz de TransferLab](http://127.0.0.1:3000/transfers) requiere las credenciales de una fixture vigente; las pruebas crean y autentican las suyas.

Todos los datos de negocio y el outbox están en memoria. La colección `/api/transfers` es canónica e inmediata; `/api/ledger/transfers` es una proyección independiente con posible demora. Reiniciar los procesos elimina su estado.

## 3. TypeScript: ejecución y reportes existentes

Con la aplicación iniciada, en otra terminal:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\distributed'
$env:TEST_HOOK_KEY = 'classroom-demo-only'
npm test
npm run report
```

El resultado medido fue **10 aprobadas**. La configuración usa un worker y cero reintentos; conserva traces, capturas y videos de todos los casos para los tutoriales. El reporte HTML está en `evidence/html-report`; por eso se usa `npm run report` y no se presupone el directorio predeterminado de otro proyecto.

Para ejecutar los tres casos principales o mostrar el caso exitoso:

```powershell
npm test -- --grep 'TR-0[123]'
npm test -- --grep TR-01 --headed
```

Para usar Chromium descargado en vez de Edge:

```powershell
npx playwright install chromium
$env:PW_CHANNEL = 'chromium'
npm test
```

Esta alternativa está documentada; las ejecuciones registradas usaron Edge. La CLI admite selección, workers y reintentos, pero cada cambio debe respetar aislamiento y nombres reales. [CLI de Playwright Test](https://playwright.dev/docs/test-cli).

### Defecto controlado y conservación de evidencia

La variante de doble débito se inicia por separado con los puertos `3100/3101/3102` y `LAB_DEFECT_DUPLICATE=1`. Usa los comandos completos del [README distribuido](videos/lab/distributed/README.md). Su TR-03 debe fallar; el resultado registrado incluye saldo `80000` y dos registros, conservando el oráculo correcto de `90000` y un registro.

Al volver al servidor sano, cambia también el directorio de evidencia:

```powershell
$env:BASE_URL = 'http://127.0.0.1:3000'
$env:ARTIFACT_DIR = 'evidence/healthy-recheck'
npm test -- --grep TR-03
```

Esto evita sobrescribir `evidence/defect`. No cambies aserciones, skips o reintentos para convertir el defecto en éxito.

## 4. TN3270 local y Python

La ruta Python está en el proyecto `mainframe` e incluye los casos centrales y el híbrido con TNZ. Prepara el entorno antes de clase:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\mainframe'
.\setup.ps1 -Browser
.\start.ps1
```

`start.ps1` mantiene el simulador en `127.0.0.1:2323`. En otra terminal de la misma carpeta, con la aplicación distribuida también iniciada:

```powershell
.\.venv\Scripts\python.exe adapter.py health --timeout 5
$env:TEST_HOOK_KEY = 'classroom-demo-only'
.\.venv\Scripts\python.exe -m pytest test_hybrid_browser.py test_core_regression.py --browser-channel msedge --tracing=retain-on-failure --junitxml=evidence\python-core-plugin-tests.xml
```

El resultado verificado de esa selección fue **3 aprobadas**: éxito híbrido, rechazo de 1100.00 contra saldo 1000.00 e idempotencia secuencial. `pytest.ini` fija `base_url=http://127.0.0.1:3000`. Si adaptas el host, revisa también esa opción al copiar fragmentos con URL relativa; no presupongas que todas las fixtures leen `BASE_URL` automáticamente.

El híbrido respeta la propiedad de la traza del plugin y solo usa captura manual cuando esa opción está desactivada. `--tracing` es de pytest-playwright; plugins como pytest-xdist o pytest-html son dependencias adicionales, no capacidades implícitas. [Referencia del plugin](https://playwright.dev/python/docs/test-runners).

La suite de protocolo usa un servidor temporal y datos deterministas; no requiere ejecutar el navegador:

```powershell
.\.venv\Scripts\python.exe -m pytest test_terminal.py -q --junitxml=evidence\terminal-tests.xml
```

Sus **5 casos aprobados** cubren éxito, referencia desconocida, validación, timeout de pantalla y backend no disponible, mediante TNZ real y sockets locales. Para mostrar la ruta híbrida en navegador visible:

```powershell
.\.venv\Scripts\python.exe -m pytest test_hybrid_browser.py --browser-channel msedge --headed
```

El adaptador introduce la referencia exacta en el campo del simulador y recibe los mismos datos autoritativos de Accounts. No consulta un mainframe real ni una segunda fuente independiente.

## 5. Java: JUnit y Maven existentes

La instalación inicial y la alternativa Chromium están en el [README TNZ](videos/lab/mainframe/README.md). El POM utiliza Gson y excluye el paquete opcional de Node; por eso el comando necesita señalar el Node ya instalado. Con las dependencias de navegador preparadas, Edge instalado y ambos laboratorios iniciados:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\mainframe\java'
$env:TEST_HOOK_KEY = 'classroom-demo-only'
$env:PLAYWRIGHT_NODEJS_PATH = (Get-Command node).Source
$env:PW_BROWSER_CHANNEL = 'msedge'
mvn test
```

La ejecución verificada contiene **3 casos aprobados** en `HybridTransferTest` y `CoreRegressionTest`. Surefire produce XML y texto en `target/surefire-reports`; el proyecto conserva evidencia adicional en `../evidence`. No genera automáticamente el reporte HTML de Playwright Test. [Surefire](https://maven.apache.org/surefire/maven-surefire-plugin/).

La captura de trace pertenece al código Java. Los bloques de finalización intentan borrar la fixture incluso si falla el cierre de la traza. No agregues `--headed` o `--tracing` al comando Maven: una demostración con ventana requiere configurar `LaunchOptions.setHeadless(false)` en la copia de código elegida. [Java](https://playwright.dev/java/docs/intro), [tracing](https://playwright.dev/java/docs/api/class-tracing).

## 6. Híbrido TypeScript y parada de servicios

Con las dependencias distribuidas instaladas y los dos laboratorios iniciados, ejecuta desde `mainframe`:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\mainframe'
$env:TEST_HOOK_KEY = 'classroom-demo-only'
node ..\distributed\node_modules\@playwright\test\cli.js test --config typescript\playwright.config.ts
```

Esta selección registró **1 caso híbrido aprobado**, adicional a los 10 distribuidos. Para terminar, pulsa Ctrl+C en la terminal propia del simulador y después en la del coordinador distribuido. Detén también cualquier servidor de reportes que hayas abierto. No finalices procesos ajenos por coincidir con un nombre genérico.

## 7. Receta de CI: adaptación ilustrativa, no ejecución acreditada

El taller dedica 12 minutos a revisar cómo llevar estas ejecuciones a CI. La secuencia propuesta es: obtener fuentes; instalar versiones fijadas y el navegador del runner; iniciar los servicios locales; comprobar cada dependencia con plazo; ejecutar la selección; conservar código de salida y artefactos incluso al fallar; limpiar fixtures y cerrar los procesos propios.

La adaptación a Linux requiere sus rutas de entorno virtual, un navegador disponible y dependencias del sistema. Opciones como `install --with-deps chromium` pertenecen al CLI correspondiente y pueden necesitar permisos del entorno CI. Maven se ejecuta con `mvn` salvo que se agregue y verifique un wrapper. No copiar variables de canal o flags entre Java, Python y TypeScript. [CI de Playwright](https://playwright.dev/docs/ci), [CI Python](https://playwright.dev/python/docs/ci).

Sharding, matrices de lenguajes y navegadores, y despliegue corporativo son extensiones de diseño. No forman parte de los 22 resultados locales ni son requisito del taller de dos horas. El reporte debe distinguir **CI propuesto**, **CI configurado** y **CI ejecutado**; solo este último se acredita con un run real y sus artefactos.

Para evaluar el ejercicio, exigir los tres casos de negocio de la ruta elegida, aislamiento, una traza de fallo legible, limpieza documentada y resultados honestos. La instalación limpia de una cohorte, el ensayo completo de 120 minutos y un pipeline alojado siguen pendientes de comprobar.
