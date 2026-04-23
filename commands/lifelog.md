# /lifelog — 手动记录一条日记

## 使用方式

```
/lifelog [内容]                    ← 自动判断类别
/lifelog --event [内容]            ← 强制写入「记事」
/lifelog --thought [主题] [内容]   ← 强制写入「想法」
/lifelog --state [内容]            ← 强制写入「心理状态」
```

## 执行逻辑

1. **解析参数**
   - 带 `--event / --thought / --state` 标志：直接写入对应类别
   - 无标志：根据内容自动判断（事件 → event，看法 → thought，情绪 → state）

2. **调用工具**

   | 类别 | 工具 |
   |------|------|
   | 记事 | `lifelog_write_event(content)` |
   | 想法 | `lifelog_write_thought(topic, content)` |
   | 心理状态 | `lifelog_write_state(content)` |

3. **确认**：告知用户已写入，显示写入的类别。

## 注意

- 不要记录技术内容、代码、报错
- 用第一人称，口语化，保留细节
