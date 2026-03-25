# novel-analyze

[English](#english) | [中文](#中文)

---

## 中文

深度分析网络小说和长篇虚构作品，生成结构化的 Obsidian 知识库。

### 功能特性

- **多格式支持**：.txt, .epub, .pdf, .docx
- **增量批处理**：每批 20 章，自动继续分析
- **多卷小说处理**：智能章节检测，行号定位（解决重复章节名问题）
- **上下文管理**：每 60 章自动压缩上下文
- **跨会话恢复**：中断后从精确位置继续分析
- **5份输出文档**：总览、剧情分析、人物、文字风格、写作技巧

### 依赖要求

此 skill 需要与 **obsidian-markdown** skill 配合使用：

```bash
# 安装 obsidian-markdown（必需）
npx skills add https://github.com/anthropics/obsidian-markdown

# 安装 novel-analyze
npx skills add https://github.com/keeper-feather/novel-analyze
```

### 安装方式

```bash
npx skills add https://github.com/keeper-feather/novel-analyze
```

### 使用指南

#### 1. 准备小说文件

支持的格式：
- `.txt` - 直接使用
- `.epub` - 自动提取文本
- `.pdf` - 使用 pdf skill 提取
- `.docx` - 使用 docx skill 提取

#### 2. 开始分析

```bash
# 分析小说
分析 /path/to/novel.txt

# 或使用自然语言
帮我分析这本小说 ~/Downloads/仙逆.txt
拆解这部作品的剧情结构和人物关系
```

#### 3. 输出结构

分析完成后，在指定目录生成 5 个 Obsidian Markdown 文档：

```
《小说名》分析/
├── progress.json          # 进度追踪文件
├── 01_总览.md
├── 02_剧情分析.md
├── 03_人物.md
├── 04_文字风格.md
└── 05_写作技巧.md
```

#### 4. 处理上下文不足

**方式一：手动压缩**
```bash
compact
```
压缩后，在同一会话中继续分析

**方式二：新开窗口**
```
1. 开启新对话
2. 输入：继续
3. 系统自动从断点恢复
```

#### 5. 恢复中断的分析

```bash
# 自动检测未完成项目
继续

# 或
继续分析
resume
```

### 分析规范

#### 小说格式要求

- **章节标记**：使用标准章节格式（第X章、Chapter X 等）
- **编码**：推荐 UTF-8
- **来源**：正版网站或本地文件

#### 支持的章节格式

```
第X章 章节标题
第X节 章节标题
Chapter X: Title
1. 章节标题
卷X
```

### 工作流程

```
┌─────────────┐
│ 提供小说文件  │
└──────┬──────┘
       ▼
┌─────────────┐
│ 扫描章节结构  │ ← 建立章节签名表
└──────┬──────┘
       ▼
┌─────────────┐
│ 批量分析(20章)│
└──────┬──────┘
       ▼
┌─────────────┐
│ 更新进度文档  │ ← progress.json
└──────┬──────┘
       ▼
   每60章?
       ├── 是 → compact 压缩 → 继续
       └── 否 → 继续
```

### 常见问题

**Q: 分析中断了怎么办？**
A: 开启新对话，输入"继续"，系统自动恢复。

**Q: 上下文窗口不够？**
A: 输入 `compact` 命令压缩上下文，或新开对话继续。

**Q: 支持英文小说吗？**
A: 支持，自动检测中英文章节格式。

**Q: 多卷小说章节重复怎么处理？**
A: 使用行号定位系统，每个章节有唯一签名。

### 技术架构

```
novel-analyze/
├── SKILL.md              # 主技能定义
├── references/           # 参考资料库
│   ├── ANALYSIS_GUIDE.md # 4模块分析框架
│   ├── SCHEMA.md         # progress.json 数据结构
│   ├── TAGS.md           # 标签分类库
│   └── TEMPLATES.md      # 输出模板
└── scripts/              # 辅助脚本
    ├── detect_chapters.py    # 章节检测
    ├── init_progress.py      # 进度初始化
    ├── update_progress.py    # 进度更新
    └── auto_resume.py        # 自动恢复
```

### License

MIT

---

## English

Deep analysis of web novels and long-form fiction to create structured Obsidian knowledge bases.

### Features

- **Multi-format support**: .txt, .epub, .pdf, .docx
- **Incremental batch processing**: 20 chapters per batch with auto-continue
- **Multi-volume novel handling**: Smart chapter detection with line-based tracking
- **Context management**: Auto-compact every 60 chapters
- **Cross-session resume**: Continue analysis from exact position after interruption
- **5 output documents**: Overview, Plot Analysis, Characters, Writing Style, Techniques

### Dependencies

This skill requires the **obsidian-markdown** skill:

```bash
# Install obsidian-markdown (required)
npx skills add https://github.com/anthropics/obsidian-markdown

# Install novel-analyze
npx skills add https://github.com/keeper-feather/novel-analyze
```

### Installation

```bash
npx skills add https://github.com/keeper-feather/novel-analyze
```

### Usage Guide

#### 1. Prepare Novel File

Supported formats:
- `.txt` - Direct use
- `.epub` - Auto text extraction
- `.pdf` - Extract using pdf skill
- `.docx` - Extract using docx skill

#### 2. Start Analysis

```bash
# Analyze a novel
分析 /path/to/novel.txt

# Or natural language
帮我分析这本小说 ~/Downloads/novel.txt
拆解这部作品的剧情结构和人物关系
```

#### 3. Output Structure

After analysis, 5 Obsidian Markdown documents are generated:

```
《Novel Name》分析/
├── progress.json          # Progress tracking
├── 01_总览.md
├── 02_剧情分析.md
├── 03_人物.md
├── 04_文字风格.md
└── 05_写作技巧.md
```

#### 4. Handle Context Limit

**Method 1: Manual Compact**
```bash
compact
```
Then continue in the same session.

**Method 2: New Session**
```
1. Start a new conversation
2. Type: 继续
3. Auto-resume from breakpoint
```

#### 5. Resume Interrupted Analysis

```bash
# Auto-detect incomplete projects
继续

# Or
继续分析
resume
```

### Novel Format Requirements

- **Chapter markers**: Standard chapter formats (第X章, Chapter X, etc.)
- **Encoding**: UTF-8 recommended
- **Source**: Official websites or local files

#### Supported Chapter Formats

```
第X章 章节标题
Chapter X: Title
1. Chapter Title
Volume X
```

### Workflow

```
┌─────────────┐
│ Provide File │
└──────┬──────┘
       ▼
┌─────────────┐
│ Scan Chapters│ ← Build chapter registry
└──────┬──────┘
       ▼
┌─────────────┐
│ Analyze(20)  │
└──────┬──────┘
       ▼
┌─────────────┐
│ Save Progress│ ← progress.json
└──────┬──────┘
       ▼
   Every 60?
       ├── Yes → compact → continue
       └── No  → continue
```

### FAQ

**Q: What if analysis is interrupted?**
A: Start a new conversation and type "继续" to auto-resume.

**Q: Context window insufficient?**
A: Run `compact` command or start a new session.

**Q: Does it support English novels?**
A: Yes, auto-detects Chinese/English chapter formats.

**Q: How are duplicate chapter names handled?**
A: Line-based tracking gives each chapter a unique signature.

### Project Structure

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

### License

MIT
