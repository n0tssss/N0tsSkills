# N0tsSkills

个人自用 AI 技能（Skills）集合。

## 内容

| 技能 | 说明 |
|------|------|
| `short-video-gen/` | 视频制作 — 5 阶段工业化流水线：选题评估→参数确认→信息收集→脚本设计→实现渲染，4 道质量关卡 |
| `daily-ai-news/` | AI 新闻推送 — 每日 AI 科技资讯速递，14 个 RSS 源 + 中文新闻搜索，可配置推送频率 |
| `github-niuma-daily/` | GitHub 牛马日报 — 自动监控 GitHub 每日活动，生成工作强度报告，包含 AI 点评和时间段分析 |

## 安装

### 一键安装（推荐）

直接告诉 AI：

> "请把 https://github.com/n0tssss/N0tsSkills.git 克隆到 ~/.claude/skills/ 目录下"

AI 会自动：
1. 克隆仓库到 skills 目录
2. 识别并加载所有技能
3. 以后 `git pull` 即可同步最新

### 手动安装

```bash
git clone https://github.com/n0tssss/N0tsSkills.git ~/.claude/skills/
```

### 同步更新

```bash
cd ~/.claude/skills/ && git pull
```

## 添加新技能

把新技能的文件夹放入仓库根目录，推送到 GitHub 即可。

每个技能目录结构：
```
skill-name/
  SKILL.md      # 技能定义（必需）
  README.md     # 技能说明（可选）
```

## License

MIT
