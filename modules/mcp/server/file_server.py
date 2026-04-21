"""Servidor MCP que expõe arquivos locais como Resources.
Demonstra o primitivo Resource: leitura de dados, sem side effects."""

import asyncio
from pathlib import Path

import mcp.server.stdio
from mcp.server import Server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp import types

DOCS_DIR = Path("modules/rag/data/sample_docs")

app = Server("file-resource-server")


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    resources = []
    for path in DOCS_DIR.glob("*.*"):
        resources.append(
            types.Resource(
                uri=f"file://{path.as_posix()}",
                name=path.name,
                description=f"Documento: {path.name}",
                mimeType="text/plain",
            )
        )
    return resources


@app.read_resource()
async def read_resource(uri: str) -> str:
    path_str = uri.removeprefix("file://")
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return path.read_text(encoding="utf-8", errors="ignore")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_files",
            description="Lista todos os arquivos disponíveis no servidor.",
            inputSchema={"type": "object", "properties": {}},
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "list_files":
        files = [p.name for p in DOCS_DIR.glob("*.*")]
        return [types.TextContent(type="text", text="\n".join(files))]
    raise ValueError(f"Tool desconhecida: {name}")


async def main() -> None:
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="file-resource-server",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
