from decimal import Decimal
import json
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "work" / "mab-elv-quotation" / "2026-08-25-client-budgetary-draft.md"
JOB = REPO_ROOT / "work" / "mab-elv-quotation" / "2026-08-25-client-budgetary-quotation.json"
ITEM_CODE = re.compile(r"^[A-E]\d+$")


def money(value: str) -> Decimal:
    return Decimal(value.replace("P", "").replace("₱", "").replace(",", "").strip())


def quantity(value: str) -> Decimal:
    return Decimal(value.strip())


def source_items() -> dict[str, dict]:
    items = {}
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not ITEM_CODE.fullmatch(cells[0]):
            continue
        item_code, description, qty, unit, unit_price, line_total = cells
        items[item_code] = {
            "title": description,
            "quantity": quantity(qty),
            "unit": unit,
            "unit_price": money(unit_price),
            "line_total": money(line_total),
        }
    return items


class MabSourceAlignmentTests(unittest.TestCase):
    def test_every_pricing_line_matches_pasted_source(self):
        source = source_items()
        data = json.loads(JOB.read_text(encoding="utf-8"))
        job = {
            item["item_code"]: item
            for section in data["pricing"]["sections"]
            for item in section["items"]
        }
        self.assertEqual(set(job), set(source))
        self.assertEqual(len(job), 55)
        for item_code, expected in source.items():
            with self.subTest(item_code=item_code):
                actual = job[item_code]
                actual_quantity = Decimal(str(actual["quantity"]))
                actual_unit_price = Decimal(str(actual["unit_price"]))
                self.assertEqual(actual["title"], expected["title"])
                self.assertEqual(actual_quantity, expected["quantity"])
                self.assertEqual(actual["unit"], expected["unit"])
                self.assertEqual(actual_unit_price, expected["unit_price"])
                self.assertEqual(
                    actual_quantity * actual_unit_price,
                    expected["line_total"],
                )


if __name__ == "__main__":
    unittest.main()
