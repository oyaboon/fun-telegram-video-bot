# PowerShell script to download and install FFmpeg

$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$downloadPath = "$env:TEMP\ffmpeg.zip"
$extractPath = "$env:USERPROFILE\ffmpeg"
$ffmpegBinPath = "$extractPath\ffmpeg-master-latest-win64-gpl\bin"

# Create extraction directory if it doesn't exist
if (-not (Test-Path $extractPath)) {
    New-Item -ItemType Directory -Path $extractPath | Out-Null
    Write-Host "Created directory: $extractPath"
}

# Download FFmpeg
Write-Host "Downloading FFmpeg from $ffmpegUrl..."
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $downloadPath
Write-Host "Download complete."

# Extract the zip file
Write-Host "Extracting FFmpeg..."
Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
Write-Host "Extraction complete."

# Add FFmpeg to the PATH environment variable
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $currentPath.Contains($ffmpegBinPath)) {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$ffmpegBinPath", "User")
    Write-Host "Added FFmpeg to PATH environment variable."
} else {
    Write-Host "FFmpeg is already in PATH."
}

# Clean up the downloaded zip file
Remove-Item $downloadPath
Write-Host "Cleaned up temporary files."

Write-Host "FFmpeg installation complete. Please restart your terminal or PowerShell session for the PATH changes to take effect."
Write-Host "FFmpeg binary location: $ffmpegBinPath\ffmpeg.exe" 