# Progress.json Schema Reference

This document describes the standard structure for `progress.json` files used in novel analysis projects.

## Standard Format

```json
{
  "project_name": "小说名称",
  "source_file": "/path/to/source.txt",
  "current_line": 12345,
  "processed_chapters": 125,
  "last_compact_at": 60,
  "chapters_since_compact": 65,
  "chapter_markers": [
    {"seq": 1, "title": "第一章 开端", "line": 10, "volume": null},
    {"seq": 2, "title": "第二章 启程", "line": 350, "volume": null},
    {"seq": 25, "title": "第一卷 第一章 重生", "line": 8900, "volume": "第一卷"},
    {"seq": 26, "title": "第一卷 第二章 觉醒", "line": 9500, "volume": "第一卷"}
  ],
  "volume_pattern": "第[一二三四五六七八九十百千万]+卷|Book\\s+\\d+|Volume\\s+\\d+",
  "docs_status": {
    "01_总览": "completed",
    "02_剧情分析": "updating",
    "03_人物": "updating",
    "04_文字风格": "initialized",
    "05_写作技巧": "initialized"
  },
  "last_update": "2024-03-25 14:30:00"
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `project_name` | string | Name of the novel being analyzed |
| `source_file` | string | Absolute path to the source text file |
| `current_line` | number | **Primary tracking**: Current line number in source file |
| `processed_chapters` | number | Total count of chapters processed (absolute value) |
| `last_compact_at` | number | Value of `processed_chapters` when last compact was executed |
| `chapters_since_compact` | number | Chapters added since last compact (triggers at ≥40) |
| `chapter_markers` | array | **Chapter registry**: Each chapter's unique signature |
| `volume_pattern` | string | Regex pattern for detecting volume headers |
| `docs_status` | object | Status of each output document |
| `last_update` | string | Timestamp of last progress update (YYYY-MM-DD HH:MM:SS) |

## Chapter Marker Structure

```json
{
  "seq": 25,           // Sequential number (1-indexed, unique)
  "title": "第一卷 第一章 重生",
  "line": 8900,        // Starting line in source file
  "volume": "第一卷"    // Detected volume (null if none)
}
```

## Multi-Volume Novel Handling

### Problem
Multiple volumes have duplicate chapter names:
```
第一章 开端     (line 10)
...
第一章 重生     (line 8900, 第一卷)
第一章 觉醒     (line 18500, 第二卷)
```

### Solution: Line-Based Positioning + Chapter Registry

1. **Primary tracking by line number** - `current_line` is the source of truth
2. **Chapter signatures** - Each chapter gets unique `seq` number
3. **Volume detection** - Auto-detect volume headers using regex

```python
# Chapter detection patterns
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百千万\d]+章',           # 第X章
    r'^第[一二三四五六七八九十百千万\d]+节',           # 第X节
    r'^第[一二三四五六七八九十百千万\d]+回',           # 第X回
    r'^\d+[\.\s]*[章节回]',                          # 1. / 1章
    r'^Chapter\s+\d+',                              # Chapter X
]

VOLUME_PATTERNS = [
    r'^第[一二三四五六七八九十百千万]+卷',            # 第X卷
    r'^Book\s+[IVXLCDM\d]+',                         # Book X
    r'^Volume\s+\d+',                                # Volume X
    r'^卷[一二三四五六七八九十百千万\d]+',            # 卷X
]
```

## Chapter Detection Algorithm

```python
import re

def detect_chapters(source_file):
    """Scan source file and build chapter marker list."""
    markers = []
    current_volume = None
    seq = 1

    with open(source_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Check for volume header
            volume_match = match_volume(line)
            if volume_match:
                current_volume = volume_match.group(0)
                continue

            # Check for chapter header
            chapter_match = match_chapter(line)
            if chapter_match:
                markers.append({
                    "seq": seq,
                    "title": line,
                    "line": line_num,
                    "volume": current_volume
                })
                seq += 1

    return markers

def match_volume(line):
    """Match volume header patterns."""
    patterns = [
        r'^第[一二三四五六七八九十百千万]+卷',
        r'^Book\s+[IVXLCDM\d]+',
        r'^Volume\s+\d+',
    ]
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            return match
    return None

def match_chapter(line):
    """Match chapter header patterns."""
    patterns = [
        r'^第[一二三四五六七八九十百千万\d]+章[^\n]*$',
        r'^第[一二三四五六七八九十百千万\d]+节[^\n]*$',
        r'^第[一二三四五六七八九十百千万\d]+回[^\n]*$',
        r'^\d+[\.\s]+[^\n]*$',  # 1. or 1 标题
        r'^Chapter\s+\d+',
    ]
    for pattern in patterns:
        if re.match(pattern, line):
            return True
    return None
```

## Resumption Protocol

When resuming an analysis session:

1. Read `progress.json`
2. Load `chapter_markers` array
3. Find last processed marker by `current_line`
4. Next chapter = markers[index + 1]
5. Read source file from next chapter's `line` number
6. Continue processing

```python
# Load progress
with open('progress.json', 'r', encoding='utf-8') as f:
    progress = json.load(f)

# Find last processed chapter
last_seq = progress['processed_chapters']
start_line = progress['current_line']

# Or find by marker
if last_seq > 0 and 'chapter_markers' in progress:
    last_marker = progress['chapter_markers'][-1]
    start_line = last_marker['line']

# Process next batch from start_line
# After processing 20 chapters:
progress['current_line'] = new_line_position
progress['processed_chapters'] += 20
progress['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Save
with open('progress.json', 'w', encoding='utf-8') as f:
    json.dump(progress, f, ensure_ascii=False, indent=2)
```

## Batch Processing with Chapter Markers

```python
def process_batch(progress, source_file, batch_size=20):
    """Process a batch of chapters using line-based positioning."""
    start_line = progress['current_line']
    start_seq = progress['processed_chapters'] + 1

    # Read source from start_line
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[start_line:]

    # Extract next batch_size chapters
    markers = []
    current_volume = progress.get('current_volume')

    for i, line in enumerate(lines):
        line_num = start_line + i + 1
        line = line.strip()

        # Detect volume change
        volume = match_volume(line)
        if volume:
            current_volume = volume.group(0)
            continue

        # Detect chapter
        if match_chapter(line):
            markers.append({
                "seq": start_seq + len(markers),
                "title": line,
                "line": line_num,
                "volume": current_volume
            })

            if len(markers) >= batch_size:
                break

    return markers
```

## Progress Report Format

```
[Batch Complete]
已分析：第 1-20 章 (共 50 章)
当前行：第 12500 行
卷信息：第一卷 (第 1-20 章)
文档状态：
  - 01_总览: updating
  - 02_剧情分析: updating
  - 03_人物: updating
  - 04_文字风格: updating
  - 05_写作技巧: initialized
继续下 20 章...
```
