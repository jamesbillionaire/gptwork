"""Structured-data validation and commercial arithmetic for quotations."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from .contract import PROHIBITED_RELEASE_TEXT, TEMPLATE_ID
from .profiles import LIFES_AWESOME_TEMPLATE_ID, TEMPLATE_PROFILES


MONEY = Decimal("0.01")


class QuotationValidationError(ValueError):
    """Raised when quotation data violates the locked engine contract."""


def _required(mapping: dict[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        raise QuotationValidationError(f"Missing required field: {path}.{key}")
    return mapping[key]


def _reject_unknown(mapping: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise QuotationValidationError(
            f"Unsupported field at {path}: {', '.join(unknown)}"
        )


def _text(value: Any, path: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise QuotationValidationError(f"{path} must be text")
    value = value.strip()
    if not allow_empty and not value:
        raise QuotationValidationError(f"{path} must not be empty")
    return value


def _decimal(value: Any, path: str, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool):
        raise QuotationValidationError(f"{path} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise QuotationValidationError(f"{path} must be numeric") from None
    if not result.is_finite():
        raise QuotationValidationError(f"{path} must be finite")
    if positive and result <= 0:
        raise QuotationValidationError(f"{path} must be greater than zero")
    if result.as_tuple().exponent < -2:
        raise QuotationValidationError(f"{path} may have at most two decimal places")
    return result


def _walk_text(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _walk_text(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_text(child)


def iter_pricing_items(data: dict[str, Any]):
    """Yield all line items from flat or grouped pricing data."""

    pricing = data["pricing"]
    if "items" in pricing:
        yield from pricing["items"]
        return
    for section in pricing["sections"]:
        yield from section["items"]


def calculate_section_totals(data: dict[str, Any]) -> list[Decimal]:
    """Calculate section totals for grouped-pricing templates."""

    sections = data["pricing"].get("sections", [])
    return [
        sum(
            (
                _decimal(item["quantity"], "pricing.sections.items.quantity", positive=True)
                * _decimal(
                    item["unit_price"],
                    "pricing.sections.items.unit_price",
                    positive=True,
                )
            )
            for item in section["items"]
        ).quantize(MONEY, rounding=ROUND_HALF_UP)
        for section in sections
    ]


def calculate_totals(data: dict[str, Any]) -> dict[str, Decimal]:
    items = iter_pricing_items(data)
    subtotal = sum(
        (_decimal(item["quantity"], "pricing.items.quantity", positive=True)
         * _decimal(item["unit_price"], "pricing.items.unit_price", positive=True))
        for item in items
    ).quantize(MONEY, rounding=ROUND_HALF_UP)
    vat_rate = _decimal(data["pricing"]["vat_rate"], "pricing.vat_rate")
    vat = Decimal("0.00")
    if data["pricing"]["tax_treatment"] == "VAT Inclusive":
        vat = (subtotal * vat_rate).quantize(MONEY, rounding=ROUND_HALF_UP)
    grand_total = (subtotal + vat).quantize(MONEY, rounding=ROUND_HALF_UP)
    return {"subtotal": subtotal, "vat": vat, "grand_total": grand_total}


def validate_quotation(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise QuotationValidationError("Quotation data must be a JSON object")
    _reject_unknown(
        data,
        {
            "template_version",
            "document",
            "client",
            "project",
            "introduction",
            "pricing",
            "pricing_basis",
            "additional_notes",
            "signatures",
        },
        "$",
    )

    template_version = _text(_required(data, "template_version", "$"), "template_version")
    if template_version not in TEMPLATE_PROFILES:
        supported = ", ".join(sorted(TEMPLATE_PROFILES))
        raise QuotationValidationError(
            f"template_version must be one of {supported}; received {template_version}"
        )

    document = _required(data, "document", "$" )
    client = _required(data, "client", "$" )
    project = _required(data, "project", "$" )
    pricing = _required(data, "pricing", "$" )
    signatures = _required(data, "signatures", "$" )
    for name, value in (
        ("document", document),
        ("client", client),
        ("project", project),
        ("pricing", pricing),
        ("signatures", signatures),
    ):
        if not isinstance(value, dict):
            raise QuotationValidationError(f"{name} must be an object")

    _reject_unknown(
        document,
        {"quote_reference", "quote_date", "validity_days", "status"},
        "document",
    )
    _reject_unknown(
        client,
        {"company", "attention", "salutation", "business_address"},
        "client",
    )
    _reject_unknown(project, {"title", "subtitle", "location"}, "project")
    _reject_unknown(
        pricing,
        {"currency", "tax_treatment", "vat_rate", "items", "sections", "amount_in_words"},
        "pricing",
    )
    _reject_unknown(
        signatures,
        {
            "prepared_name",
            "prepared_role",
            "accepted_name",
            "accepted_company",
            "accepted_detail",
        },
        "signatures",
    )

    required_document_keys = ["quote_date"]
    if template_version == TEMPLATE_ID:
        required_document_keys.append("quote_reference")
    for key in required_document_keys:
        _text(_required(document, key, "document"), f"document.{key}")
    if "quote_reference" in document:
        _text(document["quote_reference"], "document.quote_reference", allow_empty=True)
    if "status" in document:
        _text(document["status"], "document.status")
    try:
        date.fromisoformat(document["quote_date"])
    except (TypeError, ValueError):
        raise QuotationValidationError("document.quote_date must use YYYY-MM-DD") from None
    validity_days = _required(document, "validity_days", "document")
    if not isinstance(validity_days, int) or isinstance(validity_days, bool) or validity_days < 1:
        raise QuotationValidationError("document.validity_days must be a positive integer")

    for key in ("company", "attention"):
        _text(_required(client, key, "client"), f"client.{key}")
    if "business_address" in client:
        _text(client["business_address"], "client.business_address", allow_empty=True)
    if "salutation" in client:
        _text(client["salutation"], "client.salutation")

    for key in ("title", "subtitle", "location"):
        _text(_required(project, key, "project"), f"project.{key}")

    introduction = _required(data, "introduction", "$" )
    if not isinstance(introduction, list) or not introduction:
        raise QuotationValidationError("introduction must be a non-empty list of paragraphs")
    for index, item in enumerate(introduction):
        _text(item, f"introduction[{index}]")

    if pricing.get("currency") != "PHP":
        raise QuotationValidationError("pricing.currency must be PHP")
    vat_rate = _decimal(_required(pricing, "vat_rate", "pricing"), "pricing.vat_rate")
    if template_version == TEMPLATE_ID:
        if vat_rate != Decimal("0.12"):
            raise QuotationValidationError(
                "pricing.vat_rate must be 0.12 for this template release"
            )
        if pricing.get("tax_treatment") != "VAT Inclusive":
            raise QuotationValidationError("pricing.tax_treatment must be VAT Inclusive")
    else:
        if vat_rate != Decimal("0"):
            raise QuotationValidationError(
                "pricing.vat_rate must be 0 for VAT Exclusive quotations"
            )
        if pricing.get("tax_treatment") != "VAT Exclusive":
            raise QuotationValidationError("pricing.tax_treatment must be VAT Exclusive")

    if "amount_in_words" in pricing:
        _text(pricing["amount_in_words"], "pricing.amount_in_words")

    def validate_item(item: Any, path: str) -> None:
        if not isinstance(item, dict):
            raise QuotationValidationError(f"{path} must be an object")
        _reject_unknown(
            item,
            {
                "item_code",
                "quantity",
                "unit",
                "title",
                "description",
                "unit_price",
                "amount",
            },
            path,
        )
        _decimal(_required(item, "quantity", path), f"{path}.quantity", positive=True)
        _decimal(_required(item, "unit_price", path), f"{path}.unit_price", positive=True)
        for key in ("unit", "title"):
            _text(_required(item, key, path), f"{path}.{key}")
        _text(
            _required(item, "description", path),
            f"{path}.description",
            allow_empty=template_version == LIFES_AWESOME_TEMPLATE_ID,
        )
        if "item_code" in item:
            _text(item["item_code"], f"{path}.item_code")
        if "amount" in item:
            raise QuotationValidationError(
                f"{path}.amount is not accepted; the engine calculates line amounts"
            )

    if template_version == TEMPLATE_ID:
        if "sections" in pricing:
            raise QuotationValidationError(
                "pricing.sections is not supported by the LAVI-QUOTATION-2026.2 template"
            )
        items = _required(pricing, "items", "pricing")
        if not isinstance(items, list) or not items:
            raise QuotationValidationError("pricing.items must be a non-empty list")
        for index, item in enumerate(items):
            validate_item(item, f"pricing.items[{index}]")
    else:
        if "items" in pricing:
            raise QuotationValidationError(
                "pricing.items is not supported by the Lifes Awesome grouped template"
            )
        sections = _required(pricing, "sections", "pricing")
        if not isinstance(sections, list) or not sections:
            raise QuotationValidationError("pricing.sections must be a non-empty list")
        for section_index, section in enumerate(sections):
            section_path = f"pricing.sections[{section_index}]"
            if not isinstance(section, dict):
                raise QuotationValidationError(f"{section_path} must be an object")
            _reject_unknown(section, {"code", "title", "items"}, section_path)
            _text(_required(section, "code", section_path), f"{section_path}.code")
            _text(_required(section, "title", section_path), f"{section_path}.title")
            section_items = _required(section, "items", section_path)
            if not isinstance(section_items, list) or not section_items:
                raise QuotationValidationError(
                    f"{section_path}.items must be a non-empty list"
                )
            for item_index, item in enumerate(section_items):
                validate_item(item, f"{section_path}.items[{item_index}]")

    if "pricing_basis" in data:
        _text(data["pricing_basis"], "pricing_basis")

    notes = _required(data, "additional_notes", "$" )
    if not isinstance(notes, list) or not notes:
        raise QuotationValidationError("additional_notes must be a non-empty list")
    for index, note in enumerate(notes):
        path = f"additional_notes[{index}]"
        if not isinstance(note, dict):
            raise QuotationValidationError(f"{path} must be an object")
        _reject_unknown(note, {"heading", "text"}, path)
        _text(_required(note, "heading", path), f"{path}.heading")
        _text(_required(note, "text", path), f"{path}.text")

    for key in ("prepared_name", "prepared_role"):
        _text(_required(signatures, key, "signatures"), f"signatures.{key}")
    for key in ("accepted_name", "accepted_company", "accepted_detail"):
        value = _required(signatures, key, "signatures")
        _text(
            value,
            f"signatures.{key}",
            allow_empty=template_version == LIFES_AWESOME_TEMPLATE_ID,
        )

    combined_text = "\n".join(_walk_text(data)).lower()
    for phrase in PROHIBITED_RELEASE_TEXT:
        if phrase in combined_text:
            raise QuotationValidationError(f"Prohibited template wording detected: {phrase}")

    calculate_totals(data)
    return data


def load_and_validate(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise QuotationValidationError(f"Quotation data file not found: {source}") from None
    except json.JSONDecodeError as exc:
        raise QuotationValidationError(
            f"Invalid JSON in {source}: line {exc.lineno}, column {exc.colno}"
        ) from None
    return validate_quotation(data)
