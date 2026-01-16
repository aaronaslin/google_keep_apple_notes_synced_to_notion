import os
from dotenv import load_dotenv
from notion_client import Client
from collections import defaultdict

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
    
    # Normalize database ID (remove hyphens for comparison)
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
    
    print(f"Found {len(all_pages)} total pages\n")
    return all_pages

def extract_page_info(page):
    """Extract title and content from a page"""
    page_id = page['id']
    
    # Extract title
    title_prop = page['properties'].get('Title', {})
    if title_prop.get('title'):
        title = title_prop['title'][0]['plain_text'] if title_prop['title'] else ""
    else:
        title = ""
    
    # Extract content
    content_prop = page['properties'].get('Content', {})
    if content_prop.get('rich_text'):
        content = content_prop['rich_text'][0]['plain_text'] if content_prop['rich_text'] else ""
    else:
        content = ""
    
    return page_id, title, content

def find_duplicates(pages):
    """Find duplicate pages based on title + content"""
    seen = defaultdict(list)
    
    for page in pages:
        page_id, title, content = extract_page_info(page)
        key = (title, content)  # Tuple of title and content
        seen[key].append(page_id)
    
    # Find entries with duplicates
    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    return duplicates

def cleanup_duplicates():
    """Remove duplicate pages, keeping only the first occurrence"""
    pages = get_all_pages()
    duplicates = find_duplicates(pages)
    
    if not duplicates:
        print("✓ No duplicates found!")
        return
    
    print(f"Found {len(duplicates)} sets of duplicates\n")
    
    total_deleted = 0
    
    for (title, content), page_ids in duplicates.items():
        print(f"Duplicate: '{title}' ({len(page_ids)} copies)")
        
        # Keep the first, delete the rest
        keep_id = page_ids[0]
        to_delete = page_ids[1:]
        
        print(f"  ✓ Keeping: {keep_id}")
        
        for page_id in to_delete:
            try:
                notion.pages.update(page_id=page_id, archived=True)
                print(f"  🗑️  Deleted: {page_id}")
                total_deleted += 1
            except Exception as e:
                print(f"  ✗ Failed to delete {page_id}: {str(e)}")
        
        print()
    
    print(f"\n--- Cleanup Complete ---")
    print(f"Total duplicates removed: {total_deleted}")

if __name__ == "__main__":
    print("🧹 Starting duplicate cleanup...\n")
    
    response = input("This will archive duplicate pages in Notion. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        cleanup_duplicates()
    else:
        print("Cleanup cancelled.")
