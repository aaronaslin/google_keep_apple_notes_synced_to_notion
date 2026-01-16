#!/usr/bin/env python3
"""
Google Keep & Apple Notes to Notion Sync Tool

This script parses notes from Google Keep and Apple Notes,
converts them to Notion format, and uploads them to a new Notion database.
"""

import json
import os
import sys
import argparse
from typing import Dict, List

from google_keep_parser import parse_google_keep
from apple_notes_parser import parse_apple_notes
from notion_formatter import NotionFormatter
from notion_uploader import NotionUploader


def load_config(config_path: str = 'config.json') -> Dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        print("Please create a config.json file based on config.example.json")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def parse_notes(config: Dict, sources: List[str]) -> List[Dict]:
    """
    Parse notes from specified sources.
    
    Args:
        config: Configuration dictionary
        sources: List of sources to parse ('google_keep', 'apple_notes')
        
    Returns:
        Combined list of parsed notes
    """
    all_notes = []
    
    if 'google_keep' in sources:
        print("\n=== Parsing Google Keep Notes ===")
        google_keep_config = config.get('google_keep', {})
        
        username = google_keep_config.get('username')
        password = google_keep_config.get('password')
        
        if not username or not password:
            print("Google Keep credentials not configured. Skipping...")
        else:
            google_notes = parse_google_keep(username, password)
            all_notes.extend(google_notes)
            print(f"Added {len(google_notes)} notes from Google Keep")
    
    if 'apple_notes' in sources:
        print("\n=== Parsing Apple Notes ===")
        apple_notes_config = config.get('apple_notes', {})
        
        database_path = apple_notes_config.get('database_path')
        
        if not database_path:
            print("Apple Notes database path not configured. Skipping...")
        else:
            apple_notes = parse_apple_notes(database_path)
            all_notes.extend(apple_notes)
            print(f"Added {len(apple_notes)} notes from Apple Notes")
    
    return all_notes


def upload_to_notion(config: Dict, notes: List[Dict], database_title: str):
    """
    Format and upload notes to Notion.
    
    Args:
        config: Configuration dictionary
        notes: List of parsed notes
        database_title: Title for the new Notion database
    """
    if not notes:
        print("\nNo notes to upload!")
        return
    
    print(f"\n=== Formatting {len(notes)} Notes for Notion ===")
    formatter = NotionFormatter()
    formatted_notes = formatter.format_notes(notes)
    print(f"Formatted {len(formatted_notes)} notes")
    
    print("\n=== Uploading to Notion ===")
    notion_config = config.get('notion', {})
    
    api_token = notion_config.get('api_token')
    parent_page_id = notion_config.get('parent_page_id')
    
    if not api_token or not parent_page_id:
        print("Notion configuration incomplete. Please check config.json")
        return
    
    uploader = NotionUploader(api_token, parent_page_id)
    
    # Create database
    print(f"Creating Notion database: {database_title}")
    database_id = uploader.create_database(database_title)
    
    if not database_id:
        print("Failed to create database. Aborting upload.")
        return
    
    # Upload notes
    print(f"\nUploading {len(formatted_notes)} notes to Notion...")
    results = uploader.upload_notes(formatted_notes)
    
    print("\n=== Upload Summary ===")
    print(f"Total notes: {len(formatted_notes)}")
    print(f"Successful: {results['success']}")
    print(f"Failed: {results['failed']}")
    print(f"\nDatabase URL: https://notion.so/{database_id.replace('-', '')}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Sync Google Keep and Apple Notes to Notion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync both Google Keep and Apple Notes
  python main.py
  
  # Sync only Google Keep
  python main.py --sources google_keep
  
  # Sync only Apple Notes
  python main.py --sources apple_notes
  
  # Use custom config file
  python main.py --config my_config.json
  
  # Custom database title
  python main.py --title "My Notes Archive"
        """
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['google_keep', 'apple_notes'],
        default=['google_keep', 'apple_notes'],
        help='Sources to sync (default: both)'
    )
    
    parser.add_argument(
        '--title',
        default='Notes Archive',
        help='Title for the Notion database (default: Notes Archive)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Google Keep & Apple Notes to Notion Sync Tool")
    print("=" * 60)
    
    # Load configuration
    config = load_config(args.config)
    
    # Parse notes from specified sources
    notes = parse_notes(config, args.sources)
    
    if not notes:
        print("\nNo notes found to sync!")
        return
    
    # Upload to Notion
    upload_to_notion(config, notes, args.title)
    
    print("\n" + "=" * 60)
    print("Sync Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
