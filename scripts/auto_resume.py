#!/usr/bin/env python3
"""
Auto-resume script for novel analysis.
Finds the most recent progress.json and resumes analysis.
Usage: python auto_resume.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

def migrate_progress_schema(progress):
    """Migrate legacy progress fields to the current schema."""

    if "processed_chapters" not in progress:
        progress["processed_chapters"] = progress.get("current_chapter", 0)

    if "last_compact_at" not in progress:
        progress["last_compact_at"] = 0

    if "chapters_since_compact" not in progress:
        progress["chapters_since_compact"] = (
            progress["processed_chapters"] - progress["last_compact_at"]
        )

    if "current_volume" not in progress:
        progress["current_volume"] = None

    progress.pop("current_chapter", None)
    progress.pop("compact_count", None)

    return progress

def get_resume_targets(project_dir):
    """Return resume file targets for the current environment."""

    env_name = os.environ.get("AGENT_ENV", "").lower()
    explicit_path = os.environ.get("NOVEL_ANALYZE_RESUME_FILE")
    targets = []

    targets.append(Path(project_dir) / ".novel_analyze_resume.json")
    targets.append(Path.cwd() / ".novel_analyze_resume.json")

    if explicit_path:
        targets.append(Path(explicit_path).expanduser())

    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    if xdg_state_home:
        targets.append(Path(xdg_state_home).expanduser() / "novel-analyze" / "novel_analyze_resume.json")
    else:
        targets.append(Path.home() / ".local" / "state" / "novel-analyze" / "novel_analyze_resume.json")

    if "gemini" in env_name or Path.home().joinpath(".gemini").exists():
        targets.append(Path.home() / ".gemini" / "memory" / "novel_analyze_resume.json")

    if "claude" in env_name or Path.home().joinpath(".claude").exists():
        targets.append(Path.home() / ".claude" / "memory" / "novel_analyze_resume.json")

    deduped = []
    seen = set()
    for target in targets:
        normalized = target.expanduser()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)

    return deduped

def find_latest_progress():
    """Find the most recently modified progress.json file."""

    # Common workspace locations
    search_paths = [
        Path.home() / "Documents" / "小说分析",
        Path.home() / "Desktop" / "小说分析",
        Path.home() / "小说启动",
        Path.cwd(),
    ]

    progress_files = []

    for base_path in search_paths:
        if not base_path.exists():
            continue
        # Find all progress.json files
        for progress_file in base_path.rglob("progress.json"):
            if progress_file.is_file():
                mtime = progress_file.stat().st_mtime
                progress_files.append((progress_file, mtime))

    if not progress_files:
        return None

    # Sort by modification time, newest first
    progress_files.sort(key=lambda x: x[1], reverse=True)
    return progress_files[0][0]

def load_progress(progress_file):
    """Load and display progress information."""

    with open(progress_file, 'r', encoding='utf-8') as f:
        progress = json.load(f)

    return migrate_progress_schema(progress)

def main():
    progress_file = find_latest_progress()

    if not progress_file:
        print("未找到任何分析进度文件")
        print("请确保已经启动过小说分析")
        return

    progress = load_progress(progress_file)
    project_dir = progress_file.parent

    print(f"""
╔════════════════════════════════════════════════════════════╗
║              找到最近的小说分析进度                        ║
╚════════════════════════════════════════════════════════════╝

📖 项目: {progress.get('project_name', '未知')}
📂 目录: {project_dir}
📍 当前进度: 第 {progress.get('processed_chapters', 0)} 章
📍 当前行号: {progress.get('current_line', '未知')}
📚 当前卷: {progress.get('current_volume') or '未知'}
📊 总章数: {progress.get('total_chapters', '未知')}
⏰ 最后更新: {progress.get('last_update', '未知')}

───────────────────────────────────────────────────────────────

📄 文档状态:""")

    docs_status = progress.get('docs_status', {})
    for doc, status in docs_status.items():
        status_icon = "🟡" if status == "updating" else "🟢" if status == "completed" else "⚪"
        print(f"   {status_icon} {doc}: {status}")

    print(f"""
───────────────────────────────────────────────────────────────

✅ 继续分析此项目

直接回复: 继续分析
或在提示中说: 分析 "{project_dir}"

进度文件: {progress_file}
""")

    # Save resume info for the skill to pick up
    resume_info = {
        "project_dir": str(project_dir),
        "progress_file": str(progress_file),
        "project_name": progress.get('project_name', ''),
        "processed_chapters": progress.get('processed_chapters', 0),
        "current_line": progress.get('current_line', 0),
        "current_volume": progress.get('current_volume'),
        "last_resume_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    resume_targets = get_resume_targets(project_dir)
    written_targets = []
    for resume_file in resume_targets:
        try:
            resume_file.parent.mkdir(parents=True, exist_ok=True)
            with open(resume_file, 'w', encoding='utf-8') as f:
                json.dump(resume_info, f, ensure_ascii=False, indent=2)
            written_targets.append(resume_file)
        except OSError:
            continue

    if written_targets:
        print(f"💾 恢复信息已保存: {written_targets[0]}")
    else:
        print("⚠️ 未能写入恢复信息文件，请检查目录权限或设置 NOVEL_ANALYZE_RESUME_FILE")

if __name__ == "__main__":
    main()
