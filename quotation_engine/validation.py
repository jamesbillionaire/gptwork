"""Structured-data validation and commercial arithmetic for quotations."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from .contract import PROHIBITED_RELEASE_TEXT, TEMPLATE_ID


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


def calculate_totals(data: dict[str, Any]) -> dict[str, Decimal]:
    items = data["pricing"]["items"]
    subtotal = sum(
        (_decimal(item["quantity"], "pricing.items.quantity", positive=True)
         * _decimal(item["unit_price"], "pricing.items.unit_price", positive=True))
        for item in items
    ).quantize(MONEY, rounding=ROUND_HALF_UP)
    vat_rate = _decimal(data["pricing"]["vat_rate"], "pricing.vat_rate")
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
    if template_version != TEMPLATE_ID:
        raise QuotationValidationError(
            f"template_version must be exactly {TEMPLATE_ID}; received {template_version}"
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

    _reject_unknown(document, {"quote_reference", "quote_date", "validity_days"}, "document")
    _reject_unknown(client, {"company", "attention", "business_address"}, "client")
    _reject_unknown(project, {"title", "subtitle", "location"}, "project")
    _reject_unknown(pricing, {"currency", "tax_treatment", "vat_rate", "items"}, "pricing")
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

    for key in ("quote_reference", "quote_date"):
        _text(_required(document, key, "document"), f"document.{key}")
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
    if vat_rate != Decimal("0.12"):
        raise QuotationValidationError("pricing.vat_rate must be 0.12 for this template release")
    if pricing.get("tax_treatment") != "VAT Inclusive":
        raise QuotationValidationError("pricing.tax_treatment must be VAT Inclusive")

    items = _required(pricing, "items", "pricing")
    if not isinstance(items, list) or not items:
        raise QuotationValidationError("pricing.items must be a non-empty list")
    for index, item in enumerate(items):
        path = f"pricing.items[{index}]"
        if not isinstance(item, dict):
            raise QuotationValidationError(f"{path} must be an object")
        _reject_unknown(
            item,
            {"quantity", "unit", "title", "description", "unit_price", "amount"},
            path,
        )
        _decimal(_required(item, "quantity", path), f"{path}.quantity", positive=True)
        _decimal(_required(item, "unit_price", path), f"{path}.unit_price", positive=True)
        for key in ("unit", "title", "description"):
            _text(_required(item, key, path), f"{path}.{key}")
        if "amount" in item:
            raise QuotationValidationError(
                f"{path}.amount is not accepted; the engine calculates line amounts"
            )

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

    for key in (
        "prepared_name",
        "prepared_role",
        "accepted_name",
        "accepted_company",
        "accepted_detail",
    ):
        _text(_required(signatures, key, "signatures"), f"signatures.{key}")

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
