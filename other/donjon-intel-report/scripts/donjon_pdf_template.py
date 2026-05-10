#!/usr/bin/env python3
"""
Donjon Intelligence Systems — PDF Report Template
===================================================

This is the canonical PDF generation template for all Donjon Intel Reports.
Copy this file, rename it, and modify the CONTENT SECTIONS to build your report.

Everything above the "CONTENT STARTS HERE" marker is infrastructure — don't change it
unless you're deliberately evolving the brand. Everything below it is where you write
your report.

Dependencies: reportlab (pip install reportlab --break-system-packages)

Usage:
  1. Copy this file to your working directory
  2. Update REPORT_CONFIG at the top
  3. Replace the content sections with your report
  4. Run: python your_report.py
"""

import os
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, Image
)

# ═══════════════════════════════════════════════════════════════════════════════
# REPORT CONFIGURATION — Update these for each report
# ═══════════════════════════════════════════════════════════════════════════════

REPORT_CONFIG = {
    "title": "Report Title Here",
    "subtitle": "Report Type — Key Focus Areas",
    "subject": "Subject of the report",
    "scope": "What this report covers",
    "prepared_for": "Client Name — Context",
    "prepared_by": "Donjon Intelligence Systems",
    "report_date": date.today().strftime("%B %d, %Y"),
    "classification": "Client Use Only",
    "report_number": "DIS-2026-001",
    "header_right": "INTELLIGENCE REPORT  //  CLASSIFIED: CLIENT USE ONLY",
    "footer_left": "Report Title — Intelligence Report",
    "output_path": "output_report.pdf",

    # Optional
    "interview_date": None,          # e.g., "Thursday, April 16, 2026"
    "series_name": None,             # e.g., "(Ad Astra Series)"
    "insignia_path": None,           # Path to donjon_insignia.png if available
    "signoff_name": "Clayton Christian, Founder & CTO",
}


# ═══════════════════════════════════════════════════════════════════════════════
# BRAND PALETTE — The Donjon color system
# ═══════════════════════════════════════════════════════════════════════════════

DONJON_DARK       = HexColor("#1a1a2e")   # Primary dark — headers, footer bars
DONJON_INDIGO     = HexColor("#16213e")   # Secondary dark — subtle backgrounds
DONJON_BLUE       = HexColor("#0f3460")   # Section headers, table accents
DONJON_ACCENT     = HexColor("#e94560")   # Warning boxes, accent line under header
DONJON_EMBER      = HexColor("#d4a574")   # Callout borders, brand warmth, org name
DONJON_SILVER     = HexColor("#a0a0b0")   # Subtitle text, footer text, rules
DONJON_LIGHT_BG   = HexColor("#f5f5f0")   # Table alternating rows, label backgrounds
DONJON_WARM_BG    = HexColor("#fdf6ec")   # Warm callout backgrounds (optional)
DONJON_MUTED      = HexColor("#444466")   # H3 headers, callout text
DONJON_GREEN      = HexColor("#2d6a4f")   # Positive indicators (optional)
DONJON_GOLD       = HexColor("#b8860b")   # Premium accents (optional)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE TEMPLATE — Header and footer bars on every page
# ═══════════════════════════════════════════════════════════════════════════════

def header_footer(canvas_obj, doc):
    """Draw branded header and footer bars on every page."""
    canvas_obj.saveState()
    w, h = letter

    # ── Header bar ──
    canvas_obj.setFillColor(DONJON_DARK)
    canvas_obj.rect(0, h - 40, w, 40, fill=1, stroke=0)

    # Organization name (left, ember)
    canvas_obj.setFillColor(DONJON_EMBER)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawString(0.75 * inch, h - 28, "DONJON INTELLIGENCE SYSTEMS")

    # Classification (right, silver)
    canvas_obj.setFillColor(DONJON_SILVER)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawRightString(
        w - 0.75 * inch, h - 28,
        REPORT_CONFIG["header_right"]
    )

    # Accent line under header
    canvas_obj.setStrokeColor(DONJON_ACCENT)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(0, h - 41, w, h - 41)

    # ── Footer bar ──
    canvas_obj.setFillColor(DONJON_DARK)
    canvas_obj.rect(0, 0, w, 30, fill=1, stroke=0)

    canvas_obj.setFillColor(DONJON_SILVER)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawString(0.75 * inch, 12, REPORT_CONFIG["footer_left"])
    canvas_obj.drawRightString(w - 0.75 * inch, 12, f"Page {doc.page}")

    canvas_obj.restoreState()


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

doc = SimpleDocTemplate(
    REPORT_CONFIG["output_path"],
    pagesize=letter,
    topMargin=0.9 * inch,
    bottomMargin=0.7 * inch,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
)

styles = getSampleStyleSheet()


# ═══════════════════════════════════════════════════════════════════════════════
# PARAGRAPH STYLES — The Donjon type system
# ═══════════════════════════════════════════════════════════════════════════════

title_style = ParagraphStyle(
    'DonjonTitle', parent=styles['Title'],
    fontName='Helvetica-Bold', fontSize=22, leading=26,
    textColor=DONJON_DARK, spaceAfter=4, alignment=TA_LEFT,
)

subtitle_style = ParagraphStyle(
    'DonjonSubtitle', parent=styles['Normal'],
    fontName='Helvetica', fontSize=11, leading=14,
    textColor=DONJON_SILVER, spaceAfter=16,
)

h1_style = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName='Helvetica-Bold', fontSize=16, leading=20,
    textColor=DONJON_DARK, spaceBefore=20, spaceAfter=8,
)

h2_style = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName='Helvetica-Bold', fontSize=13, leading=16,
    textColor=DONJON_BLUE, spaceBefore=14, spaceAfter=6,
)

h3_style = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontName='Helvetica-Bold', fontSize=11, leading=14,
    textColor=DONJON_MUTED, spaceBefore=10, spaceAfter=4,
)

body_style = ParagraphStyle(
    'DonjonBody', parent=styles['Normal'],
    fontName='Helvetica', fontSize=10, leading=14,
    textColor=black, spaceAfter=8, alignment=TA_JUSTIFY,
)

bullet_style = ParagraphStyle(
    'DonjonBullet', parent=body_style,
    leftIndent=20, bulletIndent=8, spaceAfter=4,
    bulletFontName='Helvetica', bulletFontSize=10,
)

callout_style = ParagraphStyle(
    'Callout', parent=body_style,
    fontName='Helvetica-Oblique', fontSize=10, leading=14,
    textColor=DONJON_MUTED, leftIndent=16, rightIndent=16,
    spaceBefore=8, spaceAfter=8,
    borderColor=DONJON_EMBER, borderWidth=2, borderPadding=8,
)

warn_style = ParagraphStyle(
    'Warn', parent=body_style,
    fontName='Helvetica-Oblique', fontSize=10, leading=14,
    textColor=DONJON_ACCENT, leftIndent=12, rightIndent=12,
    spaceBefore=6, spaceAfter=12, backColor=HexColor("#fff5f5"),
    borderColor=DONJON_ACCENT, borderWidth=1, borderPadding=10,
)

label_style = ParagraphStyle(
    'Label', parent=body_style,
    fontName='Helvetica-Bold', fontSize=9, textColor=DONJON_BLUE,
)

value_style = ParagraphStyle(
    'Value', parent=body_style,
    fontName='Helvetica', fontSize=9,
)

signoff_style = ParagraphStyle(
    'Signoff', parent=body_style,
    fontName='Helvetica-Oblique', fontSize=9,
    textColor=DONJON_SILVER, alignment=TA_CENTER,
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS — Use these to build content
# ═══════════════════════════════════════════════════════════════════════════════

def hr():
    """Horizontal rule — thin silver line."""
    return HRFlowable(
        width="100%", thickness=0.5, color=DONJON_SILVER,
        spaceBefore=6, spaceAfter=6
    )

def bullet(text):
    """Styled bullet point. Supports <b>, <i> inline formatting."""
    return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet_style)

def callout(text):
    """Ember-bordered insight box. Use for 'why this matters' moments."""
    return Paragraph(text, callout_style)

def warn(text):
    """Red-bordered warning box. Use for risks, red flags, compliance notes."""
    return Paragraph(text, warn_style)

def make_table(data, col_widths, header_color=DONJON_DARK):
    """
    Create a branded table with dark header row and alternating backgrounds.

    Args:
        data: List of lists. First row is headers. Each cell should be a
              Paragraph (for formatting) or a plain string.
        col_widths: List of column widths (use inch units, e.g., [2*inch, 4.6*inch])
        header_color: Background color for header row (default: DONJON_DARK)
    """
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, DONJON_SILVER),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, DONJON_LIGHT_BG]),
    ]))
    return t

def make_metadata_table(rows):
    """
    Create the cover-page metadata table (label-value pairs).

    Args:
        rows: List of [label_string, value_string] pairs.
              e.g., [["Subject", "Company X"], ["Scope", "Financial analysis"]]
    """
    data = [
        [Paragraph(f"<b>{label}</b>", label_style), Paragraph(value, value_style)]
        for label, value in rows
    ]
    t = Table(data, colWidths=[1.6 * inch, 5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), DONJON_LIGHT_BG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, DONJON_SILVER),
    ]))
    return t

def confidence_table(rows):
    """
    Create a confidence scores table.

    Args:
        rows: List of [conclusion, confidence_level, basis] tuples.
              confidence_level should be: HIGH, MEDIUM-HIGH, MEDIUM, LOW-MEDIUM, LOW
    """
    header = [
        Paragraph("<b>Conclusion</b>", label_style),
        Paragraph("<b>Confidence</b>", label_style),
        Paragraph("<b>Basis</b>", label_style),
    ]
    data = [header] + [
        [Paragraph(c, value_style), Paragraph(conf, value_style), Paragraph(basis, value_style)]
        for c, conf, basis in rows
    ]
    return make_table(data, [2.4 * inch, 1.1 * inch, 3.1 * inch])

def add_insignia(story, skill_dir=None):
    """
    Add the Donjon insignia to the cover page if available.

    Args:
        story: The story list to append to
        skill_dir: Path to the skill directory containing assets/donjon_insignia.png
    """
    if skill_dir:
        img_path = os.path.join(skill_dir, "assets", "donjon_insignia.png")
        if os.path.exists(img_path):
            story.append(Spacer(1, 0.2 * inch))
            img = Image(img_path, width=1.5 * inch, height=1.5 * inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
            return True
    return False

def build_cover(story, config=None):
    """
    Build the standard cover / title block.

    Uses REPORT_CONFIG by default, or pass a custom config dict.
    """
    cfg = config or REPORT_CONFIG

    story.append(Spacer(1, 0.3 * inch))

    # Optional insignia
    if cfg.get("insignia_path"):
        add_insignia(story, os.path.dirname(cfg["insignia_path"]))

    # Title and subtitle
    story.append(Paragraph(cfg["title"], title_style))
    story.append(Paragraph(cfg["subtitle"], subtitle_style))

    # Metadata table
    meta_rows = [
        ["Subject", cfg["subject"]],
        ["Scope", cfg["scope"]],
        ["Prepared For", cfg["prepared_for"]],
        ["Prepared By", cfg["prepared_by"]],
        ["Report Date", cfg["report_date"]],
        ["Classification", cfg["classification"]],
        ["Report #", cfg["report_number"]],
    ]
    if cfg.get("interview_date"):
        meta_rows.insert(5, ["Interview Date", cfg["interview_date"]])

    story.append(make_metadata_table(meta_rows))
    story.append(Spacer(1, 0.2 * inch))
    story.append(hr())

def build_signoff(story, config=None):
    """Add the standard closing signoff block."""
    cfg = config or REPORT_CONFIG
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        f"Prepared with care by Donjon Intelligence Systems<br/>"
        f"{cfg['signoff_name']}<br/>"
        f"{cfg['report_date']}",
        signoff_style
    ))


# ═══════════════════════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████████████████████
#
#                        CONTENT STARTS HERE
#
#   Everything below this line is where you write your report.
#   The infrastructure above handles all styling and layout.
#
# ██████████████████████████████████████████████████████████████████████████████
# ═══════════════════════════════════════════════════════════════════════════════

story = []

# ── COVER ──
build_cover(story)

# ── EXECUTIVE READ ──
story.append(Paragraph("Executive Read", h1_style))
story.append(Paragraph(
    "Write the executive summary here. This should be 3-4 paragraphs that give the "
    "reader the core message even if they read nothing else. Lead with the single most "
    "important insight. Bold the key phrases.",
    body_style
))
story.append(callout(
    "<b>Bottom line:</b> The single-sentence takeaway that frames the entire report."
))

story.append(PageBreak())

# ── MAIN SECTIONS ──
# Add your analytical sections here. Use:
#   Paragraph("text", h1_style)     — major section headers
#   Paragraph("text", h2_style)     — subsection headers
#   Paragraph("text", h3_style)     — sub-subsection headers
#   Paragraph("text", body_style)   — body text (justified)
#   bullet("text")                  — bullet points
#   callout("text")                 — insight boxes (ember border)
#   warn("text")                    — warning boxes (red border)
#   make_table(data, col_widths)    — data tables
#   hr()                            — horizontal rules
#   PageBreak()                     — force new page

story.append(Paragraph("Part I — [Section Title]", h1_style))
story.append(Paragraph("Your analysis here.", body_style))

# ── CONFIDENCE SCORES ──
story.append(PageBreak())
story.append(Paragraph("Confidence Scores", h1_style))
story.append(confidence_table([
    # ["Conclusion", "CONFIDENCE", "Source basis"],
    ["Example conclusion", "HIGH", "Primary source, cross-referenced"],
    ["Another conclusion", "MEDIUM", "Single source, not independently verified"],
]))

# ── SOURCE BASE ──
story.append(hr())
story.append(Paragraph("Source Base", h1_style))
story.append(bullet("Source 1 — description"))
story.append(bullet("Source 2 — description"))

# ── SIGNOFF ──
build_signoff(story)


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════════════════════

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"Report generated: {REPORT_CONFIG['output_path']}")
