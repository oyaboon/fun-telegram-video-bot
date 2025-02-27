#!/bin/bash

# Initialize Git repository
git init

# Add all files (respecting .gitignore)
git add .

# Make initial commit
git commit -m "Initial commit of Telegram Video Bot"

# Instructions for adding a remote repository
echo ""
echo "Repository initialized successfully!"
echo ""
echo "To connect to a remote repository, use:"
echo "git remote add origin <your-repository-url>"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "Replace <your-repository-url> with your GitHub/GitLab repository URL." 