"""Deterministic PDF renderer for the locked LAVI quotation template."""

from __future__ import annotations

from copy import copy
from datetime import date
from decimal import Decimal
from functools import partial
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .contract import (
    BOTTOM_MARGIN,
    CONTENT_WIDTH,
    FONT_BOLD,
    FONT_REGULAR,
    LEFT_MARGIN,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    PRICING_COLUMN_WIDTHS,
    RIGHT_MARGIN,
    TOP_MARGIN,
    TOTALS_COLUMN_WIDTHS,
)
from .profiles import TemplateProfile, get_template_profile
from .validation import (
    calculate_section_totals,
    calculate_totals,
    validate_quotation,
)


def _safe(value: object) -> str:
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})


def _safe_lines(value: object) -> str:
    return _safe(value).replace("\n", "<br/>")


def _format_money(value: Decimal) -> str:
    return f"P {value:,.2f}"


def _format_quantity(value: object) -> str:
    number = Decimal(str(value))
    if number == number.to_integral():
        return f"{number:.0f}"
    return format(number.normalize(), "f")


def _format_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.day} {parsed.strftime('%B %Y')}"


def register_fonts() -> None:
    """PDF-standard fonts require no external registration."""


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas with deterministic metadata and Page x of y footers."""

    def __init__(
        self,
        *args,
        footer_label: str,
        profile: TemplateProfile,
        **kwargs,
    ):
        if kwargs.get("invariant") is None:
            kwargs["invariant"] = 1
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []
        self._footer_label = footer_label
        self._profile = profile

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(page_count)
            super().showPage()
        super().save()

    def _draw_footer(self, page_count: int) -> None:
        y = 0.27 * inch
        self.setStrokeColor(self._profile.grid)
        self.setLineWidth(0.55)
        self.line(LEFT_MARGIN, y + 11, PAGE_WIDTH - RIGHT_MARGIN, y + 11)
        self.setFillColor(self._profile.muted)
        self.setFont(FONT_REGULAR, 7.1)
        self.drawString(LEFT_MARGIN, y, self._footer_label)
        self.drawRightString(
            PAGE_WIDTH - RIGHT_MARGIN,
            y,
            f"Page {self._pageNumber} of {page_count}",
        )


def _paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def _build_styles(profile: TemplateProfile) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "LAVIBody",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=8.35,
            leading=10.6,
            textColor=profile.ink,
            spaceAfter=4,
        ),
        "muted": ParagraphStyle(
            "LAVIMuted",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=7.2,
            leading=9.1,
            textColor=profile.muted,
        ),
        "center_small": ParagraphStyle(
            "LAVICenterSmall",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=6.55,
            leading=8.0,
            alignment=TA_CENTER,
            textColor=profile.muted,
        ),
        "title": ParagraphStyle(
            "LAVITitle",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=11.6,
            leading=13.5,
            alignment=TA_LEFT,
            textColor=profile.navy,
            spaceAfter=2,
        ),
        "title_eyebrow": ParagraphStyle(
            "LAVITitleEyebrow",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.9,
            leading=8.2,
            alignment=TA_LEFT,
            textColor=profile.teal,
        ),
        "subtitle": ParagraphStyle(
            "LAVISubtitle",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=7.8,
            leading=9.4,
            alignment=TA_LEFT,
            textColor=profile.muted,
        ),
        "section": ParagraphStyle(
            "LAVISection",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=9.4,
            leading=11.0,
            textColor=profile.teal,
            spaceAfter=0,
        ),
        "label": ParagraphStyle(
            "LAVILabel",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.5,
            leading=7.7,
            textColor=profile.teal,
            spaceAfter=2,
        ),
        "value": ParagraphStyle(
            "LAVIValue",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=8.15,
            leading=10.0,
            textColor=profile.ink,
        ),
        "table_header": ParagraphStyle(
            "LAVITableHeader",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.7,
            leading=7.8,
            alignment=TA_CENTER,
            textColor=profile.white,
        ),
        "table_text": ParagraphStyle(
            "LAVITableText",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=6.65,
            leading=8.15,
            textColor=profile.ink,
        ),
        "table_center": ParagraphStyle(
            "LAVITableCenter",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=6.65,
            leading=8.15,
            alignment=TA_CENTER,
            textColor=profile.ink,
        ),
        "table_qty": ParagraphStyle(
            "LAVITableQty",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=6.65,
            leading=8.15,
            alignment=TA_RIGHT,
            textColor=profile.ink,
        ),
        "table_right": ParagraphStyle(
            "LAVITableRight",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.75,
            leading=8.15,
            alignment=TA_RIGHT,
            textColor=profile.ink,
        ),
        "pricing_section": ParagraphStyle(
            "LAVIPricingSection",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=7.2,
            leading=8.7,
            textColor=profile.navy,
        ),
        "section_total_label": ParagraphStyle(
            "LAVISectionTotalLabel",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.75,
            leading=8.15,
            alignment=TA_RIGHT,
            textColor=profile.ink,
        ),
        "total_label": ParagraphStyle(
            "LAVITotalLabel",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.75,
            leading=8.15,
            alignment=TA_RIGHT,
            textColor=profile.ink,
        ),
        "total_amount": ParagraphStyle(
            "LAVITotalAmount",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.75,
            leading=8.15,
            alignment=TA_RIGHT,
            textColor=profile.ink,
        ),
        "grand_label": ParagraphStyle(
            "LAVIGrandLabel",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=10.2,
            alignment=TA_RIGHT,
            textColor=profile.navy,
        ),
        "grand_amount": ParagraphStyle(
            "LAVIGrandAmount",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=10.2,
            alignment=TA_RIGHT,
            textColor=profile.navy,
        ),
        "condition": ParagraphStyle(
            "LAVICondition",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=7.75,
            leading=10.2,
            leftIndent=15,
            firstLineIndent=-15,
            spaceAfter=6,
            textColor=profile.ink,
        ),
        "signature_label": ParagraphStyle(
            "LAVISignatureLabel",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=6.6,
            leading=8,
            textColor=profile.teal,
        ),
        "signature_name": ParagraphStyle(
            "LAVISignatureName",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=10.2,
            textColor=profile.ink,
        ),
    }


def _section_heading(
    text: str,
    styles: dict[str, ParagraphStyle],
    profile: TemplateProfile,
) -> Table:
    heading = Table(
        [[_paragraph(_safe(text.upper()), styles["section"])]],
        colWidths=[CONTENT_WIDTH],
    )
    heading.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 1.1, profile.teal),
            ]
        )
    )
    return heading


def _draw_continuation_header(
    quote_reference: str,
    profile: TemplateProfile,
):
    def draw(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
        if doc.page == 1:
            return
        y = PAGE_HEIGHT - 0.31 * inch
        canv.saveState()
        canv.setStrokeColor(profile.teal)
        canv.setLineWidth(1.2)
        canv.line(LEFT_MARGIN, y, PAGE_WIDTH - RIGHT_MARGIN, y)
        canv.setFont(FONT_BOLD, 7.5)
        canv.setFillColor(profile.navy)
        canv.drawString(LEFT_MARGIN, y - 12, profile.company_name)
        canv.setFont(FONT_REGULAR, 7.2)
        canv.setFillColor(profile.muted)
        canv.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, y - 12, quote_reference)
        canv.restoreState()

    return draw


def _title_style(title: str, styles: dict[str, ParagraphStyle]) -> ParagraphStyle:
    style = copy(styles["title"])
    # Deterministic scale rule keeps ordinary project titles to one line when possible.
    if len(title) > 78:
        style.fontSize = 10.2
        style.leading = 12.2
    elif len(title) > 64:
        style.fontSize = 10.8
        style.leading = 12.8
    return style


def _build_pricing_table(
    data: dict,
    styles: dict[str, ParagraphStyle],
    profile: TemplateProfile,
) -> Table:
    raw_rows = [["QTY", "UNIT", "DESCRIPTION / ACTIVITY", "UNIT PRICE", "AMOUNT"]]
    for item in data["pricing"]["items"]:
        quantity = Decimal(str(item["quantity"]))
        unit_price = Decimal(str(item["unit_price"]))
        amount = quantity * unit_price
        item_code = item.get("item_code")
        title = f"{item_code} - {item['title']}" if item_code else item["title"]
        description = f"<b>{_safe(title)}</b>"
        if item["description"]:
            description += f"<br/>{_safe_lines(item['description'])}"
        raw_rows.append(
            [
                _format_quantity(quantity),
                _safe(item["unit"]).upper(),
                description,
                _format_money(unit_price),
                _format_money(amount),
            ]
        )

    rows = []
    for index, row in enumerate(raw_rows):
        if index == 0:
            rows.append([_paragraph(cell, styles["table_header"]) for cell in row])
        else:
            rows.append(
                [
                    _paragraph(row[0], styles["table_qty"]),
                    _paragraph(row[1], styles["table_center"]),
                    _paragraph(row[2], styles["table_text"]),
                    _paragraph(row[3], styles["table_right"]),
                    _paragraph(row[4], styles["table_right"]),
                ]
            )

    table = Table(
        rows,
        colWidths=list(PRICING_COLUMN_WIDTHS),
        repeatRows=1,
        splitByRow=1,
        splitInRow=0,
        hAlign="LEFT",
    )
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), profile.navy),
        ("LINEABOVE", (0, 0), (-1, 0), 1.4, profile.teal),
        ("GRID", (0, 0), (-1, -1), 0.45, profile.grid),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("ALIGN", (0, 1), (0, -1), "RIGHT"),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("ALIGN", (3, 1), (4, -1), "RIGHT"),
    ]
    for index in range(1, len(rows)):
        if index % 2 == 0:
            commands.append(("BACKGROUND", (0, index), (-1, index), profile.row_alt))
    table.setStyle(TableStyle(commands))
    return table


def _build_grouped_pricing(
    data: dict,
    styles: dict[str, ParagraphStyle],
    profile: TemplateProfile,
) -> list:
    """Build independently flowing section tables with calculated subtotals."""

    tables = []
    section_totals = calculate_section_totals(data)
    for section_index, (section, section_total) in enumerate(
        zip(data["pricing"]["sections"], section_totals)
    ):
        rows = [
            [
                _paragraph(
                    f"{_safe(section['code'])}. {_safe(section['title'])}",
                    styles["pricing_section"],
                ),
                "",
                "",
                "",
                "",
            ],
            [
                _paragraph("QTY", styles["table_header"]),
                _paragraph("UNIT", styles["table_header"]),
                _paragraph("DESCRIPTION / ACTIVITY", styles["table_header"]),
                _paragraph("UNIT PRICE", styles["table_header"]),
                _paragraph("AMOUNT", styles["table_header"]),
            ],
        ]
        for item in section["items"]:
            quantity = Decimal(str(item["quantity"]))
            unit_price = Decimal(str(item["unit_price"]))
            amount = quantity * unit_price
            item_code = item.get("item_code")
            title = f"{item_code} - {item['title']}" if item_code else item["title"]
            description = f"<b>{_safe(title)}</b>"
            if item["description"]:
                description += f"<br/>{_safe_lines(item['description'])}"
            rows.append(
                [
                    _paragraph(_format_quantity(quantity), styles["table_qty"]),
                    _paragraph(_safe(item["unit"]).upper(), styles["table_center"]),
                    _paragraph(description, styles["table_text"]),
                    _paragraph(_format_money(unit_price), styles["table_right"]),
                    _paragraph(_format_money(amount), styles["table_right"]),
                ]
            )
        subtotal_row = len(rows)
        rows.append(
            [
                _paragraph(
                    f"SECTION {_safe(section['code'])} SUBTOTAL",
                    styles["section_total_label"],
                ),
                "",
                "",
                "",
                _paragraph(_format_money(section_total), styles["table_right"]),
            ]
        )

        table = Table(
            rows,
            colWidths=list(PRICING_COLUMN_WIDTHS),
            repeatRows=2,
            splitByRow=1,
            splitInRow=0,
            hAlign="LEFT",
        )
        commands = [
            ("SPAN", (0, 0), (-1, 0)),
            ("SPAN", (0, subtotal_row), (3, subtotal_row)),
            ("NOSPLIT", (0, subtotal_row - 1), (-1, subtotal_row)),
            ("BACKGROUND", (0, 0), (-1, 0), profile.pale_teal),
            ("BACKGROUND", (0, 1), (-1, 1), profile.navy),
            ("BACKGROUND", (0, subtotal_row), (-1, subtotal_row), profile.pale_blue),
            ("LINEABOVE", (0, 0), (-1, 0), 1.4, profile.teal),
            ("GRID", (0, 0), (-1, -1), 0.45, profile.grid),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, 0), 5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            ("TOPPADDING", (0, 1), (-1, 1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
            ("TOPPADDING", (0, 2), (-1, subtotal_row - 1), 5),
            ("BOTTOMPADDING", (0, 2), (-1, subtotal_row - 1), 5),
            ("TOPPADDING", (0, subtotal_row), (-1, subtotal_row), 6),
            ("BOTTOMPADDING", (0, subtotal_row), (-1, subtotal_row), 6),
            ("ALIGN", (0, 2), (0, subtotal_row - 1), "RIGHT"),
            ("ALIGN", (1, 2), (1, subtotal_row - 1), "CENTER"),
            ("ALIGN", (3, 2), (4, -1), "RIGHT"),
        ]
        for row_index in range(2, subtotal_row):
            if (row_index - 2) % 2 == 1:
                commands.append(
                    ("BACKGROUND", (0, row_index), (-1, row_index), profile.row_alt)
                )
        table.setStyle(TableStyle(commands))
        tables.append(table)
        if section_index < len(data["pricing"]["sections"]) - 1:
            tables.append(Spacer(1, 7))
    return tables


def _build_project_summary(
    data: dict,
    styles: dict[str, ParagraphStyle],
    profile: TemplateProfile,
) -> Table:
    section_totals = calculate_section_totals(data)
    rows = []
    for section, amount in zip(data["pricing"]["sections"], section_totals):
        rows.append(
            [
                _paragraph(
                    f"{_safe(section['code'])}. {_safe(section['title'])}",
                    styles["table_text"],
                ),
                "",
                "",
                "",
                _paragraph(_format_money(amount), styles["table_right"]),
            ]
        )
    total_row = len(rows)
    grand_total = calculate_totals(data)["grand_total"]
    rows.append(
        [
            _paragraph("TOTAL QUOTATION, VAT EXCLUSIVE", styles["grand_label"]),
            "",
            "",
            "",
            _paragraph(_format_money(grand_total), styles["grand_amount"]),
        ]
    )
    table = Table(rows, colWidths=list(PRICING_COLUMN_WIDTHS), hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.5, profile.grid),
        ("BACKGROUND", (0, total_row), (-1, total_row), profile.pale_gold),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (4, 0), (4, -1), "RIGHT"),
    ]
    for row_index in range(len(rows)):
        commands.append(("SPAN", (0, row_index), (3, row_index)))
    for row_index in range(total_row):
        commands.append(
            (
                "BACKGROUND",
                (0, row_index),
                (-1, row_index),
                profile.row_alt if row_index % 2 else profile.white,
            )
        )
    table.setStyle(TableStyle(commands))
    return table


def _build_totals(
    data: dict,
    styles: dict[str, ParagraphStyle],
    profile: TemplateProfile,
) -> Table:
    totals = calculate_totals(data)
    vat_percent = int(Decimal(str(data["pricing"]["vat_rate"])) * 100)
    table = Table(
        [
            [
                _paragraph("SUBTOTAL", styles["total_label"]),
                _paragraph(_format_money(totals["subtotal"]), styles["total_amount"]),
            ],
            [
                _paragraph(f"{vat_percent}% VAT", styles["total_label"]),
                _paragraph(_format_money(totals["vat"]), styles["total_amount"]),
            ],
            [
                _paragraph("GRAND TOTAL", styles["grand_label"]),
                _paragraph(_format_money(totals["grand_total"]), styles["grand_amount"]),
            ],
        ],
        colWidths=list(TOTALS_COLUMN_WIDTHS),
        hAlign="RIGHT",
    )
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, profile.grid),
                ("BACKGROUND", (0, 0), (-1, 0), profile.white),
                ("BACKGROUND", (0, 1), (-1, 1), profile.pale_blue),
                ("BACKGROUND", (0, 2), (-1, 2), profile.pale_gold),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def render_quotation(data: dict, output_path: str | Path) -> Path:
    """Validate and render one quotation without allowing layout overrides."""

    validate_quotation(data)
    register_fonts()
    profile = get_template_profile(data["template_version"])
    styles = _build_styles(profile)

    output = Path(output_path)
    if output.suffix.lower() != ".pdf":
        raise ValueError("Output path must end in .pdf")
    output.parent.mkdir(parents=True, exist_ok=True)

    reference = data["document"].get("quote_reference") or data["document"].get(
        "status", "QUOTATION"
    )
    footer_label = (
        f"{profile.company_name} | {data['client']['company']} QUOTATION".upper()
    )
    doc = BaseDocTemplate(
        str(output),
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=f"{profile.metadata_brand} Quotation - {data['project']['title']}",
        author=profile.metadata_brand,
        subject=data["project"]["subtitle"],
        keywords=(
            f"{profile.metadata_brand}, quotation, "
            f"{data['client']['company']}, {reference}"
        ),
    )

    first_frame = Frame(
        LEFT_MARGIN,
        BOTTOM_MARGIN + 0.08 * inch,
        CONTENT_WIDTH,
        PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN - 0.08 * inch,
        id="first",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    continuation_frame = Frame(
        LEFT_MARGIN,
        BOTTOM_MARGIN + 0.08 * inch,
        CONTENT_WIDTH,
        PAGE_HEIGHT - 0.72 * inch - BOTTOM_MARGIN - 0.08 * inch,
        id="continuation",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    continuation_header = _draw_continuation_header(reference, profile)
    doc.addPageTemplates(
        [
            PageTemplate(
                id="First",
                frames=[first_frame],
                onPage=continuation_header,
                autoNextPageTemplate="Later",
            ),
            PageTemplate(
                id="Later",
                frames=[continuation_frame],
                onPage=continuation_header,
                autoNextPageTemplate="Later",
            ),
        ]
    )

    story = []
    top_rule = Table([[""]], colWidths=[CONTENT_WIDTH], rowHeights=[3])
    top_rule.setStyle(
        TableStyle([("BACKGROUND", (0, 0), (-1, -1), profile.teal)])
    )
    story.extend([top_rule, Spacer(1, 5)])

    logo = Image(
        str(profile.logo_path),
        width=profile.logo_width_inches * inch,
        height=profile.logo_height_inches * inch,
    )
    logo.hAlign = "CENTER"
    story.append(logo)
    company_contact = _safe(profile.company_contact)
    if not profile.grouped_pricing:
        company_contact = company_contact.replace(" | ", " &nbsp;|&nbsp; ")
    story.append(
        _paragraph(
            f"{_safe(profile.company_address)}<br/>"
            f"{company_contact}",
            styles["center_small"],
        )
    )
    story.append(Spacer(1, 7))

    project_title = data["project"]["title"]
    title_box = Table(
        [
            [
                _paragraph(
                    profile.section_titles["title_eyebrow"],
                    styles["title_eyebrow"],
                )
            ],
            [_paragraph(_safe(project_title), _title_style(project_title, styles))],
            [_paragraph(_safe(data["project"]["subtitle"]), styles["subtitle"])],
        ],
        colWidths=[CONTENT_WIDTH],
    )
    title_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), profile.title_bg),
                ("BOX", (0, 0), (-1, -1), 0.55, profile.grid),
                ("LINEABOVE", (0, 0), (-1, 0), 2.0, profile.teal),
                ("LINEBELOW", (0, 2), (-1, 2), 0.7, profile.navy),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, 0), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 0),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 2),
                ("TOPPADDING", (0, 2), (-1, 2), 0),
                ("BOTTOMPADDING", (0, 2), (-1, 2), 7),
            ]
        )
    )
    story.extend([title_box, Spacer(1, 8)])

    prepared_lines = [data["client"]["attention"], data["client"]["company"]]
    if data["client"].get("business_address"):
        prepared_lines.append(data["client"]["business_address"])
    prepared_for = "<br/>".join(_safe(line) for line in prepared_lines)
    if profile.grouped_pricing:
        quote_details = (
            f"<font size='7' color='#6B7280'>Status:</font> "
            f"{_safe(data['document'].get('status', 'Quotation'))}"
            f"<br/><font size='7' color='#6B7280'>Date:</font> "
            f"{_format_date(data['document']['quote_date'])}"
            f"<br/><font size='7' color='#6B7280'>Validity:</font> "
            f"{data['document']['validity_days']} calendar days"
            f"<br/><font size='7' color='#6B7280'>Pricing:</font> "
            f"{_safe(data['pricing']['tax_treatment'])}"
        )
    else:
        quote_details = (
            f"<font size='7' color='#6C7A8C'>Reference:</font> {_safe(reference)}"
            f"<br/><font size='7' color='#6C7A8C'>Date:</font> {_format_date(data['document']['quote_date'])}"
            f"<br/><font size='7' color='#6C7A8C'>Validity:</font> {data['document']['validity_days']} calendar days"
        )
    info_data = [
        [
            [
                _paragraph("PREPARED FOR", styles["label"]),
                _paragraph(prepared_for, styles["value"]),
            ],
            [
                _paragraph("QUOTE DETAILS", styles["label"]),
                _paragraph(quote_details, styles["value"]),
            ],
        ],
        [
            [
                _paragraph("PROJECT LOCATION", styles["label"]),
                _paragraph(_safe(data["project"]["location"]), styles["value"]),
            ],
            [
                _paragraph("ATTENTION", styles["label"]),
                _paragraph(_safe(data["client"]["attention"]), styles["value"]),
            ],
        ],
    ]
    info_table = Table(info_data, colWidths=[CONTENT_WIDTH * 0.61, CONTENT_WIDTH * 0.39])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), profile.pale_teal),
                ("BACKGROUND", (1, 0), (1, 0), profile.pale_blue),
                ("BACKGROUND", (0, 1), (-1, 1), profile.white),
                ("GRID", (0, 0), (-1, -1), 0.55, profile.grid),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
                ("TOPPADDING", (0, 1), (-1, 1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
            ]
        )
    )
    story.extend([info_table, Spacer(1, 8)])

    salutation_name = data["client"].get("salutation", data["client"]["attention"])
    story.append(_paragraph(f"Dear {_safe(salutation_name)},", styles["body"]))
    for intro in data["introduction"]:
        story.append(_paragraph(_safe_lines(intro), styles["body"]))

    story.extend(
        [
            Spacer(1, 4),
            _section_heading(profile.section_titles["pricing"], styles, profile),
            Spacer(1, 4),
        ]
    )
    if profile.grouped_pricing:
        story.extend(_build_grouped_pricing(data, styles, profile))
        story.extend(
            [
                Spacer(1, 8),
                _section_heading(profile.section_titles["summary"], styles, profile),
                Spacer(1, 4),
                _build_project_summary(data, styles, profile),
                Spacer(1, 6),
            ]
        )
        if data["pricing"].get("amount_in_words"):
            amount_words = Table(
                [[_paragraph(
                    f"<b>Amount in Words:</b> "
                    f"{_safe_lines(data['pricing']['amount_in_words'])}",
                    styles["muted"],
                )]],
                colWidths=[CONTENT_WIDTH],
            )
            amount_words.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), profile.pale_teal),
                        ("BOX", (0, 0), (-1, -1), 0.55, profile.grid),
                        ("LEFTPADDING", (0, 0), (-1, -1), 9),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.extend([amount_words, Spacer(1, 6)])
    else:
        story.extend(
            [
                _build_pricing_table(data, styles, profile),
                Spacer(1, 5),
                _build_totals(data, styles, profile),
                Spacer(1, 6),
            ]
        )

    if data.get("pricing_basis"):
        pricing_basis = Table(
            [[_paragraph(
                f"<b>Pricing Basis:</b> {_safe_lines(data['pricing_basis'])}",
                styles["muted"],
            )]],
            colWidths=[CONTENT_WIDTH],
        )
        pricing_basis.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), profile.pale_teal),
                    ("BOX", (0, 0), (-1, -1), 0.55, profile.grid),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.extend([pricing_basis, Spacer(1, 9)])

    story.extend(
        [
            _section_heading(profile.section_titles["notes"], styles, profile),
            Spacer(1, 6),
        ]
    )
    for index, note in enumerate(data["additional_notes"], start=1):
        heading = _safe(note["heading"].rstrip("."))
        note_text = _safe_lines(note["text"])
        note_prefix = f"{index}. "
        if not profile.grouped_pricing:
            note_prefix = f"{index}.&nbsp;&nbsp;"
        story.append(
            _paragraph(
                f"{note_prefix}<b>{heading}.</b> {note_text}",
                styles["condition"],
            )
        )

    if profile.grouped_pricing:
        story.append(_paragraph("Respectfully submitted,", styles["body"]))
    story.append(Spacer(1, 10))
    signatures = data["signatures"]
    has_conforme = any(
        signatures[key]
        for key in ("accepted_name", "accepted_company", "accepted_detail")
    )
    if has_conforme:
        signature_rows = [
            [
                _paragraph("PREPARED BY", styles["signature_label"]),
                _paragraph("ACCEPTED / CONFORME", styles["signature_label"]),
            ],
            [Spacer(1, 42), Spacer(1, 42)],
            [
                _paragraph(
                    _safe(signatures["prepared_name"]).upper(),
                    styles["signature_name"],
                ),
                _paragraph(
                    _safe(signatures["accepted_name"]).upper(),
                    styles["signature_name"],
                ),
            ],
            [
                _paragraph(_safe_lines(signatures["prepared_role"]), styles["muted"]),
                _paragraph(
                    f"{_safe(signatures['accepted_company'])}<br/>"
                    f"{_safe_lines(signatures['accepted_detail'])}",
                    styles["muted"],
                ),
            ],
        ]
        signature_widths = [CONTENT_WIDTH / 2, CONTENT_WIDTH / 2]
    else:
        signature_rows = [
            [_paragraph("PREPARED BY", styles["signature_label"])],
            [Spacer(1, 42)],
            [
                _paragraph(
                    _safe(signatures["prepared_name"]).upper(),
                    styles["signature_name"],
                )
            ],
            [_paragraph(_safe_lines(signatures["prepared_role"]), styles["muted"])],
        ]
        signature_widths = [CONTENT_WIDTH]
    signature_table = Table(signature_rows, colWidths=signature_widths)
    signature_table.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 0), (-1, 0), 0.9, profile.teal),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(KeepTogether([signature_table]))

    canvas_maker = partial(
        NumberedCanvas,
        footer_label=footer_label,
        profile=profile,
    )
    doc.build(story, canvasmaker=canvas_maker)
    return output
