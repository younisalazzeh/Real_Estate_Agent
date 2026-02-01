# How to Update GitHub Repository

## Quick Update Commands

Run these commands in your terminal from the project directory:

```bash
# 1. Add all new and modified files
git add README.md INTERVIEW_PREP.md .gitattributes .gitignore
git add src/ chainlit_app.py requirements.txt chainlit.md

# 2. Stage deleted files (if any)
git add -u

# 3. Commit with a message
git commit -m "Update: Add comprehensive README, interview prep guide, and improved LangGraph architecture"

# 4. Push to GitHub
git push origin main
```

## Or Use the Script (Linux/Mac)

```bash
chmod +x update_repo.sh
./update_repo.sh
```

## For Windows PowerShell

```powershell
# Add files
git add README.md INTERVIEW_PREP.md .gitattributes .gitignore
git add src/ chainlit_app.py requirements.txt chainlit.md
git add -u

# Commit
git commit -m "Update: Add comprehensive README, interview prep guide, and improved LangGraph architecture"

# Push
git push origin main
```

## What's Being Added

✅ **README.md** - Comprehensive project documentation
✅ **INTERVIEW_PREP.md** - Interview preparation guide with Q&A
✅ **.gitattributes** - File handling configuration
✅ **Updated .gitignore** - Better ignore patterns
✅ **All source code** - Complete project files

## Verify After Push

Visit: https://github.com/younisalazzeh/Real_Estate_Agent

You should see:
- Updated README with project description
- Interview prep guide
- All source files organized

## Troubleshooting

If you get authentication errors:
```bash
# Check remote URL
git remote -v

# If needed, update remote
git remote set-url origin https://github.com/younisalazzeh/Real_Estate_Agent.git
```

If you need to force push (be careful!):
```bash
git push origin main --force
```
