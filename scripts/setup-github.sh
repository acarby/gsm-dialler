#!/bin/bash
# Setup script to configure GitHub repository

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}GitHub Repository Setup${NC}"
echo "========================"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    echo "Initialize with: git init"
    exit 1
fi

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    current_url=$(git remote get-url origin)
    echo -e "${YELLOW}Remote 'origin' already configured:${NC}"
    echo "  $current_url"
    echo ""
    echo "Change it? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Keeping existing remote."
        exit 0
    fi
    git remote remove origin
fi

echo "Enter your GitHub repository URL:"
echo "  Example: https://github.com/username/gsm-dialler.git"
echo "  Or: git@github.com:username/gsm-dialler.git"
read -r repo_url

if [ -z "$repo_url" ]; then
    echo -e "${RED}Error: Repository URL required${NC}"
    exit 1
fi

# Add remote
git remote add origin "$repo_url"

echo ""
echo -e "${GREEN}✅ Remote configured!${NC}"
echo ""
echo "Next steps:"
echo "  1. Create the repository on GitHub (if not already created)"
echo "  2. Push your code:"
echo "     git push -u origin main"
echo ""
echo "Or use the helper script:"
echo "     ./scripts/push-to-github.sh"

