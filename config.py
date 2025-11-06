"""
Configuration module for Discord Task & Note Manager Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration settings"""
    
    # Discord settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!g')
    
    # Gemini API settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # Bot behavior settings
    MESSAGE_BUFFER_SIZE = int(os.getenv('MESSAGE_BUFFER_SIZE', '500'))
    MONITORED_CHANNELS = [
        int(ch_id.strip()) 
        for ch_id in os.getenv('MONITORED_CHANNELS', '').split(',') 
        if ch_id.strip()
    ]
    
    # Persistence settings
    ENABLE_PERSISTENCE = os.getenv('ENABLE_PERSISTENCE', 'true').lower() == 'true'
    PERSISTENCE_FILE = os.getenv('PERSISTENCE_FILE', 'data/bot_data.json')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        return True

