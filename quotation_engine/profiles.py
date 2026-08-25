"""Locked brand profiles supported by the quotation engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import Color

from .contract import (
    COMPANY_ADDRESS,
    COMPANY_CONTACT,
    COMPANY_NAME,
    GRID,
    INK,
    LOCKED_SECTION_TITLES,
    LOGO_PATH,
    MUTED,
    NAVY,
    PALE_BLUE,
    PALE_GOLD,
    PALE_TEAL,
    REPOSITORY_ROOT,
    ROW_ALT,
    TEAL,
    TEMPLATE_ID,
    TITLE_BG,
    WHITE,
)


LIFES_AWESOME_TEMPLATE_ID = "LIFES-AWESOME-QUOTATION-2026.1"


@dataclass(frozen=True)
class TemplateProfile:
    """Brand and presentation values selected by template_version."""

    template_id: str
    company_name: str
    company_address: str
    company_contact: str
    logo_path: Path
    logo_width_inches: float
    logo_height_inches: float
    metadata_brand: str
    section_titles: dict[str, str]
    teal: Color
    navy: Color
    ink: Color
    muted: Color
    pale_teal: Color
    pale_blue: Color
    pale_gold: Color
    grid: Color
    row_alt: Color
    title_bg: Color
    white: Color
    grouped_pricing: bool = False


LAVI_PROFILE = TemplateProfile(
    template_id=TEMPLATE_ID,
    company_name=COMPANY_NAME,
    company_address=COMPANY_ADDRESS,
    company_contact=COMPANY_CONTACT,
    logo_path=LOGO_PATH,
    logo_width_inches=1.42,
    logo_height_inches=0.465,
    metadata_brand="LAVI Technologies Inc.",
    section_titles=LOCKED_SECTION_TITLES,
    teal=TEAL,
    navy=NAVY,
    ink=INK,
    muted=MUTED,
    pale_teal=PALE_TEAL,
    pale_blue=PALE_BLUE,
    pale_gold=PALE_GOLD,
    grid=GRID,
    row_alt=ROW_ALT,
    title_bg=TITLE_BG,
    white=WHITE,
)

LIFES_AWESOME_PROFILE = TemplateProfile(
    template_id=LIFES_AWESOME_TEMPLATE_ID,
    company_name="LIFES AWESOME VENTURES INC.",
    company_address=(
        "C-One Industrial Park, Rodolfo Palaez Blvd., Kauswagan, "
        "Cagayan De Oro City"
    ),
    company_contact="0939-9264230 / 09173082354 | james@brownjourney.com",
    logo_path=(
        REPOSITORY_ROOT
        / "templates"
        / "lifes-awesome"
        / "quotation-2026"
        / "Lifes-Awesome-Logo.png"
    ),
    logo_width_inches=2.55,
    logo_height_inches=0.502,
    metadata_brand="Lifes Awesome Ventures Inc.",
    section_titles={
        "title_eyebrow": "COMMERCIAL AND TECHNICAL QUOTATION",
        "pricing": "SCOPE AND PRICING",
        "summary": "PROJECT COST SUMMARY",
        "notes": "ADDITIONAL NOTES",
    },
    teal=colors.HexColor("#00ADED"),
    navy=colors.HexColor("#555B63"),
    ink=colors.HexColor("#242A31"),
    muted=colors.HexColor("#6B7280"),
    pale_teal=colors.HexColor("#EAF8FD"),
    pale_blue=colors.HexColor("#F1F3F5"),
    pale_gold=colors.HexColor("#FFF5D8"),
    grid=colors.HexColor("#CBD3DA"),
    row_alt=colors.HexColor("#F7FAFC"),
    title_bg=colors.HexColor("#F5FAFC"),
    white=colors.white,
    grouped_pricing=True,
)

TEMPLATE_PROFILES = {
    LAVI_PROFILE.template_id: LAVI_PROFILE,
    LIFES_AWESOME_PROFILE.template_id: LIFES_AWESOME_PROFILE,
}


def get_template_profile(template_id: str) -> TemplateProfile:
    """Return the locked profile for a validated template ID."""

    try:
        return TEMPLATE_PROFILES[template_id]
    except KeyError:
        supported = ", ".join(sorted(TEMPLATE_PROFILES))
        raise ValueError(
            f"Unsupported template_version {template_id}; expected one of: {supported}"
        ) from None
