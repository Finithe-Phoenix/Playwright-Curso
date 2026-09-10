"""Core browser/API regressions: insufficient funds and sequential idempotency."""
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:3000")
EVIDENCE = Path(__file__).resolve().parent / "evidence"


@pytest.fixture
def account_fixture(page: Page, request):
    key = os.environ.get("TEST_HOOK_KEY")
    assert key, "Set TEST_HOOK_KEY to the running local gateway key"
    headers = {"X-Test-Hook-Key": key}
    response = page.request.post(BASE_URL + "/__test/fixtures", headers=headers, data={
        "runId": "python-core-" + uuid4().hex, "caseId": request.node.name,
        "currency": "MXN", "balanceMinor": 100000,
    })
    assert response.status == 201, response.text()
    fixture = response.json()
    try:
        login = page.context.request.post(BASE_URL + "/api/session", data={
            "username": fixture["username"], "password": fixture["password"],
        })
        assert login.status == 200
        yield fixture
    finally:
        deleted = page.request.delete(BASE_URL + "/__test/fixtures/" + fixture["fixtureId"], headers=headers)
        assert deleted.status == 204, "Fixture cleanup failed"


def state(page, fixture, expected_balance, expected_count):
    account = page.request.get(BASE_URL + "/api/accounts/" + fixture["sourceAccountId"])
    assert account.status == 200
    assert account.json()["balanceMinor"] == expected_balance
    transfers = page.request.get(BASE_URL + "/api/transfers", params={"sourceAccountId": fixture["sourceAccountId"]})
    assert transfers.status == 200
    result = transfers.json()
    assert result["total"] == expected_count
    return result


def test_tr02_insufficient_funds_creates_no_transfer(page: Page, account_fixture):
    page.goto(BASE_URL + "/transfers")
    page.get_by_label("Cuenta origen", exact=True).select_option(account_fixture["sourceAccountId"])
    page.get_by_label("Beneficiario", exact=True).select_option(account_fixture["beneficiaryId"])
    page.get_by_label("Importe (MXN)", exact=True).fill("1100.00")
    with page.expect_response(lambda response: response.url.endswith("/api/transfers") and response.request.method == "POST") as captured:
        page.get_by_role("button", name="Transferir", exact=True).click()
    assert captured.value.status == 422
    assert captured.value.json()["code"] == "INSUFFICIENT_FUNDS"
    expect(page.get_by_role("alert")).to_have_text("Saldo insuficiente")
    expect(page.get_by_test_id("account-balance")).to_have_text("MXN 1000.00")
    result = state(page, account_fixture, 100000, 0)
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "python-tr02-result.json").write_text(json.dumps({"httpStatus": 422, "code": "INSUFFICIENT_FUNDS", "balanceMinor": 100000, "transfers": result}, indent=2), encoding="utf-8")
    page.screenshot(path=str(EVIDENCE / "python-tr02-browser.png"), full_page=True)


def test_tr03_sequential_retry_debits_once(page: Page, account_fixture):
    transfer = {"sourceAccountId": account_fixture["sourceAccountId"], "beneficiaryId": account_fixture["beneficiaryId"], "currency": "MXN", "amountMinor": 10000}
    headers = {"Idempotency-Key": str(uuid4())}
    first = page.request.post(BASE_URL + "/api/transfers", headers=headers, data=transfer)
    second = page.request.post(BASE_URL + "/api/transfers", headers=headers, data=transfer)
    assert first.status == 201
    assert second.status == 200
    assert second.json() == first.json()
    result = state(page, account_fixture, 90000, 1)
    assert result["items"][0]["id"] == first.json()["id"]
    page.goto(BASE_URL + "/transfers")
    expect(page.get_by_test_id("account-balance")).to_have_text("MXN 900.00")
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "python-tr03-result.json").write_text(json.dumps({"httpStatuses": [201, 200], "sameResponse": True, "balanceMinor": 90000, "transfers": result}, indent=2), encoding="utf-8")
    page.screenshot(path=str(EVIDENCE / "python-tr03-browser.png"), full_page=True)
