# AgentCart AI — GitHub Push & Repository Guide

> **Why GitHub**: Official hackathon rules require projects to be hosted on **GitHub**, **GitLab**, or **Bitbucket** with an OSI-approved open-source license (MIT) visible in the repository root.

---

## 1. Quick Push Instructions (5 Minutes)

Open **Terminal**, **PowerShell**, or **Git Bash** in the project root:

```bash
# Initialize git if not already initialized
git init

# Add all files
git add .

# Create initial commit
git commit -m "feat: AgentCart AI autonomous shopping assistant with spending guardrails"

# Set remote origin (replace with your repo URL if different)
git remote add origin https://github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant.git
# If remote origin already exists, update it:
# git remote set-url origin https://github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant.git

# Set default branch to main and push
git branch -M main
git push -u origin main --force
```

---

## 2. Fallback: If Your GitHub Default Branch is `master`

If your remote repository uses `master` as its primary branch, push to `master`:

```bash
git push -u origin main:master --force
```

Then navigate to **GitHub Repo Settings &rarr; Branches** and verify that the default branch points to the branch containing the latest code.

---

## 3. Verification Checklist

After pushing, confirm that:
- [ ] Visiting `https://github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant` shows the updated AgentCart AI `README.md`.
- [ ] `LICENSE` is clearly present as MIT.
- [ ] Running `git clone https://github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant.git` and `python eval.py` yields:
  ```text
  172 passed, 0 failed
  ```
- [ ] The repository is set to **Public** so judges and evaluators can view and clone it without credentials.

