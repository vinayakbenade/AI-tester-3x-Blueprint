"""Generate test strategy markdown from Jira ticket data using GROQ."""
import sys
import json
import requests


def build_prompt(ticket_id, summary, description, acceptance_criteria):
    return f"""You are a test strategy expert. Generate a test strategy document that follows the EXACT structure and format of the sample template below.

### SAMPLE OUTPUT FORMAT (follow this exactly):
# Test Strategy for {{Project Name}}

## Objective
Brief objective paragraph describing what will be tested.

## Scope
**In scope:**
- Bullet item one.
- Bullet item two.
- Bullet item three.
**Out of scope:**
- Bullet item one.
- Bullet item two.

## Focus Areas
- Functional correctness of flows.
- UI / navigation.
- Performance — load, stress and scalability.
- Security — vulnerabilities, encryption.
- Compatibility — browsers, devices, OS.
- Usability — ease of use, accessibility.

## Approach
- Black box and white box testing techniques.
- Automated test cases using relevant tools.
- Exploratory testing for key workflows.
- Load testing for concurrent users.
- Security testing for OWASP Top 10 vulnerabilities.
- Cross browser compatibility testing.
- Ease of use evaluation with end users.

## Deliverables
- Functional test cases and reports.
- Performance test scripts and results.
- Security vulnerabilities report.
- User acceptance testing report.
- Test coverage and defect reports.
- Automation regression suite.

## Team & Schedule Testing
Brief team description and timeline paragraph.
- Month 1: Functional and security testing.
- Month 2: Load / performance testing.
- Month 3: Compatibility testing, UAT.
- Month 4: Regression testing.

## Entry & Exit Criteria
Brief entry/exit criteria paragraph.

## Risks
- Risk item one.
- Risk item two.
- Risk item three.

### FORMATTING RULES — Follow these strictly:
- Section headings use "## Heading Name" (H2). Never use ### or other levels.
- Use "**bold**" for sub-headings like "In scope:", "Out of scope:".
- Use "- " for all bullet points. Each bullet is ONE line.
- Every bullet must end with a period (fullstop).
- Between sections, leave exactly ONE blank line.
- Do not join multiple items into one bullet — each bullet is separate.
- Do not add extra text, commentary, or explanations outside the sections.

Jira Ticket: {ticket_id}
Summary: {summary}
Description: {description}
Acceptance Criteria: {acceptance_criteria}"""


def generate_strategy(groq_key, ticket_id, summary, description, acceptance_criteria):
    """Generate test strategy via GROQ API."""
    prompt = build_prompt(ticket_id, summary, description, acceptance_criteria)

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
        "temperature": 0.3,
    }

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if resp.status_code == 401:
        return {"error": "GROQ authentication failed. Check your API key."}
    if resp.status_code != 200:
        return {"error": f"GROQ API error: {resp.status_code} — {resp.text[:300]}"}

    data = resp.json()
    markdown = data["choices"][0]["message"]["content"].strip()

    return {
        "raw_markdown": markdown,
        "model": payload["model"],
        "ticket_id": ticket_id,
    }


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python groq_generator.py <key> <ticket_id> <summary> <description> <acceptance_criteria>")
        sys.exit(1)

    result = generate_strategy(
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    )
    print(json.dumps(result, indent=2))
