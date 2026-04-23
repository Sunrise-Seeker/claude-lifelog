# claude-lifelog

AI-powered personal lifelog plugin for Claude Code. Captures daily thoughts, feelings, and life events from conversations — so your brain doesn't have to.

## What it does

- **Auto-captures** personal content from conversations (daily events, feelings, ideas)
- **Two-track storage**: daily diary (small things) + life story (major events)
- **Proactive**: Claude decides when to record, you don't have to ask
- **Markdown-first**: human-readable files, Git-friendly

## Storage

| Content | Location |
|---------|----------|
| Daily thoughts & feelings | `~/.lifelog/日记/YYYY-MM-DD.md` |
| Major life events | Configured via `LIFELOG_STORY_FILE` env var |

## Installation

```bash
cd claude-lifelog
uv sync
claude /plugin install .
```

## Configuration (via environment variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `LIFELOG_DIARY_DIR` | `~/.lifelog/日记` | Directory for daily diary files |
| `LIFELOG_STORY_FILE` | `~/.lifelog/人生故事.md` | Path to the life story file |

## Commands

| Command | Description |
|---------|-------------|
| `/lifelog` | Manually record a thought or event |
| `/lifelog-today` | View today's diary entries |

## MCP Tools

| Tool | Description |
|------|-------------|
| `lifelog_write` | Write an entry to today's diary |
| `lifelog_read_today` | Read today's diary |
| `lifelog_search` | Search across all diary files |
| `lifelog_append_story` | Append a major life event to the story file |

## How it works

1. A **hook** fires every 5 messages (or 30 min), signaling Claude to consider recording
2. The **lifelog-capture skill** makes Claude proactively judge whether conversation content is worth saving
3. Claude calls `lifelog_write` silently and mentions it at the end of the reply

## License

MIT
