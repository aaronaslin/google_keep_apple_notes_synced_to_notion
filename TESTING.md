# Testing Guide

This guide explains how to test the Google Keep & Apple Notes to Notion sync tool.

## Manual Testing

Since this tool interacts with external APIs and databases, manual testing is the primary approach.

### Prerequisites for Testing

1. Valid Google Keep credentials
2. Access to Apple Notes database (macOS only)
3. Notion API integration token and parent page

### Test Scenarios

#### 1. Test Configuration Loading

```bash
# Should fail gracefully with helpful message
python main.py

# Copy example config
cp config.example.json config.json

# Edit config.json with test credentials (don't commit this!)
# Then try again - should proceed to parsing
```

#### 2. Test Google Keep Only

```bash
# Configure only Google Keep credentials in config.json
python main.py --sources google_keep --title "Test Google Keep Sync"
```

**Expected Results:**
- Authenticates with Google Keep
- Retrieves all non-trashed notes
- Creates Notion database
- Uploads notes with proper formatting
- Shows summary statistics

#### 3. Test Apple Notes Only

```bash
# Configure only Apple Notes database path in config.json
python main.py --sources apple_notes --title "Test Apple Notes Sync"
```

**Expected Results:**
- Connects to Apple Notes SQLite database
- Retrieves notes
- Creates Notion database
- Uploads notes
- Shows summary statistics

#### 4. Test Both Sources

```bash
# Configure both sources in config.json
python main.py --title "Test Combined Sync"
```

**Expected Results:**
- Processes both sources sequentially
- Combines notes from both sources
- Creates single Notion database
- Notes are tagged by source
- Shows combined statistics

#### 5. Test Error Handling

Test various error conditions:

**Invalid Google Keep credentials:**
```json
{
  "google_keep": {
    "username": "invalid@example.com",
    "password": "wrong_password"
  }
}
```
Expected: Authentication error message, continues with other sources

**Invalid Apple Notes path:**
```json
{
  "apple_notes": {
    "database_path": "/path/that/does/not/exist"
  }
}
```
Expected: Database not found message, continues with other sources

**Invalid Notion credentials:**
```json
{
  "notion": {
    "api_token": "invalid_token",
    "parent_page_id": "invalid_id"
  }
}
```
Expected: API error message when creating database

#### 6. Test CLI Options

```bash
# Test help
python main.py --help

# Test custom config
cp config.json test_config.json
python main.py --config test_config.json

# Test custom title
python main.py --title "My Custom Title"

# Test source selection
python main.py --sources google_keep
python main.py --sources apple_notes
python main.py --sources google_keep apple_notes
```

### Verification Checklist

After running tests, verify in Notion:

- [ ] Database created with correct title
- [ ] All expected notes present
- [ ] Note titles correct
- [ ] Note content preserved
- [ ] Checklist items formatted correctly (Google Keep)
- [ ] Metadata fields populated (dates, colors, tags)
- [ ] Source field shows correct origin
- [ ] No duplicate notes (unless intentional)

### Performance Testing

For large note collections:

1. Monitor upload time
2. Check for rate limiting issues
3. Verify all notes uploaded successfully
4. Check memory usage doesn't grow excessively

### Clean Up After Testing

1. Delete test databases from Notion
2. Remove test config files
3. Do NOT commit config.json with real credentials

## Automated Testing (Future Enhancement)

For production use, consider adding:

- Unit tests for parsers with mock data
- Integration tests with test Notion workspace
- Fixture files for sample notes
- CI/CD pipeline with test credentials

## Common Issues During Testing

### "Module not found" errors
**Solution:** `pip install -r requirements.txt`

### Google Keep authentication fails repeatedly
**Solution:** Use App Password, not regular password. Enable 2FA.

### Apple Notes returns empty
**Solution:** Verify database path is correct for your macOS username

### Notion rate limiting
**Solution:** Increase delay parameter or reduce number of notes

### Character encoding issues
**Solution:** The parsers use `errors='ignore'` to handle encoding gracefully

## Test Data Recommendations

For comprehensive testing:

- Create test notes with various formats
- Include notes with emojis and special characters
- Test with very long notes (>2000 chars)
- Test with empty notes
- Test with notes containing only checklists
- Test with heavily tagged/labeled notes
- Test with notes of different colors

## Reporting Issues

If you encounter bugs during testing:

1. Check the error message
2. Verify configuration is correct
3. Test with minimal data first
4. Check GitHub issues for similar problems
5. Report with error logs and steps to reproduce
