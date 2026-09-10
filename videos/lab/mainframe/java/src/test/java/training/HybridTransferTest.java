package training;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.RequestOptions;
import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;

class HybridTransferTest {
  static JsonObject json(APIResponse response) {
    return JsonParser.parseString(response.text()).getAsJsonObject();
  }

  @Test
  void browserTransferMatchesSimulated3270Screen() throws Exception {
    String key = System.getenv("TEST_HOOK_KEY");
    assertNotNull(key, "Set TEST_HOOK_KEY to the running local gateway classroom key");
    String baseUrl = System.getenv().getOrDefault("BASE_URL", "http://127.0.0.1:3000");
    Path mainframe = Path.of("..").toAbsolutePath().normalize();
    Path evidence = mainframe.resolve("evidence");
    Files.createDirectories(evidence);
    String defaultPython = mainframe.resolve(System.getProperty("os.name").startsWith("Windows")
        ? ".venv/Scripts/python.exe" : ".venv/bin/python").toString();
    String python = System.getenv().getOrDefault("TNZ_PYTHON", defaultPython);

    try (Playwright playwright = Playwright.create()) {
      BrowserType.LaunchOptions options = new BrowserType.LaunchOptions().setHeadless(true);
      String channel = System.getenv("PW_BROWSER_CHANNEL");
      if (channel != null && !channel.isBlank()) options.setChannel(channel);
      try (Browser browser = playwright.chromium().launch(options);
           BrowserContext context = browser.newContext(new Browser.NewContextOptions().setBaseURL(baseUrl))) {
        APIRequestContext api = context.request();
        APIResponse created = api.post("/__test/fixtures", RequestOptions.create()
            .setHeader("X-Test-Hook-Key", key).setData(Map.of("runId", "java-" + UUID.randomUUID(),
                "caseId", "HYBRID-JAVA-01", "currency", "MXN", "balanceMinor", 100000)));
        assertEquals(201, created.status(), created.text());
        JsonObject fixture = json(created);
        String source = fixture.get("sourceAccountId").getAsString();
        boolean traceStarted = false;
        try {
          context.tracing().start(new Tracing.StartOptions().setScreenshots(true).setSnapshots(true).setSources(true));
          traceStarted = true;
          APIResponse login = api.post("/api/session", RequestOptions.create().setData(Map.of(
              "username", fixture.get("username").getAsString(), "password", fixture.get("password").getAsString())));
          assertEquals(200, login.status());
          Page page = context.newPage();
          page.navigate("/transfers");
          page.getByLabel("Cuenta origen", new Page.GetByLabelOptions().setExact(true)).selectOption(source);
          page.getByLabel("Beneficiario", new Page.GetByLabelOptions().setExact(true))
              .selectOption(fixture.get("beneficiaryId").getAsString());
          page.getByLabel("Importe (MXN)", new Page.GetByLabelOptions().setExact(true)).fill("100.00");
          page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Transferir").setExact(true)).click();
          assertThat(page.getByRole(AriaRole.STATUS)).hasText("Transferencia realizada");
          assertThat(page.getByTestId("account-balance")).hasText("MXN 900.00");
          APIResponse transfers = api.get("/api/transfers", RequestOptions.create().setQueryParam("sourceAccountId", source));
          assertEquals(200, transfers.status());
          JsonObject records = json(transfers);
          assertEquals(1, records.get("total").getAsInt());
          String reference = records.getAsJsonArray("items").get(0).getAsJsonObject().get("id").getAsString();
          // No shell command composition: ProcessBuilder passes exact arguments to Python.
          Process process = new ProcessBuilder(python, mainframe.resolve("adapter.py").toString(), "lookup", reference,
              "--timeout", "8", "--snapshot", evidence.resolve("hybrid-java-terminal.txt").toString())
              .redirectErrorStream(true).start();
          if (!process.waitFor(12, TimeUnit.SECONDS)) {
            process.destroyForcibly();
            fail("TNZ adapter exceeded the bounded 12-second process timeout");
          }
          String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
          assertEquals(0, process.exitValue(), output);
          JsonObject terminal = JsonParser.parseString(output).getAsJsonObject();
          assertEquals(reference, terminal.get("reference").getAsString());
          assertEquals("COMPLETED", terminal.get("status").getAsString());
          assertEquals(source, terminal.get("sourceAccountId").getAsString());
          assertEquals(10000, terminal.get("amountMinor").getAsInt());
          assertEquals("MXN", terminal.get("currency").getAsString());
          assertEquals(90000, terminal.get("balanceMinor").getAsInt());
          assertTrue(terminal.get("simulated").getAsBoolean());
          Files.writeString(evidence.resolve("hybrid-java-result.json"), terminal.toString(), StandardCharsets.UTF_8);
          page.screenshot(new Page.ScreenshotOptions().setPath(evidence.resolve("hybrid-java-browser.png")).setFullPage(true));
        } finally {
          try {
            if (traceStarted) context.tracing().stop(new Tracing.StopOptions().setPath(evidence.resolve("hybrid-java-trace.zip")));
          } finally {
            APIResponse deleted = api.delete("/__test/fixtures/" + fixture.get("fixtureId").getAsString(),
                RequestOptions.create().setHeader("X-Test-Hook-Key", key));
            assertEquals(204, deleted.status(), "Fixture cleanup failed");
          }
        }
      }
    }
  }
}
