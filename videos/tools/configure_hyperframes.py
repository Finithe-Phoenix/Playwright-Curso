"""Apply the documented, narrowly scoped Hyperframes 0.8.33 verification-budget hook.

The upstream 15-second default remains unless HF_COURSE_STATIC_VERIFY_MAX_MS is set.
Pixel comparisons, sample selection, codecs, quality, and frame rate are unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "node_modules/hyperframes/dist/cli.js"
BEFORE = b"STATIC_VERIFY_MAX_MS = 15e3;"
AFTER = b'STATIC_VERIFY_MAX_MS = Number(process.env.HF_COURSE_STATIC_VERIFY_MAX_MS ?? "15000");'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write_atomic(path, payload):
    path = path.resolve()
    path.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def configure(budget_ms=90000, *, dry_run=False):
    if not 15000 <= budget_ms <= 300000:
        raise ValueError("Verification budget must be between 15000 and 300000 ms")
    package = json.loads((ROOT / "node_modules/hyperframes/package.json").read_text(encoding="utf-8"))
    if package.get("version") != "0.8.33":
        raise ValueError("The budget hook is restricted to Hyperframes 0.8.33; inspect a new version before changing it")
    CLI.resolve().relative_to(ROOT)
    current = CLI.read_bytes()
    already_patched = current.count(AFTER) == 1 and current.count(BEFORE) == 0
    if already_patched:
        original = current.replace(AFTER, BEFORE, 1)
        updated = current
    elif current.count(BEFORE) == 1 and current.count(AFTER) == 0:
        original = current
        updated = current.replace(BEFORE, AFTER, 1)
    else:
        raise ValueError("Expected exactly one known STATIC_VERIFY_MAX_MS assignment; preserving the CLI unchanged")
    backup = ROOT / ".tools/hyperframes-backups" / f"cli-0.8.33-{sha(original)}.js"
    record = {"hyperframesVersion": "0.8.33", "originalSha256": sha(original), "patchedSha256": sha(updated),
              "cli": CLI.relative_to(ROOT).as_posix(), "backup": backup.relative_to(ROOT).as_posix(),
              "modifiedAssignmentCount": 1, "upstreamDefaultMs": 15000, "courseBudgetMs": budget_ms,
              "environmentVariable": "HF_COURSE_STATIC_VERIFY_MAX_MS", "frameComparisonsEnabled": True,
              "change": "Allow a longer verification budget before falling back to frame capture; keep pixel comparisons unchanged",
              "alreadyPatched": already_patched, "dryRun": dry_run, "checkedAt": datetime.now(timezone.utc).isoformat()}
    if not dry_run:
        if backup.exists() and backup.read_bytes() != original:
            raise ValueError("The existing CLI backup does not match its recorded SHA; preserving all files")
        if not backup.exists():
            write_atomic(backup, original)
        if CLI.read_bytes() != current:
            raise ValueError("CLI changed during configuration; retry after confirming the owner")
        if not already_patched:
            write_atomic(CLI, updated)
        write_atomic(ROOT / "qa/hyperframes-performance.json", json.dumps(record, indent=2).encode("utf-8"))
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verification-budget-ms", type=int, default=90000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(configure(args.verification_budget_ms, dry_run=args.dry_run), indent=2))
