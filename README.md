# Google Keep & Apple Notes to Notion Sync Tool

A Python tool to parse notes from Google Keep and Apple Notes, convert them to Notion format, and upload them to a new Notion database.

## Features

- ✅ Parse notes from Google Keep with full metadata
- ✅ Parse notes from Apple Notes SQLite database
- ✅ Support for checklist items from Google Keep
- ✅ Preserve note metadata (creation date, update date, labels, colors, etc.)
- ✅ Automatic Notion database creation with proper schema
- ✅ Batch upload with rate limiting to avoid API limits
- ✅ Flexible command-line interface
- ✅ Support for both sources simultaneously or individually

## Prerequisites

- Python 3.7 or higher
- A Notion account with API access
- Google account (for Google Keep sync)
- macOS with Apple Notes (for Apple Notes sync)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/aaronaslin/google_keep_-_apple_notes_synced_to_notion.git
cd google_keep_-_apple_notes_synced_to_notion
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a configuration file:
```bash
cp config.example.json config.json
```

## Configuration

Edit `config.json` with your credentials:

### Notion Configuration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration and copy the API token
3. Create a page in Notion where you want the database to be created
4. Share that page with your integration
5. Copy the page ID from the URL (the part after the workspace name and before the `?`)

```json
{
  "notion": {
    "api_token": "secret_xxxxxxxxxxxxx",
    "parent_page_id": "xxxxxxxxxxxxx"
  }
}
```

### Google Keep Configuration

1. Use your Gmail address
2. For password, create an [App Password](https://myaccount.google.com/apppasswords) (not your regular password)
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail" on "Other"

```json
{
  "google_keep": {
    "username": "your_email@gmail.com",
    "password": "your_app_password"
  }
}
```

### Apple Notes Configuration

The default path works for most macOS users. If you have a different setup, adjust the path:

```json
{
  "apple_notes": {
    "database_path": "/Users/YOUR_USERNAME/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite"
  }
}
```

**Note:** Replace `YOUR_USERNAME` with your actual macOS username.

## Usage

### Sync Both Sources

```bash
python main.py
```

### Sync Only Google Keep

```bash
python main.py --sources google_keep
```

### Sync Only Apple Notes

```bash
python main.py --sources apple_notes
```

### Custom Configuration File

```bash
python main.py --config my_config.json
```

### Custom Database Title

```bash
python main.py --title "My Notes Archive 2026"
```

### Combined Options

```bash
python main.py --sources google_keep --title "Google Keep Archive" --config custom_config.json
```

## Command-Line Options

```
usage: main.py [-h] [--config CONFIG] [--sources {google_keep,apple_notes} [{google_keep,apple_notes} ...]] [--title TITLE]

Sync Google Keep and Apple Notes to Notion

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Path to configuration file (default: config.json)
  --sources {google_keep,apple_notes} [{google_keep,apple_notes} ...]
                        Sources to sync (default: both)
  --title TITLE         Title for the Notion database (default: Notes Archive)
```

## What Gets Synced

### Google Keep Notes

- ✅ Title
- ✅ Content/text
- ✅ Checklist items (with checked status)
- ✅ Creation and modification dates
- ✅ Labels/tags
- ✅ Color
- ✅ Pinned status
- ✅ Archived status
- ✅ URLs (if present)

### Apple Notes

- ✅ Title
- ✅ Content/snippet
- ✅ Creation and modification dates
- ⚠️ Limited formatting (Apple Notes uses a complex format)

## Notion Database Schema

The tool creates a database with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| Title | Title | Note title |
| Source | Select | Google Keep or Apple Notes |
| Created | Date | Creation timestamp |
| Updated | Date | Last update timestamp |
| Archived | Checkbox | Archived status |
| Pinned | Checkbox | Pinned status |
| Color | Select | Note color (Google Keep) |
| Tags | Multi-select | Labels/tags |

## Troubleshooting

### Google Keep Authentication Fails

- Make sure you're using an App Password, not your regular password
- Enable 2-factor authentication on your Google account
- Check that the username and password are correct in config.json

### Apple Notes Database Not Found

- Verify the database path is correct for your username
- Make sure Apple Notes has been opened at least once
- Check file permissions for the database

### Notion Upload Fails

- Verify your integration token is correct
- Make sure you've shared the parent page with your integration
- Check that the parent page ID is correct
- Ensure you have an active internet connection

### Rate Limiting

The tool includes a 0.3-second delay between uploads. If you still encounter rate limits:
- The Notion API has a rate limit of 3 requests per second
- Reduce upload frequency by modifying the `delay` parameter in the code

## Project Structure

```
.
├── main.py                  # Main script and CLI
├── google_keep_parser.py    # Google Keep parsing logic
├── apple_notes_parser.py    # Apple Notes parsing logic
├── notion_formatter.py      # Notion formatting logic
├── notion_uploader.py       # Notion API interaction
├── requirements.txt         # Python dependencies
├── config.example.json      # Example configuration
└── README.md               # This file
```

## Security Notes

- Never commit your `config.json` file with real credentials
- Use environment variables for sensitive data in production
- The `.gitignore` file excludes `config.json` by default
- Apple Notes database is read-only; no modifications are made

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Aaron - [GitHub](https://github.com/aaronaslin)

## Acknowledgments

- [gkeepapi](https://github.com/kiwiz/gkeepapi) - Unofficial Google Keep API
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) - Official Notion SDK for Python
