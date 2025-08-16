# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# System deps (optional)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src
COPY records.sample.json /app/records.json

# Install package
RUN pip install --upgrade pip && pip install -e .

EXPOSE 8080

# Run the HTTP/SSE FastMCP server mounted at /mcp
CMD ["python", "-m", "hiring_router_mcp.server_http_sse"]


