# claude-lifelog

> 你的 AI 外置大脑。从与 Claude 的对话中自动捕获日常事件、想法和心理状态，分类写入 Markdown 日记文件。

---

## 为什么需要这个

大脑的缓存很小。今天做了什么、突然闪过什么想法、现在是什么心情——这些如果不记下来，明天就忘了。

claude-lifelog 让 Claude 充当你的外置记忆：**你只管和 Claude 聊，它负责把值得记的内容悄悄写进日记**，不需要你手动说"帮我记一下"。

---

## 三类内容

| 类型 | emoji | 什么时候写 | 例子 |
|------|-------|-----------|------|
| **记事** | 📋 | 今天做了什么、发生了什么 | "让 Claude 搭了个日记插件" |
| **想法** | 💭 | 对某话题的看法、分析、观点 | "关于某篇论文方法的思考" |
| **心理状态** | 🌡 | 情绪、感受、整体状态 | "有点焦虑，在等 5 月的消息" |

一次对话可能同时触发多类。

另外保留了**人生故事**轨道（单独文件），专门记重大事件和人生转折点。

---

## 每日文件格式

```markdown
---
date: 2026-04-23
tags: []
---

# 2026-04-23

## 📋 记事

- **15:25** 让 Claude 搭建了 claude-lifelog 插件，用 Python 写的 MCP server

## 💭 想法

### 关于某方法的适用范围
在特定场景下这个方法的局限性很明显，换个思路可能更实际……

## 🌡 心理状态

**20:30** 有点焦虑，但今天干活效率还不错
```

---

## 自动捕获机制

claude-lifelog 有两层自动化：

1. **Hook（内容感知触发）**：每条消息提交时，Hook 脚本检测以下信号，任一满足即向 Claude 注入捕获提醒：
   - **个人关键词**：消息含情绪词（焦虑、开心…）、活动描述（今天、去了、完成了…）、观点词（我觉得、其实…）
   - **告别信号**：用户说"好了""晚安""去忙了"等，表示对话即将结束
   - **兜底计时**：距上次捕获超过 60 分钟（纯技术对话的最后安全网）

   纯技术讨论（debug、查文档、写代码）全程不触发，不浪费 token。

2. **Skill（主动判断）**：`lifelog-capture` skill 让 Claude 始终作为背景观察者——只要对话中出现个人内容，无论 Hook 是否触发，都会在回复末尾主动写入

写入成功后，Claude 会在回复末尾附上：`📝 已记入今日日记。`

---

## 安装

```bash
# 1. 克隆项目
git clone https://github.com/Sunrise-Seeker/claude-lifelog.git
cd claude-lifelog

# 2. 安装 Python 依赖
uv sync

# 3. 注册 MCP 服务器（按实际路径修改）
claude mcp add-json lifelog '{
  "type": "stdio",
  "command": "uv",
  "args": ["run", "--project", "/path/to/claude-lifelog", "python", "-m", "claude_lifelog.server"],
  "env": {
    "LIFELOG_STORY_FILE": "/path/to/人生故事.md",
    "LIFELOG_DIARY_DIR": "/path/to/.lifelog/日记"
  }
}' -s user

# 4. 复制 skill 到全局目录
cp -r skills/lifelog-capture ~/.claude/skills/

# 5. 复制 hook 脚本
cp hooks/capture-hook.js ~/.claude/lifelog-capture-hook.js

# 6. 在 ~/.claude/settings.json 的 hooks.UserPromptSubmit 中加入：
# {"type": "command", "command": "node ~/.claude/lifelog-capture-hook.js"}
```

---

## 路径配置

优先级：**环境变量 > config.json > 默认值**

### 方式一：环境变量（在 MCP 注册时设置）

| 变量名 | 说明 |
|--------|------|
| `LIFELOG_DIARY_DIR` | 每日日记目录（默认 `~/.lifelog/日记`） |
| `LIFELOG_STORY_FILE` | 人生故事文件路径（默认 `~/.lifelog/人生故事.md`） |

### 方式二：运行时修改（无需重启）

```
让 Claude 调用 lifelog_config(diary_dir="/new/path", story_file="/new/file.md")
```

配置持久化在 `~/.lifelog/config.json`。

---

## 手动命令

| 命令 | 功能 |
|------|------|
| `/lifelog [内容]` | 立即记录一条，自动分类 |
| `/lifelog-today` | 查看今天的日记 |
| `/lifelog-search [关键词]` | 全局搜索 |
| `/lifelog-summary` | 近 7 天摘要 |
| `/lifelog-summary month` | 近 30 天摘要 |

---

## MCP 工具（给 Claude 用的）

| 工具 | 说明 |
|------|------|
| `lifelog_write_event(content)` | 写记事（做了什么） |
| `lifelog_write_thought(topic, content)` | 写想法（带主题标题） |
| `lifelog_write_state(content)` | 写心理状态（情绪感受） |
| `lifelog_read_today()` | 读今天的日记 |
| `lifelog_search(query, category?, date_from?, date_to?)` | 搜索，支持分类和时间过滤 |
| `lifelog_summary(period)` | 摘要（week \| month） |
| `lifelog_append_story(content)` | 追加到人生故事（重大事件） |
| `lifelog_config(diary_dir?, story_file?, show?)` | 查看/修改路径配置 |

---

## 存储结构

```
~/.lifelog/
├── 日记/
│   ├── 2026-04-22.md
│   ├── 2026-04-23.md
│   └── ...
└── config.json          ← 可选，运行时配置

（人生故事文件路径由配置决定，默认 ~/.lifelog/人生故事.md）
```

