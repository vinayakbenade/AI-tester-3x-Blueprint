"""Handshake script: verify GROQ API connection."""
import sys
import json
import requests
from env_loader import load_env, get_env


def test_connection():
    load_env()
    key = get_env("GROQ_KEY")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "user", "content": "Reply with just the word: CONNECTED"}
        ],
        "max_tokens": 10,
    }

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if resp.status_code == 200:
        data = resp.json()
        reply = data["choices"][0]["message"]["content"].strip()
        result = {"status": "ok", "reply": reply, "model": payload["model"]}
        print(json.dumps(result, indent=2))
        return True
    else:
        print(f"ERROR: GROQ API returned {resp.status_code}: {resp.text}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
