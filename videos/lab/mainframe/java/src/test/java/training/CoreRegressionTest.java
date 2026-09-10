package training;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.RequestOptions;
import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;

class CoreRegressionTest {
  interface Scenario { JsonObject run(Page page, APIRequestContext api, JsonObject fixture); }
  static JsonObject json(APIResponse response) { return JsonParser.parseString(response.text()).getAsJsonObject(); }

  static JsonObject state(APIRequestContext api, JsonObject fixture, int balance, int count) {
    String source = fixture.get("sourceAccountId").getAsString();
    APIResponse account = api.get("/api/accounts/" + source);
    assertEquals(200, account.status());
    assertEquals(balance, json(account).get("balanceMinor").getAsInt());
    APIResponse transfers = api.get("/api/transfers", RequestOptions.create().setQueryParam("sourceAccountId", source));
    assertEquals(200, transfers.status());
    JsonObject result = json(transfers);
    assertEquals(count, result.get("total").getAsInt());
    assertEquals(count, result.getAsJsonArray("items").size());
    return result;
  }

  void runCase(String id, Scenario scenario) throws Exception {
    String key = System.getenv("TEST_HOOK_KEY");
    assertNotNull(key, "Set TEST_HOOK_KEY to the running local gateway key");
    Path evidence = Path.of("..", "evidence").toAbsolutePath().normalize();
    Files.createDirectories(evidence);
    try (Playwright playwright = Playwright.create()) {
      BrowserType.LaunchOptions options = new BrowserType.LaunchOptions().setHeadless(true);
      String channel = System.getenv("PW_BROWSER_CHANNEL");
      if (channel != null && !channel.isBlank()) options.setChannel(channel);
      try (Browser browser = playwright.chromium().launch(options);
           BrowserContext context = browser.newContext(new Browser.NewContextOptions()
               .setBaseURL(System.getenv().getOrDefault("BASE_URL", "http://127.0.0.1:3000")))) {
        APIRequestContext api = context.request();
        APIResponse created = api.post("/__test/fixtures", RequestOptions.create().setHeader("X-Test-Hook-Key", key)
            .setData(Map.of("runId", "java-core-" + UUID.randomUUID(), "caseId", id, "currency", "MXN", "balanceMinor", 100000)));
        assertEquals(201, created.status(), created.text());
        JsonObject fixture = json(created);
        boolean traceStarted = false;
        try {
          context.tracing().start(new Tracing.StartOptions().setScreenshots(true).setSnapshots(true).setSources(true));
          traceStarted = true;
          APIResponse login = api.post("/api/session", RequestOptions.create().setData(Map.of(
              "username", fixture.get("username").getAsString(), "password", fixture.get("password").getAsString())));
          assertEquals(200, login.status());
          Page page = context.newPage();
          JsonObject result = scenario.run(page, api, fixture);
          Files.writeString(evidence.resolve("java-" + id.toLowerCase() + "-result.json"), result.toString());
          page.screenshot(new Page.ScreenshotOptions().setPath(evidence.resolve("java-" + id.toLowerCase() + "-browser.png")).setFullPage(true));
        } finally {
          try {
            if (traceStarted) context.tracing().stop(new Tracing.StopOptions().setPath(evidence.resolve("java-" + id.toLowerCase() + "-trace.zip")));
          } finally {
            APIResponse deleted = api.delete("/__test/fixtures/" + fixture.get("fixtureId").getAsString(),
                RequestOptions.create().setHeader("X-Test-Hook-Key", key));
            assertEquals(204, deleted.status(), "Fixture cleanup failed");
          }
        }
      }
    }
  }

  @Test void tr02InsufficientFundsCreatesNoTransfer() throws Exception {
    runCase("TR02", (page, api, fixture) -> {
      page.navigate("/transfers");
      page.getByLabel("Cuenta origen", new Page.GetByLabelOptions().setExact(true)).selectOption(fixture.get("sourceAccountId").getAsString());
      page.getByLabel("Beneficiario", new Page.GetByLabelOptions().setExact(true)).selectOption(fixture.get("beneficiaryId").getAsString());
      page.getByLabel("Importe (MXN)", new Page.GetByLabelOptions().setExact(true)).fill("1100.00");
      Response response = page.waitForResponse(r -> r.url().endsWith("/api/transfers") && r.request().method().equals("POST"),
          () -> page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Transferir").setExact(true)).click());
      assertEquals(422, response.status());
      assertEquals("INSUFFICIENT_FUNDS", JsonParser.parseString(response.text()).getAsJsonObject().get("code").getAsString());
      assertThat(page.getByRole(AriaRole.ALERT)).hasText("Saldo insuficiente");
      assertThat(page.getByTestId("account-balance")).hasText("MXN 1000.00");
      JsonObject result = state(api, fixture, 100000, 0);
      result.addProperty("balanceMinor", 100000);
      result.addProperty("httpStatus", 422);
      return result;
    });
  }

  @Test void tr03SequentialRetryDebitsOnce() throws Exception {
    runCase("TR03", (page, api, fixture) -> {
      Map<String, Object> body = Map.of("sourceAccountId", fixture.get("sourceAccountId").getAsString(),
          "beneficiaryId", fixture.get("beneficiaryId").getAsString(), "currency", "MXN", "amountMinor", 10000);
      String key = UUID.randomUUID().toString();
      APIResponse first = api.post("/api/transfers", RequestOptions.create().setHeader("Idempotency-Key", key).setData(body));
      APIResponse second = api.post("/api/transfers", RequestOptions.create().setHeader("Idempotency-Key", key).setData(body));
      assertEquals(201, first.status());
      assertEquals(200, second.status());
      assertEquals(json(first), json(second));
      JsonObject result = state(api, fixture, 90000, 1);
      assertEquals(json(first).get("id"), result.getAsJsonArray("items").get(0).getAsJsonObject().get("id"));
      page.navigate("/transfers");
      assertThat(page.getByTestId("account-balance")).hasText("MXN 900.00");
      result.addProperty("balanceMinor", 90000);
      result.addProperty("firstHttpStatus", 201);
      result.addProperty("retryHttpStatus", 200);
      result.addProperty("sameResponse", true);
      return result;
    });
  }
}
