#!/bin/bash
# Helper script to push changes to GitHub with proper workflow

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}GitHub Push Helper${NC}"
echo "=================="
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check if remote is configured
if ! git remote get-url origin > /dev/null 2>&1; then
    echo -e "${YELLOW}No remote 'origin' configured.${NC}"
    echo "Would you like to add one? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Enter GitHub repository URL:"
        read -r repo_url
        git remote add origin "$repo_url"
        echo -e "${GREEN}Remote added!${NC}"
    else
        echo "Exiting. Configure remote with: git remote add origin <url>"
        exit 1
    fi
fi

# Show current status
echo -e "${YELLOW}Current status:${NC}"
git status --short
echo ""

# Check if there are changes to commit
if git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}No changes to commit.${NC}"
    echo "Would you like to push existing commits? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    # Show what will be committed
    echo -e "${YELLOW}Changes to be committed:${NC}"
    git diff --stat
    echo ""
    
    # Ask for commit message
    echo "Enter commit message (or press Enter for default):"
    read -r commit_msg
    
    if [ -z "$commit_msg" ]; then
        commit_msg="Update: $(date +%Y-%m-%d\ %H:%M:%S)"
    fi
    
    # Stage all changes
    echo -e "${GREEN}Staging changes...${NC}"
    git add -A
    
    # Commit
    echo -e "${GREEN}Committing changes...${NC}"
    git commit -m "$commit_msg"
fi

# Ask if user wants to push
echo ""
echo "Push to GitHub? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    # Determine branch
    branch=$(git branch --show-current)
    
    echo -e "${GREEN}Pushing to origin/$branch...${NC}"
    
    # Push to GitHub
    if git push -u origin "$branch"; then
        echo ""
        echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
        echo ""
        echo "View your repository:"
        git remote get-url origin | sed 's/\.git$//'
    else
        echo -e "${RED}❌ Push failed. Check your credentials and network connection.${NC}"
        exit 1
    fi
else
    echo "Changes committed locally but not pushed."
    echo "Push manually with: git push"
fi

