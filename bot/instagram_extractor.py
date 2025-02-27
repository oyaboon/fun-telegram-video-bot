"""
instagram_extractor.py
---------------------
Purpose: Custom Instagram video extractor that doesn't rely on cookies
Author: AI Assistant
Last Modified: 2024-02-27
"""

import os
import re
import json
import requests
from loguru import logger

class InstagramExtractor:
    """
    Custom Instagram video extractor that doesn't rely on cookies
    """
    
    def __init__(self):
        """
        Initialize the Instagram extractor
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def extract_video_url(self, instagram_url):
        """
        Extract video URL from Instagram post URL
        
        Args:
            instagram_url (str): Instagram post URL
            
        Returns:
            str: Direct video URL or None if extraction failed
        """
        try:
            # Clean up the URL
            instagram_url = self._clean_url(instagram_url)
            logger.info(f"Extracting video from Instagram URL: {instagram_url}")
            
            # Try to use the Instagram oEmbed API first
            oembed_url = f"https://api.instagram.com/oembed/?url={instagram_url}"
            response = requests.get(oembed_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("Successfully accessed Instagram oEmbed API")
                # The oEmbed API doesn't provide direct video URLs, but we can get the post ID
                data = response.json()
                if 'media_id' in data:
                    media_id = data['media_id']
                    logger.info(f"Found media ID: {media_id}")
                    # Now we can try to get the video URL using the media ID
                    # This would require additional API calls that might need authentication
            
            # If oEmbed doesn't work, try to scrape the page
            response = requests.get(instagram_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Try to find the video URL in the page
                # Look for video URLs in the page
                video_urls = re.findall(r'\"video_url\":\"([^\"]+)\"', html_content)
                if video_urls:
                    # Unescape the URL
                    video_url = video_urls[0].replace('\\u0026', '&')
                    logger.info(f"Found video URL: {video_url}")
                    return video_url
                
                # Try to find the shared data JSON
                shared_data_match = re.search(r'<script type="text/javascript">window\._sharedData = (.+?);</script>', html_content)
                if shared_data_match:
                    shared_data = json.loads(shared_data_match.group(1))
                    
                    # Navigate through the JSON to find the video URL
                    try:
                        if 'entry_data' in shared_data and 'PostPage' in shared_data['entry_data']:
                            post = shared_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
                            if post['is_video']:
                                video_url = post['video_url']
                                logger.info(f"Found video URL in shared data: {video_url}")
                                return video_url
                    except (KeyError, IndexError) as e:
                        logger.error(f"Error parsing shared data: {e}")
                
                # Try to find additional data in the page
                additional_data_match = re.search(r'<script type="text/javascript">window\.__additionalDataLoaded\(\'[^\']+\',(.+?)\);</script>', html_content)
                if additional_data_match:
                    try:
                        additional_data = json.loads(additional_data_match.group(1))
                        if 'graphql' in additional_data and 'shortcode_media' in additional_data['graphql']:
                            post = additional_data['graphql']['shortcode_media']
                            if post['is_video']:
                                video_url = post['video_url']
                                logger.info(f"Found video URL in additional data: {video_url}")
                                return video_url
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error(f"Error parsing additional data: {e}")
            
            logger.error(f"Failed to extract video URL from {instagram_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting Instagram video URL: {e}")
            return None
    
    def download_video(self, instagram_url, output_path):
        """
        Download video from Instagram URL
        
        Args:
            instagram_url (str): Instagram post URL
            output_path (str): Path to save the video
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            video_url = self.extract_video_url(instagram_url)
            if not video_url:
                logger.error(f"Could not extract video URL from {instagram_url}")
                return False
            
            # Download the video
            logger.info(f"Downloading video from {video_url}")
            response = requests.get(video_url, headers=self.headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                
                logger.info(f"Video downloaded to {output_path}")
                return True
            else:
                logger.error(f"Failed to download video: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading Instagram video: {e}")
            return False
    
    def _clean_url(self, url):
        """
        Clean up Instagram URL
        
        Args:
            url (str): Instagram URL
            
        Returns:
            str: Cleaned URL
        """
        # Remove query parameters
        url = re.sub(r'\?.*$', '', url)
        
        # Ensure URL ends with /
        if not url.endswith('/'):
            url += '/'
            
        return url 