import os
from dotenv import load_dotenv
from notion_client import Client
from parser import parse_keep_json, TAKEOUT_DIR

# Load environment variables from .env file in the project root
load_dotenv('/Users/aaslin/Documents/GitHub/gkeep_notion_integration/.env')

# Initialize Notion client
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

if not NOTION_API_TOKEN or not NOTION_DATABASE_ID:
    raise ValueError("Missing NOTION_API_TOKEN or NOTION_DATABASE_ID in .env file")

notion = Client(auth=NOTION_API_TOKEN)

def check_if_note_exists(title):
    """Check if a note with this title already exists in Notion"""
    try:
        # Normalize database ID for comparison
        db_id_normalized = NOTION_DATABASE_ID.replace('-', '')
        
        results = notion.search(
            query=title,
            filter={
                "property": "object",
                "value": "page"
            }
        )
        # Check if any results have matching title in our database
        for result in results.get('results', []):
            parent_db_id = result.get('parent', {}).get('database_id', '').replace('-', '')
            if parent_db_id == db_id_normalized:
                title_prop = result.get('properties', {}).get('Title', {})
                if title_prop.get('title'):
                    result_title = title_prop['title'][0]['plain_text'] if title_prop['title'] else ""
                    if result_title == title:
                        return True
        return False
    except Exception:
        return False

def add_note_to_notion(title, content, labels, created_date=None):
    """Add a parsed note to Notion database"""
    
    # Convert labels to multi-select format
    label_objects = [{"name": label} for label in labels]
    
    # Build properties
    properties = {
        "Title": {
            "title": [
                {
                    "text": {
                        "content": title[:100]  # Notion title has character limit
                    }
                }
            ]
        },
        "Content": {
            "rich_text": [
                {
                    "text": {
                        "content": content[:2000]  # Limit to 2000 chars
                    }
                }
            ]
        },
        "Labels": {
            "multi_select": label_objects
        }
    }
    
    # Add created date if available
    if created_date:
        properties["Created Date"] = {
            "date": {
                "start": created_date
            }
        }
    
    # Create the page in Notion
    page = notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties=properties
    )
    
    return page['id']

# Main sync function
def sync_notes_to_notion():
    """Parse all Keep JSON files and sync to Notion"""
    
    synced_count = 0
    skipped_count = 0
    failed_count = 0
    
    for filename in os.listdir(TAKEOUT_DIR):
        if filename.endswith('.json'):
            try:
                note_data = parse_keep_json(os.path.join(TAKEOUT_DIR, filename))
                
                # Check if note already exists
                if check_if_note_exists(note_data['title']):
                    skipped_count += 1
                    print(f"⊘ Skipped (already exists): {note_data['title']}")
                    continue
                
                # Add to Notion
                page_id = add_note_to_notion(
                    note_data['title'],
                    note_data['content'],
                    note_data['labels'],
                    note_data.get('created_date')
                )
                
                synced_count += 1
                print(f"✓ Synced: {note_data['title']} (ID: {page_id})")
                
            except Exception as e:
                failed_count += 1
                print(f"✗ Failed to sync {filename}: {str(e)}")
    
    print(f"\n--- Sync Complete ---")
    print(f"Successfully synced: {synced_count}")
    print(f"Skipped (duplicates): {skipped_count}")
    print(f"Failed: {failed_count}")

if __name__ == "__main__":
    sync_notes_to_notion()
