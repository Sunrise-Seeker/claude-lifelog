from mcp.server.fastmcp import FastMCP
from . import journal

mcp = FastMCP("claude-lifelog")


@mcp.tool()
def lifelog_write(content: str) -> str:
    """记录一条日记——今天发生的事、想法、感受、心理状态。写入当天的日记文件。"""
    path = journal.write_entry(content)
    return f"✓ 已写入：{path}"


@mcp.tool()
def lifelog_read_today() -> str:
    """读取今天的日记内容。"""
    return journal.read_today()


@mcp.tool()
def lifelog_search(query: str, limit: int = 10) -> str:
    """在所有日记中搜索关键词，返回匹配的日期和内容片段。"""
    results = journal.search(query, limit)
    if not results:
        return f"没有找到包含「{query}」的记录。"

    lines = []
    for r in results:
        lines.append(f"**{r['date']}**")
        for snippet in r["snippets"]:
            for s in snippet.split("\n"):
                lines.append(f"  {s}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def lifelog_append_story(content: str) -> str:
    """将重大人生事件、重要感悟、转折点追加到人生故事文件。
    仅用于真正重要的事，不是日常流水。"""
    path = journal.append_to_story(content)
    return f"✓ 已追加到人生故事：{path}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
