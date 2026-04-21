"""Servidor MCP com SQLite como resource e tools de query."""

import asyncio
import json
import sqlite3
from pathlib import Path

import mcp.server.stdio
from mcp.server import Server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp import types

DB_PATH = "modules/mcp/demo.db"
app = Server("database-server")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT
            )
        """)
        if conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0] == 0:
            conn.executemany("INSERT INTO concepts (name, category, description) VALUES (?, ?, ?)", [
                ("RAG", "Técnica", "Retrieval-Augmented Generation — combina busca com geração"),
                ("Embedding", "Conceito", "Representação vetorial de texto em alta dimensão"),
                ("ChromaDB", "Ferramenta", "Banco de dados vetorial open-source"),
                ("MCP", "Protocolo", "Model Context Protocol para integração de ferramentas"),
                ("ReAct", "Padrão", "Reasoning + Acting — padrão de agentes autônomos"),
            ])
            conn.commit()


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_concepts",
            description="Busca conceitos no banco de dados por nome ou categoria.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Termo de busca"},
                    "category": {"type": "string", "description": "Filtrar por categoria (opcional)"},
                },
                "required": ["search"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "query_concepts":
        search = f"%{arguments['search']}%"
        category = arguments.get("category")
        with get_connection() as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM concepts WHERE (name LIKE ? OR description LIKE ?) AND category = ?",
                    (search, search, category)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM concepts WHERE name LIKE ? OR description LIKE ?",
                    (search, search)
                ).fetchall()
        result = [dict(row) for row in rows]
        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    raise ValueError(f"Tool desconhecida: {name}")


async def main() -> None:
    init_db()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="database-server",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
