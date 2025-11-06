"""
Message buffer system for storing and retrieving Discord messages
"""
from collections import deque
from datetime import datetime
from typing import List, Dict, Optional
import discord
import logging

logger = logging.getLogger(__name__)


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
        self.context_channels = set()  # Channels for notes/plans (used as context)
        self.command_channels = set()  # Channels for bot commands (not used as context)
        self.monitored_channels = set()  # Legacy: all channels combined
    
    def add_monitored_channel(self, channel_id: int):
        """Add a channel to monitor (legacy method)"""
        self.monitored_channels.add(channel_id)

    def remove_monitored_channel(self, channel_id: int):
        """Remove a channel from monitoring"""
        self.monitored_channels.discard(channel_id)

    def set_context_channels(self, channel_ids: List[int]):
        """Set channels where messages are used as context (notes, plans, docs)"""
        self.context_channels = set(channel_ids)
        self.monitored_channels.update(channel_ids)
        logger.info(f"📚 Context channels set: {channel_ids}")

    def set_command_channels(self, channel_ids: List[int]):
        """Set channels where bot responds to commands (not used as context)"""
        self.command_channels = set(channel_ids)
        self.monitored_channels.update(channel_ids)
        logger.info(f"🤖 Command channels set: {channel_ids}")

    def is_monitored(self, channel_id: int) -> bool:
        """Check if a channel is being monitored (either type)"""
        return channel_id in self.monitored_channels

    def is_context_channel(self, channel_id: int) -> bool:
        """Check if a channel is a context channel (notes/plans)"""
        return channel_id in self.context_channels

    def is_command_channel(self, channel_id: int) -> bool:
        """Check if a channel is a command-only channel"""
        return channel_id in self.command_channels
    
    def add_message(self, message: discord.Message):
        """
        Add a message to the buffer
        Only messages from CONTEXT channels are stored for Gemini context

        Args:
            message: Discord message object
        """
        if not self.is_monitored(message.channel.id):
            return

        # Only store messages from context channels (notes, plans, docs)
        if self.is_context_channel(message.channel.id):
            # Get channel name (not just ID)
            channel_name = message.channel.name if hasattr(message.channel, 'name') else str(message.channel)

            message_data = {
                'id': message.id,
                'author': str(message.author),
                'author_id': message.author.id,
                'content': message.content,
                'channel': str(message.channel),
                'channel_id': message.channel.id,
                'channel_name': channel_name,  # Store channel name
                'timestamp': message.created_at.isoformat(),
                'attachments': [att.url for att in message.attachments],
                'embeds': len(message.embeds) > 0
            }

            self.messages.append(message_data)
            logger.info(f"📝 Context message added from #{channel_name}: [{message.author}] {message.content[:50]}... (Buffer: {len(self.messages)})")
        elif self.is_command_channel(message.channel.id):
            logger.info(f"🤖 Command channel message (not stored): [{message.author}] {message.content[:50]}...")
    
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
        logger.info(f"📚 Buffer contains {len(messages)} total messages")

        # Filter by channel if specified
        if channel_id is not None:
            messages = [msg for msg in messages if msg['channel_id'] == channel_id]
            logger.info(f"Filtered to {len(messages)} messages from channel {channel_id}")

        # Apply limit
        if limit is not None:
            messages = messages[-limit:]
            logger.info(f"Limited to most recent {len(messages)} messages")

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
    
    def format_messages_for_context(self, messages: List[Dict], max_chars: int = 8000) -> str:
        """
        Format messages for sending to Gemini as context
        Groups by channel and includes channel names

        Args:
            messages: List of message dictionaries
            max_chars: Maximum character limit for context

        Returns:
            Formatted string of messages grouped by channel
        """
        if not messages:
            return "No recent messages available."

        # Group messages by channel
        channels = {}
        for msg in messages:
            channel_name = msg.get('channel_name', 'unknown-channel')
            if channel_name not in channels:
                channels[channel_name] = []
            channels[channel_name].append(msg)

        # Format by channel
        formatted_lines = []
        total_chars = 0

        for channel_name, channel_messages in channels.items():
            # Channel header
            header = f"\n📌 Channel: #{channel_name}"
            separator = "=" * 60

            formatted_lines.append(header)
            formatted_lines.append(separator)
            total_chars += len(header) + len(separator) + 2

            # Messages in this channel
            for msg in channel_messages:
                timestamp = msg['timestamp'][:19]  # Remove microseconds
                line = f"[{timestamp}] {msg['author']}: {msg['content']}"

                line_length = len(line) + 1  # +1 for newline
                if total_chars + line_length > max_chars:
                    formatted_lines.append("... (context truncated)")
                    break

                formatted_lines.append(line)
                total_chars += line_length

            formatted_lines.append("")  # Empty line between channels

        return "\n".join(formatted_lines)

