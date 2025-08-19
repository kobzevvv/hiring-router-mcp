## MCP Client Connect Guide

This guide explains how to connect any MCP-compatible client to the Hiring Router MCP server. It covers cloud-to-cloud HTTP/SSE integrations and local stdio integrations, with examples for common clients.

---

## Server Overview

The server exposes a client-agnostic MCP interface.

- **Transport**: HTTP + SSE (JSON-RPC 2.0 over HTTP)
- **Endpoints**:
  - GET `/health` — health probe
  - GET `/mcp/sse` — Server-Sent Events stream (server → client)
  - POST `/mcp/message` — JSON-RPC 2.0 messages (client → server)
- **Server name**: `hiring-router`
- **Auth**: none by default (front with a gateway if needed)
- **CORS**: enable on your reverse proxy if a browser-based client calls the server directly

Cloud example base URL (Google Cloud Run):
```
https://<service>-<hash>-<region>.a.run.app
```

Full URLs (session-bound):
```
SSE:     https://<base>/mcp/sse?session_id=<id>
Message: https://<base>/mcp/message/?session_id=<id>
Health:  https://<base>/health
```
Notes:
- Open the SSE stream first, using any stable `session_id` (e.g., a UUID). Reuse the same `session_id` on the message endpoint.
- Include a trailing slash on `/mcp/message/` or allow redirects (HTTP 307 → `/mcp/message/`).

Test with curl (SSE + Message):
```bash
# 1) Start SSE (keep running)
curl -N -sS "https://<base>/mcp/sse?session_id=dev-1"

# 2) In another terminal, send a message bound to the same session
curl -sS -L -X POST "https://<base>/mcp/message/?session_id=dev-1" -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' | jq .
```

---

## Supported Tools (discover dynamically)

Discover via `tools/list`. Examples include:
- `route_hiring_task`
- `get_available_tools`
- `market_research`, `generate_job_post`, `generate_application_form`, `generate_quiz`,
  `generate_homework`, `generate_candidate_journey`, `generate_funnel_report`
- `candidate_assistant`, `resume_optimizer`, `interview_prep`, `salary_research`
- `get_request_analytics`, `export_logs`

---

## Quick Client Matrix

- **Claude Desktop (stdio)**: supported
- **Generic HTTP/SSE clients (cloud→cloud)**: supported
- **MCP Inspector (dev tool)**: supported
- **Open Chat UI / LibreChat**: supported via HTTP/SSE configuration shown below

If your UI does not yet support MCP, you can still integrate by writing a small bridge that:
- POSTs JSON-RPC to `/mcp/message`
- Subscribes to `/mcp/sse` via `EventSource`

---

## Open Chat UI (generic HTTP/SSE connector)

If Open Chat UI supports adding a custom MCP HTTP connector, configure it with these fields:

```json
{
  "name": "hiring-router",
  "sseUrl": "https://<base>/mcp/sse?session_id=<id>",
  "messageUrl": "https://<base>/mcp/message/?session_id=<id>",
  "healthUrl": "https://<base>/health"
}
```

Client behavior:
- Open an `EventSource` to `sseUrl`
- Send JSON-RPC requests to `messageUrl`
- Optionally check `healthUrl` on startup

Browser example:
```js
const sessionId = crypto.randomUUID();
const base = "https://<base>";
const config = {
  sseUrl: `${base}/mcp/sse?session_id=${encodeURIComponent(sessionId)}`,
  messageUrl: `${base}/mcp/message/?session_id=${encodeURIComponent(sessionId)}`
};

const events = new EventSource(config.sseUrl);
events.onmessage = (e) => {
  const payload = JSON.parse(e.data); // JSON-RPC results/notifications
  // route payload to your UI state
};

async function rpc(method, params, id = String(Date.now())) {
  const res = await fetch(config.messageUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id, method, params })
  });
  return res.json();
}

// List tools
rpc("tools/list", {});

// Call a tool
rpc("tools/call", {
  name: "route_hiring_task",
  arguments: {
    user_type: "recruiter",
    task_description: "research Python developers",
    context: { location: "Moscow" }
  }
});
```

---

## LibreChat (generic HTTP/SSE connector)

If LibreChat offers a custom MCP HTTP connector, use the same configuration as above. Many systems also support environment-based configuration; a typical pattern is:

```env
MCP_HIRING_ROUTER_SSE_URL=https://<base>/mcp/sse
MCP_HIRING_ROUTER_MESSAGE_URL=https://<base>/mcp/message
MCP_HIRING_ROUTER_HEALTH_URL=https://<base>/health
```

Then reference these variables in the app’s connector settings if supported. If the client does not automatically negotiate sessions, append `?session_id=<id>` to both SSE and Message URLs and ensure the same value is used for both. If you receive an HTTP 307 on the Message endpoint, include the trailing slash (`/mcp/message/`) or allow redirects.

---

## Claude Desktop (stdio transport)

Claude Desktop launches MCP servers via stdio. Add an entry to `claude_desktop_config.json`:

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

Alternative using the installed console script:

```json
{
  "mcpServers": {
    "hiring-router": { "command": "hiring-router-mcp" }
  }
}
```

Verify with the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python -m hiring_router_mcp
```

---

<!-- Deep Research MCP example removed: feature is out of scope for this project. -->

---

## Cloud-to-Cloud Deployment

Any platform that serves an ASGI app works. Google Cloud Run example (public service):

- SSE: `GET https://<service>-<hash>-<region>.a.run.app/mcp/sse?session_id=<id>`
- Message: `POST https://<service>-<hash>-<region>.a.run.app/mcp/message/?session_id=<id>`
- Health: `GET https://<service>-<hash>-<region>.a.run.app/health`

If you place the service behind an API gateway:
- Add authentication at the gateway (e.g., API key, JWT)
- Forward headers to the backend
- Enable CORS for browser-based clients

---

## JSON-RPC Reference (client → server)

- List tools
```http
POST /mcp/message
Content-Type: application/json

{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}
```

- Call a tool
```http
POST /mcp/message
Content-Type: application/json

{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"get_available_tools","arguments":{"user_type":"recruiter"}}}
```

---

## Environment Variables (server)

Create a `.env` at server runtime if desired:

```env
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_DIR=./hiring_logs
LOG_WEBHOOK_URL=https://your-worker.example.workers.dev/ingest
LOG_WEBHOOK_SECRET=your_shared_secret
LOG_CLIENT_ID=staging-macbook
HH_API_KEY=your_api_key_here
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook
```

---

## Troubleshooting

- Verify health: `GET /health` returns `{ "ok": true }`
- Validate endpoints with curl as shown above
- If the UI shows no events, ensure SSE is reachable from the browser (CORS/proxy)
- If using Claude Desktop, ensure the configured `python` is on PATH and restart the app
- Use MCP Inspector to confirm the server runs without errors
 - HTTP 307 on `/mcp/message`: include trailing slash or follow redirects
 - `session_id is required` / `Invalid session ID`: open SSE first and reuse the same `session_id` on the message endpoint

---

## Security Notes

- Add authentication and rate limiting at your gateway if running public cloud endpoints
- For webhook logging, an HMAC signature (`X-Signature: sha256=<hex>`) is sent when `LOG_WEBHOOK_SECRET` is configured
- The server avoids logging raw task text and full arguments by default; see data privacy notes in `DATA-PRIVACY.md`

---

## Need help?

Open an issue or discussion on the repository with the client name and the URLs you attempted to use; include any error messages.
