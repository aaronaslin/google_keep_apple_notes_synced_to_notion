"""
Google Keep Parser Module

This module handles parsing notes from Google Keep using the gkeepapi library.
"""

import gkeepapi
from typing import List, Dict, Optional
from datetime import datetime


class GoogleKeepParser:
    """Parser for Google Keep notes."""
    
    def __init__(self, username: str, password: str):
        """
        Initialize the Google Keep parser.
        
        Args:
            username: Google account email
            password: Google account password or app password
        """
        self.username = username
        self.password = password
        self.keep = gkeepapi.Keep()
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Keep.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.keep.login(self.username, self.password)
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_notes(self) -> List[Dict]:
        """
        Retrieve all notes from Google Keep.
        
        Returns:
            List of note dictionaries with standardized format
        """
        notes = []
        
        try:
            # Get all notes from Google Keep
            gnotes = self.keep.all()
            
            for note in gnotes:
                # Skip archived and deleted notes unless you want them
                if note.trashed:
                    continue
                
                note_data = {
                    'title': note.title or 'Untitled',
                    'content': note.text,
                    'source': 'Google Keep',
                    'created_time': note.timestamps.created.isoformat() if note.timestamps.created else None,
                    'updated_time': note.timestamps.updated.isoformat() if note.timestamps.updated else None,
                    'archived': note.archived,
                    'pinned': note.pinned,
                    'color': note.color.name if hasattr(note.color, 'name') else None,
                    'labels': [label.name for label in note.labels.all()],
                    'url': note.url if hasattr(note, 'url') else None,
                }
                
                # Handle list items for checklist notes
                if hasattr(note, 'items') and note.items:
                    checklist_items = []
                    for item in note.items:
                        checklist_items.append({
                            'text': item.text,
                            'checked': item.checked
                        })
                    note_data['checklist'] = checklist_items
                
                notes.append(note_data)
                
            print(f"Retrieved {len(notes)} notes from Google Keep")
            return notes
            
        except Exception as e:
            print(f"Error retrieving notes: {e}")
            return []


def parse_google_keep(username: str, password: str) -> List[Dict]:
    """
    Parse notes from Google Keep.
    
    Args:
        username: Google account email
        password: Google account password or app password
        
    Returns:
        List of parsed notes in standardized format
    """
    parser = GoogleKeepParser(username, password)
    
    if not parser.authenticate():
        print("Failed to authenticate with Google Keep")
        return []
    
    return parser.get_notes()
