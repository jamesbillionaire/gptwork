from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pypdf import PdfReader

from quotation_engine.contract import (
    CONTENT_WIDTH,
    LEFT_MARGIN,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    PRICING_COLUMN_WIDTHS,
    RIGHT_MARGIN,
    TEMPLATE_ID,
    TOTALS_COLUMN_WIDTHS,
)
from quotation_engine.renderer import render_quotation
from quotation_engine.validation import load_and_validate


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "approved_sample.json"
GOLDEN_CONTRACT = ROOT / "golden" / "approved_sample_contract.json"
MANIFEST = ROOT / "manifest.json"
TEXT_CHECKSUM_SUFFIXES = {".json", ".md", ".py"}


def manifest_sha256(path: Path) -> str:
    """Normalize text line endings so manifest checks are cross-platform."""

    if path.suffix.lower() in TEXT_CHECKSUM_SUFFIXES:
        normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        return sha256(normalized.encode("utf-8")).hexdigest()
    return sha256(path.read_bytes()).hexdigest()


class LayoutContractTests(unittest.TestCase):
    def test_locked_geometry(self):
        self.assertAlmostEqual(PAGE_WIDTH, 612.0)
        self.assertAlmostEqual(PAGE_HEIGHT, 1008.0)
        self.assertAlmostEqual(CONTENT_WIDTH, 532.8)
        self.assertAlmostEqual(sum(PRICING_COLUMN_WIDTHS), CONTENT_WIDTH)
        self.assertEqual(TOTALS_COLUMN_WIDTHS, PRICING_COLUMN_WIDTHS[-2:])
        self.assertAlmostEqual(
            LEFT_MARGIN + sum(PRICING_COLUMN_WIDTHS),
            PAGE_WIDTH - RIGHT_MARGIN,
        )

    def test_render_is_deterministic_and_preserves_release_contract(self):
        data = load_and_validate(SAMPLE)
        with TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.pdf"
            second = Path(tmp) / "second.pdf"
            render_quotation(data, first)
            render_quotation(data, second)
            self.assertEqual(sha256(first.read_bytes()).hexdigest(), sha256(second.read_bytes()).hexdigest())

            reader = PdfReader(str(first))
            self.assertEqual(len(reader.pages), 2)
            for page in reader.pages:
                box = page.mediabox
                self.assertAlmostEqual(float(box.width), 612.0)
                self.assertAlmostEqual(float(box.height), 1008.0)

            page_text = [page.extract_text() for page in reader.pages]
            all_text = "\n".join(page_text)
            self.assertIn("PREPARED QUOTATION FOR", all_text)
            self.assertIn("SCOPE AND PRICING", all_text)
            self.assertIn("ADDITIONAL NOTES", all_text)
            self.assertIn("P 765,000.00", all_text)
            self.assertIn("P 91,800.00", all_text)
            self.assertIn("P 856,800.00", all_text)
            self.assertIn("Page 1 of 2", page_text[0])
            self.assertIn("Page 2 of 2", page_text[1])
            self.assertIn("LAVI-QTN-20260819-SAMPLE-01", page_text[1])
            self.assertNotIn("PROFESSIONAL QUOTATION", all_text.upper())
            self.assertNotIn("RELEASE CONDITION", all_text.upper())

    def test_golden_contract_matches_current_renderer(self):
        data = load_and_validate(SAMPLE)
        contract = json.loads(GOLDEN_CONTRACT.read_text(encoding="utf-8"))
        with TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "candidate.pdf"
            render_quotation(data, candidate)
            reader = PdfReader(str(candidate))
            extracted_text = "\n\f\n".join(page.extract_text() for page in reader.pages)
            self.assertEqual(
                len(reader.pages),
                contract["expected_page_count"],
            )
            self.assertEqual(
                sha256(extracted_text.encode()).hexdigest(),
                contract["expected_extracted_text_sha256"],
            )

    def test_manifest_integrity(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["template_id"], TEMPLATE_ID)
        self.assertEqual(manifest["status"], "APPROVED_LOCKED")
        repo_root = ROOT.parent
        for relative_path, expected_hash in manifest["sha256"].items():
            actual = manifest_sha256(repo_root / relative_path)
            self.assertEqual(actual, expected_hash, relative_path)


if __name__ == "__main__":
    unittest.main()
