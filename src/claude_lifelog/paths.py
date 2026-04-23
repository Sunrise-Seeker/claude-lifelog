import os
from pathlib import Path
from datetime import date


def get_diary_dir() -> Path:
    env = os.environ.get("LIFELOG_DIARY_DIR")
    if env:
        return Path(env)
    return Path.home() / ".lifelog" / "日记"


def get_story_file() -> Path:
    env = os.environ.get("LIFELOG_STORY_FILE")
    if env:
        return Path(env)
    return Path.home() / ".lifelog" / "人生故事.md"


def get_today_diary_path() -> Path:
    diary_dir = get_diary_dir()
    diary_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    return diary_dir / f"{today}.md"
