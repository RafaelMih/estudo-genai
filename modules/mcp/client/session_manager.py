"""Gerenciador de sessão MCP reutilizável."""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from mcp import ClientSession, StdioServerParameters

from modules.mcp.client.stdio_client import notebook_safe_stdio_client
from shared.logger import get_logger

log = get_logger(__name__)


class MCPSessionManager:
    """Context manager assíncrono para sessões MCP."""

    def __init__(self, server_script: str | Path) -> None:
        self._server_script = str(server_script)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[ClientSession, None]:
        params = StdioServerParameters(
            command=sys.executable,
            args=[self._server_script],
        )
        async with notebook_safe_stdio_client(params) as (read, write):
            async with ClientSession(read, write) as sess:
                await sess.initialize()
                log.info(f"Sessão MCP iniciada: {self._server_script}")
                yield sess

    async def list_tools(self, session: ClientSession) -> list[dict]:
        result = await session.list_tools()
        return [
            {"name": t.name, "description": t.description, "schema": t.inputSchema}
            for t in result.tools
        ]

    async def call_tool(self, session: ClientSession, name: str, args: dict[str, Any]) -> str:
        result = await session.call_tool(name, args)
        return result.content[0].text if result.content else ""
