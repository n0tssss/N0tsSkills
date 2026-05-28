# GitHub 牛马日报 (github-niuma-daily)

自动监控 GitHub 每日活动，生成详细的工作强度报告。

## 功能

- 🤖 AI 智能点评（综合评分 + 工作强度等级）
- 📊 核心数据统计（提交、Push、PR、Issue、Star、Fork）
- 💻 代码变更详情（行数变化、可视化统计条）
- 🏢 组织支持（自动获取所有所属组织）
- ⏰ 时间段分析（早上/上午/中午/下午/晚上活跃情况）

## 评分标准

| 分数 | 等级 | 描述 |
|------|------|------|
| 80+ | 🔥🔥🔥🔥 超级牛马 | 代码之神！GitHub 应该给你发工资！ |
| 50-79 | 🔥🔥🔥 顶级牛马 | 卷王本王！代码量可以绕地球一圈！ |
| 30-49 | 🔥🔥 勤劳牛马 | 高产如母猪！干了不少实事！ |
| 15-29 | 🔥 正常牛马 | 稳扎稳打，正常发挥！ |
| 8-14 | 💨 轻度牛马 | 写了一点点，也算进步... |
| 3-7 | 😴 划水牛马 | 主要在思考人生... |
| 0-2 | 🏖️ 摸鱼牛马 | 休息日？还是在憋大招？ |

## 首次使用（必须配置 Token）

### 1. 生成 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**（不要用 Fine-grained token）
3. 勾选权限：**repo** + **read:user**
4. Expiration 选择 **90 days** 或 **No expiration**
5. 点击 **Generate token** 并复制

### 2. 保存 Token

由于系统会自动将 token 替换为 `***`，必须通过文件写入：

```bash
# 方法1：终端执行（推荐）
echo "ghp_你的token" > ~/.hermes/.github_token

# 方法2：Python
python3 -c "
with open('$HOME/.hermes/.github_token', 'w') as f:
    f.write('ghp_你的token')
"
```

### 3. 验证配置

```bash
python3 ~/.hermes/scripts/github-daily-summary.py
```

如果看到报告输出，说明配置成功。

## 使用

```bash
# 手动执行
python3 ~/.hermes/scripts/github-daily-summary.py

# 创建定时任务（示例：每天 22:00）
hermes cron create \
  --script github-daily-summary.py \
  --schedule "0 22 * * *" \
  --no-agent \
  --name "github-niuma-daily"
```

## 输出示例

```
🐂 GitHub 牛马日报 | 2026-05-28

🤖 AI 点评
综合评分：72 分
工作强度：🔥🔥🔥 顶级牛马
活跃时段：上午 10-12 点最活跃，下午持续输出

📊 核心数据
- 提交：23 次
- Push：18 次
- PR 创建：2 个
- PR 合并：1 个
- Issue 创建：3 个

💻 代码变更
- 总行数：+1,234 / -567
- 🟩 新增：wkea-api (+892), datazone (+342)
- 🟥 删除：wkea-cli (-423), wkea-app-v2 (-144)

🏢 组织活动
- shwkea（公司）：15 次提交
- N0tsLabs（个人）：8 次提交
```

## 仓库过滤

脚本只统计以下仓库的活动：

- 用户自己的仓库：`用户名/xxx`
- 用户所属组织的仓库（自动获取）

Star 和 Fork 事件不受过滤影响。

## 常见问题

1. **Classic Token vs Fine-grained Token**：必须用 Classic Token (ghp_)，Fine-grained Token 会导致 401
2. **Token 被系统替换**：对话中粘贴的 token 会被替换为 `***`，必须通过文件写入
3. **SSL 网络错误**：脚本自动重试（3次，指数退避）
4. **消息限流**：等待几分钟后自动恢复
5. **脚本超时**：已限制为前 40 个仓库
