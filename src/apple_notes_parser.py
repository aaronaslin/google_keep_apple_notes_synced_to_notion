import os
from pathlib import Path

# Path to Apple Notes folder
APPLE_NOTES_DIR = './data/apple_notes'

def parse_apple_note(note_folder_path):
    """
    Parse an Apple Notes folder and extract title and content.
    
    Args:
        note_folder_path: Path to the note folder
        
    Returns:
        Dictionary with title, content, and labels (empty for Apple Notes)
    """
    
    # Get folder name as title
    folder_name = os.path.basename(note_folder_path)
    title = folder_name or "Untitled"
    
    # Find the markdown file (could be Note.md or {FolderName}.md)
    md_file = None
    for file in os.listdir(note_folder_path):
        if file.endswith('.md'):
            md_file = os.path.join(note_folder_path, file)
            break
    
    # Read content
    content = ""
    if md_file:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {md_file}: {str(e)}")
    
    # Clean up content: remove extra whitespace, preserve markdown
    content = content.strip()
    
    return {
        "title": title,
        "content": content,
        "labels": ["Apple Notes"],  # Tag all Apple Notes with this label
        "created_date": None  # Apple Notes export doesn't include creation date
    }

# Scan and parse all Apple Notes
def get_all_apple_notes():
    """Scan Apple Notes folder and return all parsed notes."""
    all_notes = []
    
    if not os.path.exists(APPLE_NOTES_DIR):
        print(f"Apple Notes directory not found: {APPLE_NOTES_DIR}")
        return all_notes
    
    # Iterate through each note folder
    for item in os.listdir(APPLE_NOTES_DIR):
        item_path = os.path.join(APPLE_NOTES_DIR, item)
        
        # Skip non-directories and system files
        if not os.path.isdir(item_path) or item.startswith('.'):
            continue
        
        try:
            note_data = parse_apple_note(item_path)
            all_notes.append(note_data)
        except Exception as e:
            print(f"Error parsing {item}: {str(e)}")
    
    return all_notes

if __name__ == "__main__":
    notes = get_all_apple_notes()
    print(f"Successfully parsed {len(notes)} Apple Notes.")
    for note in notes:
        print(f"  - {note['title']}")
