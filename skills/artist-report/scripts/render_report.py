#!/usr/bin/env python3
"""Validate and render canonical bilingual artist reports as self-contained HTML."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SECTIONS = ["metadata", "visuals", "artist", "quickRead", "biography", "practice", "works", "developments", "exhibitions", "institutions", "market", "potential", "evidence", "sources"]
IMAGE_KEYS = {"path", "sourceUrl", "credit", "alt", "rightsNote"}
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "report-schema.json"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
SIZE_TARGET_BYTES = 10 * 1024 * 1024
SIZE_NOTICE_BYTES = 8 * 1024 * 1024
# Investment-advice / price-prediction phrasing that must never appear in reader-facing text.
# Kept to unambiguous phrases so neutral words such as "sold", "price", or the disclaimer itself do not trip it.
ADVICE_PATTERNS = [
    r"\bundervalued\b", r"\bovervalued\b", r"\binvestment (?:opportunity|grade|potential|pick)\b", r"\bgood investment\b",
    r"\b(?:strong )?buy (?:now|signal|rating)\b", r"\b(?:should|must) (?:buy|sell|acquire|collect)\b", r"\bprice target\b",
    r"\b(?:prices?|values?) (?:will|are expected to|is expected to|should) (?:rise|increase|grow|climb|double|appreciate)\b",
    r"\bwill (?:appreciate|rise in value|go up in value)\b", r"\bblue[- ]chip in the making\b",
    "升值潜力", "升值空间", "值得投资", "投资价值", "投资机会", "建议买入", "建议卖出", "建议购入", "建议出手", "被低估", "被高估", "抄底", "价格将上涨", "价格将翻倍", "将会升值", "必涨", "目标价",
]
ADVICE_RE = re.compile("|".join(ADVICE_PATTERNS), re.IGNORECASE)
DATE_TOKEN_RE = re.compile(r"(?<!\d)(\d{4})\s*[-./年]\s*(\d{1,2})\s*[-./月]\s*(\d{1,2})\s*日?(?!\d)")
TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "null": type(None),
    "boolean": bool,
}


def schema_error(path: str, message: str) -> None:
    raise ValueError(f"Schema violation at {path}: {message}")


def resolve_ref(schema_root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValueError(f"Unsupported schema reference: {reference}")
    current: Any = schema_root
    for part in reference[2:].split("/"):
        current = current[part.replace("~1", "/").replace("~0", "~")]
    return current


def validate_format(value: str, format_name: str, path: str) -> None:
    try:
        if format_name == "date":
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError
            date.fromisoformat(value)
        elif format_name == "date-time":
            if "T" not in value:
                raise ValueError
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif format_name == "uri":
            parsed = urlparse(value)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or any(char.isspace() for char in value):
                raise ValueError
    except ValueError:
        schema_error(path, f"must be a valid {format_name}")


def validate_schema(value: Any, schema: dict[str, Any], root: dict[str, Any], path: str = "report") -> None:
    if "$ref" in schema:
        validate_schema(value, resolve_ref(root, schema["$ref"]), root, path)
        return
    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                validate_schema(value, option, root, path)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            schema_error(path, "must match exactly one allowed shape")
        return
    expected = schema.get("type")
    if expected:
        allowed = TYPE_MAP[expected]
        valid_type = isinstance(value, allowed)
        if expected in {"integer", "number"} and isinstance(value, bool):
            valid_type = False
        if not valid_type:
            schema_error(path, f"must be {expected}")
    if "const" in schema and value != schema["const"]:
        schema_error(path, f"must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        schema_error(path, f"must be one of {schema['enum']}")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            schema_error(path, "must not be empty")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            schema_error(path, f"must match {schema['pattern']}")
        if "format" in schema:
            validate_format(value, schema["format"], path)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            schema_error(path, f"requires at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            schema_error(path, f"allows at most {schema['maxItems']} items")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], root, f"{path}[{index}]")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            schema_error(path, f"must be at least {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            schema_error(path, f"must be at most {schema['maximum']}")
    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            schema_error(path, f"missing {', '.join(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = [key for key in value if key not in properties]
            if extra:
                schema_error(path, f"unexpected {', '.join(extra)}")
        for key, child in value.items():
            if key in properties:
                validate_schema(child, properties[key], root, f"{path}.{key}")


def load_and_validate_schema(report: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validate_schema(report, schema, schema)


def resolve_asset(input_path: Path, relative_path: str) -> Path:
    report_root = input_path.parent.resolve()
    raw_assets_root = report_root / "assets"
    if raw_assets_root.is_symlink():
        raise ValueError(f"The report assets directory must not be a symlink: {raw_assets_root}")
    assets_root = raw_assets_root.resolve()
    candidate = (report_root / relative_path).resolve()
    try:
        candidate.relative_to(assets_root)
    except ValueError as exc:
        raise ValueError(f"Image path must stay inside {assets_root}: {relative_path}") from exc
    if not candidate.is_file():
        raise ValueError(f"Missing local image: {candidate}")
    return candidate


def detect_image_mime(path: Path) -> str:
    header = path.read_bytes()[:32]
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header[:6] in {b"GIF87a", b"GIF89a"}:
        return "image/gif"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image/webp"
    if len(header) >= 12 and header[4:8] == b"ftyp" and header[8:12] in {b"avif", b"avis"}:
        return "image/avif"
    raise ValueError(f"Unsupported or invalid raster image: {path}")


def asset_digest(input_path: Path, image: dict[str, Any]) -> str:
    return hashlib.sha256(resolve_asset(input_path, image["path"]).read_bytes()).hexdigest()


def collect_images(value: Any, label: str = "report") -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if set(value) == IMAGE_KEYS:
            found.append((label, value))
        else:
            for key, child in value.items():
                found.extend(collect_images(child, f"{label}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(collect_images(child, f"{label}[{index}]"))
    return found


def parse_date_range(text: str) -> tuple[date, date] | None:
    """Extract a start/end date from display text such as "2026-09-01 – 2026-10-12" or "2026年9月1日至10月12日".

    Accepts YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD and YYYY年M月D日. One date means a single-day or open-ended
    entry. More than two dates is ambiguous and must be resolved with explicit startDate/endDate fields.
    """
    found = []
    for match in DATE_TOKEN_RE.finditer(text):
        try:
            found.append(date(int(match.group(1)), int(match.group(2)), int(match.group(3))))
        except ValueError as exc:
            raise ValueError(f"Invalid calendar date {match.group(0)!r}") from exc
    if not found:
        return None
    if len(found) > 2:
        raise ValueError(f"Ambiguous date text {text!r}: found {len(found)} dates; set startDate/endDate explicitly")
    start, end = found[0], found[-1]
    if end < start:
        raise ValueError(f"Date range ends before it starts: {text!r}")
    return start, end


def exhibition_range(item: dict[str, Any], label: str) -> tuple[date, date]:
    if "startDate" in item:
        start = date.fromisoformat(item["startDate"])
        end = date.fromisoformat(item["endDate"]) if item.get("endDate") else start
        if end < start:
            raise ValueError(f"{label}: endDate is before startDate")
        return start, end
    ranges = {lang: parse_date_range(item["date"][lang]) for lang in ("zh", "en")}
    found = {lang: value for lang, value in ranges.items() if value}
    if not found:
        raise ValueError(f"{label}: current/upcoming exhibitions need startDate/endDate or a parseable date in one language")
    if len(found) == 2 and found["zh"] != found["en"]:
        raise ValueError(f"{label}: zh and en date text disagree ({found['zh']} vs {found['en']})")
    return next(iter(found.values()))


def exhibition_status(start: date, end: date, cutoff: date) -> str:
    if cutoff < start:
        return "upcoming"
    return "current" if cutoff <= end else "past"


def iter_strings(value: Any, label: str = "report"):
    if isinstance(value, str):
        yield label, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from iter_strings(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_strings(child, f"{label}[{index}]")


def validate_advice_language(report: dict[str, Any]) -> None:
    for label, text in iter_strings(report):
        if label.endswith((".url", ".sourceUrl", ".path")):
            continue
        match = ADVICE_RE.search(text)
        if match:
            raise ValueError(f"{label}: investment-advice or price-prediction wording is not allowed ({match.group(0)!r})")


def validate_potential(report: dict[str, Any]) -> None:
    potential = report["potential"]
    known_urls = {source["url"] for source in report["sources"]}
    if not potential["signals"] and not potential["gaps"]:
        raise ValueError("potential needs at least one sourced signal, or gaps explaining why none were verified")
    if not potential["counterSignals"] and not potential["gaps"]:
        raise ValueError("potential needs at least one counter-signal/risk, or gaps explaining why none were assessed")
    for group in ("signals", "counterSignals"):
        for index, signal in enumerate(potential[group]):
            label = f"potential.{group}[{index}]"
            if group == "signals" and not signal["sourceRefs"]:
                raise ValueError(f"{label}: every momentum signal needs at least one sourceRef")
            for ref in signal["sourceRefs"]:
                if ref["url"] not in known_urls:
                    raise ValueError(f"{label}: sourceRef {ref['url']} is not listed in sources")


def validate(report: dict[str, Any], input_path: Path) -> list[tuple[str, dict[str, Any]]]:
    load_and_validate_schema(report)
    missing = [key for key in SECTIONS if key not in report]
    extra = [key for key in report if key not in SECTIONS]
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected: {', '.join(extra)}")
        raise ValueError(f"Canonical top-level sections do not match ({'; '.join(details)})")
    if report["metadata"].get("sourceCount") != len(report["sources"]):
        raise ValueError("metadata.sourceCount must equal sources length")
    status = report["visuals"].get("status")
    cutoff = date.fromisoformat(report["metadata"]["informationCutoff"])
    for index, item in enumerate(report["exhibitions"].get("currentUpcoming", [])):
        start, end = exhibition_range(item, f"exhibitions.currentUpcoming[{index}]")
        expected = exhibition_status(start, end, cutoff)
        if expected == "past" or item["status"] != expected:
            raise ValueError(
                f"Exhibition status {item['status']!r} conflicts with {start}–{end} at cutoff {cutoff}"
            )
    if len(report["developments"]["entries"]) < 4 and not report["developments"].get("gapNote"):
        raise ValueError("developments needs 4–6 entries, or a gapNote explaining why phases cannot be established")
    validate_potential(report)
    validate_advice_language(report)
    for lot_label, lot in ([('market.record', report["market"].get("record"))] + [(f'market.lots[{i}]', x) for i, x in enumerate(report["market"].get("lots", []))]):
        if lot is None:
            continue
        if lot["hammer"] is None and lot["priceWithPremium"] is None:
            result_text = f"{lot['resultBasis']['zh']} {lot['resultBasis']['en']} {lot['note']['zh']} {lot['note']['en']}".lower()
            if not any(marker in result_text for marker in ("unsold", "not sold", "passed", "流拍", "未成交")):
                raise ValueError(f"{lot_label} needs a visible result or an explicit unsold/passed basis")
    images = collect_images(report)
    for label, image in images:
        local = resolve_asset(input_path, image["path"])
        detect_image_mime(local)
    total = len(images)
    unique_images = {asset_digest(input_path, image) for _, image in images}
    work_image_objects = [work["image"] for work in report["works"] if work.get("image")]
    work_hashes = [asset_digest(input_path, image) for image in work_image_objects]
    if len(work_hashes) != len(set(work_hashes)):
        raise ValueError("Representative works must not reuse the same image bytes")
    work_images = len(set(work_hashes))
    hero = bool(report["artist"].get("heroImage"))
    portrait = bool(report["artist"].get("identityImage"))
    context_count = len(report["practice"].get("contextImages", []))
    exhibition_count = len(report["exhibitions"].get("heroImages", []))
    market_objects = ([report["market"]["record"]] if report["market"].get("record") else []) + report["market"].get("lots", [])
    market_images_complete = all(item.get("image") for item in market_objects)
    gaps = report["visuals"].get("gaps", [])
    complete_categories = hero and portrait and context_count >= 2 and work_images >= 6 and exhibition_count >= 1 and market_images_complete
    if status == "complete" and (len(unique_images) < 8 or not complete_categories):
        raise ValueError(
            "visuals.status complete requires 8 unique images, hero, identity portrait, 2 context images, "
            "6 unique work images, an exhibition image, and images for every displayed market object"
        )
    if status == "partial" and (len(unique_images) < 4 or not gaps):
        raise ValueError("visuals.status partial requires at least 4 unique images and explicit gaps")
    if status == "limited" and not (1 <= len(unique_images) <= 3 and gaps):
        raise ValueError("visuals.status limited requires 1–3 unique images with explicit reasons")
    if status == "unavailable" and (total != 0 or not gaps):
        raise ValueError("visuals.status unavailable requires zero images and explicit gaps")
    return images


def embed_images(images: list[tuple[str, dict[str, Any]]], input_path: Path) -> dict[str, str]:
    embedded: dict[str, str] = {}
    for _, image in images:
        rel = image["path"]
        if rel in embedded:
            continue
        local = resolve_asset(input_path, rel)
        mime = detect_image_mime(local)
        embedded[rel] = f"data:{mime};base64,{base64.b64encode(local.read_bytes()).decode('ascii')}"
    return embedded


def render_html(report: dict[str, Any], assets: dict[str, str]) -> str:
    replacements = {
        "__STYLE__": (TEMPLATE_DIR / "report.css").read_text(encoding="utf-8"),
        "__SCRIPT__": (TEMPLATE_DIR / "report.js").read_text(encoding="utf-8"),
        "__REPORT_DATA__": json.dumps(report, ensure_ascii=False).replace("</", "<\\/"),
        "__ASSET_DATA__": json.dumps(assets, ensure_ascii=False).replace("</", "<\\/"),
    }
    shell = (TEMPLATE_DIR / "report.html").read_text(encoding="utf-8")
    # Single pass so placeholder-like text inside report data is never substituted again.
    return re.sub("|".join(replacements), lambda match: replacements[match.group(0)], shell)


def size_warning(size_bytes: int) -> str | None:
    megabytes = size_bytes / (1024 * 1024)
    if size_bytes > SIZE_TARGET_BYTES:
        return f"WARNING: report is {megabytes:.1f} MB, above the 10 MB target; optimize images or record the exception"
    if size_bytes > SIZE_NOTICE_BYTES:
        return f"NOTICE: report is {megabytes:.1f} MB, approaching the 10 MB target"
    return None


def estimate_output_bytes(report: dict[str, Any], images: list[tuple[str, dict[str, Any]]], input_path: Path) -> int:
    asset_bytes = sum(resolve_asset(input_path, path).stat().st_size for path in {image["path"] for _, image in images})
    template_bytes = sum(path.stat().st_size for path in TEMPLATE_DIR.iterdir() if path.is_file())
    report_bytes = len(json.dumps(report, ensure_ascii=False).encode("utf-8"))
    return template_bytes + report_bytes + (asset_bytes * 4 + 2) // 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    images = validate(report, args.input)
    if args.check:
        print(f"OK: canonical v2.1 report; {len(images)} local images; visual status={report['visuals']['status']}")
        warning = size_warning(estimate_output_bytes(report, images, args.input))
        if warning:
            print(f"{warning} (estimated)", file=sys.stderr)
        return 0
    if not args.output:
        parser.error("--output is required unless --check is used")
    html = render_html(report, embed_images(images, args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(args.output)
    warning = size_warning(args.output.stat().st_size)
    if warning:
        print(warning, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
