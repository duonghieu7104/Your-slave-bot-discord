"""
Message buffer system for storing and retrieving Discord messages
"""
from collections import deque
from datetime import datetime
from typing import List, Dict, Optional
import discord


class MessageBuffer:
    """In-memory circular buffer for storing Discord messages"""
    
    def __init__(self, max_size: int = 500):
        """
        Initialize message buffer
        
        Args:
            max_size: Maximum number of messages to store
        """
        self.max_size = max_size
        self.messages = deque(maxlen=max_size)
        self.monitored_channels = set()
    
    def add_monitored_channel(self, channel_id: int):
        """Add a channel to monitor"""
        self.monitored_channels.add(channel_id)
    
    def remove_monitored_channel(self, channel_id: int):
        """Remove a channel from monitoring"""
        self.monitored_channels.discard(channel_id)
    
    def is_monitored(self, channel_id: int) -> bool:
        """Check if a channel is being monitored"""
        return channel_id in self.monitored_channels
    
    def add_message(self, message: discord.Message):
        """
        Add a message to the buffer
        
        Args:
            message: Discord message object
        """
        if not self.is_monitored(message.channel.id):
            return
        
        message_data = {
            'id': message.id,
            'author': str(message.author),
            'author_id': message.author.id,
            'content': message.content,
            'channel': str(message.channel),
            'channel_id': message.channel.id,
            'timestamp': message.created_at.isoformat(),
            'attachments': [att.url for att in message.attachments],
            'embeds': len(message.embeds) > 0
        }
        
        self.messages.append(message_data)
    
    def get_recent_messages(self, limit: Optional[int] = None, channel_id: Optional[int] = None) -> List[Dict]:
        """
        Get recent messages from buffer
        
        Args:
            limit: Maximum number of messages to return (None for all)
            channel_id: Filter by specific channel (None for all channels)
        
        Returns:
            List of message dictionaries
        """
        messages = list(self.messages)
        
        # Filter by channel if specified
        if channel_id is not None:
            messages = [msg for msg in messages if msg['channel_id'] == channel_id]
        
        # Apply limit
        if limit is not None:
            messages = messages[-limit:]
        
        return messages
    
    def search_messages(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search messages by content
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of matching message dictionaries
        """
        query_lower = query.lower()
        results = []
        
        for msg in reversed(self.messages):
            if query_lower in msg['content'].lower():
                results.append(msg)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_messages_by_author(self, author_id: int, limit: int = 50) -> List[Dict]:
        """
        Get messages from a specific author
        
        Args:
            author_id: Discord user ID
            limit: Maximum number of messages
        
        Returns:
            List of message dictionaries
        """
        results = []
        
        for msg in reversed(self.messages):
            if msg['author_id'] == author_id:
                results.append(msg)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_stats(self) -> Dict:
        """Get buffer statistics"""
        return {
            'total_messages': len(self.messages),
            'max_size': self.max_size,
            'monitored_channels': len(self.monitored_channels),
            'channels': list(self.monitored_channels)
        }
    
    def clear(self):
        """Clear all messages from buffer"""
        self.messages.clear()
    
    def format_messages_for_context(self, messages: List[Dict], max_chars: int = 4000) -> str:
        """
        Format messages for sending to Gemini as context
        
        Args:
            messages: List of message dictionaries
            max_chars: Maximum character limit for context
        
        Returns:
            Formatted string of messages
        """
        if not messages:
            return "No recent messages available."
        
        formatted_lines = []
        total_chars = 0
        
        for msg in messages:
            timestamp = msg['timestamp'][:19]  # Remove microseconds
            line = f"[{timestamp}] {msg['author']}: {msg['content']}"
            
            line_length = len(line) + 1  # +1 for newline
            if total_chars + line_length > max_chars:
                break
            
            formatted_lines.append(line)
            total_chars += line_length
        
        return "\n".join(formatted_lines)

