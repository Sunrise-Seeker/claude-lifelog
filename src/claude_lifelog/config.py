import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".lifelog" / "config.json"


def load() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save(data: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get(key: str, default=None):
    return load().get(key, default)


def set_value(key: str, value: str) -> None:
    data = load()
    data[key] = value
    save(data)
