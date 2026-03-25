---
name: novel-analyze
description: Deep analysis of web novels and long-form fiction to create structured Obsidian knowledge bases. Use this skill whenever the user asks to analyze a novel, deconstruct a webnovel, extract character relationships, analyze plot structure, study writing style, extract world-building elements, create a knowledge base from fiction, or systematically break down a book's content. This applies regardless of format (txt, epub, pdf) or language (Chinese web novels, English fiction, etc.). Always use this skill when the user mentions "analyze this novel," "character extraction," "plot analysis," "writing style study," or wants to understand how a story works.
---

# Novel Deconstruction & Knowledge Base Builder

A specialized skill for deep structural analysis of web novels and long-form fiction, producing structured Obsidian knowledge bases with interconnected Markdown documents, wikilinks, and tagged content.

## ⚠️ CRITICAL: AUTO-CONTINUE MANDATORY ⚠️

**NEVER ASK FOR CONFIRMATION TO CONTINUE.**

After completing each batch (20 chapters):
- ✅ DO: Output progress report
- ✅ DO: Immediately start next batch
- ❌ DON'T: Ask "继续吗?" or "要继续吗?"
- ❌ DON'T: Ask for any confirmation
- ❌ DON'T: Wait for user input

**Only stop when:**
1. User manually stops (Ctrl+C)
2. Novel analysis complete
3. Context window error (run compact, then continue)

**Silent auto-continue is the default behavior. No questions, no confirmations.**

## Auto-Resume (自动恢复机制)

**技能启动时首先执行**：

1. **检查是否有未完成的分析**：在常见工作区位置搜索最近的 `progress.json`
   - 搜索路径：`~/Documents/小说分析/`, `~/Desktop/小说分析/`, `~/小说启动/`, 当前目录

2. **如果找到未完成项目**：
   - 显示项目信息和当前进度
   - **自动恢复分析**，无需用户指定路径
   - 用户只需确认"继续"即可

3. **用户主动恢复指令**：
   - "继续分析" / "继续" / "resume" → 自动找到最近项目并继续
   - 无需提供文件路径

**恢复提示格式**：
```
[找到未完成的分析]
📖 项目: 《小说名》
📍 当前进度: 第 50 章 (行 12500)
📂 当前卷: 第二卷
📂 目录: /path/to/project

继续此项目？(是/否)
```

## Core Workflow

The analysis process follows a strict five-phase protocol:

### Phase 1: Initialization & Workspace Setup

**Before any analysis begins, verify these prerequisites:**

1. **Source file location** — Ask the user for the path to the novel/text file
2. **Workspace directory** — Ask where the analysis results should be stored
3. **Format validation** — Check file format and convert if needed

**Directory structure to create:**
```
[workspace]/
├── 《[novel-name]》分析/
│   ├── progress.json          # Analysis tracking state
│   ├── source.txt             # Converted source file (if needed)
│   ├── 01_总览.md
│   ├── 02_剧情分析.md
│   ├── 03_人物.md
│   ├── 04_文字风格.md
│   └── 05_写作技巧.md
```

**If workspace exists:** Read `progress.json` and resume from last position
**If workspace is new:** Create directory structure and initialize `progress.json`

### Phase 2: Format Conversion

Support multiple input formats. For non-.txt files:

| Source Format | Conversion Method |
|---------------|-------------------|
| `.txt` | Use directly |
| `.epub` | Extract text content using available tools |
| `.pdf` | Extract text using pdf skill |
| `.docx` | Extract text using docx skill |

> **[Critical]** If conversion fails, stop and report: `[Error] Cannot convert [format] to .txt. Please provide a supported format.`

### Phase 2.5: Chapter Detection (章节识别)

**Before analysis begins, scan source file to build chapter registry:**

```python
# Chapter detection patterns (支持中英文混合)
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百千万\d]+章[^\n]*$',      # 第X章
    r'^第[一二三四五六七八九十百千万\d]+节[^\n]*$',      # 第X节
    r'^第[一二三四五六七八九十百千万\d]+回[^\n]*$',      # 第X回
    r'^\d+[\.\s]+[^\n]*$',                              # 1. 标题 或 1 标题
    r'^Chapter\s+\d+[^\n]*$',                           # Chapter X
    r'^卷[一二三四五六七八九十百千万\d]+[^\n]*$',        # 卷X
]

VOLUME_PATTERNS = [
    r'^第[一二三四五六七八九十百千万]+卷',                # 第X卷
    r'^Book\s+[IVXLCDM\d]+',                             # Book X
    r'^Volume\s+\d+',                                    # Volume X
]
```

**Multi-volume handling (多卷处理):**
- **Primary tracking**: Line number in source file (absolute position)
- **Chapter registry**: Each chapter gets unique `seq` number, records title + line + volume
- **Volume detection**: Auto-detect volume headers, track current volume

```json
// chapter_markers example
[
  {"seq": 1, "title": "第一章 开端", "line": 10, "volume": null},
  {"seq": 25, "title": "第一章 重生", "line": 8900, "volume": "第一卷"},
  {"seq": 50, "title": "第一章 觉醒", "line": 18500, "volume": "第二卷"}
]
```

> **[Critical]** Always use line number for position tracking. Chapter titles can be duplicated across volumes, but line numbers are unique.

### Phase 3: Progress State Management

**Initialize progress.json** (if new project):
```json
{
  "project_name": "小说名称",
  "source_file": "path/to/source.txt",
  "current_line": 0,
  "processed_chapters": 0,
  "last_compact_at": 0,
  "chapters_since_compact": 0,
  "chapter_markers": [],
  "current_volume": null,
  "docs_status": {
    "01_总览": "initialized",
    "02_剧情分析": "initialized",
    "03_人物": "initialized",
    "04_文字风格": "initialized",
    "05_写作技巧": "initialized"
  },
  "last_update": "YYYY-MM-DD HH:MM:SS"
}
```

**Load existing progress.json (migration handling):**
```python
# 读取现有进度
with open('progress.json', 'r') as f:
    progress = json.load(f)

# 迁移旧版 schema → 新版 schema
if "processed_chapters" not in progress:
    # 旧版使用 current_chapter
    progress["processed_chapters"] = progress.get("current_chapter", 0)

if "last_compact_at" not in progress:
    # 旧版没有此字段，初始化为 0
    progress["last_compact_at"] = 0

if "chapters_since_compact" not in progress:
    # 根据 processed_chapters 和 last_compact_at 计算
    last_compact = progress.get("last_compact_at", 0)
    progress["chapters_since_compact"] = progress["processed_chapters"] - last_compact

if "current_volume" not in progress:
    progress["current_volume"] = None

# 清理旧字段
if "compact_count" in progress:
    del progress["compact_count"]  # 不再需要此字段
if "current_chapter" in progress:
    del progress["current_chapter"]  # 使用 processed_chapters

# 保存迁移后的进度
with open('progress.json', 'w') as f:
    json.dump(progress, f, indent=2)
```

**Update progress.json** after each batch (every 20 chapters analyzed):
```python
# 计算新值
new_processed = previous_processed + 20
last_compact_at = progress.get("last_compact_at", 0)
chapters_since_compact = new_processed - last_compact_at

# 更新 progress.json
{
  "processed_chapters": new_processed,
  "last_compact_at": last_compact_at,
  "chapters_since_compact": chapters_since_compact,
  "current_line": <line>,
  "current_volume": <volume>,
  "docs_status": {...},
  "last_update": <timestamp>
}
```

> **[Critical]** 每批必须计算并写入 `chapters_since_compact`，auto-compact 依赖此值触发！

### Phase 4: Incremental Analysis (Batch Processing)

**Batch size: 20 chapters per iteration**

## ⚠️ AUTO-COMPACT TRIGGER ⚠️

**核心逻辑：追踪"自上次 compact 后读取的章节数"**

**progress.json 字段说明：**
```json
{
  "processed_chapters": 125,     // 累计已处理章节数（绝对值）
  "last_compact_at": 60,         // 上次 compact 时的 processed_chapters 值
  "chapters_since_compact": 65   // 自上次 compact 后新增章节数
}
```

**Compact 触发条件：当 `chapters_since_compact >= 60`**

---

**每批完成后的检查流程：**

```python
# 1. 读取 progress.json
processed = progress_json.get("processed_chapters", 0)
last_compact_at = progress_json.get("last_compact_at", 0)

# 2. 计算自上次 compact 后新增的章节数
chapters_since_compact = processed - last_compact_at

# 3. 更新到 progress.json（每批都写入）
progress_json["chapters_since_compact"] = chapters_since_compact

# 4. 检查是否需要 compact
if chapters_since_compact >= 60:
    print("🔴 [AUTO-COMPACT] 自上次 compact 后已处理 {} 章，执行压缩...".format(chapters_since_compact))
    compact                                    # ← 立即执行此命令
    progress_json["last_compact_at"] = processed  # ← 更新 compact 基准点
    progress_json["chapters_since_compact"] = 0  # ← 重置计数器
    save_progress_json()                       # ← 保存文件
    print("✓ [AUTO-COMPACT] 完成，继续分析...")
else:
    print("[Info] 距离下次 compact 还有 {} 章".format(60 - chapters_since_compact))
```

**Visual trigger indicator:**
```
Batch 1: chapters_since_compact = 20  → 继续分析
Batch 2: chapters_since_compact = 40  → 继续分析
Batch 3: chapters_since_compact = 60  → 🔴 COMPACT → 重置为 0
Batch 4: chapters_since_compact = 20  → 继续分析
Batch 5: chapters_since_compact = 40  → 继续分析
Batch 6: chapters_since_compact = 60  → 🔴 COMPACT → 重置为 0
```

---

**Automatic Continuation (重要)**:
- 完成每 20 章分析后，**自动继续**下 20 章
- 仅在以下情况暂停：
  1. 终端中断/用户手动停止
  2. 小说分析完成（到达末尾）
  3. **执行 compact 时自动压缩，完成后继续**
- 每批完成后输出简要进度报告，然后自动进入下一批

**上下文压缩机制**:
- 使用 `compact` 命令压缩对话上下文
- 保留关键信息：project_dir, progress.json 路径, 当前任务状态
- 每处理 60 章自动执行一次，避免上下文积累过多

**For each batch:**
1. Read next 20 chapters using `chapter_markers` (by line number)
2. Extract content between chapter markers
3. **Use `/obsidian-markdown` skill** to append/update the 5 core documents
4. **Update `progress.json` - 每批必须更新:**
   ```python
   # 计算并更新
   processed = previous_processed + batch_chapters
   last_compact_at = progress_json.get("last_compact_at", 0)
   chapters_since_compact = processed - last_compact_at

   # 写入 progress.json
   {
     "processed_chapters": processed,
     "last_compact_at": last_compact_at,
     "chapters_since_compact": chapters_since_compact,
     "current_line": <line>,
     "current_volume": "<volume>",
     "docs_status": {...},
     "last_update": "<timestamp>"
   }
   ```

5. Output brief progress report
6. **🔴 AUTO-COMPACT CHECK**:
   ```python
   if chapters_since_compact >= 60:
       print("🔴 [AUTO-COMPACT] 已达 {} 章，执行压缩...")
       compact
       progress_json["last_compact_at"] = processed
       progress_json["chapters_since_compact"] = 0
       save_progress_json()
       print("✓ [AUTO-COMPACT] 完成，继续分析...")
   ```
7. **Automatically continue to next batch** (unless interruption conditions met)

**Progress Report Format (每批完成后输出):**
```
[Batch Complete]
已分析：第 {start_seq}-{end_seq} 章
当前行：{line}
当前卷：{current_volume}
自上次 compact：{chapters_since_compact} / 60 章
总进度：{processed}/{total} 章 ({percentage}%)
文档状态：
  - 01_总览: {status}
  - 02_剧情分析: {status}
  - 03_人物: {status}
  - 04_文字风格: {status}
  - 05_写作技巧: {status}
继续下 20 章...
```

**Pause Conditions (暂停条件):**

**1. Context Window Limit (上下文窗口限制):**

**策略一：首选 compact 命令**
- 当遇到上下文限额错误时：
  1. 保存当前进度到 `progress.json`
  2. **执行 `compact` 命令**压缩上下文
  3. 自动继续分析（无需用户操作）

**策略二：备选跨会话恢复**
- 如果 compact 后仍有问题：
  1. 保存进度到 `progress.json`
  2. 输出提示：
     ```
     [需切换会话] 进度已保存
     第 X 章完成

     开启新对话，输入: 继续
     ```
  3. 用户开启新对话说"继续"，自动恢复

**预防性压缩**：
- 每 60 章（每 3 批）自动执行 `compact` 命令
- 避免上下文积累到达限额

### Phase 5: Output Documents

Generate exactly **5 core Markdown documents** using Obsidian Flavored Markdown syntax (via `/obsidian-markdown` skill):

---

## 📁 01_总览.md (Overview & Outline)

```yaml
---
title: "《[小说名]》总览"
tags:
  - [genre]        // 玄幻/奇幻/武侠/仙侠/都市/科幻/悬疑/历史/游戏/轻小说/言情
  - [subgenre]     // 重生流/穿越流/系统流/无限流/退婚流/凡人流/无敌流/苟道流
  - 分析/总览
created: YYYY-MM-DD
---

# 《[小说名]》总览

## 元数据
- **作者**: [作者名]
- **题材**: [[题材分类]]
- **流派**: [[流派标签]]
- **字数**: [估计字数]
- **状态**: [连载中/已完结]

## 世界观与设定

### 背景设定
[描述故事发生的世界背景，物理/魔法/修真社会规则]

### 力量/升级体系
| 境界/等级 | 描述 | 突破条件 |
|-----------|------|----------|
| [等级1] | [描述] | [条件] |
| [等级2] | [描述] | [条件] |

**资源驱动力**: [什么资源推动角色变强？]

## 主线目标
[一句话概括主角的核心目标]

## 相关文档
- [[02_剧情分析]]
- [[03_人物]]
- [[04_文字风格]]
- [[05_写作技巧]]
```

---

## 📁 02_剧情分析.md (Plot Progression & Logic)

```yaml
---
title: "《[小说名]》剧情分析"
tags: [分析/剧情]
---

# 剧情分析

## 剧情推进引擎
[分析故事靠什么驱动：外部危机？复仇执念？系统任务？生存压力？]

## 主线梳理

### [篇章/阶段名称] (第X-Y章)
- **核心冲突**: [是什么冲突？]
- **关键事件**:
  - [事件1] → [影响]
  - [事件2] → [影响]

## 伏笔与暗线

| 伏笔内容 | 埋线位置 | 收线位置 | 状态 |
|---------|---------|---------|------|
| [伏笔描述] | 第X章 | 第Y章 | 已回收/待回收 |

## 逻辑闭环分析
[分析重要剧情事件的起承转合，逻辑是否自洽，填坑情况]
```

---

## 📁 03_人物.md (Characters & Portrayal)

```yaml
---
title: "《[小说名]》人物档案"
tags: [分析/人物]
---

# 人物档案

## [主角姓名] (主角)

### 基本信息
- **身份**: [身份/职业]
- **核心动机**: [驱动角色的深层欲望]
- **性格标签**: #性格标签

### 性格特征
[描述性格特点，包括反差和成长]

### 关键剧情塑造

| 章节/事件 | 行为 | 塑造的性格侧面 |
|----------|------|---------------|
| [第X章 - 事件名] | [角色做了什么] | [展现了什么特质] |

### 人物关系
- 与[[配角A]]: [关系描述]
- 与[[反派B]]: [关系描述]

---

## [配角/反派姓名]
[按相同结构记录重要配角]
```

---

## 📁 04_文字风格.md (Writing Style Analysis)

```yaml
---
title: "《[小说名]》文字风格分析"
tags: [分析/文风]
---

# 文字风格分析

> 用显微镜级别拆解作者的写作手法，**持续从原文中摘抄积累实例**

## 1. 文戏描写（张力与博弈）

### 特点总结
[如何处理权力交锋、情感拉扯、智斗博弈的张力？]

### 实例积累（持续追加）

#### 潜台词运用
> 第X章：[引用原文]
> **分析**：[分析台面下的潜台词]

#### 细节暗示
> 第X章：[引用原文]
> **分析**：[分析如何通过微小动作表现心理压迫]

---

## 2. 战斗描写（画面与痛感）

### 特点总结
- 感官调用：[使用了哪些感官]
- 空间调度：[如何交代地形和走位]
- 动词特点：[高频使用的动词类型]

### 实例积累（持续追加）

#### 画面与动感
> 第X章：[引用原文]
> **分析**：[分析画面感和动感]

#### 痛感与暴力
> 第X章：[引用原文]
> **分析**：[分析如何表现痛感]

#### 短句快节奏
> 第X章：[引用原文]
> **分析**：[分析短句组合如何加快呼吸感]

---

## 3. 环境描写（气氛与隐喻）

### 实例积累（持续追加）

#### 气氛渲染
> 第X章：[引用原文]
> **分析**：[分析环境如何渲染气氛]

#### 命运暗示
> 第X章：[引用原文]
> **分析**：[分析环境对人物命运或剧情走向的暗示]

---

## 4. 心理活动描写（潜意识剖析）

### 实例积累（持续追加）

#### 挣扎与矛盾
> 第X章：[引用原文]
> **分析**：[分析心理挣扎的表现]

#### 潜意识暴露
> 第X章：[引用原文]
> **分析**：[分析如何剥开角色伪装]

---

## 5. 外貌描写（骨相与皮相）

### 实例积累（持续追加）

#### 衣着器物
> 第X章：[引用原文]
> **分析**：[分析]

#### 骨相气质
> 第X章：[引用原文]
> **分析**：[分析]

---

## 6. 对话描写（闻声知人）

### 实例积累（持续追加）

#### 身份体现
> 第X章 [角色]：[引用对话]
> **分析**：[分析对话如何体现身份地位]

#### 情绪变化
> 第X章 [角色]：[引用对话]
> **分析**：[分析对话中的情绪层次]

---

## 7. 排版与段落习惯

### 实例积累（持续追加）

#### 短段落示例
> 第X章：[引用原文短段落排版]
> **效果**：[分析]

---

## 8. 统计数据

| 维度 | 实例数量 |
|------|----------|
| 文戏 | X条 |
| 战斗 | X条 |
| 环境 | X条 |
| 心理 | X条 |
| 外貌 | X条 |
| 对话 | X条 |
| **总计** | **X条** |
```

> **[重要]** 文字风格分析的核心在于**实例积累**。每分析一批章节，都必须从原文中摘抄典型例子，注明章节位置，并附带简短分析。随着分析深入，这些实例将形成丰富的写作技法资料库。

---

## 📁 05_写作技巧.md (Writing Techniques)

```yaml
---
title: "《[小说名]》写作技巧分析"
tags: [分析/技巧]
---

# 写作技巧分析

## 视角运用
- [视角类型]: [使用场景和效果]
  - 例子: [引用原文说明]

## Show, Don't Tell
[展示与讲述的比例分析]
- 展示占比: [估计比例]
- 典型展示手法: [描述]
- 典型讲述手法: [描述]

> [对比例子]

## 悬念与卡点设置
[章节末尾如何设置悬念吸引读者继续阅读？]

### 常用卡点类型
1. [类型1]: [说明]
2. [类型2]: [说明]

> [引用原文卡点例子]

## 节奏控制
[整体叙事节奏：快/慢/变化规律]
```

---

## Interlinking Rules

**Use wikilinks `[[ ]]` for all cross-references:**

- When mentioning a character in plot analysis: `[[03_人物#角色名]]`
- When referring to writing style examples: `[[04_文字风格#章节]]`
- World-building elements: `[[01_总览#世界观]]`

**Use tags `#` for categorization:**
- Genre tags: `#玄幻` `#都市` `#科幻` `#重生流` `#系统流`
- Status tags: `#分析中` `#已完成`
- Element tags: `#伏笔` `#战斗场面` `#人物弧光`

---

## Execution Constraints

1. **Pre-scan chapters**: Before analysis, scan source file to build `chapter_markers` registry
2. **Line-based tracking**: Use line numbers as primary position tracking (handles duplicate chapter names)
3. **Fixed batch size**: 20 chapters per batch
4. **Auto-continue**: After each batch, automatically continue to next batch
5. **Checkpoint every batch**: Save progress.json after every batch (enables cross-session resume)
6. **Auto-compact every 60 chapters**: Track chapters since last compact, execute when ≥60
7. **Use /obsidian-markdown skill**: For all Markdown output generation
8. **Handle context window limit**: First try `compact`, if still issues then switch session
9. **Enable seamless resume**: New session reads progress.json and continues from exact line

> **三重保障机制**：
> - **章节扫描**：启动时扫描全文，建立章节签名表（处理多卷重复章节名）
> - **上下文压缩**：追踪 `chapters_since_compact`，满 60 章自动执行 compact
> - **跨会话恢复**：用户说"继续"即可从精确行号恢复，compact 基准点不丢失

> **Compact 检查逻辑**：
> ```python
> # 每批完成后检查
> chapters_since_compact = processed_chapters - last_compact_at
> if chapters_since_compact >= 60:
>     run compact command
>     last_compact_at = processed_chapters
>     chapters_since_compact = 0
>     save to progress.json
> ```

---

## Supported Genres Classification

**Main Categories (主分类):**
- `#玄幻` `#奇幻` `#武侠` `#仙侠` `#都市` `#科幻` `#悬疑` `#历史` `#游戏` `#轻小说` `#言情`

**Flow Types (流派):**
- `#重生流` `#穿越流` `#系统流` `#无限流` `#退婚流` `#凡人流` `#无敌流` `#苟道流` `#群像流` `#多女主` `#单女主`

Match existing tags when possible, create new ones when needed.
