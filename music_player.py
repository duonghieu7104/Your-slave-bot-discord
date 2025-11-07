"""
Music player module for YouTube audio playback
"""
import discord
import asyncio
import yt_dlp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MusicPlayer:
    """Handles YouTube audio playback in voice channels"""
    
    def __init__(self, bot):
        """Initialize music player"""
        self.bot = bot
        self.voice_client: Optional[discord.VoiceClient] = None
        self.current_song = None
        self.is_playing = False
        
        # yt-dlp options for audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }
        
        # FFmpeg options
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
    
    async def join_voice_channel(self, channel_id: int) -> bool:
        """Join a voice channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Voice channel {channel_id} not found")
                return False
            
            if not isinstance(channel, discord.VoiceChannel):
                logger.error(f"Channel {channel_id} is not a voice channel")
                return False
            
            # If already connected to this channel
            if self.voice_client and self.voice_client.channel.id == channel_id:
                logger.info(f"Already connected to voice channel {channel.name}")
                return True
            
            # Disconnect from current channel if connected elsewhere
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()
            
            # Connect to the voice channel
            self.voice_client = await channel.connect()
            logger.info(f"Connected to voice channel: {channel.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining voice channel: {e}")
            return False
    
    async def leave_voice_channel(self):
        """Leave the current voice channel"""
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            self.voice_client = None
            self.is_playing = False
            logger.info("Disconnected from voice channel")
    
    def extract_info(self, url: str) -> Optional[dict]:
        """Extract video information from YouTube URL"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Handle playlists
                if 'entries' in info:
                    info = info['entries'][0]
                
                return {
                    'url': info['url'],
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url)
                }
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            return None
    
    async def play(self, url: str, channel_id: int) -> tuple[bool, str]:
        """
        Play audio from YouTube URL
        
        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            # Join voice channel
            if not await self.join_voice_channel(channel_id):
                return False, "Failed to join voice channel"
            
            # Stop current playback if any
            if self.voice_client.is_playing():
                self.voice_client.stop()
            
            # Extract video info
            logger.info(f"Extracting info from: {url}")
            info = self.extract_info(url)
            
            if not info:
                return False, "Failed to extract video information"
            
            self.current_song = info
            
            # Create audio source
            audio_source = discord.FFmpegPCMAudio(
                info['url'],
                **self.ffmpeg_options
            )
            
            # Play audio
            def after_playing(error):
                if error:
                    logger.error(f"Playback error: {error}")
                self.is_playing = False
                self.current_song = None
            
            self.voice_client.play(audio_source, after=after_playing)
            self.is_playing = True
            
            logger.info(f"Now playing: {info['title']}")
            return True, f"Now playing: **{info['title']}**"
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False, f"Error: {str(e)}"
    
    async def stop(self) -> bool:
        """Stop current playback"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            self.is_playing = False
            self.current_song = None
            logger.info("Playback stopped")
            return True
        return False
    
    async def pause(self) -> bool:
        """Pause current playback"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            logger.info("Playback paused")
            return True
        return False
    
    async def resume(self) -> bool:
        """Resume paused playback"""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            logger.info("Playback resumed")
            return True
        return False
    
    def get_current_song(self) -> Optional[dict]:
        """Get currently playing song info"""
        return self.current_song if self.is_playing else None

