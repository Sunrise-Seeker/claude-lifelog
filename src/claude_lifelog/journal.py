from pathlib import Path
from datetime import datetime
from .paths import get_diary_dir, get_story_file, get_today_diary_path


def write_entry(content: str) -> str:
    path = get_today_diary_path()
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    if not path.exists():
        path.write_text(f"# 日记 · {date_str}\n", encoding="utf-8")

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n## {time_str}\n{content.strip()}\n")

    return str(path)


def read_today() -> str:
    path = get_today_diary_path()
    if not path.exists():
        return "今天还没有日记。"
    return path.read_text(encoding="utf-8")


def search(query: str, limit: int = 10) -> list:
    diary_dir = get_diary_dir()
    results = []

    for md_file in sorted(diary_dir.glob("*.md"), reverse=True):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        if query.lower() not in content.lower():
            continue

        lines = content.split("\n")
        snippets = []
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                snippets.append("\n".join(lines[start:end]).strip())
                if len(snippets) >= 3:
                    break

        results.append({"date": md_file.stem, "snippets": snippets})
        if len(results) >= limit:
            break

    return results


def append_to_story(content: str) -> str:
    story_file = get_story_file()
    story_file.parent.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n---\n\n## 日记 · {date_str}\n\n{content.strip()}\n"

    with open(story_file, "a", encoding="utf-8") as f:
        f.write(entry)

    return str(story_file)
