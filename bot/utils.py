"""
utils.py
--------
Purpose: Utility functions for link detection, logging, and other helper functions
Author: AI Assistant
Last Modified: 2024-02-27
"""

import os
import re
import logging
import subprocess
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(
    "bot.log",
    level=LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="10 MB",
    retention="1 week",
)

# Configure standard logging to use loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=LOG_LEVEL)

# Constants
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50))  # in MB
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "bot/downloads")
TARGET_QUALITY = os.getenv("TARGET_QUALITY", "720")

# Create downloads directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Regular expressions for video link detection
YOUTUBE_SHORTS_REGEX = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:shorts\/|watch\?v=)|youtu\.be\/)([\w-]{11})'
TIKTOK_REGEX = r'(?:https?:\/\/)?(?:www\.|vt\.)?(?:tiktok\.com\/(?:@[\w.-]+\/video\/|@[\w.-]+\/|[\w.-]+\/|v\/)?)([\w.-]+)'
INSTAGRAM_REELS_REGEX = r'(?:https?:\/\/)?(?:www\.)?(?:instagram\.com\/(?:reel|p|reels|stories)\/)([\w-]+)(?:\/|\?.*)?'
VK_REGEX = r'(?:https?:\/\/)?(?:www\.)?(?:vk\.com\/(?:feed\?z=clip-|video-|clip|video|wall-|wall|feed\?w=wall-|feed\?w=clip-|feed\?.*clip-|feed\?.*video-))?([\w.-]+)'

def extract_video_id(url):
    """
    Extract video ID from supported platform URLs
    
    Args:
        url (str): URL to extract video ID from
        
    Returns:
        tuple: (platform, video_id) or (None, None) if not supported
    """
    # Check YouTube Shorts/Videos
    youtube_match = re.search(YOUTUBE_SHORTS_REGEX, url)
    if youtube_match:
        return "youtube", youtube_match.group(1)
    
    # Check TikTok
    tiktok_match = re.search(TIKTOK_REGEX, url)
    if tiktok_match:
        # For TikTok, we'll use the full URL as the ID might be complex
        return "tiktok", url
    
    # Check Instagram Reels
    instagram_match = re.search(INSTAGRAM_REELS_REGEX, url)
    if instagram_match:
        # For Instagram, we'll use the full URL as the ID might not be sufficient
        return "instagram", url
    
    # Check VK videos
    vk_match = re.search(VK_REGEX, url)
    if vk_match:
        # For VK, we'll use the full URL
        return "vk", url
    
    return None, None

def contains_video_link(text):
    """
    Check if text contains any supported video links
    
    Args:
        text (str): Text to check for video links
        
    Returns:
        bool: True if text contains supported video link, False otherwise
    """
    if not text:
        return False
    
    # First, check if the text contains "http" or "www" to quickly filter out non-links
    if not ("http" in text.lower() or "www" in text.lower()):
        return False
        
    patterns = [YOUTUBE_SHORTS_REGEX, TIKTOK_REGEX, INSTAGRAM_REELS_REGEX, VK_REGEX]
    
    for pattern in patterns:
        if re.search(pattern, text):
            # Extract the match to verify it's a valid URL
            match = re.search(pattern, text)
            if match:
                # Check if the matched text is substantial (not just a few characters)
                matched_text = match.group(0)
                if len(matched_text) > 10:  # A reasonable URL should be longer than 10 chars
                    return True
    
    return False

def get_temp_filepath(platform, video_id):
    """
    Generate a temporary filepath for downloaded video
    
    Args:
        platform (str): Platform name (youtube, tiktok, instagram)
        video_id (str): Video ID
        
    Returns:
        str: Path to temporary file
    """
    # For platforms where we use the full URL as ID, create a hash
    if platform in ["tiktok", "instagram", "vk"]:
        import hashlib
        # Create a hash of the URL to use as filename
        hash_object = hashlib.md5(video_id.encode())
        video_id = hash_object.hexdigest()[:15]  # Use first 15 chars of hash
    
    return os.path.join(DOWNLOAD_DIR, f"{platform}_{video_id}.mp4")

def is_valid_video_file(file_path):
    """
    Check if a file is a valid video file
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if file is a valid video, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        logger.error(f"File is empty: {file_path}")
        return False
    
    # Check file extension
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
        logger.error(f"File has invalid extension: {file_path}")
        return False
    
    # Try to get video info using ffmpeg
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', file_path, '-hide_banner'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        # ffmpeg outputs to stderr for file info
        if "Invalid data found" in result.stderr or "Error" in result.stderr:
            logger.error(f"FFmpeg reports invalid video data: {file_path}")
            return False
        
        # Check if file contains video stream
        if "Video:" not in result.stderr:
            logger.error(f"No video stream found in file: {file_path}")
            return False
            
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout checking video file: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error checking video file: {file_path}, Error: {e}")
        # If we can't check with ffmpeg, assume it's valid
        return True

def clean_temp_files():
    """
    Remove all temporary files from download directory
    """
    try:
        for file in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.debug(f"Removed temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning temporary files: {e}") 