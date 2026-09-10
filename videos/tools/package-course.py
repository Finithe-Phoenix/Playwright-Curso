"""Inventory or create a source-only course ZIP; default is a read-only dry run.

Examples:
  py -3.12 tools/package-course.py --dry-run
  py -3.12 tools/package-course.py --create

No media, model weights, installed environments, session dumps or heavy evidence
are packaged. The original files are never edited or deleted.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import zipfile


VIDEO_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = VIDEO_ROOT.parent.resolve()
PREFIX = "playwright-ai-course"
TOP_LEVEL_FILES = {
    "01-PLAN-DEL-CURSO.md", "02-PROMPTS-COPIAR-PEGAR.md", "03-LABORATORIO-Y-LENGUAJES.md",
    "04-COMANDOS-Y-CI.md", "05-PREPARACION-Y-EVALUACION.md", "CURSO-PLAYWRIGHT-IA.html", "LEEME.md",
}
VIDEO_FILES = {"LEEME-VIDEOS.md", "COURSE-VIDEO-MAP.md", "FRAGMENTOS-PARA-LA-CLASE.md", "AI-PROMPTS-REGRESSION.md", "BRIEF.md", "DESIGN.md",
               "package.json", "package-lock.json", ".gitignore"}
SOURCE_FOLDERS = {"lab", "scripts", "tools", "compositions", "assets", "qa"}
EXCLUDED_DIRECTORIES = {
    "node_modules", ".venv", "venv", "models", ".tools", "target", "evidence", "logs",
    "renders", "render-temp", "render_tmp", "test-results", "playwright-report", "html-report",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".runtime",
    "delivery", "exports", "dist", "build",
}
TEXT_EXTENSIONS = {".md", ".json", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".py", ".ps1",
                   ".html", ".css", ".yml", ".yaml", ".toml", ".txt", ".srt", ".vtt",
                   ".xml", ".lock", ".properties", ".java", ".ini", ".gitignore"}
BINARY_ASSET_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}
SECRET_FILE = re.compile(r"(?:^\.env(?:\.|$)|(?:credentials|secrets|storage[-_]?state|session[-_]?state)\.)", re.I)
SECRET_PATTERNS = {
    "private-key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "AWS access-key form": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GitHub token form": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b"),
    "OpenAI key form": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}\b"),
}


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False


def source_files(include_subtitles: bool):
    candidates: set[Path] = set()
    for name in TOP_LEVEL_FILES:
        path = WORK_ROOT / name
        if path.is_file():
            candidates.add(path)
    for name in VIDEO_FILES:
        path = VIDEO_ROOT / name
        if path.is_file():
            candidates.add(path)
    for folder in SOURCE_FOLDERS:
        start = VIDEO_ROOT / folder
        if not start.is_dir():
            continue
        for current, directories, files in os.walk(start, followlinks=False):
            directories[:] = [name for name in directories if name.casefold() not in EXCLUDED_DIRECTORIES
                               and not (Path(current) / name).is_symlink()]
            for name in files:
                path = Path(current) / name
                # Only small, textual verification summaries belong in the source package.
                if folder == "qa" and path.suffix.casefold() not in {".md", ".json"}:
                    continue
                if path.is_symlink() or not inside(path, WORK_ROOT) or SECRET_FILE.search(name):
                    continue
                suffix = path.suffix.casefold()
                is_text = suffix in TEXT_EXTENSIONS or name == ".gitignore"
                is_asset = folder in {"assets", "compositions"} and suffix in BINARY_ASSET_EXTENSIONS
                if (is_text or is_asset) and (include_subtitles or suffix not in {".srt", ".vtt"}):
                    candidates.add(path)
    # Include selected evidence summaries, never full reports, requests, traces or recordings.
    for lab in ("distributed", "mainframe"):
        summary = VIDEO_ROOT / "lab" / lab / "evidence" / "VERIFICATION.md"
        if summary.is_file():
            candidates.add(summary)
    if include_subtitles:
        for folder in sorted((VIDEO_ROOT / "audio").glob("[0-9][0-9]")):
            if folder.name not in {f"{number:02}" for number in range(1, 13)} or folder.is_symlink():
                continue
            for name in ("subtitles.srt", "subtitles.vtt", "timeline.json"):
                path = folder / name
                if path.is_file():
                    candidates.add(path)
    # Calibration compositions are production diagnostics, not delivered source lessons.
    return sorted((path for path in candidates
                   if not any(part.startswith(("00-", "98-")) for part in path.relative_to(WORK_ROOT).parts)),
                  key=lambda path: path.relative_to(WORK_ROOT).as_posix())


def build_inventory(paths: list[Path]):
    inventory = []
    for path in paths:
        if path.is_symlink() or not inside(path, WORK_ROOT):
            raise ValueError(f"Source leaves the course workspace: {path.name}")
        relative_path = path.relative_to(WORK_ROOT).as_posix()
        if path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError(f"Unexpected source file larger than 5 MiB: {relative_path}")
        content = path.read_bytes()
        if path.suffix.casefold() in TEXT_EXTENSIONS or path.name == ".gitignore":
            decoded = content.decode("utf-8-sig")
            for kind, pattern in SECRET_PATTERNS.items():
                if pattern.search(decoded):
                    # Do not print the matching secret or surrounding text.
                    raise ValueError(f"Review required: {kind} detected in {relative_path}")
        inventory.append({"path": relative_path, "bytes": len(content),
                          "sha256": hashlib.sha256(content).hexdigest()})
    required = {"videos/lab/distributed/package-lock.json", "videos/lab/distributed/start-lab.mjs",
                "videos/lab/mainframe/adapter.py", "videos/lab/mainframe/requirements.txt",
                "videos/lab/mainframe/requirements-browser.txt", "videos/lab/mainframe/java/pom.xml",
                "videos/scripts/episodes.json", "02-PROMPTS-COPIAR-PEGAR.md"}
    missing = required - {entry["path"] for entry in inventory}
    if missing:
        raise ValueError("Required course sources are missing: " + ", ".join(sorted(missing)))
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--create", action="store_true", help="Actually write the source-only ZIP")
    action.add_argument("--dry-run", action="store_true", help="Inventory only; the default")
    parser.add_argument("--without-subtitles", action="store_true")
    parser.add_argument("--output", type=Path, default=VIDEO_ROOT / "delivery" / "Playwright-IA-sources.zip")
    parser.add_argument("--overwrite", action="store_true", help="Permit replacing this exact output ZIP")
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.suffix.casefold() != ".zip" or not inside(output, WORK_ROOT):
        raise ValueError("Output must be a .zip path inside this course's work folder.")
    paths = source_files(not args.without_subtitles)
    inventory = build_inventory(paths)
    summary = {"mode": "create" if args.create else "dry-run", "files": len(inventory),
               "sourceBytes": sum(entry["bytes"] for entry in inventory), "output": str(output),
               "containsInstalledDependencies": False, "containsModelWeights": False,
               "containsVideoAudioOrTraces": False,
               "containsGeneratedPlayableLibrary": False,
               "subtitlesIncluded": not args.without_subtitles,
               "secretPatternChecks": "passed; not a guarantee against every possible secret format"}
    if not args.create:
        print(json.dumps(summary, indent=2))
        return 0
    if output.exists() and not args.overwrite:
        raise FileExistsError("Output already exists; use a new name or explicit --overwrite.")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".building")
    if temporary.exists():
        raise FileExistsError("A prior .building file exists; inspect it before retrying.")
    packaged_at = datetime.now(timezone.utc).isoformat()
    manifest = {"generatedAt": packaged_at, "packageType": "source-only", "files": inventory,
                "excluded": sorted(EXCLUDED_DIRECTORIES), "note": "Public synthetic classroom values remain in example code."}
    readme = """# Playwright + IA: paquete de fuentes

Este ZIP contiene código, guiones, prompts y documentación del curso. No incluye
videos MP4, voz WAV, trazas, modelos de IA, navegadores ni dependencias instaladas.
La instalación inicial necesita las herramientas y descargas indicadas en los README.
No es un paquete listo para ejecutarse sin conexión en un Windows recién instalado.

1. Extrae la carpeta completa y conserva su estructura.
2. Abre videos/LEEME-VIDEOS.md y los README de videos/lab/distributed y mainframe.
3. Instala las dependencias de la ruta elegida; ajusta las rutas al lugar donde extrajiste el ZIP.
4. Ejecuta las pruebas y conserva tus propios resultados.

El reproductor generado videos/index.html se excluye porque sus MP4 no están en
este paquete. Con el conjunto completo de videos puedes regenerarlo mediante
node videos/tools/build-library.mjs. El paquete de fuentes no presenta videos
ausentes como lecciones disponibles.

Los resúmenes de verificación describen ejecuciones previas en la estación de
producción. No significan que las pruebas ya hayan corrido en tu máquina.
SOURCE-MANIFEST.json contiene tamaños y SHA-256 de los archivos fuente.
Los ejemplos conservan únicamente valores públicos y sintéticos de entrenamiento.
"""
    with zipfile.ZipFile(temporary, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr(f"{PREFIX}/README-SOURCES.md", readme)
        archive.writestr(f"{PREFIX}/SOURCE-MANIFEST.json", json.dumps(manifest, indent=2))
        for path, record in zip(paths, inventory, strict=True):
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != record["sha256"]:
                raise RuntimeError(f"Source changed during packaging: {record['path']}. Re-run after editing completes.")
            archive.writestr(f"{PREFIX}/{record['path']}", content)
    with zipfile.ZipFile(temporary) as archive:
        damaged = archive.testzip()
        if damaged:
            raise RuntimeError(f"ZIP integrity check failed for {damaged}")
    # Both paths were resolved and verified within the explicitly requested work folder.
    os.replace(temporary, output)
    summary.update(zipBytes=output.stat().st_size, zipSha256=hashlib.sha256(output.read_bytes()).hexdigest(), integrity="passed")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Packaging stopped: {error}", file=sys.stderr)
        sys.exit(1)
