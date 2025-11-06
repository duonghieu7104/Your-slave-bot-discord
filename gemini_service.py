"""
Gemini API integration service
"""
import google.generativeai as genai
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """
        Initialize Gemini service
        
        Args:
            api_key: Google Gemini API key
            model_name: Model to use (default: gemini-pro)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat_sessions = {}  # Store chat sessions per user/channel
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate a response from Gemini
        
        Args:
            prompt: User's prompt/question
            context: Additional context (e.g., recent messages, tasks, notes)
        
        Returns:
            Generated response text
        """
        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            return response.text
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _build_prompt(self, user_prompt: str, context: Optional[str] = None) -> str:
        """
        Build the full prompt with system instructions and context
        
        Args:
            user_prompt: User's question/request
            context: Additional context information
        
        Returns:
            Complete prompt string
        """
        system_instruction = """You are a helpful Discord bot assistant that helps users manage tasks, notes, and summarize conversations.

Your capabilities:
- Summarize recent Discord messages
- Help manage tasks (create, update, track)
- Help manage notes (create, search, organize)
- Answer questions about conversation history
- Provide insights and suggestions

When responding:
- Be concise and helpful
- Use Discord-friendly formatting (markdown)
- If asked to create tasks or notes, provide clear confirmation
- If searching or summarizing, be specific about what you found
"""
        
        parts = [system_instruction]
        
        if context:
            parts.append(f"\n--- CONTEXT ---\n{context}\n--- END CONTEXT ---\n")
        
        parts.append(f"\nUser Request: {user_prompt}")
        
        return "\n".join(parts)
    
    def summarize_messages(self, messages: List[Dict], focus: Optional[str] = None) -> str:
        """
        Summarize a list of messages
        
        Args:
            messages: List of message dictionaries
            focus: Optional focus area for summary
        
        Returns:
            Summary text
        """
        if not messages:
            return "No messages to summarize."
        
        # Format messages for context
        message_text = "\n".join([
            f"[{msg['timestamp']}] {msg['author']}: {msg['content']}"
            for msg in messages
        ])
        
        prompt = "Please provide a concise summary of the following Discord conversation"
        if focus:
            prompt += f", focusing on: {focus}"
        prompt += "."
        
        return self.generate_response(prompt, message_text)
    
    def analyze_tasks(self, tasks: List[Dict], query: str) -> str:
        """
        Analyze tasks based on user query
        
        Args:
            tasks: List of task dictionaries
            query: User's query about tasks
        
        Returns:
            Analysis response
        """
        if not tasks:
            return "No tasks found to analyze."
        
        # Format tasks for context
        task_text = "\n".join([
            f"Task #{task['id']}: {task['title']} (Status: {task['status']}, Priority: {task['priority']})\n"
            f"  Description: {task['description']}\n"
            f"  Created: {task['created_at']}"
            for task in tasks
        ])
        
        context = f"Current Tasks:\n{task_text}"
        
        return self.generate_response(query, context)
    
    def analyze_notes(self, notes: List[Dict], query: str) -> str:
        """
        Analyze notes based on user query
        
        Args:
            notes: List of note dictionaries
            query: User's query about notes
        
        Returns:
            Analysis response
        """
        if not notes:
            return "No notes found to analyze."
        
        # Format notes for context
        note_text = "\n".join([
            f"Note #{note['id']}: {note['title']}\n"
            f"  Content: {note['content']}\n"
            f"  Tags: {', '.join(note['tags']) if note['tags'] else 'None'}\n"
            f"  Created: {note['created_at']}"
            for note in notes
        ])
        
        context = f"Current Notes:\n{note_text}"
        
        return self.generate_response(query, context)
    
    def extract_task_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract task information from natural language text
        
        Args:
            text: User's text describing a task
        
        Returns:
            Dictionary with task fields or None
        """
        prompt = f"""Extract task information from the following text and return it in this exact format:
TITLE: <task title>
DESCRIPTION: <task description>
PRIORITY: <low/medium/high>
DUE_DATE: <date if mentioned, otherwise "none">

Text: {text}

Only return the formatted information, nothing else."""
        
        try:
            response = self.generate_response(prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            task_info = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'title':
                        task_info['title'] = value
                    elif key == 'description':
                        task_info['description'] = value
                    elif key == 'priority':
                        task_info['priority'] = value if value in ['low', 'medium', 'high'] else 'medium'
                    elif key == 'due_date':
                        task_info['due_date'] = None if value.lower() == 'none' else value
            
            return task_info if 'title' in task_info else None
        
        except Exception as e:
            logger.error(f"Error extracting task: {e}")
            return None
    
    def extract_note_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract note information from natural language text
        
        Args:
            text: User's text describing a note
        
        Returns:
            Dictionary with note fields or None
        """
        prompt = f"""Extract note information from the following text and return it in this exact format:
TITLE: <note title>
CONTENT: <note content>
TAGS: <comma-separated tags if any, otherwise "none">

Text: {text}

Only return the formatted information, nothing else."""
        
        try:
            response = self.generate_response(prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            note_info = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'title':
                        note_info['title'] = value
                    elif key == 'content':
                        note_info['content'] = value
                    elif key == 'tags':
                        if value.lower() != 'none':
                            note_info['tags'] = [tag.strip() for tag in value.split(',')]
                        else:
                            note_info['tags'] = []
            
            return note_info if 'title' in note_info else None
        
        except Exception as e:
            logger.error(f"Error extracting note: {e}")
            return None

