---
name: short-video-gen
description: 短视频生成 — 分析→脚本→设计→实现 四阶段流水线，输出高质量 4:3+3:4 双比例视频
argument-hint: "<视频主题描述>"
level: 4
---

# 短视频生成

四阶段专业流水线：**分析 → 脚本 → 设计 → 实现**。每阶段有明确交付物，脚本需用户确认后才进入实现。

## 工作目录

```
D:\视频生成\
  .config.json           # 风格配置
  .history.json          # 生成记录
  <project>/
    分析报告.md           # Phase 1 输出
    视频脚本.md           # Phase 2 输出（用户确认）
    设计稿.md             # Phase 3 输出
    素材/                 # 截图、图片、BGM
    43/                   # 4:3 横屏项目
    34/                   # 3:4 竖屏项目
    43-横屏.mp4
    34-竖屏.mp4
```

---

## 首次配置

`.config.json` 不存在时，一次性打印全部选项，等用户输入序号（不用 AskUserQuestion 工具）：

```
🎬 短视频生成 — 首次配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1. 视频时长】 [0] 自动判断（根据题材智能决定） [1] 15秒 [2] 30秒 [3] 60秒 [4] 自定义秒数
【2. 背景音乐】 [1] 自动合成 [2] 不加 [3] 手动提供 MP3
【3. 视觉配色】 [1] 赛博朋克 [2] 极简白 [3] 暗金 [4] 活力橙蓝
                [5] 暗夜绿 [6] 霓虹粉紫 [7] 纯黑暴力 [8] 暖橘日落
                [9] 冰川蓝 [10] 红黑警戒
【4. 文案风格】 [1] 一句话暴力 [2] 痛点轰炸 [3] 颠覆认知
【5. 内容侧重】 [1] 核心亮点 [2] 功能罗列
【6. TTS 配音】 [1] 小米 MiMo TTS（需 API Key） [2] 暂不加配音

回复格式：2-1, 3-2, 4-3, 5-1, 6-1  （跳过1就是自动判断时长）
```

如果用户选了 TTS，额外询问：

```
🔑 小米 MiMo TTS 配置

请提供你的 MIMO_API_KEY（在 https://platform.xiaomimimo.com 控制台获取）：
> [等待用户输入]

请选择语音方式：
  [1] 预置语音 — 直接用现成的声音（推荐，最快）
  [2] 语音设计 — 用文字描述你想要的声音（如"25岁女生，温柔但有力量感"）
  [3] 语音克隆 — 上传一段音频，复刻那个人的声音

> [等待用户输入]
```

**选 1 — 预置语音**：
```
请选择预置语音：
  [1] 冰糖 — 甜美女声（推荐）
  [2] 茉莉 — 温柔女声
  [3] 苏打 — 阳光男声
  [4] 白桦 — 沉稳男声
  [5] Mia — 英文女声
  [6] Chloe — 英文女声
  [7] Milo — 英文男声
  [8] Dean — 英文男声
```

**选 2 — 语音设计**：
```
请用 1-4 句话描述你想要的声音，可以参考这些维度：
  · 性别和年龄 — "25 岁左右的女生"
  · 音色质感 — "温暖但干脆，不带气泡音"
  · 情绪基调 — "自信、专业，但不过于严肃"
  · 语速节奏 — "正常语速偏快，断句利落"

> [等待用户输入描述]
```

**选 3 — 语音克隆**：
```
请提供一段 10-30 秒的音频样本（MP3 或 WAV）：
  · 最好是干净的人声，没有背景音乐和噪音
  · 放在 D:\视频生成\voice-sample.mp3（或 .wav）
  · 支持中文、英文或中英混合

音频文件路径：
> [等待用户输入路径，默认 D:\视频生成\voice-sample.mp3]
```

**安全规则**：API Key 和音频样本路径存储在本地 `.config.json` 中，**绝不硬编码在技能文件里**，**绝不提交到 Git**。

---

## 视频生成流水线

### Phase 1: 分析

**目标**：深度理解要介绍的主题，找到最打动人的角度。

**时长判断**：
- 如果用户在调用时指定了秒数（如"做个 45 秒的视频"）→ 用用户指定的时长
- 如果用户没指定，但 `.config.json` 中有预设时长 → 用预设
- 如果都没指定，根据题材自动判断：

| 题材类型 | 建议时长 | 理由 |
|---------|---------|------|
| 单个工具/产品介绍 | 30-45s | 够讲清楚 3-4 个卖点 + CTA |
| 教程/操作指南 | 45-60s | 需要展示步骤 |
| 概念/趋势解读 | 20-30s | 一个核心观点，快速传达 |
| 多工具对比/合集 | 60-90s | 多个项目需要更多时间 |
| 品牌/团队宣传 | 15-25s | 一个 punchline 就够了 |

在分析报告中写明建议时长及理由。

**步骤**：

1. **如果是网站/Web 产品**：必须用 kimi-webbridge 实地访问
   - 截图首页、核心功能页、登录流程
   - 提取真实数据（用户数、内容量等）
   - 了解实际功能入口和操作流程
   - 记录页面上的真实文案和 slogan

2. **如果是开源仓库**：读取 README、查看 Demo、下载官方截图
   - 提取核心功能列表
   - 了解技术栈和兼容性
   - 记录 Stars、License 等数据

3. **输出分析报告**（`分析报告.md`）：
   ```markdown
   # 分析报告：<主题名>
   
   ## 一句话定位
   用一句话说清楚这是什么
   
   ## 核心卖点（3个，按重要性排序）
   1. xxx
   2. xxx  
   3. xxx
   
   ## 目标受众
   谁会看这个视频？他们在什么场景下看？
   
   ## 竞品/替代方案
   没有这个工具之前，人们怎么做？
   
   ## 最打动人的数据/事实
   - 具体数字
   - 用户评价
   - 使用场景
   
   ## 可用素材清单
   - 截图：xxx
   - Logo：xxx
   - Demo 视频：xxx
   ```

---

### Phase 2: 脚本

**目标**：根据 Phase 1 确定的时长，编写完整的视频脚本（画面 + 台词 + 动画）。

**脚本格式**（每行一个镜头，含 TTS 信息）：

```markdown
# 视频脚本：<主题名>
## 时长：30s | 风格：颠覆认知 | 视觉：极简白 | TTS：冰糖

| # | 时间 | 类型 | 画面描述 | 画面文字 | 台词（TTS） | TTS 风格 | 动画 |
|---|------|------|---------|---------|------------|---------|------|
| 1 | 0-3s | 砸脸 | 纯色底，大字居中 | "XXX" | "完整的口播台词" | 语速偏快，有冲击力 | 弹入+微震 |
| 2 | ... | ... | ... | ... | ... | ... | ... |
```

**台词规则**：
- 每句台词独立一个 TTS 调用，对应一个 `<audio>` 轨道
- 台词字数 × 0.3 ≈ 需要的秒数（约 3.3 字/秒语速）
- 画面文字 ≠ 台词：画面是 punchline，台词是完整的口语表达
- TTS 风格列描述语气、语速、情感，直接传给 MiMo API 的 user message

**脚本原则**：
- 每屏 ≤15 字（中文），≤8 词（英文）
- 动词开头，口语化
- 第一屏必须让人停下来看
- 最后一屏必须让人记住名字和地址
- 不写安装步骤，不写技术细节
- 每个画面描述要具体到元素位置、大小、颜色

**脚本必须输出给用户确认。用户说"可以"才进入 Phase 3。**

---

### Phase 3: 设计

**目标**：确定视觉语言，不写代码先出设计稿。

**设计稿内容**（`设计稿.md`）：

```markdown
# 设计稿：<主题名>

## 色彩方案
- 底色：#xxx
- 主色：#xxx（标题、CTA）
- 辅色：#xxx（标签、强调）
- 文字色：#xxx / #xxx
- orb 色：渐变1 + 渐变2

## 字体层级
- 砸脸标题：120px / weight 900 / letter-spacing -3px
- 场景标题：80px / weight 800 / letter-spacing -2px
- 副标题：36px / weight 400
- 标签/按钮：24px / weight 700
- CTA：28px / weight 700 / monospace

## 空间布局
- 砸脸场景：纯文字居中，上下留白 35%
- 截图+文字场景：截图占 55-65% 面积
- 列表场景：垂直间距 ≥ 元素高度 × 0.5
- 每个场景 padding：横屏 80px / 竖屏 56px

## 关键帧设计（至少3帧的文字描述）
### 帧1：开场
- 底色纯色，无 orb
- 标题在正中央，字号最大
- 标签在标题上方 40px

### 帧2：截图+标注
- 截图占左侧 55%，带圆角和阴影
- 右侧 3 个 chip 垂直排列，间距 18px
- 每个 chip 左侧 icon + 右侧文字

### 帧3：结尾 CTA
- 中央大标题 + 下方链接按钮
- 按钮用主色填充，圆角 20px
```

---

### Phase 4: 实现

脚本和设计稿确认后，开始实现。

#### 4.1 TTS 配音生成（如果启用）

使用小米 MiMo TTS API（OpenAI 兼容接口）为脚本中每句台词生成配音。

**API 参考**：
- 端点：`https://api.xiaomimimo.com/v1/chat/completions`
- 认证：Header `api-key: $MIMO_API_KEY`（从 `.config.json` 读取）
- 模型选择：见下方三种模式
- 音频：24kHz, mono, WAV 格式（非流式）/ PCM16（流式）

**三种模式调用**（Python）：

```python
import os, base64, json
from openai import OpenAI

config = json.load(open("D:/视频生成/.config.json"))
client = OpenAI(
    api_key=config["ttsApiKey"],
    base_url="https://api.xiaomimimo.com/v1"
)

# 读取台词列表
script = json.load(open("D:/视频生成/<project>/台词.json"))

for i, line in enumerate(script):
    # 根据 ttsMode 选择模型和参数
    if config["ttsMode"] == "preset":
        # 预置语音
        resp = client.chat.completions.create(
            model="mimo-v2.5-tts",
            messages=[
                {"role": "user", "content": line.get("style", "")},
                {"role": "assistant", "content": line["text"]}
            ],
            audio={"format": "wav", "voice": config["ttsVoice"]}
        )
    elif config["ttsMode"] == "voicedesign":
        # 语音设计：用文字描述音色，voice 参数不需要传
        resp = client.chat.completions.create(
            model="mimo-v2.5-tts-voicedesign",
            messages=[
                {"role": "user", "content": config["ttsVoiceDesign"]},
                {"role": "assistant", "content": line["text"]}
            ],
            audio={"format": "wav"}
        )
    elif config["ttsMode"] == "voiceclone":
        # 语音克隆：base64 编码音频样本
        sample_path = config["ttsCloneSample"]
        with open(sample_path, "rb") as f:
            sample_b64 = base64.b64encode(f.read()).decode()
        mime = "audio/wav" if sample_path.endswith(".wav") else "audio/mpeg"
        voice_data_url = f"data:{mime};base64,{sample_b64}"
        
        resp = client.chat.completions.create(
            model="mimo-v2.5-tts-voiceclone",
            messages=[
                {"role": "user", "content": line.get("style", "")},
                {"role": "assistant", "content": line["text"]}
            ],
            audio={"format": "wav", "voice": voice_data_url}
        )
    
    # 解码并保存
    audio_b64 = resp.choices[0].message.audio.data
    with open(f"台词-{i:02d}.wav", "wb") as f:
        f.write(base64.b64decode(audio_b64))
```

**语音克隆要求**：
- 音频 10-30 秒，干净人声，无背景音乐/噪音
- 支持 MP3/WAV，≤10MB base64 编码后
- 支持中文、英文或中英混合
- 克隆后的声音可以通过 user message 进行风格控制

**预置语音**：`冰糖`、`茉莉`、`苏打`、`白桦`、`Mia`、`Chloe`、`Milo`、`Dean`

**语音设计提示**：描述性别年龄、音色质感、情绪基调、语速节奏，1-4 句话即可。避免矛盾描述和音效词汇（如"混响"）。

**台词 JSON 格式**（`台词.json`）：
```json
[
  {"text": "你的 AI 助手，真的够强吗？", "start": 0, "duration": 3.5, "style": "语速偏快，带一点挑衅感"},
  {"text": "其实不是 AI 本身的问题。", "start": 3.5, "duration": 2.5, "style": "语气一转，变得沉稳"},
  ...
]
```

生成后每个台词一个 `.wav` 文件（`台词-00.wav`, `台词-01.wav` ...），在 HTML 中用独立 `<audio>` 标签引用。

#### 4.2 写视频 HTML

**关键实现原则**：

1. **不要每次都从零写** — 积累常用动画模式：
   - `.hero-text` — 大标题弹入（scale 0.85→1 + y 40→0）
   - `.chip-pop` — chip 逐个弹出（scale 0.4→1, stagger 0.12s）
   - `.shot-reveal` — 截图从下方滑入（y 60→0, scale 0.9→1）
   - `.fade-swap` — 场景切换（统一 0.25s out + 0.3s in）

2. **布局要有变化** — 不要每个场景都是居中 flex-col：
   - 砸脸：纯居中
   - 截图+列表：左右分栏 (horiz)
   - 证据：截图大屏占满，文字 overlay
   - CTA：居中

3. **动画要有节奏感**：
   - 开场用 back.out 缓动（有回弹）
   - 中间场景用 power3.out（流畅）
   - 列表元素用 stagger 产生节奏
   - 场景切换 0.25s 淡出 → 0.3s 淡入（利落）

4. **素材要大**：
   - 截图至少占画面 50%
   - 不要把小图放在角落
   - 截图上可以叠加半透明标注气泡

5. **颜色要有层次**：
   - 标题用渐变色（主色→辅色）
   - 标签/按钮用半透明底色
   - CTA 用实色填充

**双比例实现**：
- 先写 4:3 横屏，确认渲染成功
- 基于 4:3 改 3:4：把左右布局改为上下布局，调整字号
- 不要重写，复用相同的 CSS 变量和动画逻辑

**渲染后检查**：
- 两个视频都能正常播放
- 复制到项目根目录命名 `43-横屏.mp4` / `34-竖屏.mp4`
- 更新 `.history.json`

---

## 视觉风格参数速查

| 风格 | 底色 | 标题渐变 | 标签底+字 | CTA |
|------|------|---------|----------|-----|
| 赛博朋克 | `#0a0a12` | `#c084fc→#22d3ee` | `rgba(34,211,238,0.12)` + `#22d3ee` | `#7c3aed→#06b6d4` |
| 极简白 | `#fafafa` | `#4f46e5→#7c3aed` | `#eef2ff` + `#4f46e5` | `#4f46e5` |
| 暗金 | `#0c0c0c` | `#fbbf24→#f59e0b` | `rgba(251,191,36,0.12)` + `#fbbf24` | `#b45309→#d97706` |
| 活力橙蓝 | `#0f0f1a` | `#f97316→#3b82f6` | `rgba(249,115,22,0.15)` + `#fb923c` | `#ea580c→#2563eb` |
| 暗夜绿 | `#0a0f0a` | `#22c55e→#06b6d4` | `rgba(34,197,94,0.12)` + `#4ade80` | `#15803d→#0891b2` |
| 霓虹粉紫 | `#0f0a14` | `#ec4899→#a855f7` | `rgba(236,72,153,0.12)` + `#f472b6` | `#db2777→#7c3aed` |
| 纯黑暴力 | `#000` | `#fff` 纯白无渐变 | `rgba(255,255,255,0.06)` + `#fff` | `#ef4444` |
| 暖橘日落 | `#1a100a` | `#f97316→#ec4899` | `rgba(249,115,22,0.12)` + `#fb923c` | `#c2410c→#be185d` |
| 冰川蓝 | `#f0f5fa` | `#1e40af→#0369a1` | `#dbeafe` + `#1d4ed8` | `#1e40af` |
| 红黑警戒 | `#0a0000` | `#ef4444→#dc2626` | `rgba(239,68,68,0.12)` + `#f87171` | `#b91c1c→#991b1b` |

## 通用规则

- 标题 ≥80px，副标题 ≥36px，正文 ≥28px
- 每屏 ≤15 字，一屏一个信息
- 砸脸标题 ≥100px，weight 900
- 优先用真实截图，纯文字是最后手段
- 最后必须放链接/地址
- 不要安装命令、技术细节、大段文字
- 场景切换 0.25s out + 0.3s in

## 环境要求

- Node.js ≥ 22 (`nvm use 22`)
- FFmpeg (`scoop install ffmpeg`)
- kimi-webbridge（网站调研用）
- HyperFrames（`npx hyperframes init` 自动下载）

## 实现注意

- 符合 HyperFrames 规范：`class="clip"`、`data-start/duration/track-index`
- GSAP timeline `paused: true`，注册到 `window.__timelines`
- orb 用不同 track-index，每场景结束加 `tl.set()` hard kill
- 竖屏 `1080×1440`，横屏 `1600×1200`
- BGM 复制到项目内 `src="bgm.mp3"`
- 输出命名 `43-横屏.mp4` / `34-竖屏.mp4`
