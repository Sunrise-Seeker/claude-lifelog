from pathlib import Path
from datetime import datetime, date, timedelta
from .paths import get_diary_dir, get_story_file, get_today_diary_path

MAX_ENTRY_LEN = 500  # 单条记录最大字符数（超过则截断并提示）

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

def _validate(content: str, label: str = "内容") -> str:
    content = content.strip()
    if not content:
        raise ValueError(f"{label}不能为空")
    if len(content) > MAX_ENTRY_LEN:
        content = content[:MAX_ENTRY_LEN] + "……（已截断）"
    return content


def _tokenize(text: str) -> set:
    """Character-level tokens for CJK; alphanumeric for ASCII. Works for mixed text."""
    tokens = []
    for ch in text.lower():
        if '一' <= ch <= '鿿':  # CJK Unified Ideographs
            tokens.append(ch)
        elif ch.isalnum():
            tokens.append(ch)
    return set(tokens)


def _is_duplicate(existing_text: str, new_content: str, threshold: float = 0.55) -> bool:
    """Return True if new_content is substantially similar to any line in existing_text."""
    if not existing_text.strip():
        return False
    new_tokens = _tokenize(new_content)
    if len(new_tokens) < 4:
        return False
    for line in existing_text.split("\n"):
        line = line.strip()
        if len(line) < 5:
            continue
        line_tokens = _tokenize(line)
        if len(line_tokens) < 3:
            continue
        union = new_tokens | line_tokens
        if union and len(new_tokens & line_tokens) / len(union) >= threshold:
            return True
    return False


def write_event(content: str) -> str | None:
    """Returns file path if written, None if duplicate."""
    content = _validate(content, "记事")
    path = get_today_diary_path()
    _ensure_today(path, date.today().strftime("%Y-%m-%d"))
    existing = _extract_section(path.read_text(encoding="utf-8"), SECTIONS["event"])
    if _is_duplicate(existing, content):
        return None
    time_str = datetime.now().strftime("%H:%M")
    _append_to_section(path, SECTIONS["event"], f"- **{time_str}** {content}")
    return str(path)


def _append_to_thought_topic(path: Path, topic: str, additional: str) -> None:
    """Append additional content under an existing ### topic heading."""
    text = path.read_text(encoding="utf-8")
    sub_marker = f"### {topic}"
    if sub_marker not in text:
        return
    sub_start = text.index(sub_marker) + len(sub_marker)
    after = text[sub_start:]
    ends = [after.find(m) for m in ("\n### ", "\n## ") if after.find(m) != -1]
    if ends:
        insert_at = sub_start + min(ends)
        new_text = text[:insert_at].rstrip() + f"\n\n{additional}\n" + text[insert_at:]
    else:
        new_text = text.rstrip() + f"\n\n{additional}\n"
    path.write_text(new_text, encoding="utf-8")


def write_thought(topic: str, content: str) -> str | None:
    """Returns file path if written, None if duplicate."""
    topic = _validate(topic, "想法主题")
    content = _validate(content, "想法内容")
    path = get_today_diary_path()
    _ensure_today(path, date.today().strftime("%Y-%m-%d"))
    existing = _extract_section(path.read_text(encoding="utf-8"), SECTIONS["thought"])
    if _is_duplicate(existing, content):
        return None
    if f"### {topic}" in existing:
        # Same topic exists but different content — append under existing heading
        _append_to_thought_topic(path, topic, content)
    else:
        _append_to_section(path, SECTIONS["thought"], f"### {topic}\n{content}")
    return str(path)


def write_state(content: str) -> str | None:
    """Returns file path if written, None if duplicate."""
    content = _validate(content, "心理状态")
    path = get_today_diary_path()
    _ensure_today(path, date.today().strftime("%Y-%m-%d"))
    existing = _extract_section(path.read_text(encoding="utf-8"), SECTIONS["state"])
    if _is_duplicate(existing, content):
        return None
    time_str = datetime.now().strftime("%H:%M")
    _append_to_section(path, SECTIONS["state"], f"**{time_str}** {content}")
    return str(path)


# ── Read ──────────────────────────────────────────────────────────────────────

def read_today() -> str:
    path = get_today_diary_path()
    if not path.exists():
        return "今天还没有日记。"
    return path.read_text(encoding="utf-8")


def read_recent(days: int = 3) -> str:
    diary_dir = get_diary_dir()
    cutoff = date.today() - timedelta(days=days)
    entries = []
    for md_file in sorted(diary_dir.glob("*.md"), reverse=True):
        try:
            file_date = date.fromisoformat(md_file.stem)
        except ValueError:
            continue
        if file_date < cutoff:
            break
        try:
            entries.append((md_file.stem, md_file.read_text(encoding="utf-8")))
        except Exception:
            continue
    if not entries:
        return f"最近 {days} 天没有日记记录。"
    return "\n\n---\n\n".join(f"# {d}\n\n{text.strip()}" for d, text in entries)


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

    # 预解析日期过滤（用 date 对象而不是字符串比较）
    from_date = date.fromisoformat(date_from) if date_from else None
    to_date = date.fromisoformat(date_to) if date_to else None

    for md_file in sorted(diary_dir.glob("*.md"), reverse=True):
        date_str = md_file.stem
        try:
            file_date = date.fromisoformat(date_str)
        except ValueError:
            continue  # 跳过非日期命名的文件

        if from_date and file_date < from_date:
            continue
        if to_date and file_date > to_date:
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
