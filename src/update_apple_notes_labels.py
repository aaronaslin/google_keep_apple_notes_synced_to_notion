import os
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
load_dotenv('/Users/aaslin/Documents/GitHub/gkeep_notion_integration/.env')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

if not NOTION_API_TOKEN or not NOTION_DATABASE_ID:
    raise ValueError("Missing NOTION_API_TOKEN or NOTION_DATABASE_ID in .env file")

notion = Client(auth=NOTION_API_TOKEN)

def find_apple_notes():
    """Find all notes with 'Apple Notes' label"""
    db_id_normalized = NOTION_DATABASE_ID.replace('-', '')
    
    results = notion.search(
        filter={
            "property": "object",
            "value": "page"
        }
    )
    
    apple_notes = []
    for result in results.get('results', []):
        parent_db_id = result.get('parent', {}).get('database_id', '').replace('-', '')
        if parent_db_id == db_id_normalized:
            labels_prop = result.get('properties', {}).get('Labels', {})
            if labels_prop.get('multi_select'):
                label_names = [label['name'] for label in labels_prop['multi_select']]
                if 'Apple Notes' in label_names:
                    apple_notes.append({
                        'id': result['id'],
                        'title': result.get('properties', {}).get('Title', {}).get('title', [{}])[0].get('plain_text', 'Untitled'),
                        'current_labels': label_names
                    })
    
    return apple_notes

def update_label(page_id, old_labels):
    """Update labels: remove 'Apple Notes' and add 'source'"""
    # Remove 'Apple Notes' and add 'source'
    new_labels = [label for label in old_labels if label != 'Apple Notes']
    new_labels.append('source')
    
    # Update the page
    notion.pages.update(
        page_id=page_id,
        properties={
            "Labels": {
                "multi_select": [{"name": label} for label in new_labels]
            }
        }
    )

if __name__ == "__main__":
    print("Searching for Apple Notes...")
    apple_notes = find_apple_notes()
    
    print(f"\nFound {len(apple_notes)} notes with 'Apple Notes' label\n")
    
    if not apple_notes:
        print("No notes to update!")
    else:
        updated = 0
        failed = 0
        
        for note in apple_notes:
            try:
                update_label(note['id'], note['current_labels'])
                print(f"✓ Updated: {note['title']}")
                updated += 1
            except Exception as e:
                print(f"✗ Failed: {note['title']} - {str(e)}")
                failed += 1
        
        print(f"\n--- Update Complete ---")
        print(f"Successfully updated: {updated}")
        print(f"Failed: {failed}")
