from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP


@dataclass
class Record:
    id: str
    title: str
    text: str
    metadata: Dict[str, Any]


def _load_records(records_path: Path | str) -> List[Record]:
    path = Path(records_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Records file not found at: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Records JSON must be a list of objects")
    return [Record(**item) for item in data]


def create_server(
    records_path: Path | str,
    name: Optional[str] = None,
    instructions: Optional[str] = None,
) -> FastMCP:
    """Create an HTTP-capable FastMCP server for ChatGPT Deep Research.

    This server intentionally exposes ONLY two tools required by ChatGPT Deep Research:
    - search(query: str) -> {"ids": List[str]}
    - fetch(id: str) -> Record

    The server loads records from a JSON file where each item has fields:
    {"id": str, "title": str, "text": str, "metadata": object}.

    Tool usage guidance for ChatGPT (critical for good results):
    - search: Provide natural-language or keyword queries. The server performs a
      simple case-insensitive keyword match across title, text, and flattened metadata values.
      It returns a list of matching record IDs to subsequently fetch.
    - fetch: Provide a single ID returned by search. The server returns the full
      record so ChatGPT can analyze, quote, and cite it.
    """

    records: List[Record] = _load_records(records_path)
    id_to_record: Dict[str, Record] = {rec.id: rec for rec in records}

    server = FastMCP(name=name or "Deep Research MCP", instructions=instructions)

    @server.tool()
    def search(query: str) -> Dict[str, List[str]]:
        """Search across the record corpus and return matching IDs.

        Guidance for ChatGPT:
        - Accepts free-form queries (keywords, phrases, or questions)
        - Matches any query token across title, text, and metadata values
        - Returns a list of matching record IDs for use with fetch()
        - If no matches are found, returns an empty list
        """
        normalized_tokens = [tok for tok in (query or "").lower().split() if tok]
        if not normalized_tokens:
            return {"ids": []}

        matching_ids: List[str] = []
        for record in records:
            aggregate_text = " ".join(
                [
                    record.title or "",
                    record.text or "",
                    " ".join(
                        [str(v) for v in (record.metadata or {}).values()]
                    ),
                ]
            ).lower()
            if any(token in aggregate_text for token in normalized_tokens):
                matching_ids.append(record.id)
        return {"ids": matching_ids}

    @server.tool()
    def fetch(id: str) -> Dict[str, Any]:
        """Fetch a single record by ID and return the complete object.

        Guidance for ChatGPT:
        - Provide an ID returned by search()
        - The full record includes title, text, and metadata; cite these fields as needed
        - If the ID is unknown, an error is raised
        """
        if id not in id_to_record:
            raise ValueError(f"Unknown record ID: {id}")
        return asdict(id_to_record[id])

    return server


def run() -> None:
    """Run the Deep Research server over HTTP.

    Configuration via environment variables:
    - DEEP_RESEARCH_RECORDS_PATH: Path to JSON records file
    - PORT: Port to bind the HTTP server (default: 8000)
    - BIND: Host/interface to bind (default: 0.0.0.0)

    The HTTP transport path is /mcp/ by default.
    """
    records_path = os.getenv("DEEP_RESEARCH_RECORDS_PATH", "./records.json")
    port_str = os.getenv("PORT", "8000")
    bind_host = os.getenv("BIND", "0.0.0.0")

    try:
        port = int(port_str)
    except ValueError:
        raise ValueError(f"PORT must be an integer, got: {port_str}")

    server = create_server(records_path=records_path)
    # HTTP transport is required for ChatGPT Deep Research
    server.run(transport="http", host=bind_host, port=port)


if __name__ == "__main__":
    run()


