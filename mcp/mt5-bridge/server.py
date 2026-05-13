#!/usr/bin/env python3
"""mt5-bridge MCP server — JSON-RPC 2.0."""
from __future__ import annotations

import json
import sys

def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    if method == "initialize":
        return {"jsonrpc": "2.0", "result": {"name": "mt5-bridge"}, "id": request.get("id")}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "result": {"tools": []}, "id": request.get("id")}
    return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request.get("id")}

def main():
    for line in sys.stdin:
        request = json.loads(line.strip())
        response = handle_request(request)
        print(json.dumps(response), flush=True)

if __name__ == "__main__":
    main()
