"""Handshake script: verify Jira connection — discover projects and search for VWO-48."""
import sys
import json
import requests
from env_loader import load_env, get_env


def discover_jira():
    load_env()
    email = get_env("JIRA_EMAIL")
    token = get_env("JIRA_API_TOKEN")
    url = get_env("JIRA_URL").rstrip("/")

    auth = (email, token)
    headers = {"Accept": "application/json"}

    # 1. Get all projects
    proj_url = f"{url}/rest/api/3/project"
    resp = requests.get(proj_url, auth=auth, headers=headers, timeout=15)

    if resp.status_code != 200:
        print(f"ERROR: Cannot fetch projects: {resp.status_code} {resp.text}")
        return False

    projects = resp.json()
    print("=== JIRA PROJECTS ===")
    for p in projects:
        print(f"  {p['key']} — {p['name']} (id: {p['id']})")

    # 2. Try to search for VWO-48 specifically
    search_url = f"{url}/rest/api/3/search/jql"
    params = {"jql": "issueKey=VWO-48"}
    resp2 = requests.get(search_url, auth=auth, headers=headers, params=params, timeout=15)

    if resp2.status_code == 200:
        issues = resp2.json().get("issues", [])
        if issues:
            issue = issues[0]
            print(f"\n=== VWO-48 FOUND ===")
            print(f"  Summary: {issue['fields'].get('summary', '')}")
            print(f"  Status: {issue['fields'].get('status', {}).get('name', '')}")
            print(f"  Type: {issue['fields'].get('issuetype', {}).get('name', '')}")
        else:
            print("\n=== VWO-48 NOT FOUND ===")
            # Show recent issues instead
            params2 = {"jql": "ORDER BY created DESC", "maxResults": 10}
            resp3 = requests.get(search_url, auth=auth, headers=headers, params=params2, timeout=15)
            if resp3.status_code == 200:
                issues3 = resp3.json().get("issues", [])
                print("\n=== RECENT 10 ISSUES ===")
                for issue in issues3:
                    key = issue["key"]
                    summary = issue["fields"].get("summary", "")
                    print(f"  {key} — {summary}")
    else:
        print(f"Search failed: {resp2.status_code} {resp2.text}")

    return True


if __name__ == "__main__":
    success = discover_jira()
    sys.exit(0 if success else 1)
