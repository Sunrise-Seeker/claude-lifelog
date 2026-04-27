#!/usr/bin/env node
// Content-aware lifelog capture hook.
// Fires when the user's prompt contains personal content signals, a farewell,
// OR as a 60-minute safety net — not blindly on message count.

const fs = require('fs');
const os = require('os');
const path = require('path');

const STATE_FILE = path.join(os.homedir(), '.lifelog', 'capture-state.json');
const FALLBACK_INTERVAL_MS = 60 * 60 * 1000; // 60 min safety net

// Personal content signal words — any match triggers capture consideration
const PERSONAL_KEYWORDS = [
  // Activities / events
  '今天', '昨天', '早上', '下午', '晚上',
  '去了', '做了', '写了', '看了', '聊了', '吃了', '参加了', '完成了', '开始了',
  // Opinions / thoughts
  '我觉得', '我认为', '感觉', '我发现', '说实话', '坦白说', '其实',
  // Emotions / state
  '焦虑', '开心', '高兴', '难过', '失落', '担心', '期待', '兴奋',
  '累了', '紧张', '郁闷', '烦', '无聊', '空洞', '崩溃', '后悔', '压力',
];

// Farewell signals — conversation is ending, always trigger
// Note: '好了' excluded — too common in non-farewell contexts
const FAREWELL_KEYWORDS = [
  '再见', '晚安', '去忙了', '谢了', '拜拜',
  '先这样', '就这样吧', '去睡了', '我先去', '告辞', '下线了',
];

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    return { lastCapture: 0 };
  }
}

function saveState(state) {
  const dir = path.dirname(STATE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(state), 'utf8');
}

function containsAny(text, keywords) {
  return keywords.some(kw => text.includes(kw));
}

const data = JSON.parse(fs.readFileSync(0, 'utf8').trim() || '{}'); // fd 0 = stdin, cross-platform
const prompt = (data.prompt || '').toLowerCase();

const state = loadState();
const now = Date.now();
const timeSinceLast = now - (state.lastCapture || 0);

const isFarewell = containsAny(prompt, FAREWELL_KEYWORDS);
const hasPersonalContent = containsAny(prompt, PERSONAL_KEYWORDS);
const isFallback = timeSinceLast >= FALLBACK_INTERVAL_MS;

const shouldCapture = isFarewell || hasPersonalContent || isFallback;

if (shouldCapture) {
  state.lastCapture = now;
  saveState(state);

  const reason = isFarewell ? '对话即将结束' : hasPersonalContent ? '检测到个人内容' : '定时兜底';
  const output = {
    hookSpecificOutput: {
      hookEventName: 'UserPromptSubmit',
      additionalContext:
        `[lifelog-capture:${reason}] 请在本轮回复结束前判断是否有值得记录的个人内容` +
        '（今天的事、心情、想法）。有则调用相应工具写入日记；纯技术内容跳过。',
    },
  };
  process.stdout.write(JSON.stringify(output));
} else {
  saveState(state);
}
