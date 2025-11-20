#!/bin/bash
# Interactive script to setup GitHub token authentication

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GitHub Token Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo -e "${YELLOW}No remote 'origin' configured.${NC}"
    echo "Please run: ./scripts/setup-github.sh first"
    exit 1
fi

current_url=$(git remote get-url origin)
echo -e "${GREEN}Current remote:${NC} $current_url"
echo ""

echo -e "${YELLOW}Step 1: Get your GitHub Personal Access Token${NC}"
echo "If you don't have one, create it at:"
echo "  https://github.com/settings/tokens"
echo ""
echo "Required scopes:"
echo "  ✅ repo (Full control of private repositories)"
echo "  ✅ workflow (Update GitHub Action workflows)"
echo ""

# Get token
echo -e "${BLUE}Enter your GitHub Personal Access Token:${NC}"
echo -e "${YELLOW}(Input will be hidden)${NC}"
read -rs token

if [ -z "$token" ]; then
    echo -e "${RED}Error: Token is required${NC}"
    exit 1
fi

# Get username
echo ""
echo -e "${BLUE}Enter your GitHub username:${NC}"
read -r username

if [ -z "$username" ]; then
    echo -e "${RED}Error: Username is required${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Configure Git Credential Helper${NC}"

# Configure credential helper
git config --global credential.helper store

# Create credentials file
credentials_file="$HOME/.git-credentials"
credentials_url="https://${username}:${token}@github.com"

# Check if file exists and has content
if [ -f "$credentials_file" ]; then
    # Remove old GitHub entries
    grep -v "@github.com" "$credentials_file" > "${credentials_file}.tmp" 2>/dev/null || true
    mv "${credentials_file}.tmp" "$credentials_file" 2>/dev/null || true
fi

# Add new credentials
echo "$credentials_url" >> "$credentials_file"
chmod 600 "$credentials_file"

echo -e "${GREEN}✅ Credentials stored${NC}"

# Update remote URL to use HTTPS if it's not already
if [[ "$current_url" == git@* ]]; then
    echo ""
    echo -e "${YELLOW}Remote is using SSH. Would you like to switch to HTTPS? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        repo_path=$(echo "$current_url" | sed 's/git@github.com://' | sed 's/\.git$//')
        new_url="https://github.com/${repo_path}.git"
        git remote set-url origin "$new_url"
        echo -e "${GREEN}✅ Remote URL updated to HTTPS${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Step 3: Testing Authentication${NC}"

# Test authentication
if git ls-remote origin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Authentication successful!${NC}"
else
    echo -e "${RED}❌ Authentication failed${NC}"
    echo "Please check:"
    echo "  - Token is correct and not expired"
    echo "  - Token has 'repo' scope"
    echo "  - Username is correct"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "You can now push to GitHub:"
echo "  git push origin main"
echo ""
echo "Or use the helper script:"
echo "  ./scripts/push-to-github.sh"
echo ""

