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

    return progress

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
📍 当前进度: 第 {progress.get('current_chapter', 0)} 章
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
        "current_chapter": progress.get('current_chapter', 0),
        "last_resume_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    resume_file = Path.home() / ".claude" / "projects" / "-Users-keeper-----" / "memory" / "novel_analyze_resume.json"
    resume_file.parent.mkdir(parents=True, exist_ok=True)

    with open(resume_file, 'w', encoding='utf-8') as f:
        json.dump(resume_info, f, ensure_ascii=False, indent=2)

    print(f"💾 恢复信息已保存，技能将自动继续分析")

if __name__ == "__main__":
    main()
