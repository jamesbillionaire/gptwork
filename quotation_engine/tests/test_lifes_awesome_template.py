from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pypdf import PdfReader

from quotation_engine.profiles import LIFES_AWESOME_TEMPLATE_ID
from quotation_engine.renderer import render_quotation
from quotation_engine.validation import (
    calculate_section_totals,
    calculate_totals,
    iter_pricing_items,
    load_and_validate,
)


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
JOB = REPO_ROOT / "work" / "mab-elv-quotation" / "2026-08-25-client-budgetary-quotation.json"
GOLDEN = ROOT / "golden" / "lifes_awesome_mab_contract.json"
MANIFEST = ROOT / "manifests" / "lifes-awesome-quotation-2026.1.json"
TEXT_CHECKSUM_SUFFIXES = {".json", ".md", ".py"}


def manifest_sha256(path: Path) -> str:
    if path.suffix.lower() in TEXT_CHECKSUM_SUFFIXES:
        normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        return sha256(normalized.encode("utf-8")).hexdigest()
    return sha256(path.read_bytes()).hexdigest()


class LifesAwesomeTemplateTests(unittest.TestCase):
    def setUp(self):
        self.data = load_and_validate(JOB)

    def test_source_commercial_totals_and_line_count(self):
        self.assertEqual(self.data["template_version"], LIFES_AWESOME_TEMPLATE_ID)
        self.assertEqual(len(list(iter_pricing_items(self.data))), 55)
        self.assertEqual(
            [str(value) for value in calculate_section_totals(self.data)],
            [
                "2145000.00",
                "1248200.00",
                "1038200.00",
                "1694000.00",
                "420000.00",
            ],
        )
        self.assertEqual(
            {key: str(value) for key, value in calculate_totals(self.data).items()},
            {
                "subtotal": "6545400.00",
                "vat": "0.00",
                "grand_total": "6545400.00",
            },
        )

    def test_render_matches_lifes_awesome_contract(self):
        contract = json.loads(GOLDEN.read_text(encoding="utf-8"))
        with TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "lifes-awesome-mab.pdf"
            render_quotation(self.data, candidate)
            reader = PdfReader(str(candidate))
            self.assertEqual(len(reader.pages), contract["expected_page_count"])
            for page in reader.pages:
                self.assertAlmostEqual(float(page.mediabox.width), 612.0)
                self.assertAlmostEqual(float(page.mediabox.height), 1008.0)

            page_text = [page.extract_text() for page in reader.pages]
            extracted_text = "\n\f\n".join(page_text)
            for label in contract["required_labels"]:
                self.assertIn(label, extracted_text)
            self.assertIn("Page 1 of 3", page_text[0])
            self.assertIn("Page 2 of 3", page_text[1])
            self.assertIn("Page 3 of 3", page_text[2])
            self.assertIn("Preliminary Budgetary Draft", page_text[1])
            self.assertEqual(len(reader.pages[0].images), 1)
            self.assertEqual(
                sha256(extracted_text.encode("utf-8")).hexdigest(),
                contract["expected_extracted_text_sha256"],
            )

    def test_candidate_manifest_integrity(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["template_id"], LIFES_AWESOME_TEMPLATE_ID)
        self.assertEqual(manifest["status"], "CANDIDATE_REVIEW")
        for relative_path, expected_hash in manifest["sha256"].items():
            actual = manifest_sha256(REPO_ROOT / relative_path)
            self.assertEqual(actual, expected_hash, relative_path)


if __name__ == "__main__":
    unittest.main()
