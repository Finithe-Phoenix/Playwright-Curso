"""Audit active visual sources and current MP4 midpoint frames for green/teal.

Only qa/blue-palette-validation.json is written. Images, narration, generators,
compositions, checkpoints and videos are never edited. Use --sources-only during
production; the default final audit requires 144 current frames from 12 MP4s.
"""
from __future__ import annotations

import argparse
import colorsys
from fractions import Fraction
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent
REPORT = ROOT / "qa/blue-palette-validation.json"
HUE_MIN, HUE_MAX = 60.0, 180.0
SATURATION_MIN = .20
VALUE_MIN = 20
CHROMA_MIN = 16
MIN_REGION_AREA = 16
HEX = re.compile(r"#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{4}|[0-9a-f]{3})(?![0-9a-z_-])", re.I)
RGB = re.compile(r"\brgba?\(\s*([^()]*)\)", re.I)
IGNORED = {"assets", "node_modules", ".venv", ".tools", ".git", "historical", "history", "archive", "archives"}


def load_course():
    spec = importlib.util.spec_from_file_location("complete_course_palette", ROOT / "tools/package-full-course.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def relative(path):
    return Path(path).relative_to(WORK).as_posix()


def secure_file(path):
    path = Path(path)
    path.resolve().relative_to(WORK.resolve())
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Missing or symlinked active file: {relative(path)}")
    return path


def load_json(path, hashes):
    path = secure_file(path)
    content = path.read_bytes()
    hashes[path] = hashlib.sha256(content).hexdigest()
    return json.loads(content.decode("utf-8-sig"))


def green_rgba(rgba):
    red, green, blue, alpha = rgba
    hue, saturation, value_byte = colorsys.rgb_to_hsv(red, green, blue)
    value = value_byte / 255
    hue *= 360
    selected = (alpha > 0 and HUE_MIN <= hue <= HUE_MAX and saturation >= SATURATION_MIN
                and value_byte >= VALUE_MIN and max(red, green, blue) - min(red, green, blue) >= CHROMA_MIN)
    return selected, {"hueDegrees": round(hue, 3), "saturation": round(saturation, 6),
                      "value": round(value, 6), "alpha": round(alpha, 6)}


def decode_hex(token):
    digits = token[1:]
    if len(digits) in {3, 4}:
        digits = "".join(character * 2 for character in digits)
    values = [int(digits[index:index + 2], 16) for index in range(0, len(digits), 2)]
    return (*values[:3], values[3] / 255 if len(values) == 4 else 1.0)


def decode_rgb(body):
    # Covers comma notation, CSS space/slash notation and percentages. Values
    # using var()/calc() are not literals and are outside this lexical audit.
    parts = re.split(r"[\s,/]+", body.strip())
    if len(parts) not in {3, 4}:
        raise ValueError("Expected three RGB components and an optional alpha.")
    channels = [float(value[:-1]) * 255 / 100 if value.endswith("%") else float(value) for value in parts[:3]]
    alpha = 1.0
    if len(parts) == 4:
        alpha = float(parts[3][:-1]) / 100 if parts[3].endswith("%") else float(parts[3])
    if not all(math.isfinite(value) for value in [*channels, alpha]):
        raise ValueError("RGB components must be finite.")
    return (*[min(255.0, max(0.0, value)) for value in channels], min(1.0, max(0.0, alpha)))


def audit_source(path, hashes):
    content = secure_file(path).read_bytes()
    checksum = hashlib.sha256(content).hexdigest()
    hashes[path] = checksum
    text = content.decode("utf-8-sig")
    tokens = [(match.start(), match.group(), decode_hex(match.group())) for match in HEX.finditer(text)]
    unsupported = []
    for match in RGB.finditer(text):
        try:
            tokens.append((match.start(), match.group(), decode_rgb(match.group(1))))
        except ValueError:
            unsupported.append({"line": text.count("\n", 0, match.start()) + 1, "literal": match.group()})
    green, palette = [], {}
    for start, token, rgba in sorted(tokens):
        selected, hsv = green_rgba(rgba)
        normalized = "#" + "".join(f"{round(value):02X}" for value in rgba[:3])
        palette[(normalized, rgba[3])] = {"rgb": normalized, **hsv}
        if selected:
            green.append({"line": text.count("\n", 0, start) + 1,
                          "column": start - text.rfind("\n", 0, start), "literal": token,
                          "rgb": normalized, **hsv})
    return {"file": relative(path), "sha256": checksum, "bytes": len(content),
            "literalCount": len(tokens), "uniqueColors": list(palette.values()),
            "greenTealLiteralCount": len(green), "findings": green, "unsupportedRGB": unsupported}


def source_paths(episodes):
    paths = [ROOT / "tools/build_compositions.py", ROOT / "tools/build-library.mjs",
             ROOT / "tools/build-course-guide.mjs", WORK / "CURSO-PLAYWRIGHT-IA.html",
             ROOT / "index.html", ROOT / "lab/distributed/web.html"]
    missing = []
    for episode in episodes:
        project = ROOT / "compositions" / f"{episode['id']}-{episode['slug']}"
        for expected in [project / "index.html", *[project / "compositions" / f"s{episode['id']}{number:02}.html" for number in range(1, 13)]]:
            if not expected.is_file():
                missing.append(f"Missing active composition HTML: {relative(expected)}")
        if project.is_dir():
            for current, directories, files in os.walk(project, followlinks=False):
                directories[:] = [name for name in directories if name.casefold() not in IGNORED
                                   and not (Path(current) / name).is_symlink()]
                paths.extend(Path(current) / name for name in files if name.lower().endswith(".html"))
    return sorted(set(paths), key=relative), missing


def connected_components(mask):
    """Eight-connected components by horizontal runs; efficient for solid fills too."""
    data, width, height = mask.tobytes(), mask.width, mask.height
    parents, sizes, boxes = [], [], []

    def find(label):
        while parents[label] != label:
            parents[label] = parents[parents[label]]
            label = parents[label]
        return label

    def union(left, right):
        left, right = find(left), find(right)
        if left == right:
            return
        parents[right] = left
        sizes[left] += sizes[right]
        a, b = boxes[left], boxes[right]
        boxes[left] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]

    previous = []
    for y in range(height):
        row_start, row_end, current, cursor = y * width, (y + 1) * width, [], y * width
        previous_start = 0
        while (start := data.find(b"\xff", cursor, row_end)) >= 0:
            end = data.find(b"\x00", start, row_end)
            if end < 0:
                end = row_end
            x0, x1, label = start - row_start, end - row_start, len(parents)
            parents.append(label); sizes.append(x1 - x0); boxes.append([x0, y, x1, y + 1])
            while previous_start < len(previous) and previous[previous_start][1] < x0:
                previous_start += 1
            index = previous_start
            while index < len(previous) and previous[index][0] <= x1:
                union(label, previous[index][2])
                index += 1
            current.append((x0, x1, label))
            cursor = end
        previous = current
    return sorted(({"pixels": sizes[label], "boundingBox": boxes[label]} for label in range(len(parents))
                   if find(label) == label), key=lambda item: (-item["pixels"], item["boundingBox"]))


def scan_frame(path):
    from PIL import Image, ImageChops

    with Image.open(path) as original:
        if original.size != (1920, 1080):
            raise ValueError(f"Expected native 1920x1080 frame: {path.name}")
        rgb = original.convert("RGB")
        red, green, blue = rgb.split()
        maximum = ImageChops.lighter(red, ImageChops.lighter(green, blue))
        minimum = ImageChops.darker(red, ImageChops.darker(green, blue))
        chroma = ImageChops.subtract(maximum, minimum)
        # For non-gray RGB, hue is in [60,180] iff green is a maximum channel.
        # This is exact; quantized HSV bins admitted hue values above 180 degrees.
        if (HUE_MIN, HUE_MAX) != (60.0, 180.0):
            raise ValueError("The exact RGB-sector predicate requires hue bounds 60 and 180.")
        hmask = ImageChops.subtract(maximum, green).point([255 if number == 0 else 0 for number in range(256)])
        required_chroma = maximum.point([math.ceil(number * Fraction(str(SATURATION_MIN))) for number in range(256)])
        smask = ImageChops.subtract(required_chroma, chroma).point([255 if number == 0 else 0 for number in range(256)])
        vmask = maximum.point([255 if number >= VALUE_MIN else 0 for number in range(256)])
        cmask = chroma.point([255 if number >= CHROMA_MIN else 0 for number in range(256)])
        mask = ImageChops.multiply(ImageChops.multiply(hmask, smask), ImageChops.multiply(vmask, cmask))
        count = mask.histogram()[255]
        pixels = rgb.width * rgb.height
        bounds = mask.getbbox()
        components = connected_components(mask)
        significant = [item for item in components if item["pixels"] >= MIN_REGION_AREA]
        return {"width": rgb.width, "height": rgb.height, "pixels": pixels,
                "greenTealPixels": count, "greenTealPercent": round(count / pixels * 100, 9),
                "greenTealBoundingBox": list(bounds) if bounds else None,
                "greenTealComponents": components, "significantGreenRegions": len(significant),
                "subthresholdGreenComponents": len(components) - len(significant),
                "subthresholdGreenPixels": sum(item["pixels"] for item in components if item["pixels"] < MIN_REGION_AREA),
                "largestGreenComponentPixels": max((item["pixels"] for item in components), default=0),
                "method": "Exact RGB hue sector and rational saturation; Pillow channel masks; eight-connected component area; no image writes"}


def audit_frames(episodes, course, hashes):
    results, errors = [], []
    progress = load_json(ROOT / "production-progress.json", hashes)
    for episode in episodes:
        eid = episode["id"]
        folder = ROOT / "qa/export-review" / eid
        try:
            mp4 = secure_file(ROOT / "renders" / f"{eid}-{episode['slug']}.mp4")
            input_hash, video_hash = course.verify_provenance(episode, mp4, progress)
            hashes[mp4] = video_hash
            checkpoint = progress["episodes"][eid]
            for name, expected in checkpoint["inputFiles"].items():
                path = secure_file(ROOT / name)
                if sha(path) != expected:
                    raise ValueError(f"Episode {eid}: checkpoint input changed: {name}")
                hashes[path] = expected
            load_json(ROOT / "qa/episodes" / eid / "validation.json", hashes)
            timeline = load_json(ROOT / "audio" / eid / "timeline.json", hashes)
            manifest = load_json(folder / "manifest.json", hashes)
            if (manifest.get("episode") != eid or manifest.get("input", {}).get("sha256") != video_hash
                    or manifest.get("timeline", {}).get("sha256") != hashes[ROOT / "audio" / eid / "timeline.json"]):
                raise ValueError(f"Episode {eid}: sample manifest is not bound to the current MP4 and timeline.")
            expected_ids = [f"{eid}-{number:02}" for number in range(1, 13)]
            observations = load_json(folder / "observations.json", hashes)
            if (observations.get("mp4Sha256") != video_hash or observations.get("visualReviewPerformedByAgent") is not True
                    or observations.get("reviewedSceneIds") != expected_ids or observations.get("issues") != []):
                raise ValueError(f"Episode {eid}: a current issue-free visual review of all twelve samples is required.")
            frames = manifest.get("frames", [])
            if [item.get("sceneId") for item in frames] != expected_ids or len(timeline.get("scenes", [])) != 12:
                raise ValueError(f"Episode {eid}: exactly twelve consecutive midpoint samples are required.")
            if {path.name for path in folder.glob("*-midpoint.png")} != {f"{sid}-midpoint.png" for sid in expected_ids}:
                raise ValueError(f"Episode {eid}: midpoint file set differs from the required twelve scenes.")
            staged = []
            for frame, scene in zip(frames, timeline["scenes"], strict=True):
                sid = frame["sceneId"]
                if frame.get("file") != f"{sid}-midpoint.png" or scene.get("id") != sid:
                    raise ValueError(f"Episode {eid}: frame filename or scene mismatch.")
                midpoint = scene["start"] + scene["duration"] / 2
                if abs(frame.get("sampleSeconds", -1) - midpoint) > .001:
                    raise ValueError(f"Episode {eid}: sample time is not its current scene midpoint.")
                path = secure_file(folder / frame["file"])
                checksum = sha(path)
                if checksum != frame.get("sha256"):
                    raise ValueError(f"Episode {eid}: sampled PNG differs from its manifest: {sid}")
                hashes[path] = checksum
                staged.append({"episode": eid, "sceneId": sid, "file": relative(path), "sha256": checksum,
                               "mp4Sha256": video_hash, "productionInputHash": input_hash,
                               "sampleSeconds": frame["sampleSeconds"], **scan_frame(path)})
            results.extend(staged)
            print(json.dumps({"episode": eid, "acceptedCurrentFrames": 12,
                              "greenTealPixels": sum(item["greenTealPixels"] for item in staged)}), flush=True)
        except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
            errors.append(str(error))
    return results, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources-only", action="store_true", help="Audit active source literals only; never counts as the 144-frame final audit")
    args = parser.parse_args()
    course = load_course()
    episodes = course.expected_episodes()
    hashes = {ROOT / "scripts/episodes.json": sha(ROOT / "scripts/episodes.json")}
    paths, errors = source_paths(episodes)
    files = []
    for path in paths:
        try:
            record = audit_source(path, hashes)
            if record["unsupportedRGB"]:
                errors.append(f"Unsupported RGB expression in active source: {relative(path)}")
            files.append(record)
        except (OSError, ValueError) as error:
            errors.append(str(error))
    frames = []
    if not args.sources_only:
        try:
            frames, frame_errors = audit_frames(episodes, course, hashes)
            errors.extend(frame_errors)
        except (OSError, ValueError, KeyError) as error:
            errors.append(str(error))
        if len(frames) != 144:
            errors.append(f"Final audit needs 144 current frames; accepted {len(frames)}.")
    # No acceptance based on sources or samples that changed while being audited.
    for path, expected in hashes.items():
        if not path.is_file() or sha(path) != expected:
            errors.append(f"Input changed during palette audit: {relative(path)}")
    green_literals = sum(item["greenTealLiteralCount"] for item in files)
    green_pixels = sum(item["greenTealPixels"] for item in frames)
    regions = sum(item["significantGreenRegions"] for item in frames)
    pixels = sum(item["pixels"] for item in frames)
    detected = green_literals > 0 or regions > 0
    passed = not detected and not errors and (args.sources_only or len(frames) == 144)
    report = {"schemaVersion": 1, "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
              "auditorSha256": sha(Path(__file__)), "pythonVersion": sys.version.split()[0],
              "mode": "sources-only" if args.sources_only else "sources-and-current-sampled-frames",
              "passed": passed, "finalCoursePaletteAuditPassed": passed and not args.sources_only,
              "criteria": {"hueDegreesInclusive": [HUE_MIN, HUE_MAX], "minimumHSVSaturation": SATURATION_MIN,
                           "minimumValueByte": VALUE_MIN, "minimumRGBChromaByte": CHROMA_MIN,
                           "huePredicate": "G >= R and G >= B", "componentConnectivity": 8,
                           "minimumRegionAreaPixels": MIN_REGION_AREA, "allowedSignificantGreenRegions": 0,
                           "rawQualifyingPixelsAreReportedNotHidden": True, "fullyTransparentSourceColorsIgnored": True},
              "sources": {"filesAudited": len(files), "literalCount": sum(item["literalCount"] for item in files),
                          "greenTealLiteralCount": green_literals, "files": files},
              "sampledFrames": {"requiredForFinal": 144, "acceptedCurrentFrames": len(frames), "pixelsAudited": pixels,
                                "greenTealPixels": green_pixels,
                                "significantGreenRegions": regions,
                                "largestGreenComponentPixels": max((item["largestGreenComponentPixels"] for item in frames), default=0),
                                "subthresholdGreenComponents": sum(item["subthresholdGreenComponents"] for item in frames),
                                "subthresholdGreenPixels": sum(item["subthresholdGreenPixels"] for item in frames),
                                "greenTealPercent": round(green_pixels / pixels * 100, 9) if pixels else None,
                                "framesWithQualifyingPixels": sum(item["greenTealPixels"] > 0 for item in frames), "frames": frames},
              "errors": errors,
              "scope": "Active hexadecimal/RGB palette literals, current visual reviews and significant green regions in current MP4 sampled frames; raw small-component pixels remain reported. Not all video frames or UI states.",
              "limitations": ["Gray and low-saturation colors, very dark pixels and small channel differences are intentionally excluded by the reported thresholds.",
                              "Hue is tested exactly in RGB. A significant decoded-MP4 region means an eight-connected component with at least 16 qualifying pixels; smaller rasterization/compression fringes are counted but do not alone fail palette acceptance.",
                              "Source inspection is lexical: CSS hex/RGB literals and equivalent animation color literals. Named colors, computed expressions and external stylesheets are outside this check.",
                              "Only twelve midpoint frames per MP4 are examined. A pass means clean source literals, current visual review and no regions meeting the spatial criterion; it does not mean zero green-valued pixels.",
                              "Historical exports, calibrations 00/98, asset dependencies, contact sheets and earlier review snapshots are excluded from the active-source/frame selection."],
              "modifications": {"reportOnly": True, "imagesModified": False, "narrationModified": False, "videosModified": False,
                                "sourceInputsModified": False, "rendersStarted": False},
              "inputSha256": {relative(path): value for path, value in sorted(hashes.items(), key=lambda item: relative(item[0]))}}
    if REPORT.is_symlink() or REPORT.resolve().parent != (ROOT / "qa").resolve():
        raise ValueError("Palette report must stay in the current QA folder.")
    temporary = REPORT.with_name(REPORT.name + f".tmp-{os.getpid()}")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, REPORT)
    print(json.dumps({"mode": report["mode"], "passed": passed, "finalCoursePaletteAuditPassed": report["finalCoursePaletteAuditPassed"],
                      "sourcesAudited": len(files), "greenTealLiterals": green_literals, "currentFramesAudited": len(frames),
                      "greenTealPixels": green_pixels, "significantGreenRegions": regions,
                      "largestGreenComponentPixels": report["sampledFrames"]["largestGreenComponentPixels"],
                      "errors": errors, "report": str(REPORT)}, ensure_ascii=True, indent=2))
    return 1 if detected else 2 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        print(f"Palette audit stopped: {error}", file=sys.stderr)
        sys.exit(2)
