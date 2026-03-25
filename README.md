# novel-analyze

Deep analysis of web novels and long-form fiction to create structured Obsidian knowledge bases.

## Features

- **Multi-format support**: .txt, .epub, .pdf, .docx
- **Incremental batch processing**: 20 chapters per batch with auto-continue
- **Multi-volume novel handling**: Smart chapter detection with line-based tracking
- **Context management**: Auto-compact every 60 chapters
- **Cross-session resume**: Continue analysis from exact position after interruption
- **5 output documents**: 总览, 剧情分析, 人物, 文字风格, 写作技巧

## Installation

```bash
npx skills add https://github.com/YOUR_USERNAME/novel-analyze
```

## Usage

```bash
# Analyze a novel
分析 /path/to/novel.txt

# Resume interrupted analysis
继续
```

## Requirements

- Claude Code CLI
- Python 3.10+ (for bundled scripts)

## Skill Structure

```
novel-analyze/
├── SKILL.md              # Main skill definition
├── references/           # Reference materials
│   ├── ANALYSIS_GUIDE.md # Analysis framework
│   ├── SCHEMA.md         # progress.json schema
│   ├── TAGS.md           # Tag library
│   └── TEMPLATES.md      # Output templates
└── scripts/              # Helper scripts
    ├── detect_chapters.py    # Chapter detection
    ├── init_progress.py      # Initialize progress
    ├── update_progress.py    # Update progress
    └── auto_resume.py        # Auto-resume utility
```

## License

MIT
