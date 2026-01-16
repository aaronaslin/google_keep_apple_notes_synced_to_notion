import os
from dotenv import load_dotenv
from notion_client import Client
from parser import parse_keep_json, TAKEOUT_DIR
from datetime import datetime

# Load environment variables
load_dotenv('/Users/aaslin/Documents/GitHub/gkeep_notion_integration/.env')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

notion = Client(auth=NOTION_API_TOKEN)

def get_all_pages():
    """Retrieve all pages from the database"""
    all_pages = []
    has_more = True
    start_cursor = None
    
    print("📥 Fetching all pages from Notion...")
    
    # Normalize database ID
    db_id_normalized = NOTION_DATABASE_ID.replace('-', '')
    
    while has_more:
        response = notion.search(
            filter={
                "property": "object",
                "value": "page"
            },
            start_cursor=start_cursor,
            page_size=100
        )
        
        # Filter to only pages from our database
        for page in response['results']:
            parent_db_id = page.get('parent', {}).get('database_id', '')
            if parent_db_id.replace('-', '') == db_id_normalized:
                all_pages.append(page)
        
        has_more = response['has_more']
        start_cursor = response.get('next_cursor')
    
    print(f"Found {len(all_pages)} pages\n")
    return all_pages

def extract_page_title(page):
    """Extract title from a page"""
    title_prop = page['properties'].get('Title', {})
    if title_prop.get('title'):
        return title_prop['title'][0]['plain_text'] if title_prop['title'] else ""
    return ""

def create_json_title_map():
    """Create a map of titles to their timestamps from JSON files"""
    title_map = {}
    
    print("📋 Parsing JSON files...")
    for filename in os.listdir(TAKEOUT_DIR):
        if filename.endswith('.json'):
            try:
                note_data = parse_keep_json(os.path.join(TAKEOUT_DIR, filename))
                title = note_data['title']
                created_date = note_data.get('created_date')
                
                if created_date:
                    title_map[title] = created_date
            except Exception as e:
                print(f"  ✗ Error parsing {filename}: {str(e)}")
    
    print(f"Found {len(title_map)} notes with timestamps\n")
    return title_map

def update_timestamps():
    """Update all existing Notion pages with timestamps from JSON files"""
    
    # Get all pages from Notion
    pages = get_all_pages()
    
    # Create map of titles to timestamps
    title_map = create_json_title_map()
    
    print("🔄 Updating timestamps...\n")
    
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for page in pages:
        page_id = page['id']
        title = extract_page_title(page)
        
        # Find corresponding timestamp
        if title in title_map:
            created_date = title_map[title]
            
            try:
                notion.pages.update(
                    page_id=page_id,
                    properties={
                        "Created Date": {
                            "date": {
                                "start": created_date
                            }
                        }
                    }
                )
                updated_count += 1
                print(f"✓ Updated: {title}")
                
            except Exception as e:
                failed_count += 1
                print(f"✗ Failed to update {title}: {str(e)}")
        else:
            skipped_count += 1
            print(f"⊘ No timestamp found: {title}")
    
    print(f"\n--- Update Complete ---")
    print(f"Updated: {updated_count}")
    print(f"Skipped (no timestamp): {skipped_count}")
    print(f"Failed: {failed_count}")

if __name__ == "__main__":
    print("🕒 Starting timestamp update...\n")
    update_timestamps()
