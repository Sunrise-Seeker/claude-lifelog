# /lifelog-config — 查看或修改存储路径

## 使用方式

```
/lifelog-config                              # 查看当前路径配置
/lifelog-config --diary /new/diary/dir      # 修改每日日记目录
/lifelog-config --story /new/story.md       # 修改人生故事文件路径
```

## 执行

```python
# 查看
lifelog_config(show=True)

# 修改日记目录
lifelog_config(diary_dir="/path/to/新目录")

# 修改人生故事路径
lifelog_config(story_file="/path/to/人生故事.md")
```

## 配置优先级

```
环境变量（LIFELOG_DIARY_DIR / LIFELOG_STORY_FILE）
    > ~/.lifelog/config.json（此命令修改的地方）
        > 默认值（~/.lifelog/日记 / ~/.lifelog/人生故事.md）
```

## 注意

- 修改后立即生效，无需重启
- 修改的是 `~/.lifelog/config.json`，如果同时设置了环境变量，环境变量优先级更高
