"""Command-line interface for validating and rendering quotation job files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .contract import MANIFEST_PATH
from .renderer import render_quotation
from .validation import QuotationValidationError, calculate_totals, load_and_validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Locked LAVI quotation engine")
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser("validate", help="Validate a quotation job")
    validate.add_argument("job", type=Path)

    render = subcommands.add_parser("render", help="Validate and render a quotation PDF")
    render.add_argument("job", type=Path)
    render.add_argument("--output", required=True, type=Path)

    subcommands.add_parser("manifest", help="Print the locked template manifest")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "manifest":
            print(MANIFEST_PATH.read_text(encoding="utf-8"))
            return 0

        data = load_and_validate(args.job)
        totals = calculate_totals(data)
        if args.command == "validate":
            print(
                "VALID "
                f"subtotal=P {totals['subtotal']:,.2f} "
                f"vat=P {totals['vat']:,.2f} "
                f"grand_total=P {totals['grand_total']:,.2f}"
            )
            return 0

        output = render_quotation(data, args.output)
        print(json.dumps({"status": "rendered", "output": str(output), "totals": {k: str(v) for k, v in totals.items()}}))
        return 0
    except (QuotationValidationError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
