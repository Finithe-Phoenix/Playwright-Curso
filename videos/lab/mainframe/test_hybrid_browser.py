"""Playwright browser -> transfer reference -> IBM tnz real socket -> assertions."""
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

ROOT = Path(__file__).resolve().parent
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:3000")


@pytest.mark.hybrid
def test_browser_transfer_matches_simulated_terminal(page: Page, pytestconfig):
    hook_key = os.environ.get("TEST_HOOK_KEY")
    assert hook_key, "Set TEST_HOOK_KEY to the local gateway's classroom test key"
    hook_headers = {"X-Test-Hook-Key": hook_key}
    created = page.request.post(BASE_URL + "/__test/fixtures", headers=hook_headers, data={
        "runId": "python-" + uuid4().hex, "caseId": "HYBRID-01", "currency": "MXN", "balanceMinor": 100000,
    })
    assert created.status == 201, created.text()
    fixture = created.json()
    evidence = ROOT / "evidence"
    manual_trace_started = False
    try:
        evidence.mkdir(exist_ok=True)
        # The pytest plugin owns tracing when --tracing is enabled.
        if pytestconfig.getoption("--tracing") == "off":
            page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
            manual_trace_started = True
        login = page.context.request.post(BASE_URL + "/api/session", data={
            "username": fixture["username"], "password": fixture["password"],
        })
        assert login.status == 200
        page.goto(BASE_URL + "/transfers")
        page.get_by_label("Cuenta origen", exact=True).select_option(fixture["sourceAccountId"])
        page.get_by_label("Beneficiario", exact=True).select_option(fixture["beneficiaryId"])
        page.get_by_label("Importe (MXN)", exact=True).fill("100.00")
        page.get_by_role("button", name="Transferir", exact=True).click()
        expect(page.get_by_role("status")).to_have_text("Transferencia realizada")
        expect(page.get_by_test_id("account-balance")).to_have_text("MXN 900.00")
        transfers = page.request.get(BASE_URL + "/api/transfers", params={"sourceAccountId": fixture["sourceAccountId"]})
        assert transfers.status == 200
        records = transfers.json()
        assert records["total"] == 1
        reference = records["items"][0]["id"]
        # Dedicated process: clear ownership of the tnz event loop, portable to Java/TS.
        process = subprocess.run([
            sys.executable, str(ROOT / "adapter.py"), "lookup", reference,
            "--timeout", "8", "--snapshot", str(evidence / "hybrid-python-terminal.txt"),
        ], text=True, capture_output=True, timeout=12, check=False)
        assert process.returncode == 0, process.stdout + process.stderr
        result = json.loads(process.stdout)
        assert result == {"reference": reference, "status": "COMPLETED", "simulated": True,
                          "amountMinor": 10000, "currency": "MXN", "sourceAccountId": fixture["sourceAccountId"], "balanceMinor": 90000}
        (evidence / "hybrid-python-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        page.screenshot(path=str(evidence / "hybrid-python-browser.png"), full_page=True)
    finally:
        try:
            if manual_trace_started:
                page.context.tracing.stop(path=evidence / "hybrid-python-trace.zip")
        finally:
            deleted = page.request.delete(BASE_URL + "/__test/fixtures/" + fixture["fixtureId"], headers=hook_headers)
            assert deleted.status == 204, "Fixture cleanup failed"
