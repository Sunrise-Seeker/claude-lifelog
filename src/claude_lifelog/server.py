from mcp.server.fastmcp import FastMCP
from . import journal, config
from .paths import get_diary_dir, get_story_file

mcp = FastMCP("claude-lifelog")


@mcp.tool()
def lifelog_write_event(content: str) -> str:
    """记录一条「记事」——今天做了什么、发生了什么，写成简洁的事件条目。"""
    path = journal.write_event(content)
    return f"✓ 记事已写入：{path}"


@mcp.tool()
def lifelog_write_thought(topic: str, content: str) -> str:
    """记录一个「想法」——对某个话题（论文/方向/某人/某事）的看法、分析和观点。
    topic: 想法的主题标题，如「关于 PINN 的收敛性」
    content: 具体内容
    """
    path = journal.write_thought(topic, content)
    return f"✓ 想法已写入：{path}"


@mcp.tool()
def lifelog_write_state(content: str) -> str:
    """记录「心理状态」——今天的情绪、感受、焦虑或期待。"""
    path = journal.write_state(content)
    return f"✓ 心理状态已写入：{path}"


@mcp.tool()
def lifelog_read_today() -> str:
    """读取今天的完整日记。"""
    return journal.read_today()


@mcp.tool()
def lifelog_search(
    query: str,
    category: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 10,
) -> str:
    """在日记中搜索关键词。
    category: 'event'(记事) | 'thought'(想法) | 'state'(心理状态) | 不填=全部搜索
    date_from / date_to: 'YYYY-MM-DD' 格式，可只填其一
    limit: 最多返回结果数（默认10）
    """
    results = journal.search(query, category, date_from, date_to, limit)
    if not results:
        scope = f"「{category}」分类中" if category else "日记中"
        return f"在{scope}没有找到包含「{query}」的记录。"

    lines = []
    for r in results:
        lines.append(f"**{r['date']}**")
        for snippet in r["snippets"]:
            for s in snippet.split("\n"):
                lines.append(f"  {s}")
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def lifelog_summary(period: str = "week") -> str:
    """生成一段时间内的日记摘要。
    period: 'week'(近7天) | 'month'(近30天)
    """
    return journal.summary(period)


@mcp.tool()
def lifelog_append_story(content: str) -> str:
    """将重大人生事件、重要感悟、转折点追加到「人生故事」文件。
    仅用于真正值得长期保留的事，不是日常流水。
    """
    path = journal.append_to_story(content)
    return f"✓ 已追加到人生故事：{path}"


@mcp.tool()
def lifelog_config(
    diary_dir: str = None,
    story_file: str = None,
    show: bool = False,
) -> str:
    """查看或修改日记文件的存储路径。
    diary_dir: 设置每日日记目录（绝对路径）
    story_file: 设置人生故事文件路径（绝对路径）
    show: 传 True 可查看当前配置
    """
    if diary_dir:
        config.set_value("diary_dir", diary_dir)
    if story_file:
        config.set_value("story_file", story_file)

    current = config.load()
    return (
        f"当前配置：\n"
        f"  每日日记目录：{get_diary_dir()}\n"
        f"  人生故事文件：{get_story_file()}\n\n"
        f"配置文件位置：{config.CONFIG_FILE}\n"
        f"（env 变量 LIFELOG_DIARY_DIR / LIFELOG_STORY_FILE 优先级更高）"
    )


def main():
    mcp.run()


if __name__ == "__main__":
    main()
