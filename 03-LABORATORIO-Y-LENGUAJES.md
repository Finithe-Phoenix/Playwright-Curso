# Laboratorio entregado: TransferLab y equivalencias entre lenguajes

**Estado: laboratorio local implementado y verificado.** Accede a la [biblioteca de 12 lecciones y estado de producción](videos/index.html) y a [las instrucciones de instalación](videos/LEEME-VIDEOS.md). Los proyectos entregados están en `videos/lab/distributed` y `videos/lab/mainframe`, con **22 casos aprobados localmente**: [10 distribuidos](videos/lab/distributed/evidence/VERIFICATION.md) y [12 de protocolo y regresión híbrida](videos/lab/mainframe/evidence/VERIFICATION.md). La producción de MP4 se comprueba por separado. TransferLab es una aplicación educativa ficticia; no representa una aplicación, API, política ni sistema de HSBC.

El taller utiliza el motor Chromium; las ejecuciones medidas usaron **Microsoft Edge en contextos de pruebas nuevos**, sin reutilizar perfiles personales. La alternativa con Chromium descargado está documentada y no fue el navegador utilizado en esos resultados. Cada participante elige **Java, TypeScript o Python** para resolver los mismos tres casos. El instructor muestra una implementación y compara las decisiones con las otras dos; construir tres frameworks en vivo no cabe en dos horas.

## 1. Qué incluye el material y qué prepara el instructor

El [proyecto distribuido](videos/lab/distributed/README.md) incluye gateway, Accounts, Ledger y pruebas TypeScript. El [proyecto TNZ](videos/lab/mainframe/README.md) incluye simulador TN3270, adaptador Python y regresiones de los tres lenguajes. Python y Java ya contienen los tres casos centrales; su caso exitoso incorpora también la comparación con el terminal. La variante defectuosa se activa únicamente mediante el mecanismo explícito documentado, en puertos separados.

El instructor conserva estas soluciones y prepara una copia con puntos concretos a completar durante la clase. Esa selección pedagógica y un ensayo con participantes siguen pendientes; no requieren construir nuevamente la aplicación desde cero.

La preparación de cada estación ocurre **fuera de los 120 minutos**. Incluye instalación real, versiones compatibles, descargas y ejecución del lenguaje elegido. La verificación de esta entrega no equivale a una instalación limpia de Windows ni al ensayo de clase. Los comandos para las rutas existentes aparecen en [04-COMANDOS-Y-CI.md](04-COMANDOS-Y-CI.md).

## 2. Contrato de dominio, versión 1

Base URL: `http://127.0.0.1:3000`. Usar esta dirección de forma consistente; no mezclarla con `localhost` en cookies y navegación.

Los importes del servidor son **enteros en centavos**, moneda `MXN`: `100000` representa MXN 1000.00. La interfaz recibe un decimal con punto y hasta dos decimales. La cuenta origen pertenece al usuario de la fixture; el beneficiario es sintético. Accounts confirma el débito, el registro canónico y el evento del outbox en una sección síncrona del mismo proceso. **Todos estos datos viven en memoria y desaparecen al reiniciar**; no se demuestra durabilidad ni una transacción entre bases de datos.

Las consultas de cuenta y `/api/transfers` reflejan inmediatamente la operación. La ruta distinta `/api/ledger/transfers` consulta una proyección en otro proceso que puede demorarse y requiere sondeo de lectura acotado por el identificador exacto. El terminal simulado consulta `/__test/lookup`, que lee los mismos datos autoritativos de Accounts; no demuestra que la proyección de Ledger esté lista ni una conciliación independiente en un mainframe.

Una transferencia completada tiene este esquema JSON:

```json
{
  "id": "<id generado por el servidor>",
  "status": "COMPLETED",
  "sourceAccountId": "<id de cuenta origen>",
  "beneficiaryId": "<id de beneficiario>",
  "currency": "MXN",
  "amountMinor": 10000
}
```

Los identificadores son cadenas opacas seguras para una URL, formadas con UUID; no son números bancarios reales. Los textos entre `<...>` describen valores que generará la aplicación: no se copian como datos fijos de pruebas.

### API del laboratorio

| Método y ruta | Entrada | Respuesta y reglas |
|---|---|---|
| `GET /health` | Sin autenticación | `200`, `{"status":"ok","environment":"test","contractVersion":"1"}`. Confirma proceso listo y contrato esperado. |
| `POST /__test/fixtures` | Cabecera `X-Test-Hook-Key`; JSON `{"runId":"<ejecución>","caseId":"TR-01","currency":"MXN","balanceMinor":100000}` | `201`, `{fixtureId,username,password,sourceAccountId,beneficiaryId}`. Crea usuario, cuenta, beneficiario, saldo inicial y cero transferencias. La respuesta contiene datos sintéticos de esa fixture. |
| `POST /api/session` | JSON `{username,password}` | `200`, `{userId}` y cookie `transferlab_session`; credenciales incorrectas: `401`. Usa el mecanismo normal de autenticación del laboratorio. |
| `GET /api/accounts/{sourceAccountId}` | Cookie de sesión | `200`, `{id,currency:"MXN",balanceMinor}`. |
| `POST /api/transfers` | Cookie; cabecera `Idempotency-Key`; JSON `{sourceAccountId,beneficiaryId,currency:"MXN",amountMinor}` | Primera operación válida: `201` y objeto transferencia. Misma clave y mismo cuerpo: `200` y **el mismo objeto e id**, sin segundo débito ni registro. Misma clave con otro cuerpo: `409`, `{code:"IDEMPOTENCY_CONFLICT",message:"Clave de idempotencia reutilizada"}`. |
| `GET /api/transfers?sourceAccountId={sourceAccountId}` | Cookie de sesión | `200`, `{items:[<transferencias>],total:<entero>}`. Lista completa de esa cuenta, sin paginación para el laboratorio. |
| `GET /api/ledger/transfers?sourceAccountId={sourceAccountId}` | Cookie de sesión | Proyección independiente `{items,total,projectionCursor}`. Consultar hasta observar el mismo transferId, con plazo máximo de 5 segundos en el caso distribuido. |
| `GET /__test/lookup?reference={transferId}` | Puente local de lectura para el simulador | `{reference,status,amountMinor,currency,sourceAccountId,balanceMinor}` o `404`; consulta Accounts en memoria. |
| `DELETE /__test/fixtures/{fixtureId}` | Cabecera `X-Test-Hook-Key` | `204`, sin cuerpo. Elimina exclusivamente la fixture indicada y sus datos y sesiones. Repetir la limpieza devuelve `204`. |

Las API de negocio devuelven `401` sin sesión válida y `403` si la cuenta o el beneficiario pertenecen a otra fixture. Los hooks devuelven `403` con clave incorrecta y no se registran fuera del modo local de pruebas. No se les da una ruta para borrar todos los datos.

Reglas de transferencia: `amountMinor` entero positivo, `currency` igual a `MXN`, saldo suficiente e identificadores de la fixture autenticada. Importe inválido: `422`, `{"code":"INVALID_AMOUNT","message":"Importe inválido"}`. Saldo insuficiente: `422`, `{"code":"INSUFFICIENT_FUNDS","message":"Saldo insuficiente"}`. Rechazar una operación deja saldo y lista sin cambios. Los casos centrales consultan el servidor real del laboratorio, sin sustituir sus respuestas.

La clave de idempotencia queda asociada al usuario y al cuerpo de la operación durante toda la vida de su fixture. La aplicación genera una clave por intención de transferencia y la conserva al reintentar esa intención; una nueva operación deliberada recibe otra clave. Dos clics independientes con claves distintas no verifican idempotencia. La repetición secuencial de TR-03 tampoco demuestra protección frente a solicitudes concurrentes: eso sería una extensión específica.

### Interfaz del laboratorio

En `/transfers`, después de autenticar la sesión:

| Elemento | Contrato localizable |
|---|---|
| Selector HTML `select` de origen | Etiqueta accesible exacta `Cuenta origen`; valor de opción `sourceAccountId`. |
| Selector HTML `select` de beneficiario | Etiqueta accesible exacta `Beneficiario`; valor de opción `beneficiaryId`. |
| Entrada de importe | Etiqueta accesible exacta `Importe (MXN)`; acepta `100.00`. |
| Botón de envío | Rol `button`, nombre accesible exacto `Transferir`. |
| Saldo visible | `data-testid="account-balance"`; formato fijo `MXN 1000.00` o `MXN 900.00`. |
| Confirmación | Un solo elemento `role="status"`, texto exacto `Transferencia realizada`. |
| Rechazo | Un solo elemento `role="alert"`, texto exacto `Saldo insuficiente` o `Importe inválido`. |

El botón se deshabilita mientras hay una solicitud pendiente y la interfaz actualiza el saldo después de completar la operación. Los locators por rol y etiqueta expresan la intención del usuario; el test id del saldo es un contrato explícito. No hacen falta CSS estructurales ni XPath posicionales. [Locators de Playwright](https://playwright.dev/docs/locators).

## 3. Datos y autenticación aislados

Cada prueba **y cada intento** ejecuta este ciclo:

1. Verificar disponibilidad de gateway, Accounts y Ledger; el coordinador de arranque consulta cada proceso. `/health` del gateway por sí solo acredita su proceso. Un fallo de preparación debe reportarse como tal; no convertirlo en éxito ni en una prueba omitida. El híbrido requiere además una pantalla lista del simulador mediante `adapter.py health`.
2. Crear una fixture con `runId` único por ejecución y `caseId`. El servidor agrega un UUID a sus identificadores. Dos workers o dos participantes nunca comparten cuentas mutables.
3. Crear un `BrowserContext` nuevo. Iniciar sesión mediante `POST /api/session` usando las credenciales sintéticas recibidas y el cliente HTTP asociado a ese contexto. Comprobar `200` antes de navegar.
4. Ejecutar la prueba. Las consultas del saldo y las transferencias usan la misma identidad autenticada.
5. En la finalización, incluso después de un fallo, guardar evidencia, cerrar el contexto y borrar únicamente `fixtureId`. Si falla la limpieza, reportarlo y conservar su identificador para recuperación; no ocultar el fallo original. Una interrupción abrupta requiere limpieza posterior por las fixtures registradas de esa ejecución.

Las peticiones de preparación usan `TEST_HOOK_KEY` desde el entorno. TypeScript emplea un cliente de preparación separado; los ejemplos híbridos también pueden aplicar la cabecera únicamente en la petición de setup o limpieza. **La cabecera de hooks nunca se instala como cabecera global del navegador.** El servidor almacena las sesiones en memoria; borrar la fixture las revoca. La cookie es `HttpOnly`, `SameSite=Lax`, `Path=/`, con vigencia de 30 minutos. El HTTP sin `Secure` es una decisión exclusiva del servidor ficticio ligado a loopback; cualquier adaptación a un ambiente corporativo requiere su contrato de autenticación autorizado.

En Playwright, el cliente HTTP asociado al contexto comparte sus cookies. Una instancia HTTP independiente mantiene otro almacén: no asumir que iniciar sesión allí autentica automáticamente una página. Para este taller conviene iniciar sesión en el contexto de cada prueba, evitando archivos de sesión compartidos. Referencias: [API testing en TypeScript](https://playwright.dev/docs/api-testing), [APIRequestContext en Java](https://playwright.dev/java/docs/api/class-apirequestcontext), [API testing en Python](https://playwright.dev/python/docs/api-testing).

## 4. Tres casos centrales y extensiones

| Caso | Ejecución | Resultado verificable |
|---|---|---|
| **TR-01: transferencia correcta** | Fixture de MXN 1000.00; enviar MXN 100.00 desde UI. | Confirmación visible, saldo UI MXN 900.00; API saldo `90000`; `total=1`, un elemento, importe `10000`, cuenta y beneficiario correctos, estado `COMPLETED`. |
| **TR-02: saldo insuficiente** | Otra fixture de MXN 1000.00; intentar MXN 1100.00 desde UI. | Alerta exacta; respuesta de envío `422` con `INSUFFICIENT_FUNDS`; API saldo `100000`, `total=0`, lista vacía. |
| **TR-03: reenvío idempotente** | Otra fixture; dos POST autenticados secuenciales de `10000` con la **misma clave y cuerpo**. | Primer estado `201`, segundo `200`, mismo id; API saldo `90000`, `total=1`, lista de un elemento con ese id. Recargar UI y comprobar saldo. |
| TR-04: límites, extensión | Importe `0`, negativo o fracción de centavo; fixtures independientes. | Rechazo por contrato y cero efectos. Distinguir validación UI de validación directa del servidor. |
| TR-05: error de servicio, extensión | Interceptar solamente el POST de transferencia del navegador y responder `503`, `{code:"SERVICE_UNAVAILABLE",message:"Servicio temporalmente no disponible"}`. | La UI muestra ese mensaje en `role="alert"`, rehabilita el botón y el servidor mantiene `100000` y cero registros porque no recibió el POST. Esto verifica reacción de UI, no disponibilidad real del backend. |
| TR-06: proyección distribuida | Capturar el transferId y consultar `/api/ledger/transfers` por la cuenta propia. | Mismo id y campos de negocio; sondeo solo de lectura, con límite de 5 segundos y fallo explícito al agotarlo. |
| Híbrido web → TNZ | Transferir desde UI e introducir la misma referencia mediante el adaptador real IBM tnz. | Referencia, estado, cuenta, importe, moneda y saldo coinciden en la pantalla simulada; se conserva `simulated: true`. No es una segunda autoridad de datos. |

Para observar una respuesta de UI, registrar la espera por método y ruta **antes** de disparar el clic. No usar pausas fijas. Para TR-05, instalar la ruta antes de la acción y liberar la interceptación al terminar; otros métodos continúan hacia el servidor.

La entrega incluye una variante defectuosa activada con `LAB_DEFECT_DUPLICATE=1` en puertos separados. La ejecución registrada de TR-03 falló como se esperaba, con evidencia de saldo `80000` y dos transferencias. Los alumnos entregan diagnóstico y evidencia; no cambian `90000` por `80000`, no agregan `skip` y no aumentan reintentos para disimular el defecto. La versión correcta se conserva para validar el resto del taller. Los comandos y directorios de evidencia separados están en el README distribuido.

## 5. Equivalencias que sí cambian la arquitectura

| Responsabilidad | TypeScript | Java | Python |
|---|---|---|---|
| Ejecutor | `@playwright/test`. | JUnit 5, ejecutado con Maven Surefire. | `pytest` con `pytest-playwright`, API síncrona. |
| Datos por prueba | Fixture con `test.extend`; preparar/finalizar alrededor de `use`. | `@BeforeEach`/`@AfterEach` o extensión JUnit propia. | Fixture de alcance función con `yield`; depender de `context`/`page` del plugin. |
| Aserción de UI con espera | `await expect(locator).toHaveText(...)`. | `assertThat(locator).hasText(...)`. | `expect(locator).to_have_text(...)`. |
| Sesión HTTP del navegador | `page.request`. | `context.request()`. | `page.request`. |
| Trace | Configuración del runner, por ejemplo `trace: 'retain-on-failure'`. | `context.tracing().start(...)` y `stop(...)`; la fixture administra archivo y conservación. | Plugin `--tracing=retain-on-failure`. |
| Reporte | Reporter HTML y, si se configura, JUnit XML. | `target/surefire-reports`: resultados XML/texto; trace es un artefacto aparte. | `--junitxml`; HTML necesita un plugin adicional como `pytest-html`. |
| Paralelismo | Workers del runner y datos propios por prueba. | Configuración JUnit/Surefire y una instancia Playwright por hilo, usada en ese hilo. | Procesos de `pytest-xdist`, dependencia adicional; datos propios por prueba. |
| Reintentos | `retries` / `--retries`; cero al diagnosticar. | Dependen del runner/plugin elegido; no existe un `--retries` común de Playwright Java. | Un plugin de reintentos es adicional; `pytest-playwright` no aporta el de TypeScript. |

Playwright Java no es seguro para compartir entre hilos sin sincronización. Para clase, ejecutar secuencialmente; como extensión, crear/cerrar Playwright y navegador dentro del mismo hilo y mantener un contexto por prueba. Evitar una `Page` estática compartida. [JUnit y ciclo de vida](https://playwright.dev/java/docs/test-runners), [multithreading Java](https://playwright.dev/java/docs/multithreading).

Las opciones de trace/navegador del plugin Python se aplican a sus fixtures; un `browser.new_context()` manual no hereda automáticamente esa administración. Extender las fixtures del plugin y verificar la conservación de traces en un fallo real. [Referencia del plugin pytest](https://playwright.dev/python/docs/test-runners). El trace de la librería Java no sustituye el resultado JUnit ni registra sus aserciones como el runner TypeScript; conservar ambos. [Tracing Java](https://playwright.dev/java/docs/api/class-tracing), [Surefire](https://maven.apache.org/surefire/maven-surefire-plugin/).

## 6. Un mismo TR-01 en tres estilos

**Fragmentos ilustrativos; no sustituyen los archivos completos ejecutados.** Presuponen que las fixtures crearon los datos, autenticaron `page`/`context`, fijaron `baseURL` y registraron finalización. `lab` en TypeScript, `sourceAccountId`/`beneficiaryId` en Java y `fixture_data` en Python representan datos del laboratorio, no APIs de Playwright. El fragmento Java de esta sección conserva Jackson como ejemplo alternativo y requiere esa dependencia si se copia; **el proyecto Java entregado usa Gson**, por lo que para ejecutarlo sin adaptaciones hay que abrir `videos/lab/mainframe/java/src/test/java/training/HybridTransferTest.java`.

### TypeScript: cuerpo de una prueba con fixture `lab`

```typescript
// Dentro de test('TR-01', async ({ page, lab }) => { ... });
// expect se importa de '@playwright/test'.
await page.goto('/transfers');
await page.getByLabel('Cuenta origen', { exact: true }).selectOption(lab.sourceAccountId);
await page.getByLabel('Beneficiario', { exact: true }).selectOption(lab.beneficiaryId);
await page.getByLabel('Importe (MXN)', { exact: true }).fill('100.00');
await page.getByRole('button', { name: 'Transferir', exact: true }).click();
await expect(page.getByRole('status')).toHaveText('Transferencia realizada');
await expect(page.getByTestId('account-balance')).toHaveText('MXN 900.00');

const accountResponse = await page.request.get(`/api/accounts/${lab.sourceAccountId}`);
expect(accountResponse.status()).toBe(200);
expect((await accountResponse.json()).balanceMinor).toBe(90000);
const listResponse = await page.request.get('/api/transfers', {
  params: { sourceAccountId: lab.sourceAccountId },
});
expect(listResponse.status()).toBe(200);
const ledger = await listResponse.json();
expect(ledger.total).toBe(1);
expect(ledger.items).toHaveLength(1);
expect(ledger.items[0]).toMatchObject({
  sourceAccountId: lab.sourceAccountId, beneficiaryId: lab.beneficiaryId,
  currency: 'MXN', amountMinor: 10000, status: 'COMPLETED',
});
```

### Java: cuerpo de un método JUnit `@Test`

```java
// Imports: com.microsoft.playwright.*, com.microsoft.playwright.options.*,
// com.fasterxml.jackson.databind.*, static Assertions.assertThat de Playwright,
// static org.junit.jupiter.api.Assertions.assertEquals.
// El método declara throws Exception para la lectura JSON del ejemplo.
page.navigate("/transfers");
page.getByLabel("Cuenta origen", new Page.GetByLabelOptions().setExact(true))
    .selectOption(sourceAccountId);
page.getByLabel("Beneficiario", new Page.GetByLabelOptions().setExact(true))
    .selectOption(beneficiaryId);
page.getByLabel("Importe (MXN)", new Page.GetByLabelOptions().setExact(true)).fill("100.00");
page.getByRole(AriaRole.BUTTON,
    new Page.GetByRoleOptions().setName("Transferir").setExact(true)).click();
assertThat(page.getByRole(AriaRole.STATUS)).hasText("Transferencia realizada");
assertThat(page.getByTestId("account-balance")).hasText("MXN 900.00");

ObjectMapper mapper = new ObjectMapper();
APIResponse accountResponse = context.request().get("/api/accounts/" + sourceAccountId);
assertEquals(200, accountResponse.status());
assertEquals(90000, mapper.readTree(accountResponse.text()).get("balanceMinor").asInt());
APIResponse listResponse = context.request().get("/api/transfers",
    RequestOptions.create().setQueryParam("sourceAccountId", sourceAccountId));
assertEquals(200, listResponse.status());
JsonNode ledger = mapper.readTree(listResponse.text());
assertEquals(1, ledger.get("total").asInt());
assertEquals(1, ledger.get("items").size());
JsonNode transfer = ledger.get("items").get(0);
assertEquals(sourceAccountId, transfer.get("sourceAccountId").asText());
assertEquals(beneficiaryId, transfer.get("beneficiaryId").asText());
assertEquals("MXN", transfer.get("currency").asText());
assertEquals(10000, transfer.get("amountMinor").asInt());
assertEquals("COMPLETED", transfer.get("status").asText());
```

### Python: cuerpo de `test_tr01(page, fixture_data)`

```python
# expect se importa de playwright.sync_api; este es el cuerpo de la función.
page.goto("/transfers")
page.get_by_label("Cuenta origen", exact=True).select_option(fixture_data["sourceAccountId"])
page.get_by_label("Beneficiario", exact=True).select_option(fixture_data["beneficiaryId"])
page.get_by_label("Importe (MXN)", exact=True).fill("100.00")
page.get_by_role("button", name="Transferir", exact=True).click()
expect(page.get_by_role("status")).to_have_text("Transferencia realizada")
expect(page.get_by_test_id("account-balance")).to_have_text("MXN 900.00")

account_response = page.request.get(f"/api/accounts/{fixture_data['sourceAccountId']}")
assert account_response.status == 200
assert account_response.json()["balanceMinor"] == 90000
list_response = page.request.get("/api/transfers", params={
    "sourceAccountId": fixture_data["sourceAccountId"],
})
assert list_response.status == 200
ledger = list_response.json()
assert ledger["total"] == 1
assert len(ledger["items"]) == 1
transfer = ledger["items"][0]
assert transfer["sourceAccountId"] == fixture_data["sourceAccountId"]
assert transfer["beneficiaryId"] == fixture_data["beneficiaryId"]
assert transfer["currency"] == "MXN"
assert transfer["amountMinor"] == 10000
assert transfer["status"] == "COMPLETED"
```

La equivalencia importante es la misma regla y el mismo estado observado. Un mensaje verde en UI, por sí solo, no demuestra que hubo exactamente un débito. Al adaptar con IA, revisar también imports, tipos, preparación, liberación de respuestas/contextos y compatibilidad con las versiones fijadas. Las llamadas se apoyan en las APIs oficiales; estos fragmentos requieren integrarse y ejecutarse antes de entregarlos como código listo.
