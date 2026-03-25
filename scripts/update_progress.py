#!/usr/bin/env python3
"""
Update progress.json for a novel analysis project.
Usage: python update_progress.py <progress_file> --processed <n> --line <n> --doc <name> <status>
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def update_progress(progress_file: str, processed: int = None, line: int = None,
                    doc_status: dict = None, total_chapters: int = None,
                    current_volume: str = None, add_markers: list = None,
                    last_compact_at: int = None, chapters_since_compact: int = None):
    """Update an existing progress.json file."""

    progress_path = Path(progress_file)

    if not progress_path.exists():
        print(f"Error: progress.json not found at {progress_file}")
        return None

    with open(progress_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if processed is not None:
        data['processed_chapters'] = processed
    if line is not None:
        data['current_line'] = line
    if total_chapters is not None:
        data['total_chapters'] = total_chapters
    if current_volume is not None:
        data['current_volume'] = current_volume
    if add_markers:
        if 'chapter_markers' not in data:
            data['chapter_markers'] = []
        data['chapter_markers'].extend(add_markers)
    if last_compact_at is not None:
        data['last_compact_at'] = last_compact_at
    if chapters_since_compact is not None:
        data['chapters_since_compact'] = chapters_since_compact
    if doc_status:
        for doc_name, status in doc_status.items():
            if doc_name in data['docs_status']:
                data['docs_status'][doc_name] = status

    data['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Print progress summary
    total = data.get('total_chapters', '?')
    processed_count = data.get('processed_chapters', 0)
    current_vol = data.get('current_volume', '无')

    print(f"✓ Updated progress.json at: {progress_file}")
    print(f"  Progress: {processed_count}/{total} chapters")
    print(f"  Current line: {data['current_line']}")
    print(f"  Current volume: {current_vol}")
    print(f"  Last update: {data['last_update']}")

    return str(progress_file)

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_progress.py <progress_file> [options]")
        print("Options:")
        print("  --processed <n>   Set processed chapters count")
        print("  --line <n>        Set current line number")
        print("  --total <n>       Set total chapters")
        print("  --volume <name>   Set current volume")
        print("  --last-compact <n>  Set last_compact_at value")
        print("  --since-compact <n> Set chapters_since_compact value")
        print("  --doc <name> <status>  Update doc status (initialized/updating/completed)")
        sys.exit(1)

    progress_file = sys.argv[1]
    processed = None
    line = None
    total_chapters = None
    current_volume = None
    last_compact_at = None
    chapters_since_compact = None
    doc_status = {}

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--processed' and i + 1 < len(sys.argv):
            processed = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--line' and i + 1 < len(sys.argv):
            line = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--total' and i + 1 < len(sys.argv):
            total_chapters = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--volume' and i + 1 < len(sys.argv):
            current_volume = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--last-compact' and i + 1 < len(sys.argv):
            last_compact_at = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--since-compact' and i + 1 < len(sys.argv):
            chapters_since_compact = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--doc' and i + 2 < len(sys.argv):
            doc_status[sys.argv[i + 1]] = sys.argv[i + 2]
            i += 3
        else:
            i += 1

    update_progress(progress_file, processed, line, doc_status, total_chapters, current_volume,
                    last_compact_at=last_compact_at, chapters_since_compact=chapters_since_compact)

if __name__ == "__main__":
    main()
