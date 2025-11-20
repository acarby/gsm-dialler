# GitHub Token Setup Guide

## 🔑 Creating a Personal Access Token

### Step 1: Generate Token on GitHub

1. **Go to GitHub Settings:**
   - Click your profile picture (top right)
   - Click **Settings**
   - Scroll down to **Developer settings** (left sidebar)
   - Click **Personal access tokens**
   - Click **Tokens (classic)** or **Fine-grained tokens**

2. **Create New Token:**
   - Click **Generate new token** → **Generate new token (classic)**
   - Give it a name: `GSM Dialler - Raspberry Pi`
   - Set expiration (recommend: 90 days or custom)
   - Select scopes (permissions):
     - ✅ **repo** (Full control of private repositories)
       - This includes: repo:status, repo_deployment, public_repo, repo:invite, security_events
     - ✅ **workflow** (Update GitHub Action workflows)
   - Click **Generate token**

3. **Copy the Token:**
   - ⚠️ **IMPORTANT:** Copy the token immediately - you won't see it again!
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Store Token Securely

**Option A: Use Git Credential Helper (Recommended)**
```bash
# Store token in git credential helper
git config --global credential.helper store

# Next time you push, enter your token as the password
# Username: your-github-username
# Password: your-token (ghp_...)
```

**Option B: Use Environment Variable**
```bash
# Add to ~/.bashrc or ~/.profile
export GITHUB_TOKEN="ghp_your_token_here"

# Then use in scripts
git push https://$GITHUB_TOKEN@github.com/username/gsm-dialler.git
```

**Option C: Use SSH Keys (Alternative)**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Copy public key: cat ~/.ssh/id_ed25519.pub

# Use SSH URL instead of HTTPS
git remote set-url origin git@github.com:username/gsm-dialler.git
```

## 🔧 Configure Git with Token

### Method 1: Interactive Setup (Easiest)

```bash
cd ~/gsm-dialler

# Configure credential helper
git config --global credential.helper store

# Try to push (will prompt for credentials)
git push origin main
# Username: your-github-username
# Password: ghp_your_token_here
```

### Method 2: Use Helper Script

```bash
cd ~/gsm-dialler
./scripts/setup-github-token.sh
```

### Method 3: Manual Configuration

```bash
# Set remote URL with token (temporary)
git remote set-url origin https://YOUR_TOKEN@github.com/username/gsm-dialler.git

# Or use credential helper (permanent)
git config credential.helper store
echo "https://YOUR_USERNAME:YOUR_TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
```

## 🛡️ Security Best Practices

1. **Never commit tokens to git:**
   - Tokens are already in `.gitignore`
   - Never add them to code files

2. **Use token with minimal permissions:**
   - Only grant `repo` scope if needed
   - Use fine-grained tokens for better control

3. **Rotate tokens regularly:**
   - Set expiration dates
   - Revoke old tokens when creating new ones

4. **Store securely:**
   - Use credential helper or environment variables
   - Don't share tokens in chat/email

## 🔍 Verify Token Works

```bash
# Test authentication
git ls-remote origin

# Or try a simple push
git push origin main
```

## 🚨 Troubleshooting

### "Authentication failed"
- Check token hasn't expired
- Verify token has correct permissions (repo scope)
- Ensure username is correct

### "Permission denied"
- Token might not have write access
- Check repository permissions
- Verify token hasn't been revoked

### "Token not found"
- Make sure credential helper is configured
- Check environment variables are set
- Verify token is in correct format (starts with `ghp_`)

## 📝 For GitHub Actions (Secrets)

If you need to use tokens in GitHub Actions workflows:

1. Go to repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GITHUB_TOKEN` (or custom name)
4. Value: Your token
5. Use in workflow: `${{ secrets.GITHUB_TOKEN }}`

Note: GitHub Actions automatically provides `GITHUB_TOKEN` - you usually don't need to add it manually.

## 🔄 Updating Token

If your token expires or is compromised:

1. Generate new token on GitHub
2. Revoke old token
3. Update local configuration:
   ```bash
   git credential reject
   # Then push again with new token
   ```

