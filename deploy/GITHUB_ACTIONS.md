# GitHub Actions Guide

This project includes GitHub Actions workflows to automate validation, testing, and releases.

## 🚀 Available Workflows

### 1. CI Validation (`ci.yml`)
**Triggers:** On push to `main` or `develop`, and on pull requests

**What it does:**
- ✅ Validates project structure (checks for required files)
- ✅ Checks shell script syntax
- ✅ Validates Python syntax
- ✅ Scans for sensitive data (passwords, API keys)

**View results:** Go to your GitHub repository → Actions tab

### 2. Release Package (`release.yml`)
**Triggers:** 
- When you push a version tag (e.g., `v1.0.0`)
- Manual trigger from Actions tab

**What it does:**
- 📦 Creates a deployment package (tarball)
- 🏷️ Creates a GitHub Release with the package attached
- 💾 Saves package as artifact for 30 days

**How to use:**
```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

This will automatically:
1. Create a release on GitHub
2. Generate release notes
3. Attach the deployment package

## 📋 Helper Scripts

### `scripts/push-to-github.sh`
Interactive script to commit and push changes to GitHub.

**Usage:**
```bash
cd ~/gsm-dialler
./scripts/push-to-github.sh
```

**What it does:**
- Shows current git status
- Helps you write commit messages
- Commits changes
- Pushes to GitHub
- Shows repository URL

### `scripts/setup-github.sh`
Helps configure GitHub remote repository.

**Usage:**
```bash
cd ~/gsm-dialler
./scripts/setup-github.sh
```

**What it does:**
- Guides you through adding GitHub remote
- Validates repository URL
- Sets up origin for easy pushing

## 🔄 Complete Workflow Example

### Initial Setup
```bash
# 1. Setup GitHub remote
./scripts/setup-github.sh

# 2. Push initial code
git push -u origin main
```

### Daily Development
```bash
# Make changes to files
nano gpio_trigger.py

# Use helper script to push
./scripts/push-to-github.sh
```

### Creating a Release
```bash
# 1. Make sure all changes are committed
git add .
git commit -m "Final changes for v1.0.0"

# 2. Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 3. GitHub Actions will automatically:
#    - Create a release
#    - Build deployment package
#    - Attach package to release
```

## 📦 Downloading Releases

Once a release is created, users can download the package:

1. Go to GitHub repository → Releases
2. Download `gsm-dialler-package-*.tar.gz`
3. Extract and deploy:
   ```bash
   tar -xzf gsm-dialler-package-*.tar.gz
   cd gsm-dialler-package-*/gsm-dialler/deploy
   sudo bash install.sh
   ```

## 🔍 Viewing Workflow Runs

1. Go to your GitHub repository
2. Click on **Actions** tab
3. See all workflow runs and their status
4. Click on a run to see detailed logs

## ⚙️ Manual Workflow Trigger

You can manually trigger the release workflow:

1. Go to repository → **Actions** tab
2. Select **Create Release Package** workflow
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## 🐛 Troubleshooting

### Workflow fails validation
- Check the Actions tab for error details
- Fix issues shown in the logs
- Push again to trigger new run

### Release not created
- Make sure you pushed a tag starting with `v` (e.g., `v1.0.0`)
- Check Actions tab for errors
- Verify `GITHUB_TOKEN` has proper permissions

### Can't push to GitHub
- Check your credentials: `git config --list`
- Use SSH keys or Personal Access Token
- Verify repository URL: `git remote -v`

## 🔐 Security Notes

- GitHub Actions automatically have access to `GITHUB_TOKEN`
- No additional secrets needed for basic workflows
- For private repositories, workflows work automatically
- Never commit sensitive data (use GitHub Secrets if needed)

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

