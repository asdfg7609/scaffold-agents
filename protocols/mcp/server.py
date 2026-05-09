"""
protocols/mcp/server.py

MCP (Model Context Protocol) server.
Exposes pure functions from domain/tools/ via the MCP standard.
Activate: ENABLE_MCP_SERVER=true  |  python -m protocols.mcp.server
"""
import os
import json
from domain.tools.green.search import search_news, read_url
from domain.tools.yellow.write_file import write_file, list_files

MCP_TOOLS = [
    {"name": "search_news",  "description": "Search news and latest information.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]}},
    {"name": "read_url",     "description": "Read the body content of a URL.",     "inputSchema": {"type": "object", "properties": {"url":   {"type": "string"}}, "required": ["url"]}},
    {"name": "write_file",   "description": "Save a file.",                         "inputSchema": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename","content"]}},
    {"name": "list_files",   "description": "Return the list of saved files.",      "inputSchema": {"type": "object", "properties": {}}},
]

TOOL_FNS = {
    "search_news": lambda a: search_news(**a),
    "read_url":    lambda a: read_url(**a),
    "write_file":  lambda a: write_file(**a),
    "list_files":  lambda a: list_files(),
}


def handle_mcp_request(request: dict) -> dict:
    method  = request.get("method", "")
    params  = request.get("params", {})
    req_id  = request.get("id", "1")

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        fn   = TOOL_FNS.get(name)
        if fn is None:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {name}"}}
        try:
            result = fn(args)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}], "isError": False}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(e)}], "isError": True}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def start_mcp_server(host: str = "0.0.0.0", port: int = 8080):
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body     = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            response = handle_mcp_request(json.loads(body))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        def log_message(self, *args): pass

    print(f"MCP server started: http://{host}:{port}")
    HTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    start_mcp_server(port=int(os.environ.get("MCP_SERVER_PORT", "8080")))
