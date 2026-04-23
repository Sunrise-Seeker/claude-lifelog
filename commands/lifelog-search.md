# /lifelog-search — 搜索日记

## 使用方式

```
/lifelog-search [关键词]
/lifelog-search [关键词] --type event
/lifelog-search [关键词] --type thought
/lifelog-search [关键词] --type state
/lifelog-search [关键词] --from 2026-04-01
/lifelog-search [关键词] --from 2026-04-01 --to 2026-04-30
```

## 执行

解析用户输入，调用：

```python
lifelog_search(
    query="关键词",
    category="event|thought|state 或不填（全部）",
    date_from="YYYY-MM-DD 或不填",
    date_to="YYYY-MM-DD 或不填",
    limit=10
)
```

## 结果展示

- 每条结果显示：日期 + 匹配的上下文片段
- 没有结果时，建议换个关键词或扩大时间范围
- 结果超过 10 条，提示用户可以用 `--from` 缩小范围

## 示例

```
/lifelog-search 焦虑                    # 全局搜"焦虑"
/lifelog-search PINN --type thought     # 只在「想法」里搜 PINN
/lifelog-search 论文 --from 2026-04-01  # 4月以来提到论文的记录
```
