"""
Apple Notes Parser Module

This module handles parsing notes from Apple Notes by accessing the SQLite database.
"""

import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import gzip


class AppleNotesParser:
    """Parser for Apple Notes."""
    
    def __init__(self, database_path: str):
        """
        Initialize the Apple Notes parser.
        
        Args:
            database_path: Path to the Apple Notes SQLite database
        """
        self.database_path = database_path
        
    def check_database_exists(self) -> bool:
        """
        Check if the Apple Notes database exists.
        
        Returns:
            True if database exists, False otherwise
        """
        if not os.path.exists(self.database_path):
            print(f"Apple Notes database not found at: {self.database_path}")
            return False
        return True
    
    def get_notes(self) -> List[Dict]:
        """
        Retrieve all notes from Apple Notes database.
        
        Returns:
            List of note dictionaries with standardized format
        """
        if not self.check_database_exists():
            return []
        
        notes = []
        
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Query to get notes
            # The Apple Notes database structure includes ZICCLOUDSYNCINGOBJECT for notes
            query = """
                SELECT 
                    ZICCLOUDSYNCINGOBJECT.Z_PK,
                    ZICCLOUDSYNCINGOBJECT.ZTITLE1 as title,
                    ZICCLOUDSYNCINGOBJECT.ZSNIPPET as snippet,
                    ZICCLOUDSYNCINGOBJECT.ZCREATIONDATE1 as created,
                    ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE1 as modified,
                    ZICNOTEDATA.ZDATA as data
                FROM ZICCLOUDSYNCINGOBJECT
                LEFT JOIN ZICNOTEDATA ON ZICCLOUDSYNCINGOBJECT.ZNOTEDATA = ZICNOTEDATA.Z_PK
                WHERE ZICCLOUDSYNCINGOBJECT.ZTITLE1 IS NOT NULL
                    AND ZICCLOUDSYNCINGOBJECT.ZMARKEDFORDELETION = 0
                ORDER BY ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE1 DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                note_id, title, snippet, created, modified, data = row
                
                # Convert Apple timestamp (seconds since 2001-01-01) to ISO format
                created_time = None
                modified_time = None
                
                if created:
                    # Apple Core Data timestamp: seconds since Jan 1, 2001
                    timestamp = datetime(2001, 1, 1) + timedelta(seconds=created)
                    created_time = timestamp.isoformat()
                
                if modified:
                    timestamp = datetime(2001, 1, 1) + timedelta(seconds=modified)
                    modified_time = timestamp.isoformat()
                
                # Extract content from the data blob
                content = snippet or ''
                
                # Try to decompress and parse the data blob if available
                if data:
                    try:
                        # The data might be compressed with gzip
                        decompressed = gzip.decompress(data)
                        # Extract text content (simplified approach)
                        content = decompressed.decode('utf-8', errors='ignore')
                    except (gzip.BadGzipFile, UnicodeDecodeError, OSError):
                        # If decompression fails, use snippet
                        content = snippet or ''
                
                note_data = {
                    'title': title or 'Untitled',
                    'content': content,
                    'source': 'Apple Notes',
                    'created_time': created_time,
                    'updated_time': modified_time,
                    'archived': False,
                    'pinned': False,
                    'color': None,
                    'labels': [],
                }
                
                notes.append(note_data)
            
            conn.close()
            print(f"Retrieved {len(notes)} notes from Apple Notes")
            return notes
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        except Exception as e:
            print(f"Error retrieving Apple Notes: {e}")
            return []


def parse_apple_notes(database_path: str) -> List[Dict]:
    """
    Parse notes from Apple Notes.
    
    Args:
        database_path: Path to the Apple Notes SQLite database
        
    Returns:
        List of parsed notes in standardized format
    """
    parser = AppleNotesParser(database_path)
    return parser.get_notes()
