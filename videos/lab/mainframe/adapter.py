"""IBM tnz adapter for the local simulated 3270 transfer lookup screen."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from time import monotonic
from tnz import tnz

REFERENCE_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,48}\Z")


class TerminalTimeout(TimeoutError):
    pass


class TerminalSession:
    def __init__(self, host="127.0.0.1", port=2323, timeout=8):
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("This plaintext training adapter is restricted to loopback")
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self.host, self.port, self.timeout = host, port, timeout
        self.terminal = tnz.Tnz("TRAINING")
        self.terminal.encoding = "cp037"
        self.snapshots: list[dict[str, str]] = []

    def __enter__(self):
        self.terminal.connect(host=self.host, port=self.port, secure=False, verifycert=True)
        try:
            self.wait_for(lambda screen: "TRANSFER REFERENCE" in screen, "initial screen")
            self.capture("ready")
            return self
        except BaseException:
            self.close()
            raise

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    def close(self):
        self.terminal.shutdown()

    def capture(self, step: str) -> str:
        screen = self.terminal.scrstr()
        self.snapshots.append({"step": step, "screen": screen})
        return screen

    def wait_for(self, predicate, description: str, timeout=None) -> str:
        deadline = monotonic() + (self.timeout if timeout is None else timeout)
        while True:
            screen = self.terminal.scrstr()
            if predicate(screen) and not self.terminal.pwait and not self.terminal.system_lock_wait:
                return screen
            if self.terminal.seslost:
                raise ConnectionError("TN3270 session disconnected")
            remaining = deadline - monotonic()
            if remaining <= 0:
                self.capture("timeout: " + description)
                raise TerminalTimeout(f"Timed out waiting for {description}")
            # Pump real incoming terminal events, bounded by a monotonic deadline.
            self.terminal.wait(min(0.1, remaining))

    def lookup(self, reference: str) -> dict:
        if not REFERENCE_PATTERN.fullmatch(reference):
            raise ValueError("Reference must contain 1-48 ASCII letters, numbers, underscores or hyphens")
        self.terminal.key_home()
        self.terminal.key_eraseeof()
        self.terminal.key_data(reference)
        self.terminal.enter()
        self.wait_for(
            lambda screen: f"REFERENCE    : {reference}" in screen and "STATUS       : READY" not in screen,
            "lookup result for reference",
        )
        text = self.capture("lookup-result")
        def field(label):
            match = re.search(r"^\s*" + re.escape(label) + r"\s*:\s*(.*?)\s*$", text, re.MULTILINE)
            if not match:
                raise ValueError("Missing terminal field: " + label)
            return match.group(1)
        result = {"reference": field("REFERENCE"), "status": field("STATUS"), "simulated": True}
        if result["status"] == "COMPLETED":
            result.update(amountMinor=int(field("AMOUNT MINOR")), currency=field("CURRENCY"), sourceAccountId=field("SOURCE"), balanceMinor=int(field("BALANCE MINOR")))
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("health", "lookup"))
    parser.add_argument("reference", nargs="?")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2323)
    parser.add_argument("--timeout", type=float, default=8)
    parser.add_argument("--snapshot", type=Path)
    args = parser.parse_args()
    if args.action == "lookup" and not args.reference:
        parser.error("lookup requires a reference")
    session = None
    try:
        session = TerminalSession(args.host, args.port, args.timeout)
        with session:
            result = session.lookup(args.reference) if args.action == "lookup" else {"status": "READY", "simulated": True}
        print(json.dumps(result))
        return 0 if result["status"] in ("READY", "COMPLETED") else 2
    except (ValueError, TimeoutError, ConnectionError, OSError) as error:
        print(json.dumps({"error": type(error).__name__, "message": str(error)}))
        return 1
    finally:
        if args.snapshot and session:
            args.snapshot.parent.mkdir(parents=True, exist_ok=True)
            args.snapshot.write_text("\n\n".join("STEP: " + item["step"] + "\n" + item["screen"] for item in session.snapshots), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
