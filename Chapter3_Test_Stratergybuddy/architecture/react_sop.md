# SOP: React Frontend

## Goal
Provide a clean UI for users to configure Jira/GROQ credentials, enter a Jira ticket ID, and generate/download a test strategy PDF.

## Pages

### Settings Page
- Fields: Jira Email, Jira Token, Jira URL, GROQ API Key.
- Save button (stores in localStorage or state).
- Reset button to clear settings.

### Generator Page
- Input: Jira Ticket ID (text field).
- Generate button → calls backend API.
- Loading spinner during generation.
- Displays rendered markdown of the test strategy.
- Download PDF button.

## API Endpoints (Backend)
- `POST /api/generate` — Accepts `{ jira_email, jira_token, jira_url, groq_key, ticket_id }` → returns `{ markdown, pdf_url }`.
- `GET /api/download/{filename}` — Serves the generated PDF.

## UX Rules
- Disable Generate button while loading.
- Show clear error messages (toast/alert).
- Responsive design (works on mobile).
- Clean, professional look matching the test strategy domain.

## Tech Stack
- Vite + React (no CRA).
- CSS modules or inline styles (no heavy framework).
- Fetch API for backend calls.
- `react-markdown` for rendering the markdown output.
