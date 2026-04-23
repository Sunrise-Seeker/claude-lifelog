from pathlib import Path
from datetime import datetime, date, timedelta
from .paths import get_diary_dir, get_story_file, get_today_diary_path

SECTIONS = {
    "event":   "📋 记事",
    "thought": "💭 想法",
    "state":   "🌡 心理状态",
}

FILE_TEMPLATE = """\
---
date: {date}
tags: []
---

# {date}

## 📋 记事

## 💭 想法

## 🌡 心理状态

"""


def _ensure_today(path: Path, date_str: str) -> None:
    if not path.exists():
        path.write_text(FILE_TEMPLATE.format(date=date_str), encoding="utf-8")


def _append_to_section(path: Path, section_header: str, new_content: str) -> None:
    """Insert new_content inside the named section, before the next ## heading."""
    text = path.read_text(encoding="utf-8")
    marker = f"## {section_header}"

    if marker not in text:
        text = text.rstrip() + f"\n\n{marker}\n\n{new_content}\n"
        path.write_text(text, encoding="utf-8")
        return

    idx = text.index(marker) + len(marker)
    tail = text[idx:]
    next_sec = tail.find("\n## ")

    if next_sec == -1:
        new_text = text[:idx] + tail.rstrip() + f"\n\n{new_content}\n"
    else:
        new_text = (
            text[:idx]
            + tail[:next_sec].rstrip()
            + f"\n\n{new_content}\n"
            + tail[next_sec:]
        )

    path.write_text(new_text, encoding="utf-8")


def _extract_section(text: str, section_header: str) -> str:
    marker = f"## {section_header}"
    if marker not in text:
        return ""
    idx = text.index(marker) + len(marker)
    tail = text[idx:]
    next_sec = tail.find("\n## ")
    return tail[:next_sec].strip() if next_sec != -1 else tail.strip()


# ── Write helpers ─────────────────────────────────────────────────────────────

def write_event(content: str) -> str:
    path = get_today_diary_path()
    date_str = date.today().strftime("%Y-%m-%d")
    _ensure_today(path, date_str)
    time_str = datetime.now().strftime("%H:%M")
    _append_to_section(path, SECTIONS["event"], f"- **{time_str}** {content.strip()}")
    return str(path)


def write_thought(topic: str, content: str) -> str:
    path = get_today_diary_path()
    date_str = date.today().strftime("%Y-%m-%d")
    _ensure_today(path, date_str)
    entry = f"### {topic.strip()}\n{content.strip()}"
    _append_to_section(path, SECTIONS["thought"], entry)
    return str(path)


def write_state(content: str) -> str:
    path = get_today_diary_path()
    date_str = date.today().strftime("%Y-%m-%d")
    _ensure_today(path, date_str)
    time_str = datetime.now().strftime("%H:%M")
    _append_to_section(path, SECTIONS["state"], f"**{time_str}** {content.strip()}")
    return str(path)


# ── Read ──────────────────────────────────────────────────────────────────────

def read_today() -> str:
    path = get_today_diary_path()
    if not path.exists():
        return "今天还没有日记。"
    return path.read_text(encoding="utf-8")


# ── Search ────────────────────────────────────────────────────────────────────

def search(
    query: str,
    category: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 10,
) -> list:
    diary_dir = get_diary_dir()
    results = []

    for md_file in sorted(diary_dir.glob("*.md"), reverse=True):
        date_str = md_file.stem

        if date_from and date_str < date_from:
            continue
        if date_to and date_str > date_to:
            continue

        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        # Optionally restrict to one section
        search_text = text
        if category and category in SECTIONS:
            search_text = _extract_section(text, SECTIONS[category])

        if not search_text or query.lower() not in search_text.lower():
            continue

        lines = search_text.split("\n")
        snippets = []
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                ctx = lines[max(0, i - 1): i + 3]
                snippet = "\n".join(ctx).strip()
                if snippet and snippet not in snippets:
                    snippets.append(snippet)
                if len(snippets) >= 3:
                    break

        if snippets:
            results.append({"date": date_str, "snippets": snippets})
            if len(results) >= limit:
                break

    return results


# ── Summary ───────────────────────────────────────────────────────────────────

def summary(period: str = "week") -> str:
    diary_dir = get_diary_dir()
    days = 30 if period in ("month", "本月", "上个月") else 7
    cutoff = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")

    entries = []
    for md_file in sorted(diary_dir.glob("*.md"), reverse=True):
        if md_file.stem < cutoff:
            break
        try:
            entries.append((md_file.stem, md_file.read_text(encoding="utf-8")))
        except Exception:
            continue

    if not entries:
        return f"最近 {days} 天没有日记记录。"

    lines = [f"## 近 {days} 天摘要（共 {len(entries)} 天有记录）\n"]
    for date_str, text in entries:
        lines.append(f"### {date_str}")
        for cat_key, cat_name in SECTIONS.items():
            section = _extract_section(text, cat_name)
            if section:
                brief = section[:120].replace("\n", " ").strip()
                if len(section) > 120:
                    brief += "…"
                lines.append(f"**{cat_name}**：{brief}")
        lines.append("")

    return "\n".join(lines)


# ── Life story ────────────────────────────────────────────────────────────────

def append_to_story(content: str) -> str:
    story_file = get_story_file()
    story_file.parent.mkdir(parents=True, exist_ok=True)
    date_str = date.today().strftime("%Y-%m-%d")
    entry = f"\n---\n\n## 日记 · {date_str}\n\n{content.strip()}\n"
    with open(story_file, "a", encoding="utf-8") as f:
        f.write(entry)
    return str(story_file)
