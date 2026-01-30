# GitHub Setup & Workflow

## 1. Authenticate Your GitHub Account

### Option A: GitHub CLI (Recommended)
```powershell
# Install if needed
winget install GitHub.CLI

# Authenticate
gh auth login
# → Select "GitHub.com"
# → Choose "HTTPS" (easier for beginners)
# → Select "Paste an authentication token"
# → Go to https://github.com/settings/tokens/new and create a token with `repo` scope
# → Paste the token back into the CLI
```

### Option B: VS Code Integration
1. Open VS Code
2. Install **"GitHub" extension by GitHub** (ms-vscode.github)
3. Click the GitHub icon in the sidebar → **Sign in with your browser**
4. Authorize and return to VS Code

### Option C: Git + SSH Key
```powershell
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"
# Save to: C:\Users\a6384\.ssh\id_ed25519

# Add to GitHub
# 1. Copy key: type C:\Users\a6384\.ssh\id_ed25519.pub
# 2. Go to https://github.com/settings/keys
# 3. Click "New SSH key" → paste
```

## 2. Initialize Git Locally

```powershell
cd c:\Users\a6384\Dropbox\TDWilliamson\MagMotion

# Initialize repo
git init
git config user.name "Your Name"
git config user.email "your-email@example.com"

# Add all files
git add .

# First commit
git commit -m "Initial commit: MagMotion project structure"
```

## 3. Create Remote Repo on GitHub

1. Go to https://github.com/new
2. **Repository name:** `MagMotion`
3. **Description:** "Teensy 4.1 sensor monitoring and motion control with Python GUI"
4. **Public or Private:** Your choice
5. **Skip** "Add README" (we already have one)
6. Click **Create repository**

## 4. Link Local Repo to GitHub

```powershell
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/MagMotion.git

# Verify
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## 5. Ongoing Commits

```powershell
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Add serial communication functions"

# Push to GitHub
git push
```

## .gitignore (Already Created)
Configured to ignore:
- Python: `__pycache__/`, `.venv/`, `*.pyc`
- Arduino: `.build/`, `build/`
- IDE: `.DS_Store`, `.vscode/`
- OS: Thumbnails, temp files

## Branching Strategy (Optional)

For collaborative work:
```powershell
# Create feature branch
git checkout -b feature/serial-reader

# Make changes and commit
git add .
git commit -m "Add serial data parser"

# Push feature branch
git push -u origin feature/serial-reader

# On GitHub, open a Pull Request
# → Review → Merge to main
```

---

**Need help?** Run `git --help` or visit https://github.com/features/actions (CI/CD).
