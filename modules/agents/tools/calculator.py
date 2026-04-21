"""Tool de calculadora segura usando ast para evitar execução arbitrária."""

from __future__ import annotations

import ast
import operator

ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

TOOL_DEFINITION = {
    "name": "calculator",
    "description": "Avalia expressões matemáticas com segurança. Suporta +, -, *, /, **, %.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Expressão matemática (ex: '2 + 2 * 10')"}
        },
        "required": ["expression"],
    },
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    elif isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
        return ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPS:
        return ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Operação não permitida: {ast.dump(node)}")


def calculator(expression: str) -> str:
    """Avalia a expressão e retorna o resultado como string."""
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree.body)
        return str(result if result != int(result) else int(result))
    except ZeroDivisionError:
        return "Erro: divisão por zero"
    except Exception as e:
        return f"Erro: {e}"
