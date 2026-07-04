"""Convert markdown test strategy to PDF."""
import sys
import json
import os
import re
from pathlib import Path


def escape_html(text):
    """Escape HTML special chars so reportlab doesn't choke on them."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def normalize_dashes(text):
    """Replace fancy unicode dashes/hyphens with plain ASCII hyphen."""
    text = text.replace("\u2013", "-")  # en dash
    text = text.replace("\u2014", "-")  # em dash
    text = text.replace("\u2015", "-")  # horizontal bar
    text = text.replace("\u2212", "-")  # minus sign
    text = text.replace("\u2022", "-")  # bullet
    text = text.replace("\u2023", "-")  # triangular bullet
    text = text.replace("\u25E6", "-")  # white bullet
    text = text.replace("\u2043", "-")  # hyphen bullet
    text = text.replace("\u2011", "-")  # non-breaking hyphen
    text = text.replace("\uFE63", "-")  # small hyphen-minus
    text = text.replace("\uFF0D", "-")  # fullwidth hyphen-minus
    text = text.replace("\u2027", "-")  # hyphenation point
    text = text.replace("\uFE58", "-")  # small em dash
    return text


def markdown_to_reportlab_elements(markdown_text):
    """Parse markdown into reportlab flowable elements."""
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor

    styles = getSampleStyleSheet()

    # Custom styles matching template
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=16, leading=20, spaceAfter=12,
        textColor=HexColor("#1a1a1a"),
        fontName="Helvetica-Bold",
    )
    h2_style = ParagraphStyle(
        "CustomH2", parent=styles["Heading2"],
        fontSize=16, leading=20, spaceBefore=20, spaceAfter=8,
        textColor=HexColor("#1a1a1a"),
        fontName="Helvetica-Bold",
        borderPadding=(0, 0, 4, 0),
    )
    h3_style = ParagraphStyle(
        "CustomH3", parent=styles["Heading3"],
        fontSize=13, leading=17, spaceBefore=14, spaceAfter=6,
        textColor=HexColor("#2c5f8a"),
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "CustomBody", parent=styles["Normal"],
        fontSize=10, leading=14, spaceAfter=6,
        textColor=HexColor("#333"),
        fontName="Helvetica",
    )
    bullet_style = ParagraphStyle(
        "CustomBullet", parent=body_style,
        leftIndent=20, bulletIndent=8,
        spaceAfter=2,
    )
    bold_sub_style = ParagraphStyle(
        "CustomBoldSub", parent=body_style,
        fontSize=10, leading=14, spaceBefore=8, spaceAfter=4,
        textColor=HexColor("#1a1a1a"),
        fontName="Helvetica-Bold",
    )

    markdown_text = normalize_dashes(markdown_text)

    elements = []
    lines = markdown_text.split("\n")
    in_list = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            elements.append(Spacer(1, 4))
            in_list = False
            continue

        # Check if this is a list item continuation
        is_bullet = stripped.startswith("- ") or stripped.startswith("* ")
        is_numbered = re.match(r"^\d+\.\s", stripped)

        if is_bullet:
            text = stripped[2:]
            text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
            text = escape_html(text)
            elements.append(Paragraph(f"&bull; {text}", bullet_style))
            in_list = True
            continue

        if is_numbered:
            num, text = re.match(r"^(\d+\.)\s(.+)$", stripped).groups()
            text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
            text = escape_html(text)
            elements.append(Paragraph(f"<b>{num}</b> {text}", bullet_style))
            in_list = True
            continue

        in_list = False

        # Headers
        if stripped.startswith("### "):
            text = escape_html(stripped[4:])
            elements.append(Paragraph(text, h3_style))
        elif stripped.startswith("## "):
            text = escape_html(stripped[3:])
            elements.append(Paragraph(text, h2_style))
        elif stripped.startswith("# "):
            text = escape_html(stripped[2:])
            elements.append(Paragraph(text, title_style))
        elif stripped.startswith("**") and ("**" in stripped[2:]):
            text = escape_html(stripped.strip("*"))
            elements.append(Paragraph(f"<b>{text}</b>", bold_sub_style))
        else:
            text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", stripped)
            text = escape_html(text)
            elements.append(Paragraph(text, body_style))

    return elements


def build_pdf(markdown_content, ticket_id, output_dir):
    """Build PDF from markdown content."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{ticket_id}_test_strategy.pdf"
    pdf_path = os.path.join(output_dir, filename)

    from reportlab.platypus import SimpleDocTemplate, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        topMargin=25*mm,
        bottomMargin=25*mm,
        leftMargin=25*mm,
        rightMargin=25*mm,
    )

    elements = markdown_to_reportlab_elements(markdown_content)
    doc.build(elements)

    return {
        "pdf_path": pdf_path,
        "filename": filename,
        "success": True,
    }


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python pdf_builder.py <markdown_file_path> <ticket_id> <output_dir>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        md = f.read()

    result = build_pdf(md, sys.argv[2], sys.argv[3])
    print(json.dumps(result, indent=2))
