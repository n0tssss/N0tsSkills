/**
 * TTS 配音生成模块 — 小米 MiMo API
 *
 * 用法：
 *   1. 在项目根目录创建 tts-config.json：
 *      { "apiKey": "your-key-here", "voice": "auto" }
 *   2. node tts-generate.js
 *
 * 输入：tts-lines.json — 台词列表
 *   [{ "text": "台词内容", "start": 0, "duration": 2.5 }]
 *
 * 输出：assets/tts/ 目录下的 WAV 文件
 *       以及 HTML <audio> 标签片段
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const CONFIG_PATH = './tts-config.json';
const LINES_PATH = './tts-lines.json';
const OUTPUT_DIR = './assets/tts';

// ============ Config ============

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    console.error(`[TTS] 未找到 ${CONFIG_PATH}，请创建：`);
    console.error(`  { "apiKey": "your-key", "voice": "auto" }`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

function loadLines() {
  if (!fs.existsSync(LINES_PATH)) {
    console.error(`[TTS] 未找到 ${LINES_PATH}`);
    console.error(`  格式: [{ "text": "...", "start": 0, "duration": 2.5 }]`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(LINES_PATH, 'utf8'));
}

// ============ MiMo TTS API ============

function callTTS(text, voice, apiKey) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'tts-1',
      input: text,
      voice: voice || 'alloy',
      response_format: 'wav',
      speed: 1.0,
    });

    const options = {
      hostname: 'api.xiaomimimo.com',
      path: '/v1/audio/speech',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'Content-Length': Buffer.byteLength(data),
      },
    };

    // 尝试通过代理连接
    const proxyHost = process.env.HTTP_PROXY || '127.0.0.1';
    const proxyPort = parseInt(process.env.HTTP_PROXY?.split(':')[2] || '7897');

    const req = http.request(
      { hostname: proxyHost, port: proxyPort, method: 'CONNECT', path: 'api.xiaomimimo.com:443' },
      (res) => {
        if (res.statusCode !== 200) {
          // 直连 fallback
          const directReq = https.request(options, (directRes) => {
            const chunks = [];
            directRes.on('data', (c) => chunks.push(c));
            directRes.on('end', () => resolve(Buffer.concat(chunks)));
          });
          directReq.on('error', reject);
          directReq.write(data);
          directReq.end();
          return;
        }
        const httpsReq = https.request({ ...options, host: 'api.xiaomimimo.com' }, (httpsRes) => {
          const chunks = [];
          httpsRes.on('data', (c) => chunks.push(c));
          httpsRes.on('end', () => resolve(Buffer.concat(chunks)));
        });
        httpsReq.on('error', reject);
        httpsReq.write(data);
        httpsReq.end();
      }
    );
    req.on('error', () => {
      // 直连 fallback
      const directReq = https.request(options, (directRes) => {
        const chunks = [];
        directRes.on('data', (c) => chunks.push(c));
        directRes.on('end', () => resolve(Buffer.concat(chunks)));
      });
      directReq.on('error', reject);
      directReq.write(data);
      directReq.end();
    });
    req.end();
  });
}

// ============ Main ============

async function main() {
  const config = loadConfig();
  const lines = loadLines();

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  console.log(`[TTS] 开始生成 ${lines.length} 句配音...`);

  let audioTags = [];
  let totalSize = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const filename = `tts_${String(i).padStart(3, '0')}.wav`;
    const filepath = path.join(OUTPUT_DIR, filename);
    const displayText = line.text.length > 30 ? line.text.slice(0, 30) + '...' : line.text;

    process.stdout.write(`  [${i + 1}/${lines.length}] "${displayText}"... `);

    try {
      const audioBuffer = await callTTS(line.text, config.voice || 'alloy', config.apiKey);
      fs.writeFileSync(filepath, audioBuffer);
      totalSize += audioBuffer.length;

      const duration = line.duration || Math.max(2, line.text.length * 0.12);
      audioTags.push(
        `<audio class="clip" data-start="${line.start}" data-duration="${duration}" ` +
        `data-track-index="${i}" data-has-audio="true" data-volume="1.0" src="${filepath}"></audio>`
      );

      console.log(`${(audioBuffer.length / 1024).toFixed(1)}KB`);
    } catch (err) {
      console.error(`失败: ${err.message}`);
    }

    // API 限速，间隔 500ms
    if (i < lines.length - 1) {
      await new Promise((r) => setTimeout(r, 500));
    }
  }

  // 输出结果
  console.log(`\n[TTS] 完成! 总大小: ${(totalSize / 1024 / 1024).toFixed(1)}MB`);
  console.log(`\n=== HTML <audio> 标签（粘贴到 index.html #root 内）===\n`);
  console.log(audioTags.join('\n'));
  console.log(`\n=== BGM 标签 ===`);
  console.log(
    `<audio class="clip" data-start="0" data-duration="60" ` +
    `data-track-index="40" data-has-audio="true" data-volume="0.06" src="assets/bgm.mp3"></audio>`
  );
}

main().catch(console.error);
