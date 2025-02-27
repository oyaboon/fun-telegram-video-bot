"""
verify_ffmpeg.py
---------------
Purpose: Verify FFmpeg installation and print its location
Author: AI Assistant
Last Modified: 2024-02-27
"""

import os
import subprocess
import sys

def find_ffmpeg():
    """
    Try to find FFmpeg executable in common locations
    
    Returns:
        str: Path to FFmpeg executable or None if not found
    """
    # Check if FFmpeg is in PATH
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               shell=True)
        if result.returncode == 0:
            print("✅ FFmpeg found in PATH")
            print(f"Version info: {result.stdout.splitlines()[0]}")
            return 'ffmpeg'
    except Exception as e:
        print(f"❌ Error checking FFmpeg in PATH: {e}")
    
    # Check common installation locations
    possible_paths = [
        os.path.expanduser("~/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"),
        "C:/ffmpeg/bin/ffmpeg.exe",
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
        os.path.expanduser("~/ffmpeg/bin/ffmpeg.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ FFmpeg found at: {path}")
            try:
                result = subprocess.run([path, '-version'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      text=True)
                print(f"Version info: {result.stdout.splitlines()[0]}")
            except Exception as e:
                print(f"❌ Error running FFmpeg: {e}")
            return path
    
    print("❌ FFmpeg not found in any common locations")
    return None

def check_path_env():
    """
    Check if FFmpeg is in the PATH environment variable
    """
    path_env = os.environ.get('PATH', '')
    print("\nPATH Environment Variable:")
    paths = path_env.split(os.pathsep)
    
    ffmpeg_paths = []
    for p in paths:
        if 'ffmpeg' in p.lower():
            ffmpeg_paths.append(p)
    
    if ffmpeg_paths:
        print("FFmpeg-related paths found in PATH:")
        for p in ffmpeg_paths:
            print(f"  - {p}")
    else:
        print("No FFmpeg-related paths found in PATH")

def main():
    """
    Main function to verify FFmpeg installation
    """
    print("=== FFmpeg Verification ===\n")
    
    ffmpeg_path = find_ffmpeg()
    
    if not ffmpeg_path:
        print("\n❌ FFmpeg not found. Please install FFmpeg or add it to your PATH.")
        print("You can run the install_ffmpeg.ps1 script to install FFmpeg.")
        print("After installation, restart your terminal for the changes to take effect.")
        sys.exit(1)
    
    check_path_env()
    
    print("\n✅ FFmpeg verification complete.")
    print("If you're still having issues with the bot, try restarting your terminal.")

if __name__ == "__main__":
    main() 