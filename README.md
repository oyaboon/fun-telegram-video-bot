# Telegram Video Bot

A Telegram bot that automatically detects short video links (YouTube Shorts, TikTok, Instagram Reels), downloads the video, uploads it to the chat, and deletes the original link message.

## Features

- **Link Detection**: Automatically detects links to YouTube Shorts, TikTok videos, and Instagram Reels
- **Video Download**: Downloads videos using yt-dlp with optimized quality settings
- **Auto-Upload**: Uploads the downloaded video directly to the chat
- **Message Cleanup**: Deletes the original message containing the link
- **Error Handling**: Comprehensive error handling for various scenarios

## Requirements

- Python 3.7+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- FFmpeg (for video processing)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/telegram-video-bot.git
   cd telegram-video-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install FFmpeg (if not already installed):
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

4. Create a `.env` file based on the provided `.env.example`:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file and add your Telegram Bot Token:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ```

## Usage

1. Start the bot:
   ```
   python run.py
   ```

2. Add the bot to a Telegram group or send a message directly to the bot with a supported video link.

3. The bot will:
   - Detect the video link
   - Download the video
   - Upload it to the chat
   - Delete the original message with the link

## Supported Platforms

- YouTube Shorts
- TikTok
- Instagram Reels

## Configuration

You can customize the bot's behavior by modifying the `.env` file:

- `BOT_TOKEN`: Your Telegram Bot Token
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `DOWNLOAD_DIR`: Directory for temporary video storage
- `MAX_FILE_SIZE`: Maximum file size in MB (Telegram limit is 50MB)
- `TARGET_QUALITY`: Target video quality (720p recommended)

## Project Structure

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
│── .env.example        # Example environment variables
│── requirements.txt    # Dependencies
│── run.py              # Entry point script
│── README.md           # Project documentation
```

## Error Handling

The bot handles various error scenarios:

- Network errors (timeout, connection refused)
- Platform API changes
- Geo-restricted content
- Video no longer available
- File size exceeding Telegram's limits

## License

MIT

## Acknowledgements

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot API framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading library
- [loguru](https://github.com/Delgan/loguru) - Logging library
