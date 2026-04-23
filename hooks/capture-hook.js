#!/usr/bin/env node
// Tracks conversation progress and signals Claude to consider capturing lifelog entries.
// Fires when: 5+ messages have passed since last capture, OR 30+ minutes elapsed.

const fs = require('fs');
const os = require('os');
const path = require('path');

const STATE_FILE = path.join(os.homedir(), '.lifelog', 'capture-state.json');
const MESSAGE_THRESHOLD = 5;
const TIME_THRESHOLD_MS = 30 * 60 * 1000;

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    return { lastCapture: 0, messageCount: 0 };
  }
}

function saveState(state) {
  const dir = path.dirname(STATE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(state), 'utf8');
}

const state = loadState();
state.messageCount = (state.messageCount || 0) + 1;

const now = Date.now();
const timeSinceLast = now - (state.lastCapture || 0);
const shouldCapture =
  state.messageCount >= MESSAGE_THRESHOLD || timeSinceLast >= TIME_THRESHOLD_MS;

if (shouldCapture) {
  state.lastCapture = now;
  state.messageCount = 0;
  saveState(state);

  // Output signal to Claude via additionalContext
  const output = {
    hookSpecificOutput: {
      hookEventName: 'UserPromptSubmit',
      additionalContext:
        '[lifelog-capture] 对话已进行一段时间。请在本轮回复结束前，' +
        '判断是否有值得记录的个人内容（今天的事、心情、想法）。' +
        '如果有，调用 lifelog_write 写入日记；如果本次对话与个人无关，跳过即可。',
    },
  };
  process.stdout.write(JSON.stringify(output));
} else {
  saveState(state);
}
