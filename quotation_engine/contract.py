"""Immutable geometry and brand contract for the approved LAVI template."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import legal
from reportlab.lib.units import inch


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent
LOGO_PATH = (
    REPOSITORY_ROOT
    / "templates"
    / "lavi"
    / "quotation-2026"
    / "LAVI_New_Logo_2026.png"
)
MANIFEST_PATH = PACKAGE_ROOT / "manifest.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "quotation.schema.json"

TEMPLATE_ID = "LAVI-QUOTATION-2026.2"
TEMPLATE_STATUS = "APPROVED_LOCKED"
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

PAGE_WIDTH, PAGE_HEIGHT = legal
LEFT_MARGIN = RIGHT_MARGIN = 0.55 * inch
TOP_MARGIN = 0.42 * inch
BOTTOM_MARGIN = 0.52 * inch
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

# Approved pricing columns: QTY / UNIT / DESCRIPTION / UNIT PRICE / AMOUNT.
PRICING_COLUMN_WIDTHS = (32.5, 36.0, 275.5, 94.4, 94.4)
TOTALS_COLUMN_WIDTHS = PRICING_COLUMN_WIDTHS[-2:]
TOTALS_LEFT_EDGE = LEFT_MARGIN + sum(PRICING_COLUMN_WIDTHS[:3])

TEAL_HEX = "#03A5B0"
NAVY_HEX = "#324F79"
INK_HEX = "#26364A"
MUTED_HEX = "#6C7A8C"
PALE_TEAL_HEX = "#EAF7F8"
PALE_BLUE_HEX = "#EEF2F7"
PALE_GOLD_HEX = "#FFF5D8"
GRID_HEX = "#CDD7E0"
ROW_ALT_HEX = "#F7FAFC"
TITLE_BG_HEX = "#F6F9FB"

TEAL = colors.HexColor(TEAL_HEX)
NAVY = colors.HexColor(NAVY_HEX)
INK = colors.HexColor(INK_HEX)
MUTED = colors.HexColor(MUTED_HEX)
PALE_TEAL = colors.HexColor(PALE_TEAL_HEX)
PALE_BLUE = colors.HexColor(PALE_BLUE_HEX)
PALE_GOLD = colors.HexColor(PALE_GOLD_HEX)
GRID = colors.HexColor(GRID_HEX)
ROW_ALT = colors.HexColor(ROW_ALT_HEX)
TITLE_BG = colors.HexColor(TITLE_BG_HEX)
WHITE = colors.white

COMPANY_NAME = "LAVI TECHNOLOGIES INC."
COMPANY_ADDRESS = (
    "C-One Industrial Park, Rodolfo Pelaez Boulevard, Kauswagan, "
    "Cagayan de Oro City"
)
COMPANY_CONTACT = (
    "0939 926 4230 / 0917 308 2354 | "
    "info@lavitechnologies.com | www.lavitechnologies.com"
)

LOCKED_SECTION_TITLES = {
    "title_eyebrow": "PREPARED QUOTATION FOR",
    "pricing": "SCOPE AND PRICING",
    "notes": "ADDITIONAL NOTES",
}

PROHIBITED_RELEASE_TEXT = (
    "approval by the authority having jurisdiction cannot be guaranteed",
    "release condition",
    "professional quotation",
)
