# AI Tester 3x Blueprint

This repository contains AI-assisted testing and prompt engineering projects, including a dedicated Test Strategy Buddy project in `Chapter3_Test_Stratergybuddy`.

## Key Projects

- `Chapter02_PromptEngg/Project_02_APItestingframework/`: API testing framework with pytest and requests.
- `Chapter02_PromptEngg/Project01_TP_Gen/`: Prompt engineering and test plan generation utilities.
- `Chapter3_Test_Stratergybuddy/`: A test strategy generator that fetches Jira ticket details, generates a strategy via GROQ, and exports a PDF.

## Chapter3 Test Strategy Buddy

This project is designed to:
- Fetch Jira ticket data from Atlassian Cloud.
- Generate a structured test strategy using the GROQ AI API.
- Convert the generated Markdown strategy into a downloadable PDF.
- Provide a React frontend interface and Flask backend.

### How to run

1. Install Python dependencies:
   ```powershell
   cd "Chapter3_Test_Stratergybuddy"
   python -m pip install Flask Flask-Cors requests reportlab
   ```
2. Start the backend server:
   ```powershell
   python tools/server.py
   ```
3. Start the frontend:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
4. Open the Vite app in your browser, configure Jira and GROQ settings, and generate a strategy.

### Notes

- Add your Jira and GROQ credentials to `Chapter3_Test_Stratergybuddy/.env` or the frontend settings panel.
- The `.gitignore` file now ignores `.env` files and local generated output for the Chapter3 project.

## Repository status

This README was added to document the current workspace and provide startup instructions for the Test Strategy Buddy project.
