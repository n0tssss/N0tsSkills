# N0tsSkills

个人自用 AI 技能（Skills）集合。

## 技能列表

| 技能 | 说明 | 依赖 |
|------|------|------|
| `daily-ai-news/` | AI 新闻推送 — 每日 AI 科技资讯速递，14+ RSS 源 + 中文搜索 | Playwright |
| `github-niuma-daily/` | GitHub 牛马日报 — 自动监控每日活动，生成工作强度报告 | Playwright |
| `short-video-gen/` | 短视频制作 — 选题评估→脚本设计→渲染，4 道质量关卡 | HyperFrames |
| `daily-weather/` | 每日天气卡片 — 查询天气渲染为精美图片，不同天气自动切换背景 | Playwright |
| `my-coffee/` | 瑞幸咖啡点单 — 查门店/下单/取餐码/查订单 | MCP API |

## 安装

### 找到你的 Skill 目录

不同 AI 工具的 skill 目录不一样，先确认你的目录在哪：

| 工具 | 默认 Skill 目录 |
|------|-----------------|
| Hermes Agent | `~/.hermes/skills/` |
| Claude Code | `~/.claude/skills/` |
| Cursor | `.cursor/skills/`（项目根目录） |
| Windsurf | `.windsurf/skills/`（项目根目录） |

不确定的话，问你的 AI：`你的 skill 加载目录是什么路径？`

### 克隆到 Skill 目录

```bash
# 替换为你的实际 skill 目录路径
SKILL_DIR="~/.hermes/skills"  # 例如 Hermes

# 克隆（仓库里的技能文件夹会直接出现在 skill 目录下）
git clone https://github.com/n0tssss/N0tsSkills.git "$SKILL_DIR/"
```

克隆后，技能目录结构如下：
```
~/.hermes/skills/
├── N0tsSkills/          # 仓库本身
│   ├── daily-ai-news/
│   ├── github-niuma-daily/
│   ├── short-video-gen/
│   ├── daily-weather/
│   └── my-coffee/
├── ai-model-rank/       # 你的其他技能...
└── ...
```

**为什么是这样？** 每个技能文件夹（如 `daily-ai-news/`）本身就是独立技能，里面有 `SKILL.md`。AI 工具扫描 skill 目录时会自动识别它们。仓库只是用来方便更新，不影响技能加载。

### 同步更新

```bash
cd ~/.hermes/skills/N0tsSkills && git pull
```

技能有新版本时，pull 一下就完事。

### 或者告诉你的 AI

直接对 AI 说：

> "请把 https://github.com/n0tssss/N0tsSkills.git 克隆到我的 skill 目录下"

AI 会自动找到目录并克隆。

## 技能结构

每个技能遵循标准结构：
```
skill-name/
  SKILL.md          # 技能定义（必需）
  scripts/          # 脚本（可选）
  templates/        # 模板（可选）
  references/       # 参考文档（可选）
```

## License

MIT
