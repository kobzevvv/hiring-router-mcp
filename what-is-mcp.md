## What is MCP (Model Context Protocol)?

MCP is a simple protocol that lets AI clients (like Claude Desktop) talk to external tools and data sources through lightweight servers. Think of it as a standard way for an AI to call your functions ("tools") securely and reliably.

At a glance:
- **Client**: The AI app (e.g., Claude Desktop)
- **Server**: Your program that exposes tools/resources
- **Transport**: Usually stdio (spawned process) for Desktop apps
- **Tools**: Named functions the client can call with JSON arguments
- **Resources/Prompts**: Optional data or reusable prompts the server can expose

This repository implements an MCP server for hiring/recruitment workflows that Claude can use on demand.

## How FastMCP works (Python)

FastMCP is a thin Python server framework from the MCP SDK that makes it easy to:
- Define tools (regular Python callables)
- Register them with decorators
- Run a stdio server that Claude can auto-start

When Claude needs your tools, it spawns your command (from its config), then exchanges JSON messages over stdio: list tools, call a tool, stream results, etc.

### Minimal example from this repo

```31:41:src/hiring_router_mcp/server.py
def build_server() -> FastMCP:
    config = load_config()
    setup_logging(config.log_dir, config.log_level)

    server = FastMCP("hiring-router")

    # Register tools
    # Register tools (logging of calls can be added later per tool)
    server.tool()(market_research)
    server.tool()(generate_job_post)
    server.tool()(generate_application_form)
```

The server registers more tools and then `run()` starts the stdio loop. Claude discovers available tools and invokes them with JSON args.

## Core MCP concepts

- **Tools**: Named functions with typed parameters and JSON-serializable results. In this repo:
  - Recruiter tools: `market_research`, `generate_job_post`, `generate_application_form`, `generate_quiz`, `generate_homework`, `generate_candidate_journey`, `generate_funnel_report`
  - Candidate tools: `candidate_assistant`, `resume_optimizer`, `interview_prep`, `salary_research`
  - Analytics tools: `get_request_analytics`, `export_logs`
- **Routing**: A convenience tool that routes natural language tasks to specific tools:
  - `route_hiring_task(user_type, task_description, context?)`
- **Resources/Prompts**: Not heavily used here yet, but MCP supports exposing static or generated data, and prompt templates.
- **Transport**: stdio. Claude spawns a process (your command) and communicates over stdin/stdout.

## How Claude Desktop integrates

Claude Desktop reads `claude_desktop_config.json` and knows how to start your MCP server:

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

When a chat message asks for your tools (e.g., "Hiring Router, are you here?"), Claude will spawn the server and call tools via MCP.

## What this repository provides

- A Python MCP server using FastMCP:
  - `src/hiring_router_mcp/server.py`: builds and runs the server, registers tools, defines `get_available_tools` and `route_hiring_task`
  - `src/hiring_router_mcp/config.py`: environment and logging configuration
  - `src/hiring_router_mcp/logging_setup.py`: JSON log setup to `./hiring_logs`
  - `src/hiring_router_mcp/tools/`: recruiter, candidate, analytics tool implementations
  - `pyproject.toml`: defines the console entry `hiring-router-mcp` and module entry `hiring_router_mcp`

## Install, Run, and Test

Install from GitHub:
```bash
pip install git+https://github.com/kobzevvv/hiring-router-mcp.git
```

Run manually (for local testing):
```bash
python -m hiring_router_mcp

# or, via console script
hiring-router-mcp
```

Test with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python -m hiring_router_mcp
```

Wire up Claude Desktop (Mac path shown):
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

Verification prompts inside Claude:
- "Hiring Router, are you here?"
- "Call get_available_tools on the hiring-router server for recruiter."
- "Use hiring-router to research Python developers in Moscow."

## FAQ

- Is this a Python library or a server?
  - Both. It installs as a Python package that also exposes an MCP server entry. Claude treats it as a server.

- Does it need Node.js?
  - No. The server is pure Python (FastMCP). Only the optional Inspector uses Node to spawn the Python process.

- Do I need to run it manually for Claude?
  - Usually no. Claude auto-starts it using your config. Manual run is helpful for debugging.

- Where does it log?
  - `./hiring_logs/` by default. Configurable via `.env` and `config.py`.

## References

- Repo: [kobzevvv/hiring-router-mcp](https://github.com/kobzevvv/hiring-router-mcp)
- Model Context Protocol (Anthropic): [modelcontextprotocol.io](https://modelcontextprotocol.io)


