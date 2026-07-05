# Taste (Continuously Learned by [CommandCode][cmd])

[cmd]: https://commandcode.ai/

# configuration
- Use gpt-oss-120b model instead of mixtral-8x7b-32768 for Groq LLM. Confidence: 0.85

# git
- On Windows, use `git commit -m "<message>" -m "Co-authored-by: CommandCodeBot <noreply@commandcode.ai>"` instead of heredoc syntax which fails on Windows cmd/powershell. Confidence: 0.65
- Name git commit-and-push skill files as "gitpush" (not "git-commit-push"). Confidence: 0.65
