# SOP: Jira Ticket Fetcher

## Goal
Fetch a Jira issue by its key (e.g., `VWO-48`) and extract structured data for test strategy generation.

## Input
- `jira_url` — Base URL of Jira instance
- `jira_email` — Email for basic auth
- `jira_token` — API token for basic auth
- `ticket_id` — Issue key (e.g., `VWO-48`)

## Process
1. Authenticate via Basic Auth (email + token).
2. Call `GET /rest/api/3/issue/{ticket_id}`.
3. Extract: summary, description, acceptance criteria (from description or custom fields), issue type, priority, status, assignee, labels, components.
4. Return structured JSON.

## Output
```json
{
  "ticket_id": "VWO-48",
  "summary": "...",
  "description": "...",
  "acceptance_criteria": "...",
  "issue_type": "Story",
  "priority": "High",
  "status": "To Do"
}
```

## Edge Cases
- **404**: Ticket not found → return error message.
- **403**: No permission → return auth error.
- **Empty description**: Use summary as fallback.
- **No acceptance criteria**: Prompt GROQ to infer from description.

## Error Handling
- All HTTP errors are caught and returned as structured error JSON.
- Network timeouts: 15-second timeout on requests.
