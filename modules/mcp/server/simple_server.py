"""Servidor MCP mínimo com duas tools: echo e add_numbers.
Roda via stdio — inicie com: python modules/mcp/server/simple_server.py"""

import asyncio
import mcp.server.stdio
from mcp.server import Server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp import types

app = Server("simple-demo-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="echo",
            description="Repete o texto fornecido.",
            inputSchema={
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Texto a repetir"}},
                "required": ["text"],
            },
        ),
        types.Tool(
            name="add_numbers",
            description="Soma dois números e retorna o resultado.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Primeiro número"},
                    "b": {"type": "number", "description": "Segundo número"},
                },
                "required": ["a", "b"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "echo":
        return [types.TextContent(type="text", text=f"Echo: {arguments['text']}")]
    elif name == "add_numbers":
        result = arguments["a"] + arguments["b"]
        return [types.TextContent(type="text", text=str(result))]
    else:
        raise ValueError(f"Tool desconhecida: {name}")


async def main() -> None:
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-demo-server",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
