"""Finalize course QA only after all twelve current exports and reviews pass.

Default --dry-run reads evidence without writing. --create atomically publishes
qa/VIDEO-REVIEW.md and qa/final-validation.json after all gates pass.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("complete_course", ROOT / "tools/package-full-course.py")
course = importlib.util.module_from_spec(spec)
spec.loader.exec_module(course)
IDS = course.IDS
LIMITS = [
    "Revisión visual por un agente de 12 cuadros muestreados por video, uno en el punto medio de cada escena; no reproducción visual completa.",
    "No se realizó escucha humana completa ni reconocimiento automático de la narración. Los controles de audio son técnicos.",
    "El muestreo no certifica todas las transiciones, continuidad de animaciones o sincronización de subtítulos entre muestras.",
    "La auditoría de paleta analiza literales hex/RGB y 144 cuadros medios con umbrales explícitos de hue, saturación, valor y diferencia de canales; excluye colores casi grises o muy oscuros y no cubre todos los cuadros.",
    "Las 22 pruebas corresponden a ejecuciones locales documentadas; no equivalen a una matriz completa de navegadores o sistemas operativos.",
    "El servidor TN3270 es un simulador local con cliente IBM tnz real; no hay validación contra z/OS, CICS o DB2.",
    "La comprobación de idempotencia es secuencial; concurrencia y recuperación real siguen fuera de la cobertura ejecutada.",
    "CI alojada y ensayo completo del taller de 120 minutos: no ejecutados.",
]


class Evidence:
    def __init__(self):
        self.hashes = {}

    def read(self, path):
        path = Path(path)
        if path.is_symlink() or not course.sources.inside(path, ROOT.parent.resolve()):
            raise ValueError("Evidence must stay within the course workspace.")
        content = path.read_bytes()
        relative = Path(os.path.relpath(path, ROOT)).as_posix()
        digest = hashlib.sha256(content).hexdigest()
        if relative in self.hashes and self.hashes[relative] != digest:
            raise ValueError(f"Evidence changed during validation: {relative}")
        self.hashes[relative] = digest
        return content

    def json(self, path):
        return json.loads(self.read(path).decode("utf-8-sig"))

    def track(self, path):
        path = Path(path)
        if path.is_symlink() or not course.sources.inside(path, ROOT.parent.resolve()):
            raise ValueError("Evidence must stay within the course workspace.")
        relative, digest = Path(os.path.relpath(path, ROOT)).as_posix(), course.digest_file(path)
        if relative in self.hashes and self.hashes[relative] != digest:
            raise ValueError(f"Evidence changed during validation: {relative}")
        self.hashes[relative] = digest
        return digest

    def unchanged(self):
        for relative, expected in self.hashes.items():
            path = ROOT / relative
            if not path.is_file() or course.digest_file(path) != expected:
                raise ValueError(f"Evidence changed before finalization: {relative}; retry after production finishes.")


def audio_evidence(evidence):
    report = evidence.json(ROOT / "qa/audio-validation.json")
    rows = report.get("episodes", [])
    if (report.get("requestedEpisodes") != 12 or report.get("validatedEpisodes") != 12
            or report.get("errors") != [] or [row.get("episode") for row in rows] != IDS
            or any(row.get("valid") is not True or row.get("scenes") != 12 for row in rows)):
        raise ValueError("Audio QA must contain exactly 12 passing episodes and no errors.")
    for row in rows:
        if not (math.isfinite(row.get("seconds", float("nan"))) and 360 <= row["seconds"] <= 480
                and .01 < row.get("peak", 0) < 1 and row.get("rms", 0) > .001):
            raise ValueError(f"Audio QA has invalid duration or signal for {row.get('episode')}.")
    return report


def test_evidence(evidence):
    distributed = evidence.json(ROOT / "lab/distributed/evidence/results.json")
    stats = distributed.get("stats", {})
    if (stats.get("expected") != 10 or any(stats.get(key) != 0 for key in ("unexpected", "skipped", "flaky"))
            or distributed.get("errors") != []):
        raise ValueError("Distributed regression evidence must show 10 expected passes and no failures, skips or flaky cases.")
    mainframe = evidence.json(ROOT / "lab/mainframe/evidence/verification.json")
    suites = mainframe.get("suites", [])
    if mainframe.get("totalTests") != 12 or len(suites) != 5 or len({row.get("report") for row in suites}) != 5:
        raise ValueError("Mainframe evidence must contain the five non-overlapping suites totaling 12 tests.")
    totals = {key: 0 for key in ("tests", "failures", "errors", "skipped")}
    seen = set()
    for row in suites:
        filename = row.get("report", "")
        if Path(filename).name != filename or not filename.endswith(".xml"):
            raise ValueError("Unsafe test-report filename in verification.json.")
        document = ET.fromstring(evidence.read(ROOT / "lab/mainframe/evidence" / filename))
        leaves = [element for element in document.iter("testsuite") if not list(element.iterfind("testsuite"))]
        actual = {key: sum(int(element.get(key, "0")) for element in leaves) for key in totals}
        if any(actual[key] != row.get(key) for key in totals):
            raise ValueError(f"JUnit XML totals differ from verification.json: {filename}")
        cases = list(document.iter("testcase"))
        if len(cases) != actual["tests"]:
            raise ValueError(f"JUnit testcase count differs from its totals: {filename}")
        for case in cases:
            identity = (case.get("classname"), case.get("name"))
            if identity in seen:
                raise ValueError("A test case is counted more than once across the primary mainframe suites.")
            seen.add(identity)
            if any(case.find(tag) is not None for tag in ("failure", "error", "skipped")):
                raise ValueError(f"Non-passing testcase in {filename}")
        for key in totals:
            totals[key] += actual[key]
    if totals != {"tests": 12, "failures": 0, "errors": 0, "skipped": 0}:
        raise ValueError("Mainframe suites do not prove twelve distinct passing tests.")
    return {"passed": 22, "failed": 0, "skipped": 0,
            "distributed": {"passed": 10, "source": "lab/distributed/evidence/results.json", "stats": stats},
            "mainframe": {"passed": 12, "source": "lab/mainframe/evidence/verification.json", "suites": suites},
            "scope": "Recorded local execution; repeated contract reruns are not counted twice."}


def palette_evidence(evidence, episodes, progress):
    path = ROOT / "qa/blue-palette-validation.json"
    report = evidence.json(path)
    if (report.get("mode") != "sources-and-current-sampled-frames" or report.get("passed") is not True
            or report.get("finalCoursePaletteAuditPassed") is not True or report.get("errors") != []):
        raise ValueError("Palette audit must be a final PASS; sources-only, incomplete and failed reports are not accepted.")
    auditor_path = ROOT / "tools/audit_course_palette.py"
    if report.get("auditorSha256") != evidence.track(auditor_path):
        raise ValueError("Palette report was generated by a different auditor version; run the final audit again.")
    spec = importlib.util.spec_from_file_location("palette_final_gate", auditor_path)
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    criteria = report.get("criteria", {})
    expected = {"hueDegreesInclusive": [auditor.HUE_MIN, auditor.HUE_MAX],
                "minimumHSVSaturation": auditor.SATURATION_MIN, "minimumValueByte": auditor.VALUE_MIN,
                "minimumRGBChromaByte": auditor.CHROMA_MIN, "huePredicate": "G >= R and G >= B",
                "componentConnectivity": 8, "minimumRegionAreaPixels": auditor.MIN_REGION_AREA,
                "allowedSignificantGreenRegions": 0, "rawQualifyingPixelsAreReportedNotHidden": True}
    if any(criteria.get(key) != value for key, value in expected.items()):
        raise ValueError("Palette report thresholds differ from the current audit criteria.")
    hashes = report.get("inputSha256", {})
    if not hashes:
        raise ValueError("Palette report lacks source and media hashes.")
    for relative, expected_hash in hashes.items():
        current = ROOT.parent / relative
        if evidence.track(current) != expected_hash:
            raise ValueError(f"Palette report is stale: {relative}")
    paths, missing = auditor.source_paths(episodes)
    source_rows = report.get("sources", {}).get("files", [])
    expected_paths = {auditor.relative(source) for source in paths}
    if (missing or len(source_rows) != len(expected_paths)
            or {row.get("file") for row in source_rows} != expected_paths
            or report.get("sources", {}).get("filesAudited") != len(expected_paths)
            or report.get("sources", {}).get("greenTealLiteralCount") != 0):
        raise ValueError("Palette report does not cover every current visual source with zero detected green/teal literals.")
    for row in source_rows:
        if (row.get("sha256") != hashes.get(row.get("file")) or row.get("greenTealLiteralCount") != 0
                or row.get("findings") != [] or row.get("unsupportedRGB") != []):
            raise ValueError("Palette source row has findings, unsupported RGB or inconsistent hashes.")
    sampled = report.get("sampledFrames", {})
    frames = sampled.get("frames", [])
    expected_ids = [f"{eid}-{number:02}" for eid in IDS for number in range(1, 13)]
    if (sampled.get("requiredForFinal") != 144 or sampled.get("acceptedCurrentFrames") != 144
            or sampled.get("pixelsAudited") != 144 * 1920 * 1080 or sampled.get("significantGreenRegions") != 0
            or sampled.get("greenTealPixels") != sum(frame.get("greenTealPixels", -1) for frame in frames)
            or sampled.get("framesWithQualifyingPixels") != sum(frame.get("greenTealPixels", 0) > 0 for frame in frames)
            or sampled.get("largestGreenComponentPixels") != max((frame.get("largestGreenComponentPixels", -1) for frame in frames), default=-1)
            or [frame.get("sceneId") for frame in frames] != expected_ids):
        raise ValueError("Final palette audit must cover 144 current Full HD frames, report all qualifying pixels and find zero regions meeting the spatial criterion.")
    for frame in frames:
        eid, sid = frame["sceneId"].split("-", 1)
        checkpoint = progress.get("episodes", {}).get(eid, {})
        expected_file = f"videos/qa/export-review/{eid}/{eid}-{sid}-midpoint.png"
        if (frame.get("episode") != eid or frame.get("file") != expected_file
                or frame.get("sha256") != hashes.get(expected_file)
                or frame.get("mp4Sha256") != checkpoint.get("artifact", {}).get("sha256")
                or frame.get("productionInputHash") != checkpoint.get("inputHash")
                or frame.get("significantGreenRegions") != 0 or frame.get("pixels") != 1920 * 1080
                or not 0 <= frame.get("greenTealPixels", -1) <= frame["pixels"]
                or not 0 <= frame.get("largestGreenComponentPixels", -1) < auditor.MIN_REGION_AREA
                or (frame.get("width"), frame.get("height")) != (1920, 1080)):
            raise ValueError(f"Palette frame is stale, incomplete or contains a qualifying green region: {frame.get('sceneId')}")
        components = frame.get("greenTealComponents", [])
        if (sum(component.get("pixels", -1) for component in components) != frame["greenTealPixels"]
                or any(not 0 < component.get("pixels", -1) < auditor.MIN_REGION_AREA for component in components)
                or max((component["pixels"] for component in components), default=0) != frame["largestGreenComponentPixels"]):
            raise ValueError(f"Palette component accounting is inconsistent: {frame['sceneId']}")
    return {"status": "passed_for_active_sources_and_sampled_frames", "source": "qa/blue-palette-validation.json",
            "sha256": evidence.track(path), "generatedAtUtc": report["generatedAtUtc"],
            "sourceFilesAudited": len(source_rows), "greenTealLiterals": 0, "currentMP4s": 12,
            "currentFramesAudited": 144, "pixelsAudited": sampled["pixelsAudited"],
            "greenTealPixels": sampled["greenTealPixels"], "greenTealPercent": sampled["greenTealPercent"],
            "significantGreenRegions": 0, "largestGreenComponentPixels": sampled["largestGreenComponentPixels"],
            "criteria": criteria, "scope": report["scope"]}


def visual_evidence(episode, timeline, video_hash, evidence):
    eid = episode["id"]
    folder = ROOT / "qa/export-review" / eid
    observations = evidence.json(folder / "observations.json")
    manifest = evidence.json(folder / "manifest.json")
    expected_ids = [f"{eid}-{number:02}" for number in range(1, 13)]
    if (observations.get("episode") != eid or observations.get("mp4Sha256") != video_hash
            or observations.get("visualReviewPerformedByAgent") is not True
            or observations.get("reviewedSceneIds") != expected_ids or observations.get("issues") != []):
        raise ValueError(f"Episode {eid}: visual observations must review its current MP4, exactly 12 scenes, and have issues=[].")
    if not observations.get("reviewMethod") or not observations.get("reviewedAtUtc"):
        raise ValueError(f"Episode {eid}: visual review method or date is missing.")
    if (manifest.get("episode") != eid or manifest.get("input", {}).get("sha256") != video_hash
            or manifest.get("timeline", {}).get("sha256") != evidence.track(ROOT / "audio" / eid / "timeline.json")):
        raise ValueError(f"Episode {eid}: visual sample manifest is stale.")
    frames = manifest.get("frames", [])
    if [frame.get("sceneId") for frame in frames] != expected_ids:
        raise ValueError(f"Episode {eid}: missing one or more midpoint frame samples.")
    for frame, scene in zip(frames, timeline["scenes"], strict=True):
        filename = frame.get("file", "")
        if Path(filename).name != filename or not filename.endswith(".png"):
            raise ValueError(f"Episode {eid}: unsafe frame filename.")
        if ((frame.get("width"), frame.get("height")) != (1920, 1080)
                or abs(frame.get("sampleSeconds", -1) - (scene["start"] + scene["duration"] / 2)) > .001
                or frame.get("sha256") != evidence.track(folder / filename)):
            raise ValueError(f"Episode {eid}: frame {frame.get('sceneId')} has stale timing or pixels.")
    for sheet in manifest.get("contactSheets", []):
        filename = sheet.get("file", "")
        if Path(filename).name != filename or sheet.get("sha256") != evidence.track(folder / filename):
            raise ValueError(f"Episode {eid}: contact-sheet hash mismatch.")
    return {"status": "passed_for_sampled_frames", "visualReviewPerformedByAgent": True,
            "reviewedSceneIds": expected_ids, "sampledFrames": 12, "issues": [],
            "reviewMethod": observations["reviewMethod"], "reviewedAtUtc": observations["reviewedAtUtc"],
            "observations": f"qa/export-review/{eid}/observations.json", "mp4Sha256": video_hash,
            "scope": "Twelve midpoint frames; no claim of complete playback or human listening."}


def collect(ffprobe):
    evidence, errors, videos = Evidence(), [], []
    evidence.track(ROOT / "scripts/episodes.json")
    episodes = course.expected_episodes()
    progress = evidence.json(ROOT / "production-progress.json")
    audio, tests, palette = None, None, None
    for label, loader in (("audio", audio_evidence), ("tests", test_evidence)):
        try:
            result = loader(evidence)
            if label == "audio": audio = result
            else: tests = result
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
            errors.append(f"{label}: {error}")
    try:
        palette = palette_evidence(evidence, episodes, progress)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        errors.append(f"palette: {error}")
    audio_by_id = {row["episode"]: row for row in (audio or {}).get("episodes", [])}
    for episode in episodes:
        eid = episode["id"]
        path = ROOT / "renders" / f"{eid}-{episode['slug']}.mp4"
        try:
            timeline, _ = course.timeline_and_subtitles(episode)
            record = progress.get("episodes", {}).get(eid, {})
            for relative in record.get("inputFiles", {}):
                evidence.track(ROOT / relative)
            input_hash, video_hash = course.verify_provenance(episode, path, progress)
            evidence.track(path)
            technical = evidence.json(ROOT / "qa/episodes" / eid / "validation.json")
            if technical.get("artifact", {}).get("audioDecode", {}).get("ok") is not True:
                raise ValueError(f"Episode {eid}: full audio decode is not confirmed by the export validation.")
            facts = course.inspect_video(path, timeline["duration"], ffprobe, None, decode=False)
            facts["audioDecode"] = {"status": "passed", "method": "Recorded full decode, bound to the verified current MP4 SHA-256",
                                    "source": f"qa/episodes/{eid}/validation.json"}
            voice = audio_by_id.get(eid, {})
            if (voice.get("voice") != timeline.get("voice") or voice.get("rate") != timeline.get("rate")
                    or abs(voice.get("seconds", 0) - timeline["duration"]) > .001
                    or voice.get("captions") != len(timeline["captions"])):
                raise ValueError(f"Episode {eid}: audio QA does not match current narration metadata.")
            visual = visual_evidence(episode, timeline, video_hash, evidence)
            videos.append({"episode": eid, "title": episode["title"], "file": path.relative_to(ROOT).as_posix(),
                           "sha256": video_hash, "inputHash": input_hash, **facts,
                           "voice": {"engine": timeline.get("engine"), "name": timeline.get("voice"), "rate": timeline.get("rate"),
                                     "language": "English", "synthetic": True},
                           "audioQA": voice, "visualReview": visual, "captions": len(timeline["captions"])})
        except (OSError, ValueError, KeyError, TypeError, IndexError, course.subprocess.TimeoutExpired) as error:
            message = str(error)
            errors.append(message if message.startswith(f"Episode {eid}:") else f"Episode {eid}: {message}")
    try:
        evidence.unchanged()
    except ValueError as error:
        errors.append(str(error))
    ready = len(videos) == 12 and not errors and audio is not None and tests is not None and palette is not None
    report = {"schemaVersion": 1, "status": "verified_with_stated_limits" if ready else "blocked",
              "generatedAtUtc": datetime.now(timezone.utc).isoformat(), "ready": ready,
              "expectedEpisodes": 12, "verifiedEpisodes": len(videos), "videos": videos,
              "totalVideoSeconds": sum(video["seconds"] for video in videos),
              "reviewedMidpointFrames": sum(video["visualReview"]["sampledFrames"] for video in videos),
              "audio": audio, "tests": tests, "palette": palette, "errors": errors, "limitations": LIMITS,
              "hostedCI": "not_executed", "fullTwoHourWorkshopRehearsal": "not_executed",
              "fullHumanAudioListening": "not_performed", "evidenceSha256": evidence.hashes}
    return report, evidence


def markdown(report):
    lines = ["# Revisión final de los videos", "",
             f"Fecha UTC: {report['generatedAtUtc']}", "",
             "Los doce MP4 coinciden con sus fuentes finales y sus hashes de producción. Cada archivo contiene imagen Full HD 1920×1080, H.264 a 24 fps y voz sintética en inglés. Todos duran entre 6 y 8 minutos.", "",
             f"Duración total: {report['totalVideoSeconds'] / 60:.2f} minutos. Se revisaron visualmente por un agente {report['reviewedMidpointFrames']} cuadros, doce por episodio. Las observaciones vigentes no contienen incidencias pendientes en esas muestras.", "",
             "| Episodio | Duración | Voz | Imagen | Cuadros revisados |",
             "|---|---:|---|---|---:|"]
    for video in report["videos"]:
        seconds = video["seconds"]
        length = f"{int(seconds // 60)}:{seconds % 60:06.3f}"
        lines.append(f"| {video['episode']} · {video['title']} | {length} | {video['voice']['name']} | 1080p · 24 fps | 12 |")
    lines.extend(["", "## Evidencia técnica", "",
        f"La auditoría de paleta vigente revisó {report['palette']['sourceFilesAudited']} fuentes visuales y los 144 cuadros medios ({report['palette']['pixelsAudited']:,} píxeles). Encontró cero literales verdes/teal y cero regiones de al menos 16 píxeles conectados en ocho direcciones. Conserva el conteo de {report['palette']['greenTealPixels']:,} píxeles candidatos, agrupados en componentes de hasta {report['palette']['largestGreenComponentPixels']} píxeles: no afirma cero píxeles verdes. El detector usa hue exacto 60–180°, saturación HSV ≥20%, valor ≥20/255 y diferencia de canales ≥16/255. La investigación de 144 pares nativos/comprimidos identifica pequeñas franjas de rasterizado y compresión. El resultado se limita a esas fuentes y cuadros muestreados; no certifica todos los cuadros ni todos los estados de la interfaz. Consulta [blue-palette-validation.json](blue-palette-validation.json) y [palette-mask-investigation.json](palette-mask-investigation.json) para hashes, conteos y criterios.", "",
        "Las doce narraciones pasan los controles registrados de duración, formato, señal finita, límites de pico y subtítulos. La decodificación completa de la pista de audio de cada MP4 está confirmada por el informe de exportación y ligada al SHA-256 vigente. Esto no equivale a una evaluación humana de pronunciación o claridad.", "",
        "Las pruebas locales suman **22 casos aprobados, cero fallos y cero omitidos**: 10 regresiones TypeScript del laboratorio distribuido y 12 casos entre TN3270, Python, Java y TypeScript. Se contrastaron los cinco XML primarios con el resumen del laboratorio mainframe; las repeticiones de casos no se suman como cobertura adicional.", "",
        "Los SHA-256, rutas de resultados y observaciones por episodio están en [final-validation.json](final-validation.json). Las pruebas son ejecuciones previas verificadas, no se vuelven a ejecutar al generar este informe.", "",
        "## Alcance y pendientes", ""])
    lines.extend(f"- {limit}" for limit in report["limitations"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dry-run", action="store_true", help="Read-only validation; default")
    action.add_argument("--create", action="store_true", help="Publish the final JSON and Markdown reports after all gates pass")
    parser.add_argument("--ffprobe", help="FFprobe executable path")
    args = parser.parse_args()
    report, evidence = collect(course.executable("ffprobe", args.ffprobe))
    summary = {"mode": "create" if args.create else "dry-run", "ready": report["ready"],
               "verifiedEpisodes": report["verifiedEpisodes"], "expectedEpisodes": 12,
               "audioEpisodesPassed": (report["audio"] or {}).get("validatedEpisodes", 0),
               "finalPalettePassed": report["palette"] is not None,
               "testsPassed": (report["tests"] or {}).get("passed", 0), "errors": report["errors"], "written": False}
    if report["ready"] and args.create:
        text = markdown(report).encode("utf-8")
        report["reviewMarkdownSha256"] = hashlib.sha256(text).hexdigest()
        json_payload = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
        targets = [(ROOT / "qa/VIDEO-REVIEW.md", text), (ROOT / "qa/final-validation.json", json_payload)]
        staged = []
        for target, payload in targets:
            if target.is_symlink() or not course.sources.inside(target, ROOT.resolve()):
                raise ValueError("Final report output must stay inside this QA folder.")
            temporary = target.with_name(target.name + ".building")
            with temporary.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if temporary.read_bytes() != payload:
                raise RuntimeError("Staged final report did not preserve its expected content.")
            staged.append((temporary, target))
        evidence.unchanged()
        # Each file is atomic. JSON is promoted last as the completion record and
        # includes the Markdown hash, so consumers can detect a mismatched pair.
        for temporary, target in staged:
            os.replace(temporary, target)
        summary.update(written=True, outputs=[str(target) for _, target in staged])
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0 if report["ready"] else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError, ET.ParseError, course.subprocess.TimeoutExpired) as error:
        print(f"Final QA stopped: {error}", file=sys.stderr)
        sys.exit(1)
