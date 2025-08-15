## Data Privacy and Logging

This document explains how we minimize and protect personal data in logs.

### Goals
- Avoid storing personally identifiable information (PII) wherever feasible
- Preserve observability and debuggability via safe metadata
- Support centralized ingestion with signature verification

### What We Log (Safe by Design)
- Event metadata: `event`, `timestamp`, `level`, `logger`, `message`
- Correlation: `request_id` (UUIDv4), `client_id` (from env)
- Performance: `duration_ms` on results/errors
- Tool info: `tool` name, `result_type`
- Arguments: only `arg_keys` (names), not values
- Routing: `user_type`, `description_length` (integer), `context_keys` (names), `routed_to`
- User: `user_hash` (SHA-256 of provided `user_id`) instead of raw identifier

### What We Explicitly Do Not Log
- Raw `task_description`
- Full `context` values
- Full tool argument values
- Any secrets or API tokens

### Code References
- Formatter and file/webhook handlers: `src/hiring_router_mcp/logging_setup.py`
- Tool-call logging (privacy-preserving arg key capture, request IDs): `src/hiring_router_mcp/server.py` within `_register_with_logging`
- Routing logs (hashing user IDs, masking text): `src/hiring_router_mcp/server.py` inside `route_hiring_task`

### Webhook Security
- Optional HMAC signing: set `LOG_WEBHOOK_SECRET`. Outgoing requests include `X-Signature: sha256=<hex>` where `<hex>` is HMAC-SHA256 over the raw JSON body using the shared secret
- Receiver SHOULD verify signature before accepting the payload

### Configuration
- `LOG_LEVEL`: log verbosity, default `INFO`
- `LOG_DIR`: local JSONL directory, default `./hiring_logs`
- `LOG_WEBHOOK_URL`: optional remote sink (e.g., Cloudflare Worker)
- `LOG_WEBHOOK_SECRET`: optional HMAC signing secret
- `LOG_CLIENT_ID`: optional identifier to distinguish environments or nodes

### Rationale
Masking sensitive content reduces breach impact and aligns with least-privilege principles. The combination of `request_id`, `client_id`, and structured event types maintains operational visibility without storing raw PII.


