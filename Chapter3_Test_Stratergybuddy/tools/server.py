"""Flask backend server that orchestrates Jira fetcher, GROQ generator, and PDF builder."""
import sys
import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from jira_fetcher import fetch_ticket
from groq_generator import generate_strategy
from pdf_builder import build_pdf

app = Flask(__name__)
CORS(app)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"


@app.route("/api/generate", methods=["POST"])
def generate():
    """Main endpoint: fetch Jira ticket, generate strategy, build PDF."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON body provided."}), 400

    # Required fields
    jira_url = data.get("jira_url", "").strip()
    jira_email = data.get("jira_email", "").strip()
    jira_token = data.get("jira_token", "").strip()
    groq_key = data.get("groq_key", "").strip()
    ticket_id = data.get("ticket_id", "").strip()

    if not all([jira_url, jira_email, jira_token, groq_key, ticket_id]):
        return jsonify({"success": False, "error": "Missing required fields."}), 400

    # Step 1: Fetch Jira ticket
    ticket = fetch_ticket(jira_url, jira_email, jira_token, ticket_id)
    if "error" in ticket:
        return jsonify({"success": False, "error": ticket["error"]}), 400

    # Step 2: Generate test strategy
    strategy = generate_strategy(
        groq_key,
        ticket["ticket_id"],
        ticket["summary"],
        ticket["description"],
        ticket["acceptance_criteria"],
    )
    if "error" in strategy:
        return jsonify({"success": False, "error": strategy["error"]}), 500

    # Save markdown to tmp for debugging
    md_path = TMP_DIR / f"{ticket_id}_strategy.md"
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    md_path.write_text(strategy["raw_markdown"], encoding="utf-8")

    # Step 3: Build PDF
    pdf_result = build_pdf(strategy["raw_markdown"], ticket_id, str(TMP_DIR))
    if "error" in pdf_result:
        return jsonify({"success": False, "error": pdf_result["error"]}), 500

    return jsonify({
        "success": True,
        "markdown": strategy["raw_markdown"],
        "pdf_url": f"/api/download/{pdf_result['filename']}",
        "filename": pdf_result["filename"],
        "ticket_id": ticket_id,
        "summary": ticket["summary"],
    })


@app.route("/api/download/<filename>")
def download(filename):
    """Serve the generated PDF."""
    pdf_path = TMP_DIR / filename
    if not pdf_path.exists():
        return jsonify({"success": False, "error": "File not found."}), 404
    return send_file(str(pdf_path), as_attachment=True, mimetype="application/pdf")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Starting Test Strategy Buddy server...")
    print(f"Temporary files: {TMP_DIR}")
    app.run(debug=True, port=5000)
