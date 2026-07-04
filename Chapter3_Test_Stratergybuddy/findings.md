# Findings & Discoveries

## Initial Scan (2026-07-04)
- **Objective**: Build a React app that takes Jira ticket ID (e.g., VWO-48), fetches ticket details, and generates a **Test Strategy** using GROQ AI.
- **GROQ Model**: `openai/gpt-oss-120b` (free tier)
- **Jira Auth**: Email + API Token + Base URL
- **Sample Template**: `Sample_template/Test Strategy for Ecommerce Website.pdf` — structure: Title, Scope, Focus Areas, Approach, Deliverables, Team & Schedule, Entry/Exit Criteria, Risks.
- **Framework**: B.L.A.S.T. protocol (Blueprint, Link, Architect, Stylize, Trigger)
- **Directory structure needed**: `architecture/`, `tools/`, `.tmp/`

## Phase 1 Discovery (2026-07-04)
- **North Star**: React app → Jira ticket ID → downloadable PDF test strategy
- **Integrations**: Jira (email + token + base URL) + GROQ (`openai/gpt-oss-120b`)
- **Source of Truth**: Jira ticket data only
- **Delivery**: PDF download matching sample template structure
- **Behavior**: Follow sample template: Scope, Focus Areas, Approach, Deliverables, Team & Schedule, Entry/Exit Criteria, Risks

## Phase 2 Connectivity (2026-07-04)
- **Jira**: API v3 works. Projects found: SCRUM (My PM Team), PROJ (Project01).
  - VWO-48 does NOT exist in this instance — the app will accept any valid ticket ID.
  - API endpoints used: `/rest/api/3/project`, `/rest/api/3/issue/{key}`, `/rest/api/3/search/jql`.
  - Note: old `/rest/api/3/search` endpoint returns 410 — must use `/rest/api/3/search/jql`.
- **GROQ**: API key valid. Model `openai/gpt-oss-120b` responds at `https://api.groq.com/openai/v1/chat/completions`.
- **PDF**: `reportlab` library installed and working. Fallback pipeline works for markdown→PDF conversion.

## Tech Stack Decisions
- **Frontend**: Vite + React (no CRA, no heavy frameworks)
- **Backend**: Flask with flask-cors
- **PDF**: reportlab (no wkhtmltopdf dependency needed)
- **Jira parsing**: Custom ADF (Atlassian Document Format) parser for description extraction
- **Settings persistence**: localStorage in browser
- **API**: Single `POST /api/generate` endpoint orchestrates all three tools
