import json
import os
from datetime import datetime

# Path to your unzipped 'Keep' folder from Google Takeout
TAKEOUT_DIR = './data'

def parse_keep_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract existing logic (title, content)
    title = data.get('title') or "Untitled"
    content = data.get('textContent', '')

    # NEW: Extract Labels
    # Google Keep stores labels as a list of objects: [{'name': 'Work'}, {'name': 'Urgent'}]
    labels_raw = data.get('labels', [])
    labels = [label['name'] for label in labels_raw]

    # Handle Checklists
    if 'listContent' in data:
        items = [f"[{'x' if i.get('checked', False) else ' '}] {i.get('text', '')}" for i in data['listContent']]
        content = "\n".join(items)

    # Extract timestamp (Google Keep stores in microseconds)
    created_micros = data.get('createdTimestampUsec', 0)
    created_date = datetime.fromtimestamp(created_micros / 1000000).isoformat() if created_micros else None

    return {
        "title": title,
        "content": content,
        "labels": labels,
        "created_date": created_date
    }

# Loop through the directory
all_notes = []
for filename in os.listdir(TAKEOUT_DIR):
    if filename.endswith('.json'):
        note_data = parse_keep_json(os.path.join(TAKEOUT_DIR, filename))
        all_notes.append(note_data)

print(f"Successfully parsed {len(all_notes)} notes.")
