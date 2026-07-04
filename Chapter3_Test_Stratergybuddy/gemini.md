# Gemini.md — Project Constitution

> This file is **law**. Update only when schemas, rules, or architecture change.

---

## Data Schemas

### Input Config (from React settings form)

```json
{
  "jira_email": "string",
  "jira_token": "string",
  "jira_url": "string",
  "groq_key": "string",
  "jira_ticket_id": "string"
}
```

### Jira API Response (raw ticket data)

```json
{
  "ticket_id": "string",
  "summary": "string",
  "description": "string",
  "acceptance_criteria": "string",
  "issue_type": "string",
  "priority": "string",
  "status": "string",
  "assignee": "string",
  "labels": ["string"],
  "components": ["string"],
  "linked_issues": ["string"]
}
```

### GROQ Prompt Template

```
You are a test strategy expert. Given the following Jira ticket details, generate a comprehensive test strategy document following this exact structure:

1. **Title**: Test Strategy for {Ticket Summary}
2. **Scope**: In-scope and out-of-scope items
3. **Focus Areas**: Key testing focus areas
4. **Approach**: Testing approach and methodologies
5. **Deliverables**: What will be delivered
6. **Team & Schedule Testing**: Team structure and timeline
7. **Entry & Exit Criteria**: Entry criteria, exit criteria, user stories covered
8. **Risks**: Identified risks and mitigation strategies

Jira Ticket: {ticket_id}
Summary: {summary}
Description: {description}
Acceptance Criteria: {acceptance_criteria}
```

### GROQ API Response (raw markdown)

```json
{
  "raw_markdown": "string",
  "model": "openai/gpt-oss-120b",
  "usage": {}
}
```

### Output Payload (final PDF data shape)

```json
{
  "ticket_id": "string",
  "generated_at": "ISO8601 timestamp",
  "test_strategy_markdown": "string",
  "pdf_filename": "string"
}
```

---

## Behavioral Rules

1. Never guess at business logic — always confirm.
2. Data schema must be defined before any code in `tools/` is written.
3. SOP in `architecture/` must be updated before code changes.
4. All API tokens/keys stored in `.env`, never hardcoded.
5. After any meaningful task → update `progress.md`.
6. GROQ model: `openai/gpt-oss-120b` (free tier).
7. Jira auth: Basic Auth with email + API token.
8. PDF generation: Use `reportlab` library (fallback pipeline from markdown content).
9. The test strategy PDF must follow the sample template structure (Arial font, A4 page size, 72pt margins).
10. Display rendered markdown in React UI before offering PDF download.

## Architecture Invariants

- **React frontend**: Vite + React (no CRA), builds to `frontend/dist/`.
- **Python backend**: Flask server in `tools/server.py` on port 5000.
- **Python scripts** in `tools/`: `jira_fetcher.py`, `groq_generator.py`, `pdf_builder.py`, `server.py`, `env_loader.py`.
- **SOP markdown files** in `architecture/`.
- **`.tmp/`** for intermediate data (downloaded PDFs, cached markdown).
- **PDF**: Generated via `reportlab` (reportlab) fallback pipeline from markdown content.
- **GROQ**: `openai/gpt-oss-120b` at `https://api.groq.com/openai/v1/chat/completions`.
- **Jira**: REST API v3 at `/rest/api/3/issue/{key}` and `/rest/api/3/search/jql`.

## Maintenance Log

### 2026-07-04 — Initial Schema Definition
- Defined Input config, Jira API response, GROQ prompt template, raw markdown response, and output payload schemas.
- Set behavioral rules for Jira auth, GROQ model, PDF generation, and template structure.

### 2026-07-04 — Full Stack Build Complete
- **Phase 1 (Blueprint)**: Discovery questions answered, data schema finalized.
- **Phase 2 (Link)**: Jira + GROQ handshake scripts built and connections verified.
  - Jira: Projects accessible (SCRUM, PROJ), API v3 working.
  - GROQ: API key valid, model `openai/gpt-oss-120b` responding.
- **Phase 3 (Architect)**: 
  - SOPs created: `jira_sop.md`, `groq_sop.md`, `pdf_sop.md`, `react_sop.md`, `server_sop.md`.
  - Tools built: `jira_fetcher.py`, `groq_generator.py`, `pdf_builder.py`, `server.py`, `env_loader.py`.
  - React frontend built with Vite, settings + generator UI.
- **Phase 4 (Stylize)**: UI polished with clean CSS, PDF formatting matches sample template (Arial, A4, 72pt margins, proper section headers).
- **Phase 5 (Trigger)**: All memory files updated.
