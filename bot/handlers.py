"""
handlers.py
----------
Purpose: Message processing logic for the Telegram bot
Author: AI Assistant
Last Modified: 2024-02-27
"""

import os
import asyncio
import traceback
from loguru import logger
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError

from .utils import contains_video_link, extract_video_id, clean_temp_files, is_valid_video_file
from .downloader import VideoDownloader, DownloadTimeoutError

# Initialize video downloader
downloader = VideoDownloader()
router = Router()

async def on_startup(bot):
    """
    Actions to perform on bot startup
    
    Args:
        bot: Bot instance
    """
    logger.info("Bot started")
    clean_temp_files()

async def on_shutdown(bot):
    """
    Actions to perform on bot shutdown
    
    Args:
        bot: Bot instance
    """
    logger.info("Bot shutting down")
    clean_temp_files()

@router.message(lambda message: message.text and len(message.text) > 10 and contains_video_link(message.text))
async def process_message(message: types.Message):
    """
    Process incoming message and check for video links
    
    Args:
        message (types.Message): Telegram message
    """
    # Extract video URL from message
    urls = message.text.split()
    for url in urls:
        platform, video_id = extract_video_id(url)
        
        if platform and video_id:
            await process_video_link(message, url, platform, video_id)
            # Only process the first valid video link
            break

async def process_video_link(message: types.Message, url: str, platform: str, video_id: str):
    """
    Process a video link and send the video back to the chat
    
    Args:
        message (types.Message): Telegram message
        url (str): Video URL
        platform (str): Platform name (youtube, tiktok, instagram)
        video_id (str): Video ID
    """
    chat_id = message.chat.id
    message_id = message.message_id
    
    # Get sender information
    sender_name = get_sender_name(message)
    
    # Send "processing" message
    processing_msg = await message.reply("⏳ Processing video...")
    
    # Update processing message periodically to show progress
    stop_progress_updates = False
    
    async def update_progress():
        progress_states = ["⏳ Processing video.", "⏳ Processing video..", "⏳ Processing video..."]
        i = 0
        while not stop_progress_updates:
            try:
                await processing_msg.edit_text(progress_states[i % len(progress_states)])
                i += 1
                await asyncio.sleep(3)  # Update every 3 seconds
            except Exception:
                break
    
    # Start progress updates in background
    progress_task = asyncio.create_task(update_progress())
    
    try:
        # Download the video
        logger.info(f"Starting download for {platform} video: {video_id}")
        video_path = downloader.download_video(url, platform, video_id)
        logger.info(f"Download completed, file path: {video_path}")
        
        # Stop progress updates
        stop_progress_updates = True
        try:
            await progress_task
        except Exception as e:
            logger.error(f"Error stopping progress task: {e}")
        
        if not video_path or not os.path.exists(video_path):
            logger.error(f"Video file not found after download: {video_path}")
            await processing_msg.edit_text("❌ Failed to download video. The video might be unavailable or private.")
            return
        
        # Verify the video file is valid
        if not is_valid_video_file(video_path):
            logger.error(f"Invalid video file: {video_path}")
            await processing_msg.edit_text("❌ The downloaded file is not a valid video. Please try a different video.")
            try:
                os.remove(video_path)
            except Exception:
                pass
            return
        
        # Log file details
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"Sending video file: {video_path}, Size: {file_size_mb:.2f}MB")
        
        # Send the video with better error handling
        try:
            with open(video_path, 'rb') as video_file:
                logger.info("Sending video to Telegram...")
                # Use InputFile to ensure proper file handling
                await message.reply_video(
                    video=types.BufferedInputFile(
                        video_file.read(),
                        filename=f"{platform}_{video_id}.mp4"
                    ),
                    caption=f"Shared by: {sender_name}",
                    supports_streaming=True
                )
                logger.info("Video sent successfully")
        except TelegramAPIError as api_error:
            logger.error(f"Telegram API error when sending video: {api_error}")
            await processing_msg.edit_text(f"❌ Error sending video: {str(api_error)}")
            return
        except Exception as send_error:
            logger.error(f"Error sending video: {send_error}\n{traceback.format_exc()}")
            await processing_msg.edit_text(f"❌ Error sending video: {str(send_error)}")
            return
        
        # Delete the original message
        try:
            await message.delete()
            logger.info("Original message deleted")
        except Exception as e:
            logger.error(f"Failed to delete original message: {e}")
        
        # Delete the processing message
        try:
            await processing_msg.delete()
            logger.info("Processing message deleted")
        except Exception as e:
            logger.error(f"Failed to delete processing message: {e}")
        
        # Clean up the downloaded file
        try:
            os.remove(video_path)
            logger.debug(f"Removed temporary file: {video_path}")
        except Exception as e:
            logger.error(f"Failed to remove temporary file: {e}")
            
    except DownloadTimeoutError as e:
        # Stop progress updates
        stop_progress_updates = True
        try:
            await progress_task
        except Exception:
            pass
        
        # Download timeout
        logger.error(f"Download timeout: {e}")
        await processing_msg.edit_text(f"❌ {str(e)}")
    except ValueError as e:
        # Stop progress updates
        stop_progress_updates = True
        try:
            await progress_task
        except Exception:
            pass
        
        # File size exceeded
        logger.error(f"Value error: {e}")
        await processing_msg.edit_text(f"❌ {str(e)}")
    except Exception as e:
        # Stop progress updates
        stop_progress_updates = True
        try:
            await progress_task
        except Exception:
            pass
        
        # Other errors
        error_message = str(e) if str(e) else "An unknown error occurred"
        logger.error(f"Error processing video: {e}\n{traceback.format_exc()}")
        await processing_msg.edit_text(f"❌ {error_message}")

def get_sender_name(message: types.Message) -> str:
    """
    Get the name of the message sender
    
    Args:
        message (types.Message): Telegram message
        
    Returns:
        str: Name of the sender
    """
    if message.from_user:
        # Try to get the user's full name
        if message.from_user.username:
            return f"@{message.from_user.username}"
        elif message.from_user.first_name and message.from_user.last_name:
            return f"{message.from_user.first_name} {message.from_user.last_name}"
        elif message.from_user.first_name:
            return message.from_user.first_name
        else:
            return f"User ID: {message.from_user.id}"
    elif message.sender_chat:
        # Message was sent by a channel or group
        return message.sender_chat.title or f"Chat ID: {message.sender_chat.id}"
    else:
        return "Unknown User"

def setup_handlers(dp):
    """
    Register message handlers
    
    Args:
        dp: Dispatcher instance
    """
    dp.include_router(router) 