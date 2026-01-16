"""
Notion Uploader Module

This module handles creating a Notion database and uploading notes to it.
"""

from notion_client import Client
from typing import List, Dict, Any, Optional
import time


class NotionUploader:
    """Uploader for creating and populating Notion databases with notes."""
    
    def __init__(self, api_token: str, parent_page_id: str):
        """
        Initialize the Notion uploader.
        
        Args:
            api_token: Notion API integration token
            parent_page_id: ID of the parent page where database will be created
        """
        self.client = Client(auth=api_token)
        self.parent_page_id = parent_page_id
        self.database_id = None
        
    def create_database(self, title: str = "Notes Database") -> Optional[str]:
        """
        Create a new Notion database for notes.
        
        Args:
            title: Title for the new database
            
        Returns:
            Database ID if successful, None otherwise
        """
        try:
            # Define database schema
            database = self.client.databases.create(
                parent={
                    'type': 'page_id',
                    'page_id': self.parent_page_id
                },
                title=[
                    {
                        'type': 'text',
                        'text': {
                            'content': title
                        }
                    }
                ],
                properties={
                    'Title': {
                        'title': {}
                    },
                    'Source': {
                        'select': {
                            'options': [
                                {'name': 'Google Keep', 'color': 'yellow'},
                                {'name': 'Apple Notes', 'color': 'blue'},
                            ]
                        }
                    },
                    'Created': {
                        'date': {}
                    },
                    'Updated': {
                        'date': {}
                    },
                    'Archived': {
                        'checkbox': {}
                    },
                    'Pinned': {
                        'checkbox': {}
                    },
                    'Color': {
                        'select': {
                            'options': [
                                {'name': 'RED', 'color': 'red'},
                                {'name': 'ORANGE', 'color': 'orange'},
                                {'name': 'YELLOW', 'color': 'yellow'},
                                {'name': 'GREEN', 'color': 'green'},
                                {'name': 'BLUE', 'color': 'blue'},
                                {'name': 'PURPLE', 'color': 'purple'},
                                {'name': 'PINK', 'color': 'pink'},
                                {'name': 'BROWN', 'color': 'brown'},
                                {'name': 'GRAY', 'color': 'gray'},
                            ]
                        }
                    },
                    'Tags': {
                        'multi_select': {
                            'options': []
                        }
                    }
                }
            )
            
            self.database_id = database['id']
            print(f"Created Notion database: {title} (ID: {self.database_id})")
            return self.database_id
            
        except Exception as e:
            print(f"Error creating database: {e}")
            return None
    
    def upload_note(self, formatted_note: Dict[str, Any]) -> bool:
        """
        Upload a single note to the Notion database.
        
        Args:
            formatted_note: Note formatted for Notion with properties and children
            
        Returns:
            True if successful, False otherwise
        """
        if not self.database_id:
            print("Database ID not set. Create a database first.")
            return False
        
        try:
            # Create page in database
            page = self.client.pages.create(
                parent={
                    'type': 'database_id',
                    'database_id': self.database_id
                },
                properties=formatted_note['properties'],
                children=formatted_note.get('children', [])
            )
            
            return True
            
        except Exception as e:
            print(f"Error uploading note: {e}")
            return False
    
    def upload_notes(self, formatted_notes: List[Dict[str, Any]], 
                     delay: float = 0.3) -> Dict[str, int]:
        """
        Upload multiple notes to the Notion database.
        
        Args:
            formatted_notes: List of notes formatted for Notion
            delay: Delay between uploads to avoid rate limiting (seconds)
            
        Returns:
            Dictionary with success and failure counts
        """
        if not self.database_id:
            print("Database ID not set. Create a database first.")
            return {'success': 0, 'failed': 0}
        
        results = {'success': 0, 'failed': 0}
        
        for i, note in enumerate(formatted_notes, 1):
            print(f"Uploading note {i}/{len(formatted_notes)}...", end=' ')
            
            if self.upload_note(note):
                results['success'] += 1
                print("✓")
            else:
                results['failed'] += 1
                print("✗")
            
            # Rate limiting delay
            if i < len(formatted_notes):
                time.sleep(delay)
        
        print(f"\nUpload complete: {results['success']} successful, {results['failed']} failed")
        return results
    
    def set_database_id(self, database_id: str):
        """
        Set the database ID for an existing database.
        
        Args:
            database_id: ID of existing Notion database
        """
        self.database_id = database_id
