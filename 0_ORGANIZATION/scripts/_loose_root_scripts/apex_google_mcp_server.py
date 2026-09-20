#!/usr/bin/env python3
"""
APEX Local Google Multi-Account MCP Server
Exposes Google APIs as local MCP tools via JSON-RPC on port 8888.
Supports multiple service accounts and OAuth accounts.
"""

import json
import sys
import os
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/root/.agents/skills/apex-sovereign-supreme/scripts")
from runtime_auth import authorization_error, is_authorized
from apex_google_multi_account import (
    get_account_manager,
    GoogleDriveClient, GmailClient, GooglePhotosClient,
    GoogleSheetsClient, GoogleDocsClient, GoogleCalendarClient,
    list_all_accounts, ACCOUNT_REGISTRY, AuthType
)


class LocalGoogleMCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for local Google Multi-Account MCP server."""

    def log_message(self, format, *args):
        pass

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ["/", "/health"]:
            am = get_account_manager()
            accounts = am.list_accounts()
            active_accounts = [a for a in accounts if a["status"] == "active"]

            self._send_json({
                "status": "OK",
                "service": "APEX Local Google Multi-Account MCP Server",
                "version": "2.0.0",
                "accounts": {
                    "total": len(accounts),
                    "active": len(active_accounts),
                },
                "tools": self._get_all_tools()
            })
        elif self.path == "/accounts":
            am = get_account_manager()
            self._send_json({"accounts": am.list_accounts()})
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"

        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        method = req.get("method", "")
        req_id = req.get("id", 1)
        params = req.get("params", {})

        if method in ["tools/call", "accounts/auth"] and not is_authorized(self.headers):
            self._send_json({"jsonrpc": "2.0", "id": req_id, "error": authorization_error()}, status=401)
            return

        if method == "initialize":
            self._send_json({
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "APEX Local Google Multi-Account MCP", "version": "2.0.0"}
                }
            })
            return

        if method == "tools/list":
            self._send_json({"jsonrpc": "2.0", "id": req_id, "result": {"tools": self._get_all_tools()}})
            return

        if method == "tools/call":
            tool_name = params.get("name", "")
            args = params.get("arguments", {})

            try:
                result = self._execute_tool(tool_name, args)
                self._send_json({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}})
            except Exception as e:
                self._send_json({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}})
            return

        if method == "accounts/list":
            am = get_account_manager()
            self._send_json({"jsonrpc": "2.0", "id": req_id, "result": {"accounts": am.list_accounts()}})
            return

        if method == "accounts/auth":
            account_name = params.get("account", "")
            if account_name:
                try:
                    config = ACCOUNT_REGISTRY.get(account_name)
                    if config and config.auth_type == AuthType.OAUTH:
                        am = get_account_manager()
                        results = {}
                        for service in ["drive", "gmail", "photos", "sheets", "docs", "calendar"]:
                            try:
                                am.get_service(account_name, service)
                                results[service] = "authenticated"
                            except Exception as e:
                                results[service] = f"failed: {e}"
                        self._send_json({"jsonrpc": "2.0", "id": req_id, "result": {"account": account_name, "services": results}})
                    else:
                        self._send_json({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": f"Account '{account_name}' not found or not OAuth type"}})
                except Exception as e:
                    self._send_json({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}})
            else:
                self._send_json({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "account parameter required"}})
            return

        self._send_json({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found"}})

    def _get_all_tools(self) -> List[Dict]:
        """Get all available tools with account-specific variants."""
        tools = []

        # Get active accounts per type
        am = get_account_manager()
        accounts = am.list_accounts()
        sa_accounts = [a["name"] for a in accounts if a["auth_type"] == "service_account" and a["status"] == "active"]
        oauth_accounts = [a["name"] for a in accounts if a["auth_type"] == "oauth" and a["status"] == "active"]

        all_drive_accounts = sa_accounts + oauth_accounts
        all_sheets_accounts = sa_accounts + oauth_accounts
        all_docs_accounts = sa_accounts + oauth_accounts
        all_calendar_accounts = oauth_accounts
        gmail_accounts = oauth_accounts
        photos_accounts = oauth_accounts

        # Account parameter schema
        def account_param(accounts_list, default=None):
            return {
                "type": "string",
                "enum": accounts_list,
                "default": default or (accounts_list[0] if accounts_list else ""),
                "description": f"Account to use. Available: {', '.join(accounts_list)}"
            }

        # Drive tools
        for acc in all_drive_accounts:
            suffix = f" ({acc})" if len(all_drive_accounts) > 1 else ""
            tools.extend([
                {"name": f"drive_{acc}.list_files", "description": f"List Google Drive files{suffix}", "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "description": "Drive search query"}, "page_size": {"type": "integer", "default": 50}}, "required": []}},
                {"name": f"drive_{acc}.search_files", "description": f"Search Google Drive files{suffix}", "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "description": "Drive search query (e.g., \"name contains 'RICO'\")"}, "page_size": {"type": "integer", "default": 50}}, "required": ["query"]}},
                {"name": f"drive_{acc}.get_file", "description": f"Get file metadata{suffix}", "inputSchema": {"type": "object", "properties": {"file_id": {"type": "string"}}, "required": ["file_id"]}},
                {"name": f"drive_{acc}.get_file_content", "description": f"Get file content as text{suffix}", "inputSchema": {"type": "object", "properties": {"file_id": {"type": "string"}}, "required": ["file_id"]}},
                {"name": f"drive_{acc}.list_folders", "description": f"List folders in parent{suffix}", "inputSchema": {"type": "object", "properties": {"parent_id": {"type": "string", "default": "root"}}, "required": []}},
            ])

        # Gmail tools
        for acc in gmail_accounts:
            suffix = f" ({acc})" if len(gmail_accounts) > 1 else ""
            tools.extend([
                {"name": f"gmail_{acc}.list_messages", "description": f"List Gmail messages{suffix}", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 50}, "label_ids": {"type": "array", "items": {"type": "string"}}}, "required": []}},
                {"name": f"gmail_{acc}.get_message", "description": f"Get full Gmail message{suffix}", "inputSchema": {"type": "object", "properties": {"msg_id": {"type": "string"}}, "required": ["msg_id"]}},
                {"name": f"gmail_{acc}.send_message", "description": f"Send Gmail message{suffix}", "inputSchema": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}, "cc": {"type": "array", "items": {"type": "string"}}, "bcc": {"type": "array", "items": {"type": "string"}}}, "required": ["to", "subject", "body"]}},
            ])

        # Photos tools
        for acc in photos_accounts:
            suffix = f" ({acc})" if len(photos_accounts) > 1 else ""
            tools.extend([
                {"name": f"photos_{acc}.list_albums", "description": f"List Google Photos albums{suffix}", "inputSchema": {"type": "object", "properties": {"page_size": {"type": "integer", "default": 50}}, "required": []}},
                {"name": f"photos_{acc}.list_media_items", "description": f"List photos/media items{suffix}", "inputSchema": {"type": "object", "properties": {"album_id": {"type": "string"}, "page_size": {"type": "integer", "default": 50}}, "required": []}},
            ])

        # Sheets tools
        for acc in all_sheets_accounts:
            suffix = f" ({acc})" if len(all_sheets_accounts) > 1 else ""
            tools.extend([
                {"name": f"sheets_{acc}.get_spreadsheet", "description": f"Get spreadsheet metadata{suffix}", "inputSchema": {"type": "object", "properties": {"spreadsheet_id": {"type": "string"}}, "required": ["spreadsheet_id"]}},
                {"name": f"sheets_{acc}.get_values", "description": f"Get values from range{suffix}", "inputSchema": {"type": "object", "properties": {"spreadsheet_id": {"type": "string"}, "range_name": {"type": "string"}}, "required": ["spreadsheet_id", "range_name"]}},
                {"name": f"sheets_{acc}.append_values", "description": f"Append values to range{suffix}", "inputSchema": {"type": "object", "properties": {"spreadsheet_id": {"type": "string"}, "range_name": {"type": "string"}, "values": {"type": "array", "items": {"type": "array"}}}, "required": ["spreadsheet_id", "range_name", "values"]}},
                {"name": f"sheets_{acc}.update_values", "description": f"Update values in range{suffix}", "inputSchema": {"type": "object", "properties": {"spreadsheet_id": {"type": "string"}, "range_name": {"type": "string"}, "values": {"type": "array", "items": {"type": "array"}}}, "required": ["spreadsheet_id", "range_name", "values"]}},
            ])

        # Docs tools
        for acc in all_docs_accounts:
            suffix = f" ({acc})" if len(all_docs_accounts) > 1 else ""
            tools.extend([
                {"name": f"docs_{acc}.get_document", "description": f"Get document metadata{suffix}", "inputSchema": {"type": "object", "properties": {"document_id": {"type": "string"}}, "required": ["document_id"]}},
                {"name": f"docs_{acc}.get_document_text", "description": f"Extract plain text from document{suffix}", "inputSchema": {"type": "object", "properties": {"document_id": {"type": "string"}}, "required": ["document_id"]}},
            ])

        # Calendar tools
        for acc in all_calendar_accounts:
            suffix = f" ({acc})" if len(all_calendar_accounts) > 1 else ""
            tools.extend([
                {"name": f"calendar_{acc}.list_events", "description": f"List calendar events{suffix}", "inputSchema": {"type": "object", "properties": {"calendar_id": {"type": "string", "default": "primary"}, "max_results": {"type": "integer", "default": 50}, "time_min": {"type": "string"}, "time_max": {"type": "string"}}, "required": []}},
                {"name": f"calendar_{acc}.create_event", "description": f"Create calendar event{suffix}", "inputSchema": {"type": "object", "properties": {"calendar_id": {"type": "string", "default": "primary"}, "summary": {"type": "string"}, "start": {"type": "string", "description": "ISO 8601 start time"}, "end": {"type": "string", "description": "ISO 8601 end time"}, "description": {"type": "string"}, "attendees": {"type": "array", "items": {"type": "string"}}}, "required": ["summary", "start", "end"]}},
            ])

        # Account management tools
        tools.extend([
            {"name": "accounts.list", "description": "List all registered Google accounts with status", "inputSchema": {"type": "object", "properties": {}, "required": []}},
            {"name": "accounts.auth", "description": "Authenticate an OAuth account (run OAuth flow for all services)", "inputSchema": {"type": "object", "properties": {"account": {"type": "string", "description": "OAuth account name"}}, "required": ["account"]}},
        ])

        return tools

    def _execute_tool(self, tool_name: str, args: dict) -> Any:
        """Execute a tool and return result."""
        # Parse tool name: service_account.method or service.method
        if "." not in tool_name:
            raise ValueError(f"Invalid tool name format: {tool_name}")

        prefix, method = tool_name.split(".", 1)

        # Account management tools
        if prefix == "accounts":
            am = get_account_manager()
            if method == "list":
                return am.list_accounts()
            elif method == "auth":
                account = args.get("account", "")
                config = ACCOUNT_REGISTRY.get(account)
                if not config or config.auth_type != AuthType.OAUTH:
                    raise ValueError(f"Account '{account}' not found or not OAuth type")
                results = {}
                for service in ["drive", "gmail", "photos", "sheets", "docs", "calendar"]:
                    try:
                        am.get_service(account, service)
                        results[service] = "authenticated"
                    except Exception as e:
                        results[service] = f"failed: {e}"
                return {"account": account, "services": results}
            raise ValueError(f"Unknown account tool: {method}")

        # Parse service and account from prefix (e.g., "drive_glacier-gdrive")
        if "_" in prefix:
            service, account = prefix.split("_", 1)
        else:
            # Default account fallback
            service = prefix
            account = "glacier-gdrive" if service in ["drive", "sheets", "docs"] else "casey-oauth"

        # Execute based on service
        if service == "drive":
            client = GoogleDriveClient(account)
            if method == "list_files":
                return client.list_files(query=args.get("query"), page_size=args.get("page_size", 50))
            elif method == "search_files":
                return client.search_files(args["query"], args.get("page_size", 50))
            elif method == "get_file":
                return client.get_file(args["file_id"])
            elif method == "get_file_content":
                return {"content": client.get_file_content(args["file_id"])}
            elif method == "list_folders":
                return client.list_folders(args.get("parent_id", "root"))

        elif service == "gmail":
            client = GmailClient(account)
            if method == "list_messages":
                return client.list_messages(query=args.get("query"), max_results=args.get("max_results", 50), label_ids=args.get("label_ids"))
            elif method == "get_message":
                return client.get_message(args["msg_id"])
            elif method == "send_message":
                return client.send_message(args["to"], args["subject"], args["body"], args.get("cc"), args.get("bcc"))

        elif service == "photos":
            client = GooglePhotosClient(account)
            if method == "list_albums":
                return client.list_albums(args.get("page_size", 50))
            elif method == "list_media_items":
                return client.list_media_items(args.get("album_id"), args.get("page_size", 50))

        elif service == "sheets":
            client = GoogleSheetsClient(account)
            if method == "get_spreadsheet":
                return client.get_spreadsheet(args["spreadsheet_id"])
            elif method == "get_values":
                return client.get_values(args["spreadsheet_id"], args["range_name"])
            elif method == "append_values":
                return client.append_values(args["spreadsheet_id"], args["range_name"], args["values"])
            elif method == "update_values":
                return client.update_values(args["spreadsheet_id"], args["range_name"], args["values"])

        elif service == "docs":
            client = GoogleDocsClient(account)
            if method == "get_document":
                return client.get_document(args["document_id"])
            elif method == "get_document_text":
                return {"content": client.get_document_text(args["document_id"])}

        elif service == "calendar":
            client = GoogleCalendarClient(account)
            if method == "list_events":
                return client.list_events(args.get("calendar_id", "primary"), args.get("max_results", 50), args.get("time_min"), args.get("time_max"))
            elif method == "create_event":
                return client.create_event(args.get("calendar_id", "primary"), args["summary"], args["start"], args["end"], args.get("description", ""), args.get("attendees"))

        raise ValueError(f"Unknown tool: {tool_name}")


def main():
    port = 8888
    server = ThreadingHTTPServer(("127.0.0.1", port), LocalGoogleMCPHandler)
    print(f"🌐 APEX Local Google Multi-Account MCP Server running on http://127.0.0.1:{port}")
    print("   Multi-account support: Service Accounts + OAuth")
    print("   Tools: Drive, Gmail, Photos, Sheets, Docs, Calendar")
    server.serve_forever()


if __name__ == "__main__":
    main()