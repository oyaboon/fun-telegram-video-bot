# Telegram Video Bot - Cursor AI Optimization Guide

## Project Overview
**Telegram Video Bot** is a Telegram bot that automatically detects short video links (YouTube Shorts, TikTok, Instagram Reels), downloads the video, uploads it to the chat, and deletes the original link message.

## Core Functionalities

### 1. Detect Video Links
* Listen for messages containing links to supported short video platforms.
* Use **regular expressions** to match URLs.
* **RegEx Examples:**
  * YouTube Shorts: `r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/shorts\/|youtu\.be\/)([\w-]{11})'`
  * TikTok: `r'(?:https?:\/\/)?(?:www\.)?(?:tiktok\.com\/@[\w.-]+\/video\/)([\d]+)'`
  * Instagram Reels: `r'(?:https?:\/\/)?(?:www\.)?(?:instagram\.com\/(?:reel|p)\/)([\w-]+)'`

### 2. Download Videos
* Extract and download videos using `yt-dlp`.
* Convert or optimize videos if needed.
* Store videos temporarily before uploading.
* **Video Limitations:**
  * Maximum size: 50MB (Telegram limit)
  * Supported formats: MP4, MOV, AVI
  * Target quality: 720p (balance between quality and file size)

### 3. Upload Videos to Chat
* Send the downloaded video back to the same chat.
* Add a custom caption (optional).

### 4. Delete the Original Message
* Remove the original message containing the link after successful upload.

### 5. Error Handling & Logging
* Notify users if a download fails.
* Log errors and API request failures.
* **Error Types to Handle:**
  * Network errors (timeout, connection refused)
  * Platform API changes
  * Geo-restricted content
  * Video no longer available

## Tech Stack

### Backend
* **Python 3** for the bot logic.
* **Aiogram** for Telegram API interactions.
* **yt-dlp** for downloading videos.

### Dependencies
* `aiogram` → For handling Telegram bot interactions.
* `yt-dlp` → For downloading videos from YouTube, TikTok, Instagram, etc.
* `requests` → For additional API requests.
* `python-dotenv` → For handling environment variables.

## File Structure

```
/telegram-video-bot
│── /bot
│   │── /downloads      # Temporary storage for downloaded videos
│   │── downloader.py   # Video download logic
│   │── handlers.py     # Message processing logic
│   │── main.py         # Main bot entry point
│   │── utils.py        # Utility functions (regex for links, logging)
│
│── .env                # API keys and bot token
│── requirements.txt    # Dependencies
│── README.md           # Project documentation
```

## Optimization Priorities

### 1. Code Cleanup
* Remove duplicate functions in `utils.py` and `downloader.py`
* Eliminate unused imports
* Standardize error handling patterns
* Remove deprecated code marked with `# TODO` or `# FIXME`

### 2. Performance Optimization
* Improve video download speed and efficiency
* Optimize memory usage when handling large videos
* Reduce unnecessary API calls

### 3. Error Handling Enhancement
* Implement more granular error catching
* Add detailed logging with context
* Create user-friendly error messages

## Code Style Guidelines

### Commenting Standards
* **File Headers:**
```python
"""
filename.py
-----------
Purpose: Brief description of file's purpose
Author: Original author
Last Modified: YYYY-MM-DD
"""
```

* **Function Documentation:**
```python
def function_name(param1, param2):
    """
    Brief description of function
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
        
    Returns:
        return_type: Description of return value
        
    Raises:
        ExceptionType: When/why this exception occurs
    """
```

### Naming Conventions
* Classes: PascalCase (`DownloadManager`)
* Functions/Methods: snake_case (`download_video`)
* Variables: snake_case (`video_url`)
* Constants: SCREAMING_SNAKE_CASE (`MAX_FILE_SIZE`)

### Logging Requirements
* Use the Python `logging` module, not `print()`
* Log levels:
  * DEBUG: Detailed debugging information
  * INFO: Confirmation of expected functionality
  * WARNING: Something unexpected but non-critical
  * ERROR: Failed operations, but bot continues
  * CRITICAL: Bot cannot continue functioning

## Testing Requirements
After optimization, verify that:
1. Bot can still detect all supported platform links
2. Videos download correctly
3. Original messages are deleted properly
4. Error messages are displayed to users when appropriate

## Criteria for Code Removal
* Code is not imported/called from any file
* Functionality is duplicated elsewhere
* Commented-out code blocks with no clear purpose
* Functions with TODOs that are older than 3 months
* Debug code not intended for production

## Architecture Preservation
* Maintain the separation of concerns between modules
* Keep the main entry point in `main.py`
* Preserve the existing handler structure in `handlers.py`
* Do not change the core bot initialization process
