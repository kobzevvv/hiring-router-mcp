# 🎯 Hiring Router MCP

An intelligent Model Context Protocol (MCP) server for recruitment automation and hiring workflow management.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![MCP](https://img.shields.io/badge/MCP-Compatible-green)
![License](https://img.shields.io/badge/license-MIT-purple)
![Version](https://img.shields.io/badge/version-0.1.0-orange)

## ✨ Features

- 🤖 **Intelligent Task Routing** - Automatically routes hiring tasks to appropriate handlers
- 👥 **Dual-Mode Support** - Separate workflows for recruiters and candidates  
- 📊 **Market Research** - Integration with HH.ru, Linkedin and Indeed for salary and market analysis
- 📝 **Content Generation** - Job posts, quizzes, application forms, 
- 🔄 **Workflow Automation** - N8n integration ready for emails routing and other tasks
— **Candidates Database** - get data and build reports about candidates
- 📈 **Logging** - Complete request tracking for continuous improvement

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Claude Desktop app (for Claude integration)

### Installation

#### Option 1: Install from GitHub
```bash
pip install git+https://github.com/kobzevvv/hiring-router-mcp.git
```

#### Option 2: Clone and Install Locally
```bash
git clone https://github.com/kobzevvv/hiring-router-mcp.git
cd hiring-router-mcp
pip install -e .
```

#### Option 3: Using uv (recommended)
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then install the package
uv pip install git+https://github.com/kobzevvv/hiring-router-mcp.git
```

## ✅ Client-agnostic MCP endpoints

This server is client-agnostic. Any MCP-compatible client can connect over HTTP/SSE.

- Endpoints (local or deployed):
  - `GET /health` — health probe
  - `GET /mcp/sse` — Server-Sent Events stream
  - `POST /mcp/message` — JSON-RPC 2.0 messages

Minimal JSON-RPC examples (for `POST /mcp/message`):

```bash
curl -sS -X POST https://<service>-<hash>-<region>.a.run.app/mcp/message \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

```bash
curl -sS -X POST https://<service>-<hash>-<region>.a.run.app/mcp/message \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"get_available_tools","arguments":{"user_type":"recruiter"}}}'
```

Note: Replace `<service>-<hash>-<region>.a.run.app` with your Cloud Run service URL. Localhost is only used for development and can be ignored in cloud‑only setups.

### Claude Desktop Integration (Step-by-step)

1. Install the server (one time):
   - `pip install git+https://github.com/kobzevvv/hiring-router-mcp.git`

2. Open Claude Desktop → Settings.

3. Locate the MCP configuration file:
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

4. Add (or merge) the hiring-router entry. If the file is empty or missing, this minimal config works:

```json
{
  "mcpServers": {
    "hiring-router": {
      "command": "python",
      "args": ["-m", "hiring_router_mcp"]
    }
  }
}
```

   - Alternative: you may use the installed console script by replacing the server with:

```json
{
  "mcpServers": {
    "hiring-router": {
      "command": "hiring-router-mcp"
    }
  }
}
```

5. Restart Claude Desktop.

#### Verify inside Claude

- Start a new chat and try one of these:
  - "Hiring Router, are you here?"
  - "Use the hiring-router MCP to call get_available_tools."
  - "Call get_available_tools on the hiring-router server for recruiter."
  - "Use hiring-router to research Python developers in Moscow." (routes via `route_hiring_task`)

Expected behavior: Claude should call the MCP server and either list tools or perform the routed action. If nothing happens, see Troubleshooting below.

#### Optional: Test from terminal

```bash
# With MCP Inspector (recommended)
npx @modelcontextprotocol/inspector python -m hiring_router_mcp

# Or run the server directly
python -m hiring_router_mcp
```

<!-- Deep Research MCP section removed as it is out of scope for this project. -->

### Container deployment (Fly.io example)

1) Install the Fly CLI and login, then initialize:

```bash
fly launch --no-deploy
```

2) Build and deploy:

```bash
fly deploy
```

3) Set environment variables (optional):

```bash
fly secrets set DEEP_RESEARCH_RECORDS_PATH=/app/records.json
```

4) Get your public URL from Fly and use it in ChatGPT with `/mcp/` appended.

<!-- Deep Research deployment notes removed. -->

#### Troubleshooting

- If Claude does not call tools:
  - Confirm the JSON config path and content are correct (valid JSON, correct key `mcpServers`).
  - Ensure Python is on PATH in the environment that launches Claude. If not, replace `"python"` with the full path to your Python (e.g., `/usr/bin/python3`).
  - Try the console script form (`"command": "hiring-router-mcp"`).
  - Restart Claude after any config change.
  - Run the Inspector command above to validate the server runs without errors.

## 🛠️ Available Tools

### For Recruiters

| Tool | Description |
|------|-------------|
| `market_research` | Analyze candidate market and salaries on HH.ru |
| `generate_job_post` | Create engaging job postings for multiple platforms |
| `generate_application_form` | Build application forms with workflow triggers |
| `generate_quiz` | Create technical assessments with custom difficulty |
| `generate_homework` | Design take-home assignments with evaluation rubrics |
| `generate_candidate_journey` | Map end-to-end hiring process |
| `generate_funnel_report` | Generate recruitment analytics and conversion metrics |

### For Candidates

| Tool | Description |
|------|-------------|
| `candidate_assistant` | Personalized job search guidance based on stage |
| `resume_optimizer` | Optimize resume for ATS systems |
| `interview_prep` | Prepare for technical and behavioral interviews |
| `salary_research` | Research market salary ranges |

### Analytics

| Tool | Description |
|------|-------------|
| `get_request_analytics` | Analyze usage patterns and tool performance |
| `export_logs` | Export activity logs for analysis |

## 💬 Usage Examples

### In Claude Desktop

Once configured, you can use natural language to interact with the hiring tools:

```
"Use hiring router to research Python developers in Moscow"

"Generate a job post for Senior Frontend Developer at a startup"

"Create a technical quiz for React developers with 10 questions"

"Design an end-to-end hiring process for a fast-growing startup"

"Generate funnel report for last quarter's hiring"

"Help me prepare for a technical interview as a candidate"
```

### Programmatic Usage

```python
from hiring_router_mcp import mcp

# Use the route_hiring_task tool
result = await mcp.route_hiring_task(
    user_type="recruiter",
    task_description="research Python developers",
    context={"location": "Moscow", "experience": 3}
)

# Get available tools
tools = await mcp.get_available_tools(user_type="recruiter")
```

## 📊 Logging and Analytics

All requests are automatically logged for analysis and improvement:

- **Location**: `./hiring_logs/` directory
- **Format**: JSON for easy parsing
- **Rotation**: Daily log files
- **Analytics**: Built-in analytics tool to review patterns
- **Webhook forwarding**: Set `LOG_WEBHOOK_URL` to forward every log event as JSON to your endpoint (e.g., Cloudflare Worker)

View logs:
```bash
# Check today's logs
cat hiring_logs/requests.jsonl | jq

# Get analytics through MCP
# In Claude: "Use hiring router to get request analytics"
```

### Webhook Event Contract

Each log is posted as a JSON object. Common fields:

```json
{
  "timestamp": "2025-08-15T12:34:56.789Z",
  "level": "INFO",
  "logger": "hiring_router_mcp.server",
  "message": "tool_call",
  "event": "tool_call",
  "request_id": "5f9f2f06-1c7d-4f87-9e7e-1e1a1b9ef0a1",
  "client_id": "staging-macbook",
  "tool": "generate_job_post",
  "arg_keys": ["company", "role"]
}
```

Other events:
- `tool_result`: adds `result_type` and `duration_ms`
- `tool_error`: adds `duration_ms` and stack trace in `exc_info`
- `route_hiring_task`: includes `user_type`, `user_hash` (SHA-256 of user_id if provided), `description_length`, `context_keys`, `routed_to`

Security:
- If `LOG_WEBHOOK_SECRET` is set, requests include header `X-Signature: sha256=<hex>` where the value is HMAC-SHA256 over the raw JSON body using the shared secret.
- Do not log raw `task_description`, raw `context`, or full tool arguments; only keys are logged by default.

Receiver should validate signature, parse JSON, and store in your analytics system (e.g., BigQuery).

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
LOG_DIR=./hiring_logs
# Optional centralized webhook sink
LOG_WEBHOOK_URL=https://your-worker.example.workers.dev/ingest
# Optional HMAC signature for webhook (hex sha256 signature sent as X-Signature: sha256=...)
LOG_WEBHOOK_SECRET=your_shared_secret
# Optional client identifier (added to every event as client_id)
LOG_CLIENT_ID=staging-macbook

# External APIs (future)
HH_API_KEY=your_api_key_here
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook
```

### Custom Configuration

Edit `src/hiring_router_mcp/config.py` to customize settings.

## 🏗️ Architecture

```
┌─────────────────┐
│  Claude Desktop │
│   (MCP Client)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Route Handler  │
│  (Main Router)  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│Recruiter│ │Candidate │
│  Tools  │ │  Tools   │
└─────────┘ └──────────┘
    │           │
    └─────┬─────┘
          ▼
    ┌──────────┐
    │   Logs   │
    │Analytics │
    └──────────┘
```

## 📖 Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Usage Guide](docs/usage.md) - Examples and best practices
- [API Reference](docs/api.md) - Complete tool documentation
- [Contributing](CONTRIBUTING.md) - How to contribute
- [MCP Client Connect Guide](docs/mcp-client-connect.md) - How to connect various MCP clients (Open Chat UI, LibreChat, Claude, generic HTTP/SSE)
- [MCP Client Connect Guide](docs/mcp-client-connect.md) - How to connect various MCP clients (Open Chat UI, LibreChat, Claude, generic HTTP/SSE)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/kobzevvv/hiring-router-mcp.git
cd hiring-router-mcp

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
ruff check src/
black src/
```

### Submitting Changes

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🗺️ Roadmap

### Version 0.1.0 (Current)
- ✅ Basic routing functionality
- ✅ Recruiter tools suite
- ✅ Candidate assistance
- ✅ Logging system

### Version 0.2.0 (Planned)
- [ ] Enhanced HH.ru API integration
- [ ] Database persistence (PostgreSQL)
- [ ] Advanced analytics dashboard
- [ ] Batch processing for multiple positions

### Version 0.3.0 (Future)
- [ ] N8n workflow templates library
- [ ] REST API endpoints
- [ ] Web dashboard UI
- [ ] Multi-language support

### Version 1.0.0 (Goal)
- [ ] Full ATS integration
- [ ] AI-powered candidate matching
- [ ] Automated interview scheduling
- [ ] Complete recruitment automation suite

## 🐛 Known Issues

- HH.ru integration currently uses web scraping guidance (API integration coming in v0.2.0)
- N8n webhook triggers are prepared but require configuration
- Large log files may impact performance (rotation recommended)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [Model Context Protocol](https://modelcontextprotocol.io) by Anthropic
- Powered by [MCP SDK](https://github.com/modelcontextprotocol)
- Inspired by modern recruitment challenges

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kobzevvv/hiring-router-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kobzevvv/hiring-router-mcp/discussions)
- **Email**: your.email@example.com

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kobzevvv/hiring-router-mcp&type=Date)](https://star-history.com/#kobzevvv/hiring-router-mcp&Date)

---

<p align="center">
  Made with ❤️ for the recruitment community
  <br>
  <a href="https://github.com/kobzevvv/hiring-router-mcp">Give us a ⭐ if this project helped you!</a>
</p>

## ☁️ Google Cloud Run (HTTP/SSE FastMCP)

This repo includes an HTTP/SSE ASGI app exposing `/health`, `GET /mcp/sse`, and `POST /mcp/message` backed by the same tools. Build and deploy with Artifact Registry in `europe-west1`:

```bash
PROJECT_ID=qaleran
REGION=europe-west1
SERVICE=hiring-router-mcp
REPO=hiring-router

gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

gcloud artifacts repositories create $REPO \
  --repository-format=docker \
  --location=$REGION || true

gcloud builds submit \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}

gcloud run deploy ${SERVICE} \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE} \
  --allow-unauthenticated \
  --min-instances=1 \
  --timeout=3600
```

Once deployed, your public MCP endpoints:
- Health: `GET https://<service>-<hash>-<region>.a.run.app/health`
- SSE: `GET https://<service>-<hash>-<region>.a.run.app/mcp/sse`
- Messages: `POST https://<service>-<hash>-<region>.a.run.app/mcp/message`

### Calling over HTTP/SSE on Cloud Run

This server uses SSE sessions for streaming responses. To call tools directly over HTTP:

1) Start an SSE stream with a session id (keep this running):

```bash
curl -N -sS "https://<service>-<hash>-<region>.a.run.app/mcp/sse?session_id=dev-1"
```

2) In a separate terminal, send JSON-RPC messages bound to the same session id:

```bash
curl -sS -L -X POST "https://<service>-<hash>-<region>.a.run.app/mcp/message/?session_id=dev-1" \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

Notes:
- Include the trailing slash on `/mcp/message/` or use `-L` to follow a 307 redirect.
- If you see `session_id is required` or `Invalid session ID`, ensure the SSE stream is opened first with the same `session_id`.

### Troubleshooting (Cloud Run)

- Container failed to start / wrong port:
  - Cloud Run injects the `PORT` environment variable. Ensure your app binds to `$PORT`. This repo’s server reads `PORT` and defaults to 8080 if missing.
  - Avoid hardcoding a port; if you specify `--port` in deploy, match what the app listens on.
  - Verify in logs that the server is running on the expected port.
- HTTP 307 redirect on `/mcp/message`:
  - Use the trailing slash (`/mcp/message/`) or pass `-L` to curl.
- Session errors for JSON-RPC calls:
  - Open the SSE connection first and reuse the same `session_id` in the message URL.