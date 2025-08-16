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
   - Paste your Hireflix token when prompted (stored per user, not in files)

## Configure the Cloud Run URL

Edit `librechat.yaml` and replace `https://REPLACE_WITH_CLOUD_RUN_URL/mcp` with your Cloud Run base URL. Example:

```
https://hiring-router-mcp-xxxx-europe-west1.a.run.app/mcp
```

LibreChat will use:
- GET /mcp/sse for streaming
- POST /mcp/message for requests

## Notes
- Each user enters their own Hireflix token in the UI; LibreChat injects it as `Authorization: Bearer <token>`.
- No credentials are committed.
