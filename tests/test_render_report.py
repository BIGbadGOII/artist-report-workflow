"""Validator and renderer tests for skills/artist-report/scripts/render_report.py (stdlib only)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "artist-report" / "scripts" / "render_report.py"
EXAMPLE = ROOT / "examples" / "marc-chalme-20260805" / "report.json"
sys.path.insert(0, str(SCRIPT.parent))

import render_report as rr  # noqa: E402

PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


def example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def image(path: str = "assets/work-1.png") -> dict:
    return {
        "path": path,
        "sourceUrl": "https://example.org/work-1",
        "credit": "Artist, Work 1. Courtesy Example Gallery.",
        "alt": {"zh": "一幅画", "en": "A painting"},
        "rightsNote": "Courtesy Example Gallery; rights reserved.",
    }


class ReportCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        (self.dir / "assets").mkdir()
        self.input = self.dir / "report.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write_asset(self, name: str, payload: bytes = PNG_1PX) -> None:
        (self.dir / "assets" / name).write_bytes(payload)

    def validate(self, report: dict):
        self.input.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        return rr.validate(report, self.input)

    def assertInvalid(self, report: dict, fragment: str) -> None:
        with self.assertRaises(ValueError) as caught:
            self.validate(report)
        self.assertIn(fragment, str(caught.exception))


class ValidatorTests(ReportCase):
    def test_example_passes(self):
        self.assertEqual(rr.validate(example(), EXAMPLE), [])

    def test_missing_top_level_section_fails(self):
        report = example()
        del report["potential"]
        self.assertInvalid(report, "missing potential")

    def test_missing_required_field_fails(self):
        report = example()
        del report["artist"]["birth"]
        self.assertInvalid(report, "report.artist: missing birth")

    def test_old_report_version_rejected(self):
        report = example()
        report["metadata"]["reportVersion"] = "2.0"
        self.assertInvalid(report, "reportVersion")

    def test_source_count_must_match(self):
        report = example()
        report["metadata"]["sourceCount"] += 1
        self.assertInvalid(report, "sourceCount")

    def test_image_with_provenance_passes(self):
        self.write_asset("work-1.png")
        report = example()
        report["visuals"]["status"] = "limited"
        report["works"][0]["image"] = image()
        self.assertEqual(len(self.validate(report)), 1)

    def test_image_without_provenance_fails(self):
        self.write_asset("work-1.png")
        for key in ("sourceUrl", "credit", "rightsNote"):
            with self.subTest(key=key):
                report = example()
                report["visuals"]["status"] = "limited"
                report["works"][0]["image"] = image()
                del report["works"][0]["image"][key]
                self.assertInvalid(report, "must match exactly one allowed shape")

    def test_image_source_must_be_http_url(self):
        self.write_asset("work-1.png")
        report = example()
        report["visuals"]["status"] = "limited"
        report["works"][0]["image"] = image() | {"sourceUrl": "google image search"}
        self.assertInvalid(report, "must match exactly one allowed shape")

    def test_image_path_cannot_escape_assets(self):
        (self.dir / "outside.png").write_bytes(PNG_1PX)
        report = example()
        report["visuals"]["status"] = "limited"
        report["works"][0]["image"] = image("assets/../outside.png")
        self.assertInvalid(report, "must stay inside")

    def test_non_image_payload_rejected(self):
        self.write_asset("work-1.png", b"<html>not an image</html>")
        report = example()
        report["visuals"]["status"] = "limited"
        report["works"][0]["image"] = image()
        self.assertInvalid(report, "Unsupported or invalid raster image")

    def test_duplicate_work_images_rejected(self):
        self.write_asset("work-1.png")
        self.write_asset("work-2.png")
        report = example()
        report["visuals"]["status"] = "limited"
        report["works"][0]["image"] = image("assets/work-1.png")
        report["works"][1]["image"] = image("assets/work-2.png")
        self.assertInvalid(report, "must not reuse the same image bytes")

    def test_unavailable_status_requires_zero_images(self):
        self.write_asset("work-1.png")
        report = example()
        report["works"][0]["image"] = image()
        self.assertInvalid(report, "unavailable requires zero images")

    def test_artist_voice_gap_or_quote_not_both(self):
        report = example()
        report["practice"]["artistVoice"] = {
            "gap": {"zh": "无", "en": "None"},
            "quote": {"zh": "引语", "en": "Quote"},
        }
        self.assertInvalid(report, "report.practice.artistVoice")

    def test_developments_need_entries_or_gap_note(self):
        report = example()
        del report["developments"]["gapNote"]
        self.assertInvalid(report, "gapNote")

    def test_unsold_lot_needs_explicit_basis(self):
        report = example()
        report["market"]["lots"] = [{
            "title": {"zh": "作品", "en": "Work"}, "workYear": "2020", "medium": {"zh": "油画", "en": "Oil"},
            "dimensions": {"zh": "10 × 10 厘米", "en": "10 × 10 cm"}, "edition": {"zh": "单件", "en": "Unique"},
            "house": "Example House", "saleTitle": "Sale", "saleDate": "2025-05-01", "city": "Paris", "lotNumber": "1",
            "currency": "EUR", "estimate": {"zh": "1,000–2,000 欧元", "en": "EUR 1,000–2,000"}, "hammer": None,
            "priceWithPremium": None, "resultBasis": {"zh": "结果未显示", "en": "Result not shown"},
            "url": "https://example.org/lot/1", "note": {"zh": "无", "en": "None"}, "image": None,
        }]
        self.assertInvalid(report, "explicit unsold/passed basis")
        report["market"]["lots"][0]["resultBasis"] = {"zh": "流拍", "en": "Passed / unsold"}
        self.validate(report)


class PotentialTests(ReportCase):
    def test_signal_requires_source_ref(self):
        report = example()
        report["potential"]["signals"][0]["sourceRefs"] = []
        self.assertInvalid(report, "needs at least one sourceRef")

    def test_signal_source_must_be_listed(self):
        report = example()
        report["potential"]["signals"][0]["sourceRefs"] = [{"label": "Blog", "url": "https://example.org/blog"}]
        self.assertInvalid(report, "is not listed in sources")

    def test_empty_assessment_needs_gaps(self):
        report = example()
        report["potential"].update(signals=[], counterSignals=[], gaps=[])
        self.assertInvalid(report, "potential needs at least one sourced signal")

    def test_counter_signals_or_gaps_required(self):
        report = example()
        report["potential"].update(counterSignals=[], gaps=[])
        self.assertInvalid(report, "counter-signal")

    def test_unknown_signal_category_rejected(self):
        report = example()
        report["potential"]["signals"][0]["category"] = "hype"
        self.assertInvalid(report, "must be one of")

    def test_investment_advice_wording_rejected(self):
        cases = [
            ("en", "The artist is undervalued relative to peers."),
            ("en", "Prices will rise after the biennial."),
            ("en", "Collectors should buy before the museum show."),
            ("en", "A clear investment opportunity."),
            ("zh", "该艺术家具有明显的升值潜力。"),
            ("zh", "建议买入早期作品。"),
            ("zh", "作品目前被低估。"),
        ]
        for lang, text in cases:
            with self.subTest(text=text):
                report = example()
                report["potential"]["summary"][lang] = text
                self.assertInvalid(report, "investment-advice")

    def test_advice_wording_checked_outside_potential(self):
        report = example()
        report["quickRead"]["body"]["en"] = "A good investment for new collectors."
        self.assertInvalid(report, "report.quickRead.body.en")

    def test_neutral_market_wording_allowed(self):
        report = example()
        report["potential"]["summary"]["en"] = (
            "Several works were marked sold; asking prices are primary-market offers. "
            "This is not a price forecast or investment opinion."
        )
        report["potential"]["summary"]["zh"] = "多件作品标注已售；本节不构成价格预测或投资意见。"
        self.validate(report)


class DateParsingTests(unittest.TestCase):
    def test_iso_range(self):
        self.assertEqual(rr.parse_date_range("2026-09-01 – 2026-10-12"), (date(2026, 9, 1), date(2026, 10, 12)))

    def test_chinese_and_dotted_formats(self):
        self.assertEqual(rr.parse_date_range("2026年9月1日至2026年10月12日"), (date(2026, 9, 1), date(2026, 10, 12)))
        self.assertEqual(rr.parse_date_range("2026.09.01–2026.10.12"), (date(2026, 9, 1), date(2026, 10, 12)))
        self.assertEqual(rr.parse_date_range("2026/9/1"), (date(2026, 9, 1), date(2026, 9, 1)))

    def test_no_date(self):
        self.assertIsNone(rr.parse_date_range("Autumn 2026"))

    def test_ambiguous_text_rejected(self):
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            rr.parse_date_range("2026-09-01 – 2026-10-12, preview 2026-08-31")

    def test_reversed_range_rejected(self):
        with self.assertRaisesRegex(ValueError, "ends before"):
            rr.parse_date_range("2026-10-12 – 2026-09-01")

    def test_invalid_calendar_date_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid calendar date"):
            rr.parse_date_range("2026-02-30")

    def test_status(self):
        cutoff = date(2026, 10, 1)
        self.assertEqual(rr.exhibition_status(date(2026, 9, 1), date(2026, 10, 12), cutoff), "current")
        self.assertEqual(rr.exhibition_status(date(2026, 11, 1), date(2026, 12, 1), cutoff), "upcoming")
        self.assertEqual(rr.exhibition_status(date(2026, 8, 1), date(2026, 9, 1), cutoff), "past")


class ExhibitionStatusTests(ReportCase):
    def show(self, status: str, **extra) -> dict:
        item = {
            "status": status,
            "title": {"zh": "展览", "en": "Show"},
            "venue": {"zh": "美术馆", "en": "Museum"},
            "date": {"zh": "2026年8月1日至9月30日", "en": "1 August – 30 September 2026"},
            "type": {"zh": "个展", "en": "Solo"},
            "accessed": "2026-08-05",
        }
        item.update(extra)
        return item

    def with_show(self, item: dict) -> dict:
        report = example()
        report["exhibitions"]["currentUpcoming"] = [item]
        return report

    def test_explicit_dates_current(self):
        self.validate(self.with_show(self.show("current", startDate="2026-08-01", endDate="2026-09-30")))

    def test_explicit_open_ended_upcoming(self):
        self.validate(self.with_show(self.show("upcoming", startDate="2026-09-01", endDate=None)))

    def test_status_mismatch_rejected(self):
        report = self.with_show(self.show("upcoming", startDate="2026-08-01", endDate="2026-09-30"))
        self.assertInvalid(report, "conflicts with")

    def test_past_show_rejected(self):
        report = self.with_show(self.show("current", startDate="2026-06-01", endDate="2026-07-01"))
        self.assertInvalid(report, "conflicts with")

    def test_end_before_start_rejected(self):
        report = self.with_show(self.show("current", startDate="2026-08-01", endDate="2026-07-01"))
        self.assertInvalid(report, "endDate is before startDate")

    def test_text_fallback_parses_chinese_range(self):
        item = self.show("current", date={"zh": "2026年8月1日至2026年9月30日", "en": "1 August – 30 September 2026"})
        self.validate(self.with_show(item))

    def test_text_fallback_languages_must_agree(self):
        item = self.show("current", date={"zh": "2026-08-01 至 2026-09-30", "en": "2026-08-01 – 2026-10-30"})
        self.assertInvalid(self.with_show(item), "disagree")

    def test_text_without_dates_rejected(self):
        item = self.show("current", date={"zh": "2026年秋季", "en": "Autumn 2026"})
        self.assertInvalid(self.with_show(item), "need startDate/endDate")


class RenderTests(unittest.TestCase):
    def test_size_warning_thresholds(self):
        mb = 1024 * 1024
        self.assertIsNone(rr.size_warning(5 * mb))
        self.assertIn("NOTICE", rr.size_warning(9 * mb))
        self.assertIn("WARNING", rr.size_warning(11 * mb))

    def test_render_html_single_pass(self):
        report = example()
        report["quickRead"]["body"]["en"] = "Literal __ASSET_DATA__ and </script> text"
        html = rr.render_html(report, {})
        for placeholder in ("__STYLE__", "__SCRIPT__", "__REPORT_DATA__"):
            self.assertNotIn(placeholder, html)
        self.assertEqual(html.count('<script id="asset-data" type="application/json">{}</script>'), 1)
        self.assertIn("Literal __ASSET_DATA__ and <\\/script> text", html)

    def test_cli_check_and_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            check = subprocess.run([sys.executable, str(SCRIPT), "--check", "--input", str(EXAMPLE)], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("OK: canonical v2.1 report", check.stdout)
            rendered = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(EXAMPLE), "--output", str(output)], capture_output=True, text=True
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            html = output.read_text(encoding="utf-8")
            self.assertIn("Marc Chalmé", html)
            self.assertIn("potential", html)
            self.assertEqual(rendered.stderr, "")

    def test_cli_warns_on_large_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets").mkdir()
            big = PNG_1PX + b"\0" * (8 * 1024 * 1024)  # ~10.7 MB once base64-embedded
            (root / "assets" / "big.png").write_bytes(big)
            report = example()
            report["visuals"]["status"] = "limited"
            report["works"][0]["image"] = image("assets/big.png")
            (root / "report.json").write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
            check = subprocess.run([sys.executable, str(SCRIPT), "--check", "--input", str(root / "report.json")], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("WARNING", check.stderr)
            rendered = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(root / "report.json"), "--output", str(root / "report.html")],
                capture_output=True, text=True,
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertIn("above the 10 MB target", rendered.stderr)


if __name__ == "__main__":
    unittest.main()
