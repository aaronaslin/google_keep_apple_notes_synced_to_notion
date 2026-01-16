import os
from dotenv import load_dotenv
from notion_client import Client
import json

load_dotenv('/Users/aaslin/Documents/GitHub/gkeep_notion_integration/.env')

notion = Client(auth=os.getenv('NOTION_API_TOKEN'))
database_id = os.getenv('NOTION_DATABASE_ID')

# Try to create a simple test page with all properties
try:
    print("Attempting to create test page with all properties...")
    page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": "Test Note with Content"
                        }
                    }
                ]
            },
            "Content": {
                "rich_text": [
                    {
                        "text": {
                            "content": "This is test content"
                        }
                    }
                ]
            },
            "Labels": {
                "multi_select": [
                    {"name": "test-label"}
                ]
            }
        }
    )
    print(f"✓ Success! Created page with ID: {page['id']}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nLet me query an existing page to see the correct structure...")
    
    # Query the database to see existing pages
    try:
        results = notion.databases.query(database_id=database_id, page_size=1)
        if results['results']:
            print("\nFound existing page. Properties structure:")
            print(json.dumps(results['results'][0]['properties'], indent=2))
        else:
            print("\nNo existing pages found in database.")
    except Exception as e2:
        print(f"Could not query database: {str(e2)}")
