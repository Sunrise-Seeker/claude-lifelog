# /lifelog-search — 搜索日记

## 使用方式

```
/lifelog-search [关键词]
/lifelog-search [关键词] --type event|thought|state
/lifelog-search [关键词] --from 2026-04-01
/lifelog-search [关键词] --from 2026-04-01 --to 2026-04-30
```

## 执行

解析用户的参数，调用：

```
lifelog_search(
  query="关键词",
  category="event|thought|state 或不填",
  date_from="YYYY-MM-DD 或不填",
  date_to="YYYY-MM-DD 或不填"
)
```

展示结果，每条结果显示日期和匹配片段。没有结果时告知用户并建议换个关键词。
