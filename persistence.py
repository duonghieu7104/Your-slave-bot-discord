"""
Persistence layer for saving and loading bot data
"""
import json
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PersistenceManager:
    """Manager for persisting bot data to JSON files"""
    
    def __init__(self, file_path: str = "data/bot_data.json"):
        """
        Initialize persistence manager
        
        Args:
            file_path: Path to JSON file for storage
        """
        self.file_path = file_path
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure the data directory exists"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created data directory: {directory}")
    
    def save(self, data: Dict) -> bool:
        """
        Save data to JSON file
        
        Args:
            data: Dictionary containing all bot data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {self.file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def load(self) -> Optional[Dict]:
        """
        Load data from JSON file
        
        Returns:
            Dictionary containing bot data, or None if file doesn't exist or error occurs
        """
        if not os.path.exists(self.file_path):
            logger.info(f"No existing data file found at {self.file_path}")
            return None
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Data loaded from {self.file_path}")
            return data
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    def backup(self) -> bool:
        """
        Create a backup of the current data file
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.file_path):
            logger.warning("No data file to backup")
            return False
        
        try:
            backup_path = f"{self.file_path}.backup"
            with open(self.file_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            logger.info(f"Backup created at {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Delete the data file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                logger.info(f"Data file deleted: {self.file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting data file: {e}")
            return False

