/**
 * TTS 配音生成模块
 *
 * 方式一：edge-tts（免费，但某些网络环境可能不可达）
 *   安装：pip install edge-tts
 *   用法：node tts-generate.js
 *
 * 方式二：小米 MiMo TTS（需 API Key，更稳定）
 *   创建 tts-config.json: { "apiKey": "sk-xxx", "voice": "alloy" }
 *   用法：node tts-generate.js --mimo
 *
 * 输入：tts-lines.json — 台词列表

const fs = require('fs');
const path = require('path');
const { execSync, exec } = require('child_process');

const LINES_PATH = './tts-lines.json';
const OUTPUT_DIR = './assets/tts';

// ============ Config ============

function loadLines() {
  if (!fs.existsSync(LINES_PATH)) {
    console.error(`[TTS] 未找到 ${LINES_PATH}`);
    console.error(`  格式: [{ "text": "...", "start": 0, "duration": 2.5 }]`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(LINES_PATH, 'utf8'));
}

// ============ edge-tts ============

function getEdgeTtsBin() {
  const candidates = [
    'edge-tts',
    'C:/Users/16560/AppData/Local/hermes/hermes-agent/venv/Scripts/edge-tts',
    '/c/Users/16560/AppData/Local/hermes/hermes-agent/venv/Scripts/edge-tts',
  ];
  for (const c of candidates) {
    try {
      execSync(`"${c}" --help >nul 2>&1`, { shell: true });
      return c;
    } catch (_) {}
  }
  return 'edge-tts'; // 最后尝试 PATH
}

async function callEdgeTTS(text, voice, outputPath) {
  return new Promise((resolve, reject) => {
    const bin = getEdgeTtsBin();
    const rate = process.env.TTS_RATE || '+0%';
    const cmd = `"${bin}" --text "${text.replace(/["]/g, '\\"')}" --voice "${voice}" --rate "${rate}" --write-media "${outputPath}"`;
    exec(cmd, { shell: true, timeout: 30000, env: { ...process.env, HTTP_PROXY: 'http://127.0.0.1:7897', HTTPS_PROXY: 'http://127.0.0.1:7897' } }, (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

// ============ Main ============

async function main() {
  const lines = loadLines();

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // 检测可用语音
  let voice = 'zh-CN-XiaoxiaoNeural';
  try {
    const bin = getEdgeTtsBin();
    const voices = execSync(`"${bin}" --list-voices`, { shell: true }).toString();
    const zhVoices = voices.split('\n').filter(v => v.includes('zh-CN'));
    if (zhVoices.length > 0) {
      // 优先 Xiaochen (男声), 其次 Xiaoxiao (女声)
      const preferred = zhVoices.find(v => v.includes('Xiaochen')) || zhVoices[0];
      voice = preferred.trim().split(/\s+/)[0];
    }
  } catch (_) {}

  console.log(`[TTS] 使用语音: ${voice}`);
  console.log(`[TTS] 开始生成 ${lines.length} 句配音...\n`);

  let audioTags = [];
  let totalSize = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const filename = `tts_${String(i).padStart(3, '0')}.wav`;
    const filepath = path.join(OUTPUT_DIR, filename);
    const displayText = line.text.length > 30 ? line.text.slice(0, 30) + '...' : line.text;

    process.stdout.write(`  [${i + 1}/${lines.length}] "${displayText}"... `);

    try {
      await callEdgeTTS(line.text, voice, filepath);
      const stat = fs.statSync(filepath);
      totalSize += stat.size;

      const duration = line.duration || Math.max(2, line.text.length * 0.12);
      audioTags.push(
        `<audio class="clip" data-start="${line.start}" data-duration="${duration}" ` +
        `data-track-index="${i}" data-has-audio="true" data-volume="1.0" src="${filepath}"></audio>`
      );

      console.log(`${(stat.size / 1024).toFixed(1)}KB`);
    } catch (err) {
      console.error(`失败: ${err.message}`);
    }

    // 限速
    if (i < lines.length - 1) {
      await new Promise((r) => setTimeout(r, 300));
    }
  }

  console.log(`\n[TTS] 完成! 总大小: ${(totalSize / 1024 / 1024).toFixed(1)}MB`);
  console.log(`\n=== HTML <audio> 标签 ===\n`);
  console.log(audioTags.join('\n'));
  console.log(`\n=== BGM 标签 ===`);
  console.log(
    `<audio class="clip" data-start="0" data-duration="60" ` +
    `data-track-index="40" data-has-audio="true" data-volume="0.06" src="assets/bgm.mp3"></audio>`
  );
}

main().catch(console.error);
