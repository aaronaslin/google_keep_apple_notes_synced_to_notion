import os
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables from .env in the project root
load_dotenv('/Users/aaslin/Documents/GitHub/gkeep_notion_integration/.env')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

print("🔍 Validating Notion connection...\n")

# Check if variables are loaded
if not NOTION_API_TOKEN:
    print("❌ NOTION_API_TOKEN not found in .env")
    exit(1)
    
if not NOTION_DATABASE_ID:
    print("❌ NOTION_DATABASE_ID not found in .env")
    exit(1)

print(f"✓ Token loaded: {NOTION_API_TOKEN[:20]}...")
print(f"✓ Database ID: {NOTION_DATABASE_ID}\n")

# Try to connect
try:
    notion = Client(auth=NOTION_API_TOKEN)
    print("✓ Connected to Notion API\n")
    
    # Try to query the database
    response = notion.databases.retrieve(NOTION_DATABASE_ID)
    
    print(f"✓ Database is accessible\n")
    
    # List database properties
    if 'properties' in response:
        print("📋 Database properties:")
        for prop_name, prop_info in response['properties'].items():
            print(f"   - {prop_name} ({prop_info['type']})")
    
    print("\n✅ All validations passed! Ready to sync.")
    
except Exception as e:
    print(f"❌ Validation failed: {str(e)}")
    print("\nCommon issues:")
    print("  1. Integration not connected to database in Notion")
    print("  2. Token is invalid or expired")
    print("  3. Database ID is incorrect")
    exit(1)
