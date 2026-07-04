# SOP: PDF Builder

## Goal
Convert markdown test strategy document into a downloadable PDF file matching the sample template format.

## Input
- `markdown_content` — Raw markdown string with test strategy
- `ticket_id` — Jira issue key (used for filename)
- `output_dir` — Directory to save the PDF

## Process
1. Parse markdown into sections (Title, Scope, Focus Areas, Approach, Deliverables, Team & Schedule, Entry/Exit Criteria, Risks).
2. Convert to HTML with proper styling matching the sample template.
3. Use `pdfkit` to convert HTML to PDF.
4. Save to `.tmp/{ticket_id}_test_strategy.pdf`.
5. Return file path.

## Output
```json
{
  "pdf_path": ".tmp/VWO-48_test_strategy.pdf",
  "filename": "VWO-48_test_strategy.pdf",
  "success": true
}
```

## Format Rules
- Font: Helvetica (reportlab default, matches sample template).
- Headers: Bold with larger font size than body text.
  - H2 (##): 16pt, bold, dark color, 20pt spaceBefore, 8pt spaceAfter.
  - H3 (###): 13pt, bold, blue color, 14pt spaceBefore, 6pt spaceAfter.
- Body text: 10pt, regular weight, 6pt spaceAfter.
- Bullets: 10pt, regular weight, 2pt spaceAfter, 20pt leftIndent.
- Page size: A4 (595.3 x 841.9 pts).
- Margins: 25mm all sides.

## Edge Cases
- **Empty markdown**: Return error.
- **Missing wkhtmltopdf**: Try alternative — markdown → PDF via Python libraries.

## Error Handling
- Check `wkhtmltopdf` availability before generation.
- Fall back to weasyprint or reportlab if pdfkit unavailable.
- All errors caught and returned as structured error.
