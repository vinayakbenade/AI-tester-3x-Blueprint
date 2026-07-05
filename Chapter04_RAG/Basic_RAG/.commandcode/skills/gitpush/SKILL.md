---
name: gitpush
description: Commit and push code to GitHub from this project.
---

# Git Commit & Push

A skill for committing and pushing code to GitHub from this project.

## When to Use

- User asks to "commit and push", "push to GitHub", "save to remote", or similar

## Workflow

### 1. Check Status

```bash
git status
```

Look for modified and untracked files.

### 2. Check the Remote

```bash
git remote -v
```

Verify `origin` points to the correct GitHub URL.

### 3. Stage Files

Only stage files relevant to the task — do not stage unrelated changes from other chapters or directories.

```bash
git add <file1> <file2> ...
```

### 4. Commit

On Windows, use a single-line command (heredoc doesn't work in cmd/PowerShell):

```bash
git commit -m "<message>" -m "Co-authored-by: CommandCodeBot <noreply@commandcode.ai>"
```

First line: capitalized, ~50 chars, imperative mood.

### 5. Push

```bash
git push origin <branch>
```

Default branch is usually `main`.

## Checklist

- [ ] `git status` — reviewed what's changed
- [ ] Only relevant files are staged
- [ ] Commit message includes co-author trailer
- [ ] `git push` completed successfully
