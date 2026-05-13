#!/usr/bin/env python3
"""metaeditor-bridge MCP server — JSON-RPC 2.0 over stdin/stdout."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tools import TOOLS, HANDLERS


def handle_request(request: dict) -> dict:
    rid = request.get("id")
    method = request.get("method", "")

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid,
                "result": {"name": "metaeditor-bridge",
                           "version": "1.0.0",
                           "capabilities": {"tools": True}}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid,
                "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        handler = HANDLERS.get(tool_name)
        if not handler:
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601,
                              "message": f"Unknown tool: {tool_name}"}}
        result = handler(tool_args)
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    return {"jsonrpc": "2.0", "id": rid,
            "error": {"code": -32601, "message": "Method not found"}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        request = json.loads(line)
        response = handle_request(request)
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
