# SOP: GROQ Test Strategy Generator

## Goal
Generate a comprehensive test strategy markdown document from Jira ticket data using GROQ API.

## Input
- `groq_key` — GROQ API key
- `ticket_id` — Jira issue key
- `summary` — Issue summary
- `description` — Issue description
- `acceptance_criteria` — Acceptance criteria (if available)

## Prompt Template
```
You are a test strategy expert. Given the following Jira ticket details, generate a comprehensive test strategy document following this exact structure:

1. **Title**: Test Strategy for {summary}
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

## Process
1. Construct the prompt with ticket data.
2. Call GROQ with `openai/gpt-oss-120b` model.
3. Extract the response content.
4. Return raw markdown.

## Output
```json
{
  "raw_markdown": "# Test Strategy for...\n\n## Scope\n...",
  "model": "openai/gpt-oss-120b"
}
```

## Edge Cases
- **GROQ API down**: Retry once after 3 seconds.
- **Empty response**: Return error message.
- **Incomplete markdown**: Pass as-is, PDF builder will handle formatting.

## Error Handling
- HTTP errors caught and structured error returned.
- 30-second timeout on API calls.
- Max tokens: 4096 for full strategy output.
