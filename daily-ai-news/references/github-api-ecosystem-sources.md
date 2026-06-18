# GitHub API Sources for AI Ecosystem News

## Overview

GitHub API provides structured data on AI tools, skills, and plugins. Far superior to web_search for tracking ecosystem trends.

## Search Queries

### 1. MCP Server Additions
```bash
# Track new MCP servers via commits to awesome-mcp-servers
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/punkpeye/awesome-mcp-servers/commits?per_page=30&since=$(date -v-7d +%Y-%m-%dT00:00:00Z)"
# Filter: commit messages containing "add" (new server additions)
# Rate: ~21 new servers per week
```

### 2. Claude Code Skills
```bash
# New Claude Code skill repos
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/search/repositories?q=claude+code+skills+created:>$SEVEN_DAYS_AGO&sort=stars&order=desc&per_page=10"
# Expected: 18,000+ total results, filter to top by stars
```

### 3. Cursor Rules
```bash
# New Cursor/Windsurf rules
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/search/repositories?q=cursor+rules+created:>$SEVEN_DAYS_AGO&sort=stars&order=desc&per_page=5"
```

### 4. AI Agent Frameworks
```bash
# New agent skill frameworks
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/search/repositories?q=AI+agent+skills+framework+created:>$THIRTY_DAYS_AGO&sort=stars&order=desc&per_page=5"
```

### 5. Vibe Coding
```bash
# Vibe coding paradigm
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/search/repositories?q=vibe+coding+created:>$THIRTY_DAYS_AGO&sort=stars&order=desc&per_page=3"
```

### 6. System Prompts
```bash
# System prompt collections
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/search/repositories?q=system+prompts+leaks+updated:>$SEVEN_DAYS_AGO&sort=stars&order=desc&per_page=3"
```

## Key Tracking Repos

| Repo | Purpose | What to track |
|------|---------|---------------|
| `punkpeye/awesome-mcp-servers` | MCP server registry | Commits with "add" prefix |
| `hesreallyhim/awesome-claude-code` | Claude Code skills collection | Commits adding new skills |
| `sickn33/antigravity-awesome-skills` | 1494+ skills registry | Version bumps, new skills |

## Auth Requirements

- Token file: `~/.hermes/.github_token`
- Unauthenticated: 60 requests/hour
- Authenticated: 5000 requests/hour
- All queries MUST use auth token

## Data Format for LLM

Output each finding as:
```json
{
  "title": "Project Name",
  "url": "https://github.com/owner/repo",
  "description": "One-line description",
  "source": "GitHub",
  "category": "ai-ecosystem",
  "stars": 1234,
  "language": "Python",
  "created": "2026-04-01"
}
```

## Test Results (2026-06-03)

- MCP: 21 new servers in 7 days (x402station, microsoft-todo, obsidian, zendesk...)
- Claude Code Skills: 18,846 new repos since April (caveman ⭐68K, graphify ⭐58K, open-design ⭐57K)
- Cursor Rules: 601 new repos since April (agent-rules-books ⭐1.7K, styleseed ⭐402)
- Vibe Coding: emerging paradigm (vibe-check, vibeguard)
- Agent Frameworks: multiple new entries
