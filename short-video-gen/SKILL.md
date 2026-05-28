---
name: short-video-gen
description: 短视频生成 — 通用视频制作流水线，带质量审核关卡
argument-hint: "<视频主题描述>"
level: 4
---

# 短视频生成

用户描述想法 → AI 走流水线 → 输出视频。**流程管质量，创意靠用户描述。**

## 流水线

```
用户描述需求
    │
    ▼
Stage 1  信息收集   深入调研主题，收集素材
    │
    ▼
Gate 1  素材审核   够不够做视频？不够打回 Stage 1
    │
    ▼
Stage 2  脚本设计   确定结构、节奏、视觉方向
    │
    ▼
Gate 2  方案审核   方案够不够好？不够打回 Stage 2
    │
    ▼
Stage 3  实现渲染   写 HTML + CSS + GSAP → MP4
    │
    ▼
Gate 3  最终审核   技术质量 + 内容质量，不通过回到对应阶段
    │
    ▼
rendered.mp4
```

---

## Stage 1: 信息收集

**目标**：搞懂要做什么、有什么素材可用。

- 网站/产品 → kimi-webbridge 实地访问，截图，记录真实数据
- 开源项目 → 读 README，下载官方截图
- 其他题材 → Web 搜索收集资料

**输出**：`素材/` 目录下有足够的图/音频/数据。

---

### Gate 1: 素材审核

打印检查结果，不通过打回：

```
□ 素材够支撑一个完整视频吗？（不是只有 1-2 张图）
□ 关键信息准确吗？（数据/功能描述有来源吗）
□ 用户的需求都理解了吗？
```

---

## Stage 2: 脚本设计

**目标**：确定视频的骨架——结构、节奏、视觉方向。

根据用户描述和已有素材，设计：
- 时长和场景划分
- 每个场景的内容和视觉风格
- 配色和字体方向
- 关键帧的布局思路

**输出**：设计方案（可以是脑中过一遍，不需要长篇文档）。

---

### Gate 2: 方案审核

打印检查结果，不通过打回：

```
□ 看完方案能一句话说清这个视频在讲什么吗？
□ 前 3 秒能抓住注意力吗？
□ 每个场景有对应的视觉素材吗？
□ 场景之间有变化吗？（不只一种布局到底）
□ 符合用户描述的要求吗？
```

---

## Stage 3: 实现渲染

写 HTML + CSS + GSAP。默认 1920×1080。

```bash
npm run check && npm run render
cp renders/*.mp4 ../rendered.mp4
```

---

### Gate 3: 最终审核

```
□ 视频能正常播放？
□ 画面无卡帧/黑屏？
□ 内容符合 Stage 2 的设计方案？
□ 作为观众，觉得这视频好看吗？
```

---

## 参数

用户调用时缺什么问什么（`AskUserQuestion`），配置里有的直接用：

- 时长、视觉风格、视频比例 → 缺就问
- BGM、TTS → 按配置

用户说"你定"就跳过。

---

## 工具

kimi-webbridge（浏览器调研+搜图）· HyperFrames（HTML→MP4）· FFmpeg（BGM）· 小米 MiMo TTS（配音）

## 环境

Node.js ≥ 22 · FFmpeg · kimi-webbridge

## HyperFrames 规则

- `class="clip"` + `data-start/duration/track-index` 管理元素时序
- GSAP `paused:true` 注册到 `window.__timelines`，只做动画不管理显示/隐藏
- orb 不同 track-index，`tl.set()` hard kill
- 不用 `Math.random()` / `Date.now()`
