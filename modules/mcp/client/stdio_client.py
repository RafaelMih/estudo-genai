"""Cliente MCP via stdio com wrapper seguro para Windows/Jupyter."""

from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = str(Path("modules/mcp/server/simple_server.py"))
DEFAULT_ERRLOG = Path(".mcp_logs/stdio_client.err.log")


@asynccontextmanager
async def notebook_safe_stdio_client(
    server_params: StdioServerParameters,
    errlog_path: str | Path | None = None,
) -> AsyncGenerator[tuple[object, object], None]:
    """Wrap stdio_client with a real file-backed stderr on Windows/Jupyter."""

    errlog_handle = None
    try:
        if sys.platform == "win32":
            log_path = Path(errlog_path) if errlog_path else DEFAULT_ERRLOG
            log_path.parent.mkdir(parents=True, exist_ok=True)
            errlog_handle = log_path.open("a", encoding="utf-8")
            async with stdio_client(server_params, errlog=errlog_handle) as streams:
                yield streams
        else:
            async with stdio_client(server_params) as streams:
                yield streams
    finally:
        if errlog_handle is not None:
            errlog_handle.close()


async def run_demo() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=None,
    )

    async with notebook_safe_stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("=== MCP CLIENT DEMO ===\n")

            tools_result = await session.list_tools()
            print(f"Tools disponíveis ({len(tools_result.tools)}):")
            for tool in tools_result.tools:
                print(f"  • {tool.name}: {tool.description}")

            print()

            echo_result = await session.call_tool("echo", {"text": "Olá do cliente MCP!"})
            print(f"echo result: {echo_result.content[0].text}")

            add_result = await session.call_tool("add_numbers", {"a": 42, "b": 58})
            print(f"add_numbers(42, 58) = {add_result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(run_demo())
