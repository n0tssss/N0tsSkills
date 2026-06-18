# GitHub API Ecosystem Tracking — Reference

## Why GitHub API over web_search

web_search returns water content, blogspam, SEO articles. GitHub API returns actual projects with star counts, descriptions, creation dates. Structured data > unstructured search for tracking new tools.

## Search Queries (6 total)

All queries use `api.github.com/search/repositories?q=...&sort=stars&order=desc`.

| Query | Label | Per Page | Time Window | Notes |
|-------|-------|----------|-------------|-------|
| `claude code skills created:>7d` | GitHub/Skills | 8 | 7 days | New skill repos |
| `cursor rules created:>7d` | GitHub/CursorRules | 5 | 7 days | New rules files |
| `AI agent skills framework created:>30d` | GitHub/Agents | 5 | 30 days | Agent frameworks |
| `vibe coding created:>30d` | GitHub/VibeCoding | 3 | 30 days | New paradigm |
| `system prompts leaks` | GitHub/Prompts | 5 | **NO date filter** | Repos update infrequently |

## Commit Tracking (2 repos)

### awesome-mcp-servers
- Repo: `punkpeye/awesome-mcp-servers`
- API: `GET /repos/punkpeye/awesome-mcp-servers/commits?per_page=30&since=7d_ago`
- Pattern: Merge commits say "Merge pull request #xxx from user/add-xxx"
- Extract server name: `re.search(r"add-([a-z0-9_-]+)", msg.lower())`
- **CRITICAL**: Do NOT filter out merge commits. The "add-" pattern is in the branch reference within merge messages.

### antigravity-awesome-skills
- Repo: `sickn33/antigravity-awesome-skills`
- API: `GET /repos/sickn33/antigravity-awesome-skills/commits?per_page=10&since=7d_ago`
- 1494+ skills for Claude Code, Cursor, Codex CLI, Gemini CLI
- Count commits with "skill" or "add" in message

## Pitfalls

### System Prompts query returns 0 with date filter
`system prompts leaks updated:>2026-05-27` returns 0 results. These repos (system_prompts_leaks, CL4R1T4S, leaked-system-prompts) are popular but don't get updated weekly. Query without date filter.

### MCP commits are ALL merge commits
The awesome-mcp-servers repo uses PR merge commits. Every "add-xxx" is merged via GitHub UI, creating a merge commit. Filtering `if "add" in msg and "merge" not in msg` returns 0 results. Must look for "add-" pattern regardless of "merge".

### skill_manage name resolution
`skill_manage(action='patch', name='N0tsSkills/daily-ai-news')` fails with "not found in active profile". Use `patch()` tool directly on the SKILL.md file path instead.

## Auth Token
- Location: `~/.hermes/.github_token`
- Unauthenticated: 60 req/hour
- Authenticated: 5000 req/hour
- Always use auth for production cron jobs
