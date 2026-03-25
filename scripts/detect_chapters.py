#!/usr/bin/env python3
"""
Detect and list chapters in a novel source file.
Usage: python detect_chapters.py <source_file>
"""

import sys
import re
from pathlib import Path

# Chapter detection patterns
CHAPTER_PATTERNS = [
    (r'^第[一二三四五六七八九十百千万\d]+章[^\n]*$', '标准章节'),
    (r'^第[一二三四五六七八九十百千万\d]+节[^\n]*$', '标准节'),
    (r'^第[一二三四五六七八九十百千万\d]+回[^\n]*$', '标准回'),
    (r'^\d+[\.\s]+[^\n]*$', '数字章节'),
    (r'^Chapter\s+\d+[^\n]*$', '英文Chapter'),
]

VOLUME_PATTERNS = [
    (r'^第[一二三四五六七八九十百千万]+卷', '中文卷'),
    (r'^Book\s+[IVXLCDM\d]+', '英文Book'),
    (r'^Volume\s+\d+', '英文Volume'),
    (r'^卷[一二三四五六七八九十百千万\d]+[^\n]*$', '数字卷'),
]

def match_chapter(line: str) -> tuple[bool, str]:
    """Check if line is a chapter header. Returns (is_match, pattern_name)."""
    line = line.strip()
    for pattern, name in CHAPTER_PATTERNS:
        if re.match(pattern, line):
            return True, name
    return False, None

def match_volume(line: str) -> tuple[bool, str]:
    """Check if line is a volume header. Returns (is_match, pattern_name)."""
    line = line.strip()
    for pattern, name in VOLUME_PATTERNS:
        match = re.match(pattern, line)
        if match:
            return True, name
    return False, None

def detect_chapters(source_file: str, limit: int = None):
    """Scan source file and detect all chapters and volumes."""
    if not Path(source_file).exists():
        print(f"Error: File not found: {source_file}")
        return

    print(f"Scanning: {source_file}")
    print("=" * 60)

    chapters = []
    volumes = []
    current_volume = None
    current_volume_line = None

    with open(source_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            if not line:
                continue

            # Check for volume
            is_vol, vol_type = match_volume(line)
            if is_vol:
                current_volume = line
                current_volume_line = line_num
                volumes.append({
                    'title': line,
                    'line': line_num,
                    'type': vol_type
                })
                print(f"[VOL] Line {line_num}: {line}")
                continue

            # Check for chapter
            is_ch, ch_type = match_chapter(line)
            if is_ch:
                chapters.append({
                    'seq': len(chapters) + 1,
                    'title': line,
                    'line': line_num,
                    'volume': current_volume,
                    'volume_line': current_volume_line,
                    'type': ch_type
                })

                if limit and len(chapters) <= limit:
                    vol_info = f" ({current_volume})" if current_volume else ""
                    print(f"[{len(chapters):3d}] Line {line_num}: {line}{vol_info}")

    # Summary
    print("=" * 60)
    print(f"Detection complete:")
    print(f"  Volumes found: {len(volumes)}")
    print(f"  Chapters found: {len(chapters)}")

    # Check for duplicate chapter titles
    title_counts = {}
    for ch in chapters:
        title = ch['title']
        title_counts[title] = title_counts.get(title, 0) + 1

    duplicates = {k: v for k, v in title_counts.items() if v > 1}
    if duplicates:
        print(f"\n⚠️  Duplicate chapter titles found:")
        for title, count in duplicates.items():
            print(f"    '{title}' appears {count} times")

    return chapters, volumes

def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_chapters.py <source_file> [--limit <n>]")
        print("Options:")
        print("  --limit <n>  Show first N chapters (default: show all in summary)")
        sys.exit(1)

    source_file = sys.argv[1]
    limit = None

    if len(sys.argv) >= 4 and sys.argv[2] == '--limit':
        limit = int(sys.argv[3])

    detect_chapters(source_file, limit)

if __name__ == "__main__":
    main()
