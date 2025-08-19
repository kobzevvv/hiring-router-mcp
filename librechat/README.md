# LibreChat for Recruiters

This folder runs a ready-to-use LibreChat instance pre-wired to your Hiring Router MCP on Cloud Run.

## Quick start

1. Install Docker and Docker Compose
2. Start LibreChat:

```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

3. Open http://localhost:3080
4. In the right panel → MCP Settings:
   - Select "Hiring Router"
   - No token required (MCP is open for now)

## Configure the Cloud Run URL

Edit `librechat.yaml` and set the MCP URL to your Cloud Run base URL. Example:

```
https://hiring-router-mcp-xxxx-europe-west1.a.run.app/mcp
```

LibreChat will use:
- GET /mcp/sse for streaming
- POST /mcp/message for requests

## Notes
- This setup does not require per-user tokens. Add headers later if you decide to restrict access.
