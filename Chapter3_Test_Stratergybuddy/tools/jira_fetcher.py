"""Fetch Jira ticket data by issue key."""
import sys
import json
import requests


def parse_atlassian_doc(doc):
    """Parse Atlassian Document Format (ADF) into plain text."""
    if isinstance(doc, str):
        return doc
    text_parts = []
    if isinstance(doc, dict):
        content = doc.get("content", [])
        for node in content:
            node_type = node.get("type", "")
            if node_type == "text":
                text_parts.append(node.get("text", ""))
            elif node_type in ("paragraph", "heading", "bulletList", "orderedList", "listItem", "codeBlock", "blockquote"):
                if node_type == "listItem":
                    text_parts.append("- ")
                text_parts.append(parse_atlassian_doc(node))
                if node_type in ("paragraph", "heading", "listItem"):
                    text_parts.append("\n")
            elif node_type == "hardBreak":
                text_parts.append("\n")
            else:
                # Recursively try content
                if "content" in node:
                    text_parts.append(parse_atlassian_doc(node))
    return "".join(text_parts)


def fetch_ticket(jira_url, jira_email, jira_token, ticket_id):
    """Fetch a Jira ticket and return structured data."""
    auth = (jira_email, jira_token)
    headers = {"Accept": "application/json"}

    url = f"{jira_url.rstrip('/')}/rest/api/3/issue/{ticket_id}"
    resp = requests.get(url, auth=auth, headers=headers, timeout=15)

    if resp.status_code == 404:
        return {"error": f"Ticket {ticket_id} not found or no permission."}
    if resp.status_code == 401:
        return {"error": "Authentication failed. Check your email and token."}
    if resp.status_code == 403:
        return {"error": "Access denied. You don't have permission to view this ticket."}
    if resp.status_code != 200:
        return {"error": f"Jira API error: {resp.status_code} — {resp.text[:200]}"}

    data = resp.json()
    fields = data.get("fields", {})

    # Extract description
    desc_raw = fields.get("description", "")
    description = parse_atlassian_doc(desc_raw) if desc_raw else ""

    # Extract acceptance criteria from description if it has AC section
    acceptance_criteria = ""
    desc_lower = description.lower()
    if "acceptance criteria" in desc_lower or "ac:" in desc_lower:
        # Try to extract content after "acceptance criteria"
        import re
        ac_match = re.search(r"(?:acceptance\s*criteria|ac)[:\s]*([\s\S]*)", desc_lower)
        if ac_match:
            acceptance_criteria = ac_match.group(1).strip()
    else:
        acceptance_criteria = "Not explicitly defined in ticket."

    def safe_get(obj, key, default=""):
        """Safely get a nested value that might be None."""
        val = obj.get(key) if obj else None
        return val if val is not None else default

    def safe_name(obj, default=""):
        """Get 'name' from a potentially None object."""
        return obj.get("name", default) if obj else default

    return {
        "ticket_id": ticket_id,
        "summary": safe_get(fields, "summary"),
        "description": description or safe_get(fields, "summary"),
        "acceptance_criteria": acceptance_criteria,
        "issue_type": safe_name(fields.get("issuetype")),
        "priority": safe_name(fields.get("priority")),
        "status": safe_name(fields.get("status")),
        "assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
        "labels": fields.get("labels", []),
        "components": [c.get("name", "") for c in fields.get("components", [])],
    }


if __name__ == "__main__":
    # CLI usage for testing
    if len(sys.argv) < 5:
        print("Usage: python jira_fetcher.py <url> <email> <token> <ticket_id>")
        sys.exit(1)

    result = fetch_ticket(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(json.dumps(result, indent=2))
