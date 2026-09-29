

import ast
import operator
import math


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculate(expression: str) -> int | float:
    """Evaluate numbers, parentheses, +, -, *, and / from a math expression."""
    if not expression or len(expression) > 200:
        raise ValueError("Expression must contain 1 to 200 characters.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
    except (SyntaxError, ZeroDivisionError, OverflowError) as error:
        raise ValueError(f"Invalid arithmetic expression: {error}") from error

    if not math.isfinite(result):
        raise ValueError("The result must be a finite number.")
    return result


def _evaluate(node: ast.expr) -> int | float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        if not math.isfinite(node.value):
            raise ValueError("Numbers must be finite.")
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        return _BINARY_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))

    raise ValueError("Only numbers, parentheses, +, -, *, and / are allowed.")
