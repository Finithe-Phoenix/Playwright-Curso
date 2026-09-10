"""Loopback-only educational TN3270 server. This does not emulate z/OS or CICS."""
from __future__ import annotations

import argparse
import json
import re
import socket
import socketserver
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

IAC, DO, DONT, WILL, WONT, SB, SE, EOR = 255, 253, 254, 251, 252, 250, 240, 239
REFERENCE_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,48}\Z")
INPUT_ADDRESS = 7 * 80 + 23


def address(value: int) -> bytes:
    """3270 14-bit binary buffer address, valid for a 24x80 screen."""
    return value.to_bytes(2, "big")


def text_at(row: int, column: int, text: str) -> bytes:
    return b"\x11" + address(row * 80 + column) + text.encode("cp037")


def screen(status: str = "READY", reference: str = "", result: dict | None = None) -> bytes:
    # Erase/Write, reset modified-data tags and restore keyboard; protected field.
    data = bytearray(b"\xf5\xc3\x1d\xf0")
    for row, line in {
        1: "TRAINING LEDGER - SIMULATED 3270",
        2: "LOCAL CLASSROOM ONLY | Python TN3270 server | No z/OS or CICS",
        4: "Find a transfer committed by the local distributed application.",
        5: "This screen reads the SAME local ledger; it is not an independent audit.",
        7: "TRANSFER REFERENCE :",
        10: f"STATUS       : {status}",
        11: f"REFERENCE    : {reference}",
        20: "Enter = lookup reference     Clear = new search",
        22: "SIMULATION: synthetic data; plaintext TN3270 bound to 127.0.0.1 only.",
    }.items():
        data.extend(text_at(row, 2, line))
    if result:
        for row, line in {
            12: f"AMOUNT MINOR : {result['amountMinor']}",
            13: f"CURRENCY     : {result['currency']}",
            14: f"SOURCE       : {result['sourceAccountId']}",
            15: f"BALANCE MINOR: {result['balanceMinor']}",
        }.items():
            data.extend(text_at(row, 2, line[:76]))
    # One 48-character unprotected input field, then resume protection.
    data.extend(b"\x11" + address(INPUT_ADDRESS - 1) + b"\x1d\x40")
    data.extend((reference or "").ljust(48).encode("cp037"))
    data.extend(b"\x1d\xf0\x11" + address(INPUT_ADDRESS) + b"\x13")
    return bytes(data).replace(b"\xff", b"\xff\xff") + b"\xff\xef"


def decode_reference(record: bytes) -> str:
    # Read Modified: AID byte, cursor address, then SBA + input field data.
    if len(record) < 6 or record[0] != 0x7D:
        return ""
    index = 3
    parts: list[bytes] = []
    while index < len(record):
        if record[index] == 0x11:
            index += 3
            start = index
            while index < len(record) and record[index] != 0x11:
                index += 1
            parts.append(record[start:index])
        else:
            index += 1
    return b"".join(parts).decode("cp037").replace("\x00", "").strip()


class TrainingHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        self.request.settimeout(30)
        negotiation = bytes([
            IAC, DO, 0, IAC, WILL, 0, IAC, DO, 25, IAC, WILL, 25,
            IAC, DO, 24, IAC, SB, 24, 1, IAC, SE,
        ])
        try:
            self.request.sendall(negotiation + screen())
            state, command = "DATA", 0
            record = bytearray()
            while True:
                chunk = self.request.recv(4096)
                if not chunk:
                    return
                for value in chunk:
                    if state == "DATA":
                        if value == IAC:
                            state = "IAC"
                        else:
                            record.append(value)
                    elif state == "IAC":
                        if value == IAC:
                            record.append(IAC)
                            state = "DATA"
                        elif value == EOR:
                            self.respond(bytes(record))
                            record.clear()
                            state = "DATA"
                        elif value in (DO, DONT, WILL, WONT):
                            command, state = value, "OPTION"
                        elif value == SB:
                            state = "SUB"
                        else:
                            state = "DATA"
                    elif state == "OPTION":
                        if value not in (0, 24, 25) and command in (DO, WILL):
                            response = WONT if command == DO else DONT
                            self.request.sendall(bytes([IAC, response, value]))
                        state = "DATA"
                    elif state == "SUB":
                        if value == IAC:
                            state = "SUB_IAC"
                    elif state == "SUB_IAC":
                        state = "DATA" if value == SE else "SUB"
                if len(record) > 8192:
                    return
        except (ConnectionError, OSError):
            return

    def respond(self, record: bytes) -> None:
        if record and record[0] == 0x6D:  # CLEAR
            self.request.sendall(screen())
            return
        if not record or record[0] != 0x7D:
            self.request.sendall(screen("PRESS ENTER"))
            return
        reference = decode_reference(record)
        if not REFERENCE_PATTERN.fullmatch(reference):
            self.request.sendall(screen("INVALID REFERENCE"))
            return
        try:
            result = self.server.lookup(reference)
            status = result.get("status", "INVALID RESPONSE")
            self.request.sendall(screen(status, reference, result))
        except LookupError:
            self.request.sendall(screen("NOT FOUND", reference))
        except (URLError, TimeoutError, OSError, ValueError, KeyError):
            self.request.sendall(screen("BACKEND UNAVAILABLE", reference))


class TrainingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, port: int = 2323, gateway: str = "http://127.0.0.1:3000", lookup=None):
        if urlparse(gateway).hostname not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("The classroom gateway must use loopback")
        self.gateway = gateway.rstrip("/")
        if lookup is not None:
            self.lookup = lookup
        super().__init__(("127.0.0.1", port), TrainingHandler)

    def lookup(self, reference: str) -> dict:
        url = self.gateway + "/__test/lookup?" + urlencode({"reference": reference})
        try:
            with urlopen(url, timeout=2) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 404:
                raise LookupError(reference) from error
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=2323)
    parser.add_argument("--gateway", default="http://127.0.0.1:3000")
    arguments = parser.parse_args()
    with TrainingServer(arguments.port, arguments.gateway) as server:
        print(json.dumps({"status": "listening", "host": "127.0.0.1", "port": server.server_address[1], "mode": "SIMULATED TN3270", "gateway": server.gateway}), flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
