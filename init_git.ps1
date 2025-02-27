# Initialize Git repository
git init

# Add all files (respecting .gitignore)
git add .

# Make initial commit
git commit -m "Initial commit of Telegram Video Bot"

# Instructions for adding a remote repository
Write-Host ""
Write-Host "Repository initialized successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To connect to a remote repository, use:" -ForegroundColor Yellow
Write-Host "git remote add origin <your-repository-url>"
Write-Host "git branch -M main"
Write-Host "git push -u origin main"
Write-Host ""
Write-Host "Replace <your-repository-url> with your GitHub/GitLab repository URL." -ForegroundColor Yellow 