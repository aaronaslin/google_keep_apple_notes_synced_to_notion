# Notes to Notion Integration

A Python-based tool that parses notes from multiple sources (Google Keep, Apple Notes) and syncs them to a Notion database.

## Purpose

This project provides an automated workflow to migrate and manage your notes from various sources in Notion. It handles parsing, formatting, deduplication, and timestamping of notes from Google Keep and Apple Notes.

## Scope

**What's Included:**
- Parse Google Keep JSON files (title, content, labels, creation date)
- Parse Apple Notes markdown folders (title, content with source label)
- Sync notes to Notion database with duplicate detection
- Automatic timestamp extraction and population (Google Keep)
- Cleanup utility to remove duplicate entries
- Validation tools to test Notion API connection
- Multi-source note consolidation

**What's NOT Included:**
- HTML files (kept for reference only)
- Images (stored locally but not uploaded)
- Real-time synchronization

## Setup

### Prerequisites
- Python 3.9+
- Virtual environment (already configured)
- Notion account with API access

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Notion integration:**
   - Go to [Notion Developers](https://developers.notion.com/docs/getting-started)
   - Create a new integration and copy your token
   - Create a Notion database with columns: `Title` (text), `Content` (text), `Labels` (multi-select), `Created Date` (date)
   - Share the database with your integration

3. **Configure credentials:**
   - Copy `.env.example` to `.env`
   - Add your Notion API token and database ID:
     ```
     NOTION_API_TOKEN=your_token_here
     NOTION_DATABASE_ID=your_database_id_here
     ```

4. **Prepare data:**
   - Export your Google Keep notes via [Google Takeout](https://takeout.google.com) and place JSON files in `data/google_notes/`
   - Export your Apple Notes as markdown folders and place them in `data/apple_notes/`

## Key Actions

### Parse Google Keep Notes
Extracts data from JSON files. Automatically called by sync scripts.
```bash
python src/parser.py
```

### Parse Apple Notes
Extracts data from markdown folders. Automatically called by sync scripts.
```bash
python src/apple_notes_parser.py
```

### Sync Google Keep to Notion
Uploads Google Keep notes to your Notion database with duplicate detection.
```bash
python src/notion_sync.py
```

### Sync Apple Notes to Notion
Uploads Apple Notes to your Notion database with duplicate detection.
```bash
python src/apple_notes_sync.py
```

**Output:**
- ✓ Synced - New note created
- ⊘ Skipped - Note already exists
- ✗ Failed - Error creating note

### Cleanup Duplicates
Removes duplicate notes from Notion (keeps first, archives rest).
```bash
python src/cleanup_duplicates.py
```

### Validate Connection
Tests Notion API connection and database access.
```bash
python src/validate_notion.py
```

### Update Timestamps
Adds creation dates to existing notes from JSON files.
```bash
python src/update_timestamps.py
```

## File Structure

```
gkeep_notion_integration/
├── data/
│   ├── google_notes/          # Google Keep JSON/HTML exports (342 notes)
│   └── apple_notes/           # Apple Notes markdown folders
├── src/
│   ├── parser.py             # Parse Google Keep JSON files
│   ├── apple_notes_parser.py # Parse Apple Notes markdown
│   ├── notion_sync.py        # Sync Google Keep to Notion
│   ├── apple_notes_sync.py   # Sync Apple Notes to Notion
│   ├── cleanup_duplicates.py # Remove duplicates
│   ├── update_timestamps.py  # Add creation dates
│   ├── validate_notion.py    # Test connection
│   └── test_create.py        # Test page creation
├── .env                       # Credentials (DO NOT COMMIT)
├── .env.example              # Template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Data Fields Extracted

### Google Keep
| Field | Source | Notion Field | Type |
|-------|--------|--------------|------|
| Title | Keep title | Title | Text |
| Content | Keep text/checklist | Content | Text |
| Labels | Keep labels | Labels | Multi-select |
| Created Date | createdTimestampUsec | Created Date | Date |

### Apple Notes
| Field | Source | Notion Field | Type |
|-------|--------|--------------|------|
| Title | Folder name | Title | Text |
| Content | Markdown file content | Content | Text |
| Labels | "Apple Notes" (source label) | Labels | Multi-select |
| Created Date | Not available | Created Date | Date |

## Notes

- **Duplicate Detection:** Based on matching title + content across all sources
- **Character Limits:** Titles limited to 100 chars, content to 2000 chars
- **Timestamps:** Google Keep timestamps converted from microseconds to ISO format
- **Checklists:** Formatted as `[x] item` or `[ ] item` (Google Keep)
- **Source Labels:** Apple Notes automatically tagged with "Apple Notes" label for easy filtering
- **Multi-source:** Consolidates notes from Google Keep and Apple Notes into single Notion database

## Security

⚠️ **Important:**
- `.env` file contains sensitive credentials
- Never commit `.env` to version control
- `.gitignore` is configured to exclude it

## Troubleshooting

**"API token is invalid"**
- Verify token is correct and not expired
- Confirm database is shared with integration in Notion

**"Title is expected to be rich_text"**
- Ensure your Notion database has correct column types
- Title column must be type "Title" (not text)

**No notes found**
- For Google Keep: Verify JSON files are in `data/google_notes/` folder
- For Apple Notes: Verify markdown folders are in `data/apple_notes/` folder
- Check file format from respective exports

## Future Enhancements

- [ ] Additional note sources (Evernote, OneNote, etc.)
- [ ] Image upload support
- [ ] Scheduled/automated sync
- [ ] HTML content parsing
- [ ] Archive vs. delete option
- [ ] Bulk note update capability
- [ ] Timestamp extraction for Apple Notes
- [ ] Attachment handling for both sources

## License

Personal use project

## Support

For issues, check:
1. `.env` credentials
2. Notion database schema
3. JSON file format from Takeout
4. Run `validate_notion.py` to test connection
