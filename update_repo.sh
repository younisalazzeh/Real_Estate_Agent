#!/bin/bash
# Script to update GitHub repository

echo "🔄 Updating GitHub repository..."

# Add all new and modified files
git add README.md
git add INTERVIEW_PREP.md
git add .gitattributes
git add .gitignore

# Add all source files
git add src/
git add chainlit_app.py
git add requirements.txt
git add chainlit.md

# Stage deleted files
git add -u

# Check status
echo ""
echo "📋 Files staged for commit:"
git status --short

echo ""
read -p "Enter commit message (or press Enter for default): " commit_msg

if [ -z "$commit_msg" ]; then
    commit_msg="Update: Add comprehensive README, interview prep guide, and improved architecture"
fi

# Commit
git commit -m "$commit_msg"

echo ""
echo "✅ Committed successfully!"
echo ""
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "🎉 Repository updated successfully!"
echo ""
echo "View your repo at: https://github.com/younisalazzeh/Real_Estate_Agent"
