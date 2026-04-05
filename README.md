# socialhub-mcp

An open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that acts as a thin, authenticated client to the [SocialHub](https://socialhub.choreografii.com) API.

Connect Claude Desktop (or any MCP-compatible host) to SocialHub and manage your social media posts entirely through natural language.

---

## Installation

### Option A — run directly with `uvx` (recommended)

No install step required. `uvx` fetches and runs the package in an isolated environment.

```bash
uvx socialhub-mcp
```

### Option B — install with pip

```bash
pip install socialhub-mcp
socialhub-mcp
```

---

## Claude Desktop configuration

Add the following block to your `claude_desktop_config.json` (usually at
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "socialhub": {
      "command": "uvx",
      "args": ["socialhub-mcp"],
      "env": {
        "SOCIALHUB_API_KEY": "sk_live_...",
        "SOCIALHUB_API_URL": "https://api.socialhub.choreografii.com"
      }
    }
  }
}
```

Restart Claude Desktop after saving the file.

---

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SOCIALHUB_API_KEY` | Yes | — | Your SocialHub API key (`sk_live_...`) |
| `SOCIALHUB_API_URL` | No | `https://api.socialhub.choreografii.com` | Override the API base URL (useful for staging) |

---

## Available tools

| Tool | Description |
|---|---|
| `social_accounts_list` | List all connected social media accounts |
| `social_post_create` | Create a post draft (platform, account, content, optional schedule & media) |
| `social_post_generate` | Generate post content with AI via the SocialHub content engine (SSE stream) |
| `social_post_list` | List posts with optional filters for status, platform, and limit |
| `social_post_approve` | Approve a draft post for publishing |
| `social_post_schedule` | Schedule an approved post at a specific ISO 8601 datetime |
| `social_post_publish` | Publish an approved post immediately |
| `social_post_cancel` | Cancel a scheduled post |
| `social_usage_current` | Retrieve current subscription plan and usage statistics |

---

## Development setup

### Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or pip

### Clone and install

```bash
git clone https://github.com/choreografii/product-socialhub-mcp.git
cd product-socialhub-mcp

# Using uv (recommended)
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"
```

### Run the server locally

```bash
export SOCIALHUB_API_KEY=sk_live_...
uv run socialhub-mcp
```

### Run tests

```bash
uv run pytest tests/ -v
```

### Project layout

```
src/socialhub_mcp/
├── __init__.py       # Package version
├── client.py         # Async httpx client with Bearer auth
├── server.py         # FastMCP server & tool definitions
└── tools/
    ├── accounts.py   # Account-related API calls
    ├── posts.py      # Post CRUD + AI generation
    └── usage.py      # Subscription / usage stats
```

---

## License

MIT — see [LICENSE](LICENSE).
