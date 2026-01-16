"""
Notion Formatter Module

This module handles converting parsed notes into Notion block format.
"""

from typing import List, Dict, Any


# Notion API has a character limit per block
NOTION_BLOCK_CHAR_LIMIT = 2000


class NotionFormatter:
    """Formatter to convert notes to Notion block format."""
    
    @staticmethod
    def format_note(note: Dict) -> Dict[str, Any]:
        """
        Format a single note for Notion.
        
        Args:
            note: Note dictionary from parser
            
        Returns:
            Dictionary with Notion-formatted properties and children blocks
        """
        # Create properties for the database
        properties = {
            'Title': {
                'title': [
                    {
                        'text': {
                            'content': note.get('title', 'Untitled')
                        }
                    }
                ]
            },
            'Source': {
                'select': {
                    'name': note.get('source', 'Unknown')
                }
            },
        }
        
        # Add created time if available
        if note.get('created_time'):
            properties['Created'] = {
                'date': {
                    'start': note['created_time']
                }
            }
        
        # Add updated time if available
        if note.get('updated_time'):
            properties['Updated'] = {
                'date': {
                    'start': note['updated_time']
                }
            }
        
        # Add archived status
        if note.get('archived') is not None:
            properties['Archived'] = {
                'checkbox': note['archived']
            }
        
        # Add pinned status
        if note.get('pinned') is not None:
            properties['Pinned'] = {
                'checkbox': note['pinned']
            }
        
        # Add color if available
        if note.get('color'):
            properties['Color'] = {
                'select': {
                    'name': note['color']
                }
            }
        
        # Add labels/tags if available
        if note.get('labels'):
            properties['Tags'] = {
                'multi_select': [
                    {'name': label} for label in note['labels']
                ]
            }
        
        # Create children blocks for content
        children = []
        
        # Add main content as paragraph blocks
        content = note.get('content', '')
        if content:
            # Split content into paragraphs
            paragraphs = content.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    children.append({
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [
                                {
                                    'type': 'text',
                                    'text': {
                                        'content': paragraph[:NOTION_BLOCK_CHAR_LIMIT]
                                    }
                                }
                            ]
                        }
                    })
        
        # Add checklist items if available
        if note.get('checklist'):
            for item in note['checklist']:
                children.append({
                    'object': 'block',
                    'type': 'to_do',
                    'to_do': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': item['text'][:NOTION_BLOCK_CHAR_LIMIT]
                                }
                            }
                        ],
                        'checked': item.get('checked', False)
                    }
                })
        
        # Add URL if available
        if note.get('url'):
            children.append({
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {
                                'content': f"URL: {note['url']}"
                            }
                        }
                    ]
                }
            })
        
        return {
            'properties': properties,
            'children': children
        }
    
    @staticmethod
    def format_notes(notes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format multiple notes for Notion.
        
        Args:
            notes: List of note dictionaries from parsers
            
        Returns:
            List of Notion-formatted note dictionaries
        """
        return [NotionFormatter.format_note(note) for note in notes]
