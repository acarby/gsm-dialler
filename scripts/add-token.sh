#!/bin/bash
# Quick script to add GitHub token
# Usage: ./add-token.sh [token] [username]
# Or: ./add-token.sh (will prompt for both)

if [ -z "$1" ]; then
    echo "Enter your GitHub Personal Access Token:"
    read -rs TOKEN
else
    TOKEN="$1"
fi

if [ -z "$TOKEN" ]; then
    echo "Error: Token required"
    exit 1
fi

echo "Configuring GitHub token..."
echo ""

# Configure credential helper
git config --global credential.helper store

# Get username
if [ -z "$2" ]; then
    echo "Enter your GitHub username:"
    read -r username
else
    username="$2"
fi

if [ -z "$username" ]; then
    echo "Error: Username required"
    exit 1
fi

# Create credentials file
credentials_file="$HOME/.git-credentials"

# Remove old GitHub entries if any
if [ -f "$credentials_file" ]; then
    grep -v "@github.com" "$credentials_file" > "${credentials_file}.tmp" 2>/dev/null || true
    mv "${credentials_file}.tmp" "$credentials_file" 2>/dev/null || true
fi

# Add new credentials
echo "https://${username}:${TOKEN}@github.com" >> "$credentials_file"
chmod 600 "$credentials_file"

echo "✅ Token configured!"
echo ""
echo "Username: $username"
echo "Token: ${TOKEN:0:10}... (hidden)"
echo ""
echo "To test, first add remote:"
echo "  git remote add origin https://github.com/$username/gsm-dialler.git"
echo ""
echo "Then test with: git ls-remote origin"

