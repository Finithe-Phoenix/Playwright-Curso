"""Actual TN3270 socket tests; only the upstream business data is a fixture."""
import threading
from pathlib import Path
from urllib.error import URLError

import pytest

from adapter import TerminalSession, TerminalTimeout
from simulator import TrainingServer


@pytest.fixture
def terminal_port():
    def lookup(reference):
        if reference != "TRAINING-0001":
            raise LookupError(reference)
        return {"reference": reference, "status": "COMPLETED", "amountMinor": 12500,
                "currency": "MXN", "sourceAccountId": "training-source", "balanceMinor": 87500}
    server = TrainingServer(port=0, lookup=lookup)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server.server_address[1]
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_real_tnz_screen_lookup_and_result(terminal_port):
    with TerminalSession(port=terminal_port, timeout=3) as session:
        result = session.lookup("TRAINING-0001")
        assert result == {"reference": "TRAINING-0001", "status": "COMPLETED", "simulated": True,
                          "amountMinor": 12500, "currency": "MXN", "sourceAccountId": "training-source", "balanceMinor": 87500}
        folder = Path(__file__).parent / "evidence"
        folder.mkdir(exist_ok=True)
        (folder / "offline-terminal.txt").write_text(session.terminal.scrstr(), encoding="utf-8")


def test_unknown_reference_is_business_result(terminal_port):
    with TerminalSession(port=terminal_port, timeout=3) as session:
        assert session.lookup("UNKNOWN")["status"] == "NOT FOUND"


def test_invalid_reference_rejected_before_send(terminal_port):
    with TerminalSession(port=terminal_port, timeout=3) as session:
        with pytest.raises(ValueError, match="1-48"):
            session.lookup("bad reference")


def test_missing_screen_condition_has_bounded_timeout(terminal_port):
    with TerminalSession(port=terminal_port, timeout=3) as session:
        with pytest.raises(TerminalTimeout, match="never appears"):
            session.wait_for(lambda screen: "NEVER-EXPECTED" in screen, "never appears", timeout=0.15)


def test_backend_unavailable_returns_explicit_terminal_status():
    def unavailable(reference):
        raise URLError("Synthetic upstream outage")
    server = TrainingServer(port=0, lookup=unavailable)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with TerminalSession(port=server.server_address[1], timeout=3) as session:
            result = session.lookup("TRAINING-OUTAGE")
            assert result == {"reference": "TRAINING-OUTAGE", "status": "BACKEND UNAVAILABLE", "simulated": True}
            folder = Path(__file__).parent / "evidence"
            folder.mkdir(exist_ok=True)
            (folder / "backend-unavailable-terminal.txt").write_text(session.terminal.scrstr(), encoding="utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
