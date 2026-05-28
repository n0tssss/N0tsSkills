# GitHub API 认证参考

## Token 类型对比

### Classic Token (ghp_)
- 格式：`ghp_xxxxxxxxxxxx`（40字符）
- 认证头：`Authorization: token ghp_xxxxx`
- 权限：粗粒度，勾选 repo 即可访问所有仓库
- **推荐使用**，设置简单

### Fine-grained Token (github_pat_)
- 格式：`github_pat_xxxxxxxxxxxx`
- 认证头：`Authorization: Bearer github_pat_xxxxx`
- 权限：细粒度，需要逐个仓库配置
- 配置复杂，容易漏权限

## 关键 API 端点

```
# 获取用户信息
GET /user

# 获取用户所属的所有组织
GET /user/orgs

# 获取用户的公开事件
GET /users/{username}/events/public

# 获取组织的事件
GET /orgs/{org_name}/events

# 获取仓库的提交（支持 author 过滤）
GET /repos/{owner}/{repo}/commits?since=...&until=...&author=...

# 获取提交详情（包含代码行数变化 stats.additions/deletions）
GET /repos/{owner}/{repo}/commits/{sha}
```

## 仓库过滤逻辑

用户的事件中可能包含 collaborator 仓库（如 `chenhg5/cc-connect`）。脚本通过 `allowed_prefixes` 过滤：
- 只统计 `username/` 前缀的仓库（用户自己的）
- 只统计 `{org}/` 前缀的仓库（所属组织的）
- Star/Fork 事件不受过滤影响

## 网络容错

脚本使用 `requests.Session` + `urllib3.Retry` + `HTTPAdapter` 实现自动重试：
- 总重试次数：3
- 退避因子：1（指数退避）
- 触发状态码：500, 502, 503, 504
- 仅对 GET 请求重试

这解决了 GitHub API 偶发的 SSL EOF 错误。

## 系统安全机制

**重要**：系统会自动将敏感信息（token、密码等）替换为 `***`，导致：
- 在对话中看到的 token 只有 3 个字符
- 必须通过 `write_file` 或 `execute_code` 写入文件
- 不能在 terminal 命令中直接包含 token

## 微信消息限流

当短时间内发送大量消息时，会触发微信限流：
```
delivery error: Weixin send failed: iLink sendmessage rate limited: ret=-2
```

解决方法：等待几分钟后重试。定时任务遇到限流时，下次执行会自动重试。
