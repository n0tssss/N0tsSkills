---
name: short-video-gen
description: 短视频生成 — 重度前期调研，丰富素材驱动，追求可商用质量
argument-hint: "<视频主题描述>"
level: 4
---

# 短视频生成

**先素材，后动笔。** 不在没素材的情况下开始写 HTML。

## 工作目录

```
D:\视频生成\<project>/
  素材/          # 截图、图片、Logo、BGM — 至少 6 个文件才能开始写 HTML
  index.html
  rendered.mp4
```

## 输出

默认 1920×1080 横屏。用户可指定竖屏/方形/其他。

---

## 开始前

缺参数就问（`AskUserQuestion`），不缺直接开始：

- 时长（用户没说+配置没有）→ 问
- 视觉风格（同上）→ 问
- 比例、BGM、TTS → 按配置，不追问

用户说"你定"就跳过。

---

## 制作流程

### Phase 1: 深度调研 + 素材收集

**这是最重要的阶段。素材不够不进入 Phase 2。**

必须做的事：

1. **网站/Web 产品** — 用 kimi-webbridge 把网站从头到尾点一遍：
   - 首页、关于、产品/服务、价格、联系 — 每页截图
   - 找到 logo（右键另存或截图裁切）
   - 找到产品图/案例图/客户 Logo — 越多越好
   - 记录页面上真实的数据和文案

2. **开源仓库/工具** — 读 README 找图片、Demo 截图、Logo
   - 去项目官网截图
   - GitHub 的 Social Preview 图直接下载

3. **游戏/影视/文化类** — 用 kimi-webbridge 去 Google Images 或壁纸站搜索下载：
   - 官方海报/Key Art、角色图、场景截图、Logo
   - 至少下载 5 张不同内容的图

**素材检查点**（进入 Phase 2 前必须确认）：
- [ ] 素材目录下有 ≥6 个文件（图片+BGM）
- [ ] 有至少 3 张不同内容的图（不是同一张图的不同尺寸）
- [ ] 有 logo 或品牌标识

### Phase 2: 脚本

基于素材写脚本。每行描述：
- 时间、场景类型、画面描述（明确指出用素材里的哪张图）
- 画面文字、台词(TTS)、动画

原则：
- 每个场景用不同的素材图，不重复
- 每 5-8 秒换一个场景
- 场景类型要变化：大图铺满→卡片分列→全屏文字→左右分栏→大图铺满...
- 前 3 秒必须抓住注意力
- 结尾必须有行动号召或记忆点

### Phase 3: 实现

写 HTML + CSS + GSAP。参考以下模式自由组合：

**全屏图片 + 暗色蒙层 + 大字标题** — 适合开场、章节分隔、结尾
```css
.full-bg { position: absolute; inset: 0; object-fit: cover; }
.overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.55); }
```

**左图右文 / 左文右图** — 适合展示产品+特性
```css
.horiz { display: flex; gap: 48px; }
.col-img { flex: 0 0 600px; }
.col-text { flex: 1; }
```

**三列/四列卡片** — 适合罗列功能、数据、卖点
```css
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
```

**大数字冲击** — 适合展示年份、数据、规模
```css
.big-num { font-size: 120px; font-weight: 900; }
```

**图片 + 标注气泡** — 适合展示截图细节
```css
.bubble { position: absolute; padding: 8px 16px; background: #fff; border-radius: 8px; }
```

**文字动画**：
- 模糊 reveal：`filter: blur(20px) → 0`
- 逐字弹入：stagger 0.03s × per-character
- 缩放弹入：`scale: 0.8→1, back.out`
- 滑入：`x: -60→0` 或 `y: 40→0`

**场景过渡**（stagger 0.25s out + 0.3s in）：
- 淡入淡出（通用）
- 缩放穿越（场景放大消失→新场景缩小恢复）
- 滑动切换（左右推出）

### Phase 4: 渲染前自查

渲染前打开 `index.html` 在脑中过一遍：

- [ ] 每个场景用的素材图都不一样（不重复）
- [ ] 有至少 1 个大数字/大数据场景
- [ ] 有至少 1 个全屏图片+蒙层场景
- [ ] 场景类型数 ≥ 总场景数的 50%（6 个场景至少有 3 种布局）
- [ ] 标题字号 ≥72px，可读性够
- [ ] 没有两屏纯文字相邻

然后：
```bash
npm run check && npm run render
cp renders/*.mp4 ../rendered.mp4
```

---

## 工具速查

| 工具 | 用途 |
|------|------|
| kimi-webbridge | 浏览器调研网站、Google Images 搜图 |
| HyperFrames | HTML → MP4（`npx hyperframes init`） |
| FFmpeg | 合成 BGM |
| 小米 MiMo TTS | 配音（需 API Key） |

## 视觉风格速查

| 风格 | 底色 | 主色 | 适合 |
|------|------|------|------|
| 极简白 | `#fafafa` | 蓝紫渐变 | 商务、SaaS、教程 |
| 纯黑暴力 | `#000` | 纯白+红 | 游戏、影视、冲击力 |
| 暗金 | `#0c0c0c` | 金色渐变 | 高端品牌、奢侈品 |
| 赛博朋克 | `#0a0a12` | 紫+青绿 | 科技、AI、Web3 |
| 暗夜绿 | `#0a0f0a` | 绿青渐变 | 终端/黑客/安全 |
| 冰川蓝 | `#f0f5fa` | 深蓝渐变 | 医疗、金融、专业 |
| 暖橘日落 | `#1a100a` | 橙粉渐变 | 生活、温暖、故事 |
| 红黑警戒 | `#0a0000` | 红色渐变 | 促销、警告、紧迫 |
| 霓虹粉紫 | `#0f0a14` | 粉紫渐变 | 潮流、年轻、音乐 |
| 活力橙蓝 | `#0f0f1a` | 橙蓝渐变 | 运动、活力、创新 |

## 环境

Node.js ≥ 22 · FFmpeg · HyperFrames · kimi-webbridge

## HyperFrames 规范

`class="clip"`、`data-start/duration/track-index`、GSAP `paused: true` 注册到 `window.__timelines`、场景结束 `tl.set()` hard kill、BGM `src="bgm.mp3"`、不用 `Math.random()`/`Date.now()`
