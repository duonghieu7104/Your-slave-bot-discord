"""
Task and Note management system
"""
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskNoteManager:
    """Manager for tasks and notes"""
    
    def __init__(self):
        """Initialize task and note storage"""
        self.tasks = []
        self.notes = []
        self.task_id_counter = 1
        self.note_id_counter = 1
    
    # ===== TASK MANAGEMENT =====
    
    def add_task(self, title: str, description: str = "", author_id: int = None, 
                 due_date: Optional[str] = None, priority: str = "medium") -> Dict:
        """
        Add a new task
        
        Args:
            title: Task title
            description: Task description
            author_id: Discord user ID who created the task
            due_date: Due date string (optional)
            priority: Task priority (low, medium, high)
        
        Returns:
            Created task dictionary
        """
        task = {
            'id': self.task_id_counter,
            'title': title,
            'description': description,
            'status': TaskStatus.TODO.value,
            'author_id': author_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'due_date': due_date,
            'priority': priority,
            'tags': []
        }
        
        self.tasks.append(task)
        self.task_id_counter += 1
        return task
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a task by ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status (todo, in_progress, done, cancelled)
        
        Returns:
            True if successful, False otherwise
        """
        task = self.get_task(task_id)
        if task:
            task['status'] = status
            task['updated_at'] = datetime.now().isoformat()
            return True
        return False
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """
        Update task fields
        
        Args:
            task_id: Task ID
            **kwargs: Fields to update
        
        Returns:
            True if successful, False otherwise
        """
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if key in task and key not in ['id', 'created_at']:
                    task[key] = value
            task['updated_at'] = datetime.now().isoformat()
            return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_tasks(self, status: Optional[str] = None, author_id: Optional[int] = None,
                  priority: Optional[str] = None) -> List[Dict]:
        """
        Get tasks with optional filters
        
        Args:
            status: Filter by status
            author_id: Filter by author
            priority: Filter by priority
        
        Returns:
            List of matching tasks
        """
        results = self.tasks.copy()
        
        if status:
            results = [t for t in results if t['status'] == status]
        
        if author_id:
            results = [t for t in results if t['author_id'] == author_id]
        
        if priority:
            results = [t for t in results if t['priority'] == priority]
        
        return results
    
    def search_tasks(self, query: str) -> List[Dict]:
        """Search tasks by title or description"""
        query_lower = query.lower()
        results = []
        
        for task in self.tasks:
            if (query_lower in task['title'].lower() or 
                query_lower in task['description'].lower()):
                results.append(task)
        
        return results
    
    # ===== NOTE MANAGEMENT =====
    
    def add_note(self, title: str, content: str, author_id: int = None, 
                 tags: List[str] = None) -> Dict:
        """
        Add a new note
        
        Args:
            title: Note title
            content: Note content
            author_id: Discord user ID who created the note
            tags: List of tags
        
        Returns:
            Created note dictionary
        """
        note = {
            'id': self.note_id_counter,
            'title': title,
            'content': content,
            'author_id': author_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': tags or []
        }
        
        self.notes.append(note)
        self.note_id_counter += 1
        return note
    
    def get_note(self, note_id: int) -> Optional[Dict]:
        """Get a note by ID"""
        for note in self.notes:
            if note['id'] == note_id:
                return note
        return None
    
    def update_note(self, note_id: int, **kwargs) -> bool:
        """
        Update note fields
        
        Args:
            note_id: Note ID
            **kwargs: Fields to update
        
        Returns:
            True if successful, False otherwise
        """
        note = self.get_note(note_id)
        if note:
            for key, value in kwargs.items():
                if key in note and key not in ['id', 'created_at']:
                    note[key] = value
            note['updated_at'] = datetime.now().isoformat()
            return True
        return False
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        note = self.get_note(note_id)
        if note:
            self.notes.remove(note)
            return True
        return False
    
    def get_notes(self, author_id: Optional[int] = None, tag: Optional[str] = None) -> List[Dict]:
        """
        Get notes with optional filters
        
        Args:
            author_id: Filter by author
            tag: Filter by tag
        
        Returns:
            List of matching notes
        """
        results = self.notes.copy()
        
        if author_id:
            results = [n for n in results if n['author_id'] == author_id]
        
        if tag:
            results = [n for n in results if tag in n['tags']]
        
        return results
    
    def search_notes(self, query: str) -> List[Dict]:
        """Search notes by title or content"""
        query_lower = query.lower()
        results = []
        
        for note in self.notes:
            if (query_lower in note['title'].lower() or 
                query_lower in note['content'].lower()):
                results.append(note)
        
        return results
    
    # ===== UTILITY METHODS =====
    
    def get_stats(self) -> Dict:
        """Get statistics about tasks and notes"""
        task_stats = {
            'total': len(self.tasks),
            'todo': len([t for t in self.tasks if t['status'] == TaskStatus.TODO.value]),
            'in_progress': len([t for t in self.tasks if t['status'] == TaskStatus.IN_PROGRESS.value]),
            'done': len([t for t in self.tasks if t['status'] == TaskStatus.DONE.value]),
            'cancelled': len([t for t in self.tasks if t['status'] == TaskStatus.CANCELLED.value])
        }
        
        return {
            'tasks': task_stats,
            'notes': {
                'total': len(self.notes)
            }
        }
    
    def to_dict(self) -> Dict:
        """Export all data to dictionary for persistence"""
        return {
            'tasks': self.tasks,
            'notes': self.notes,
            'task_id_counter': self.task_id_counter,
            'note_id_counter': self.note_id_counter
        }
    
    def from_dict(self, data: Dict):
        """Import data from dictionary"""
        self.tasks = data.get('tasks', [])
        self.notes = data.get('notes', [])
        self.task_id_counter = data.get('task_id_counter', 1)
        self.note_id_counter = data.get('note_id_counter', 1)

