"""
downloader.py
------------
Purpose: Video download logic using yt-dlp
Author: AI Assistant
Last Modified: 2024-02-27
"""

import os
import time
import shutil
import subprocess
import threading
from loguru import logger
import yt_dlp

from .utils import get_temp_filepath, MAX_FILE_SIZE, TARGET_QUALITY
from .instagram_extractor import InstagramExtractor

# Set a download timeout (in seconds)
DOWNLOAD_TIMEOUT = 180  # 3 minutes

# Try to find FFmpeg in common locations
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
            logger.info("FFmpeg found in PATH")
            return 'ffmpeg'
    except Exception:
        pass
    
    # Check common installation locations
    possible_paths = [
        os.path.expanduser("~/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"),
        "C:/ffmpeg/bin/ffmpeg.exe",
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
        os.path.expanduser("~/ffmpeg/bin/ffmpeg.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"FFmpeg found at: {path}")
            return path
    
    logger.warning("FFmpeg not found. Video processing may fail.")
    return None

# Find FFmpeg path
FFMPEG_PATH = find_ffmpeg()

class DownloadTimeoutError(Exception):
    """Exception raised when download takes too long"""
    pass

class VideoDownloader:
    """
    Class for downloading videos from supported platforms
    """
    
    def __init__(self):
        """
        Initialize the VideoDownloader
        """
        # Base options for all platforms
        self.base_opts = {
            'quiet': False,  # Set to False to see download progress
            'no_warnings': False,  # Set to False to see warnings
            'ignoreerrors': False,
            'nooverwrites': True,
            'noplaylist': True,
            'writethumbnail': False,
            'socket_timeout': 30,  # Socket timeout in seconds
            'merge_output_format': 'mp4',  # Force output to be mp4
        }
        
        # Add FFmpeg location if found
        if FFMPEG_PATH:
            self.base_opts['ffmpeg_location'] = os.path.dirname(FFMPEG_PATH)
            
        # Initialize custom extractors
        self.instagram_extractor = InstagramExtractor()
    
    def _get_platform_options(self, platform):
        """
        Get platform-specific download options
        
        Args:
            platform (str): Platform name (youtube, tiktok, instagram, vk)
            
        Returns:
            dict: Platform-specific options
        """
        opts = self.base_opts.copy()
        
        # Platform-specific format selection
        if platform == "youtube":
            opts['format'] = f'best[ext=mp4][height<={TARGET_QUALITY}]/bestvideo[ext=mp4][height<={TARGET_QUALITY}]+bestaudio[ext=m4a]/best[height<={TARGET_QUALITY}]'
        elif platform == "tiktok":
            # TikTok options without cookies
            opts['format'] = 'best[ext=mp4]/best'
            # Add custom headers to mimic a browser
            opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.tiktok.com/',
            }
            # Don't use cookies for TikTok
            opts.pop('cookiesfrombrowser', None)
        elif platform == "instagram":
            # Instagram options without cookies
            opts['format'] = 'best[ext=mp4]/best'
            # Add custom headers to mimic a browser
            opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.instagram.com/',
            }
            # Don't use cookies for Instagram
            opts.pop('cookiesfrombrowser', None)
        elif platform == "vk":
            # VK options without cookies
            opts['format'] = 'best[ext=mp4]/best'
            # Add custom headers to mimic a browser
            opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://vk.com/',
            }
            # Don't use cookies for VK
            opts.pop('cookiesfrombrowser', None)
        else:
            # Default format for other platforms
            opts['format'] = 'best[ext=mp4]/best'
        
        return opts
    
    def _download_with_timeout(self, ydl, url):
        """
        Download with timeout using a separate thread
        
        Args:
            ydl: YoutubeDL instance
            url: URL to download
            
        Returns:
            dict: Video info or None if timeout
            
        Raises:
            DownloadTimeoutError: If download times out
        """
        result = {"info": None, "error": None}
        
        def download_thread():
            try:
                result["info"] = ydl.extract_info(url, download=True)
            except Exception as e:
                result["error"] = e
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        # Wait for the thread to complete or timeout
        thread.join(DOWNLOAD_TIMEOUT)
        
        if thread.is_alive():
            # Download is taking too long, raise timeout error
            logger.error(f"Download timed out after {DOWNLOAD_TIMEOUT} seconds")
            raise DownloadTimeoutError(f"Download timed out after {DOWNLOAD_TIMEOUT} seconds. Try again later or try a different video.")
        
        if result["error"]:
            raise result["error"]
            
        return result["info"]
    
    def download_video(self, url, platform, video_id):
        """
        Download video from URL
        
        Args:
            url (str): URL to download from
            platform (str): Platform name (youtube, tiktok, instagram, vk)
            video_id (str): Video ID or full URL
            
        Returns:
            str: Path to downloaded file or None if download failed
            
        Raises:
            ValueError: If file size exceeds maximum allowed size
            Exception: For other download errors
        """
        # For platforms where video_id is the full URL, use the original URL
        if platform in ["tiktok", "instagram", "vk"]:
            url_to_download = url
        else:
            url_to_download = url
            
        temp_filepath = get_temp_filepath(platform, video_id)
        temp_dir = os.path.dirname(temp_filepath)
        
        # Ensure temp directory exists
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            logger.info(f"Downloading video from {platform}: {url_to_download}")
            start_time = time.time()
            
            # Special handling for Instagram - use our custom extractor
            if platform == "instagram":
                logger.info("Using custom Instagram extractor")
                success = self.instagram_extractor.download_video(url_to_download, temp_filepath)
                
                if success:
                    # Check file size
                    file_size_mb = os.path.getsize(temp_filepath) / (1024 * 1024)
                    if file_size_mb > MAX_FILE_SIZE:
                        logger.warning(f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE}MB)")
                        os.remove(temp_filepath)
                        raise ValueError(f"Video is too large ({file_size_mb:.2f}MB). Maximum allowed size is {MAX_FILE_SIZE}MB.")
                    
                    download_time = time.time() - start_time
                    logger.info(f"Download completed in {download_time:.2f}s. Size: {file_size_mb:.2f}MB")
                    return temp_filepath
                else:
                    # If custom extractor fails, fall back to yt-dlp
                    logger.info("Custom Instagram extractor failed, falling back to yt-dlp")
            
            # For other platforms or if Instagram custom extractor failed, use yt-dlp
            # Get platform-specific options
            ydl_opts = self._get_platform_options(platform)
            
            # Set output template to temp directory
            ydl_opts['outtmpl'] = os.path.join(temp_dir, f"{platform}_{os.path.basename(temp_filepath)}")
            
            # Special handling for Instagram URLs with yt-dlp
            if platform == "instagram":
                # Try to convert Instagram URL to a more direct format
                if "instagram.com/reel/" in url_to_download or "instagram.com/p/" in url_to_download:
                    # Extract the media ID
                    import re
                    media_id = re.search(r'/(reel|p)/([^/?]+)', url_to_download)
                    if media_id and len(media_id.groups()) >= 2:
                        # Create a more direct URL format
                        direct_url = f"https://www.instagram.com/{media_id.group(1)}/{media_id.group(2)}/"
                        logger.info(f"Using direct Instagram URL: {direct_url}")
                        url_to_download = direct_url
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Use timeout version of download
                info = self._download_with_timeout(ydl, url_to_download)
                
                if not info:
                    logger.error(f"Failed to extract info from {url_to_download}")
                    return None
                
                # Get the downloaded file path
                if 'requested_downloads' in info and info['requested_downloads']:
                    downloaded_file = info['requested_downloads'][0]['filepath']
                else:
                    # Fallback to expected path
                    downloaded_file = temp_filepath
                
                # Check if file exists
                if not os.path.exists(downloaded_file):
                    logger.error(f"Downloaded file not found: {downloaded_file}")
                    # Try to find any file with the platform in the name
                    possible_files = [f for f in os.listdir(temp_dir) if platform in f]
                    if possible_files:
                        # Sort by modification time to get the most recent file
                        possible_files.sort(key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)), reverse=True)
                        downloaded_file = os.path.join(temp_dir, possible_files[0])
                        logger.info(f"Found alternative file: {downloaded_file}")
                    else:
                        return None
                
                # Check file size
                file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE:
                    logger.warning(f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE}MB)")
                    os.remove(downloaded_file)
                    raise ValueError(f"Video is too large ({file_size_mb:.2f}MB). Maximum allowed size is {MAX_FILE_SIZE}MB.")
                
                # Ensure file has .mp4 extension
                if not downloaded_file.endswith('.mp4'):
                    new_filepath = f"{os.path.splitext(downloaded_file)[0]}.mp4"
                    shutil.move(downloaded_file, new_filepath)
                    downloaded_file = new_filepath
                
                download_time = time.time() - start_time
                logger.info(f"Download completed in {download_time:.2f}s. Size: {file_size_mb:.2f}MB")
                
                return downloaded_file
                
        except DownloadTimeoutError as e:
            logger.error(f"Download timeout: {str(e)}")
            raise
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Download error: {str(e)}")
            error_msg = str(e).lower()
            
            if "video unavailable" in error_msg:
                raise Exception("This video is no longer available or is private.")
            elif "not available in your country" in error_msg:
                raise Exception("This video is geo-restricted and not available in the bot's region.")
            elif "ffmpeg is not installed" in error_msg:
                raise Exception("FFmpeg is not properly installed. Please restart your terminal or install FFmpeg.")
            elif "unable to download webpage" in error_msg or "http error" in error_msg:
                raise Exception("Network error while downloading. Please try again later.")
            elif "unsupported url" in error_msg:
                raise Exception("This URL is not supported. Please try a direct link to the video.")
            elif "sign in to confirm your age" in error_msg or "age-restricted" in error_msg:
                raise Exception("This video is age-restricted and cannot be downloaded.")
            elif "private video" in error_msg:
                raise Exception("This video is private and cannot be downloaded.")
            elif "login required" in error_msg or "requires authentication" in error_msg:
                if platform == "instagram":
                    raise Exception("This Instagram content requires login. Try using a public Instagram video.")
                elif platform == "tiktok":
                    raise Exception("This TikTok content requires login. Try using a public TikTok video.")
                else:
                    raise Exception("This content requires login and cannot be downloaded.")
            elif "could not copy chrome cookie database" in error_msg:
                if platform == "instagram":
                    raise Exception("Could not access Instagram content. Try using a different Instagram link format.")
                elif platform == "tiktok":
                    raise Exception("Could not access TikTok content. Try using a different TikTok link format.")
                else:
                    raise Exception("Could not access browser cookies. Try using a different link format.")
            else:
                raise Exception(f"Failed to download video: {str(e)}")
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
            
    def get_video_info(self, url):
        """
        Get video information without downloading
        
        Args:
            url (str): URL to get info from
            
        Returns:
            dict: Video information or None if extraction failed
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            logger.error(f"Error extracting video info: {str(e)}")
            return None 