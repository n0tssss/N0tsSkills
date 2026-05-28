# 视频制作 (short-video-gen)

工业化视频制作流水线。5 阶段 + 4 关卡，AI 自主创意。

## 流程

选题评估 → 参数确认 → 信息收集 → 脚本设计 → 实现渲染

每阶段有关卡审核，不通过打回重做。

## 依赖

- Node.js ≥ 22
- FFmpeg
- HyperFrames（自动下载）
- kimi-webbridge（浏览器调研+搜图）

## 使用

```
/视频制作 给 SkillHub 做一个团队教程视频
```

首次使用会自动弹出配置向导。缺失参数会用 AskUserQuestion 逐一确认。

## 输出

```
D:\视频生成\<project>\
  素材/           # 截图、图片、Logo、BGM
  index.html      # 项目文件
  rendered.mp4    # 最终视频
```
