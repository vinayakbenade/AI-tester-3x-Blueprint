# SOP: Flask Backend Server

## Goal
Orchestrate the Jira fetcher, GROQ generator, and PDF builder tools behind a REST API that the React frontend consumes.

## Endpoints

### `POST /api/generate`
**Input:**
```json
{
  "jira_email": "user@email.com",
  "jira_token": "api-token",
  "jira_url": "https://instance.atlassian.net",
  "groq_key": "groq-api-key",
  "ticket_id": "VWO-48"
}
```

**Process:**
1. Call `jira_fetcher.py` to get ticket data.
2. Call `groq_generator.py` with ticket data to get markdown.
3. Call `pdf_builder.py` to generate PDF from markdown.
4. Return both markdown and PDF download URL.

**Output:**
```json
{
  "success": true,
  "markdown": "# Test Strategy...",
  "pdf_url": "/api/download/VWO-48_test_strategy.pdf",
  "filename": "VWO-48_test_strategy.pdf"
}
```

### `GET /api/download/<filename>`
- Serves the PDF file from `.tmp/` directory.
- Sets `Content-Type: application/pdf` and `Content-Disposition: attachment`.

## Error Handling
- Each tool call is wrapped in try/except.
- Errors are returned as `{ "success": false, "error": "message" }`.
- HTTP 500 for internal errors, 400 for bad input.
- CORS enabled for local React dev server.

## Tech Stack
- Flask with flask-cors.
- Subprocess or direct import for Python tools.
- `.tmp/` directory for file storage.
