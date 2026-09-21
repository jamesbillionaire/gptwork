from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import unittest

from quotation_engine.validation import (
    QuotationValidationError,
    calculate_totals,
    load_and_validate,
    validate_quotation,
)


SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "approved_sample.json"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = load_and_validate(SAMPLE)

    def test_approved_sample_totals(self):
        self.assertEqual(
            calculate_totals(self.data),
            {
                "subtotal": Decimal("765000.00"),
                "vat": Decimal("91800.00"),
                "grand_total": Decimal("856800.00"),
            },
        )

    def test_wrong_template_version_is_rejected(self):
        data = deepcopy(self.data)
        data["template_version"] = "LAVI-QUOTATION-DRAFT"
        with self.assertRaisesRegex(QuotationValidationError, "template_version"):
            validate_quotation(data)

    def test_supplied_line_amount_is_rejected(self):
        data = deepcopy(self.data)
        data["pricing"]["items"][0]["amount"] = 40000
        with self.assertRaisesRegex(QuotationValidationError, "engine calculates"):
            validate_quotation(data)

    def test_wrong_vat_rate_is_rejected(self):
        data = deepcopy(self.data)
        data["pricing"]["vat_rate"] = 0.11
        with self.assertRaisesRegex(QuotationValidationError, "must be 0.12"):
            validate_quotation(data)

    def test_layout_override_field_is_rejected(self):
        data = deepcopy(self.data)
        data["layout"] = {"title_color": "red"}
        with self.assertRaisesRegex(QuotationValidationError, "Unsupported field"):
            validate_quotation(data)

    def test_prohibited_layout_copy_is_rejected(self):
        data = deepcopy(self.data)
        data["additional_notes"][0]["text"] = "Professional Quotation"
        with self.assertRaisesRegex(QuotationValidationError, "Prohibited"):
            validate_quotation(data)


if __name__ == "__main__":
    unittest.main()
