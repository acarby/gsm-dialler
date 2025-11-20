# Git Repository Setup Guide

## 🚀 Setting Up Remote Repository

### Option 1: GitHub (Recommended)

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it: `gsm-dialler`
   - Choose Private or Public
   - Don't initialize with README (we already have one)

2. **Add remote and push:**
   ```bash
   cd ~/gsm-dialler
   git remote add origin https://github.com/YOUR_USERNAME/gsm-dialler.git
   git push -u origin main
   ```

### Option 2: GitLab

1. **Create a new project on GitLab**
2. **Add remote:**
   ```bash
   cd ~/gsm-dialler
   git remote add origin https://gitlab.com/YOUR_USERNAME/gsm-dialler.git
   git push -u origin main
   ```

### Option 3: Self-Hosted Git Server

```bash
cd ~/gsm-dialler
git remote add origin git@your-server.com:gsm-dialler.git
git push -u origin main
```

## 📥 Deploying from Git

### On a Fresh Raspberry Pi:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gsm-dialler.git
cd gsm-dialler

# Install
cd deploy
sudo bash install.sh
```

### Updating an Existing Installation:

```bash
cd ~/gsm-dialler
git pull
sudo bash deploy/install.sh
```

## 🔄 Daily Workflow

### Making Changes

```bash
# Make your changes to files
nano gpio_trigger.py

# Stage changes
git add gpio_trigger.py

# Commit
git commit -m "Updated GPIO trigger logic"

# Push to remote
git push
```

### Creating a New Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Added new feature"

# Push branch
git push -u origin feature/new-feature

# Merge back to main (on GitHub or locally)
git checkout main
git merge feature/new-feature
```

## 📋 Useful Git Commands

### View Status
```bash
git status
```

### View Commit History
```bash
git log --oneline
```

### View Changes
```bash
git diff
```

### Undo Changes
```bash
# Discard changes to a file
git checkout -- filename.py

# Unstage a file
git reset HEAD filename.py
```

### Create a Tag (for releases)
```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

## 🔐 Security Notes

- **Never commit sensitive data:**
  - Passwords
  - API keys
  - Personal phone numbers
  - Production call lists

- **Use .gitignore:**
  - Already configured to exclude:
    - Data files (`gsmdialler-data/`)
    - Logs
    - Temporary files
    - IDE files

- **If you accidentally commit sensitive data:**
  ```bash
  # Remove from history (use with caution!)
  git filter-branch --force --index-filter \
    "git rm --cached --ignore-unmatch sensitive-file.txt" \
    --prune-empty --tag-name-filter cat -- --all
  ```

## 🌿 Branch Strategy

Recommended workflow:

- **main**: Production-ready code
- **develop**: Development branch
- **feature/***: Feature branches
- **hotfix/***: Urgent fixes

Example:
```bash
git checkout -b develop
git checkout -b feature/sms-improvements
# ... work on feature ...
git checkout develop
git merge feature/sms-improvements
git checkout main
git merge develop
```

## 📦 Deployment Tags

Tag releases for easy deployment:

```bash
# Create release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Deploy specific version
git clone --branch v1.0.0 https://github.com/YOUR_USERNAME/gsm-dialler.git
```

## 🔍 Troubleshooting

### Merge Conflicts
```bash
# View conflicts
git status

# Edit conflicted files, then:
git add conflicted-file.py
git commit -m "Resolved merge conflict"
```

### Undo Last Commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Undo Last Commit (discard changes)
```bash
git reset --hard HEAD~1
```

### View Remote URLs
```bash
git remote -v
```

### Change Remote URL
```bash
git remote set-url origin NEW_URL
```

