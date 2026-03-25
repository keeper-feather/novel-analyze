#!/usr/bin/env python3
"""
Initialize progress.json for a novel analysis project.
Usage: python init_progress.py <project_name> <source_file> <workspace_dir>
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

# Chapter detection patterns
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百千万\d]+章[^\n]*$',      # 第X章
    r'^第[一二三四五六七八九十百千万\d]+节[^\n]*$',      # 第X节
    r'^第[一二三四五六七八九十百千万\d]+回[^\n]*$',      # 第X回
    r'^\d+[\.\s]+[^\n]*$',                              # 1. 标题
    r'^Chapter\s+\d+[^\n]*$',                           # Chapter X
]

VOLUME_PATTERNS = [
    r'^第[一二三四五六七八九十百千万]+卷',                # 第X卷
    r'^Book\s+[IVXLCDM\d]+',                             # Book X
    r'^Volume\s+\d+',                                    # Volume X
    r'^卷[一二三四五六七八九十百千万\d]+[^\n]*$',        # 卷X
]

def match_chapter(line: str) -> bool:
    """Check if line is a chapter header."""
    line = line.strip()
    for pattern in CHAPTER_PATTERNS:
        if re.match(pattern, line):
            return True
    return False

def match_volume(line: str) -> re.Match | None:
    """Check if line is a volume header and return match."""
    line = line.strip()
    for pattern in VOLUME_PATTERNS:
        match = re.match(pattern, line)
        if match:
            return match
    return None

def scan_chapters(source_file: str) -> list:
    """Scan source file and build chapter marker list."""
    markers = []
    current_volume = None
    seq = 1

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Check for volume header
                volume_match = match_volume(line)
                if volume_match:
                    current_volume = volume_match.group(0)
                    # Also add volume as a marker for reference
                    markers.append({
                        "seq": seq,
                        "title": line,
                        "line": line_num,
                        "volume": current_volume,
                        "type": "volume"
                    })
                    seq += 1
                    continue

                # Check for chapter header
                if match_chapter(line):
                    markers.append({
                        "seq": seq,
                        "title": line,
                        "line": line_num,
                        "volume": current_volume,
                        "type": "chapter"
                    })
                    seq += 1
    except Exception as e:
        print(f"Warning: Could not scan source file: {e}")
        return []

    return markers

def init_progress(project_name: str, source_file: str, workspace_dir: str):
    """Initialize a new progress.json file."""

    project_dir = Path(workspace_dir) / f"《{project_name}》分析"
    project_dir.mkdir(parents=True, exist_ok=True)

    progress_file = project_dir / "progress.json"

    # Scan source file for chapters
    print(f"Scanning source file for chapters...")
    chapter_markers = scan_chapters(source_file)

    # Count chapters (exclude volume markers)
    chapter_count = sum(1 for m in chapter_markers if m.get("type") != "volume")

    progress_data = {
        "project_name": project_name,
        "source_file": source_file,
        "current_line": 0,
        "processed_chapters": 0,
        "last_compact_at": 0,
        "chapters_since_compact": 0,
        "total_chapters": chapter_count,
        "chapter_markers": chapter_markers,
        "current_volume": None,
        "docs_status": {
            "01_总览": "initialized",
            "02_剧情分析": "initialized",
            "03_人物": "initialized",
            "04_文字风格": "initialized",
            "05_写作技巧": "initialized"
        },
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Initialized progress.json at: {progress_file}")
    print(f"✓ Project directory: {project_dir}")
    print(f"✓ Detected {chapter_count} chapters, {len(chapter_markers)} total markers")

    return str(progress_file)

def main():
    if len(sys.argv) < 4:
        print("Usage: python init_progress.py <project_name> <source_file> <workspace_dir>")
        sys.exit(1)

    init_progress(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()
