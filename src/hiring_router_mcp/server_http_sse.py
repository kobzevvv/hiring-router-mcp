from __future__ import annotations

import os
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .server import build_server


# Build the FastMCP server with all registered tools
_server = build_server()

# Configure SSE endpoints under /mcp with explicit paths to match expectations
_server.settings.sse_path = "/mcp/sse"
_server.settings.message_path = "/mcp/message"


@_server.custom_route("/health", methods=["GET"])
async def health(_: Request) -> Response:
    return JSONResponse({"ok": True})


# Simple root endpoint for environment health checks
@_server.custom_route("/", methods=["GET"])
async def root(_: Request) -> Response:
    return JSONResponse({"service": "hiring-router-mcp", "status": "ok"})


# Expose the ASGI app. This serves:
# - GET  /mcp/sse       (SSE stream)
# - POST /mcp/message   (client→server JSON-RPC over HTTP)
app = _server.sse_app()


if __name__ == "__main__":
    import uvicorn

    port_str = os.getenv("PORT", "8080")
    try:
        port = int(port_str)
    except ValueError:
        port = 8080

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


