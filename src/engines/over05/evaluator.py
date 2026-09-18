"""Evaluator Excel-compatibil pentru nucleul Over 0.5 V4.

Reproduce doar funcțiile și convențiile necesare formulelor din workbook.
Nu este un motor Excel general.
"""

from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from typing import Any

from openpyxl.formula.tokenizer import Tokenizer
from openpyxl.utils.cell import get_column_letter, range_boundaries
from openpyxl.workbook.workbook import Workbook


class XLException(Exception):
    """Eroare de evaluare echivalentă cu o eroare Excel (#VALUE!, #N/A, ciclu)."""


@lru_cache(maxsize=4096)
def parse_formula(formula: str) -> tuple:
    """Parsează o formulă Excel într-un AST prefixat."""
    tokens = [t for t in Tokenizer(formula).items if t.type != "WHITE-SPACE"]
    index = 0
    prec = {
        "=": 1,
        "<>": 1,
        "<": 1,
        ">": 1,
        "<=": 1,
        ">=": 1,
        "&": 2,
        "+": 3,
        "-": 3,
        "*": 4,
        "/": 4,
        "^": 5,
    }

    def expr(min_prec: int = 0) -> tuple:
        nonlocal index
        token = tokens[index]
        index += 1
        if token.type == "OPERAND":
            if token.subtype == "RANGE":
                node: tuple = ("ref", token.value)
            elif token.subtype == "TEXT":
                node = ("lit", token.value[1:-1].replace('""', '"'))
            elif token.subtype == "NUMBER":
                node = ("lit", float(token.value))
            else:
                node = ("lit", token.value == "TRUE")
        elif token.type == "OPERATOR-PREFIX":
            node = ("unary", token.value, expr(6))
        elif token.type == "PAREN" and token.subtype == "OPEN":
            node = expr()
            assert tokens[index].subtype == "CLOSE"
            index += 1
        elif token.type == "FUNC" and token.subtype == "OPEN":
            args: list[tuple] = []
            while not (tokens[index].type == "FUNC" and tokens[index].subtype == "CLOSE"):
                args.append(expr())
                if tokens[index].type == "SEP":
                    index += 1
                else:
                    break
            assert tokens[index].subtype == "CLOSE"
            index += 1
            node = ("call", token.value[:-1], tuple(args))
        else:
            raise ValueError((token.value, formula))

        while index < len(tokens):
            token = tokens[index]
            if token.type == "OPERATOR-POSTFIX":
                index += 1
                node = ("op", "/", node, ("lit", 100))
                continue
            if token.type != "OPERATOR-INFIX" or prec[token.value] < min_prec:
                break
            index += 1
            node = ("op", token.value, node, expr(prec[token.value] + 1))
        return node

    ast = expr()
    if index != len(tokens):
        raise ValueError((formula, index, len(tokens)))
    return ast


def flatten(value: Any):
    if isinstance(value, list):
        for item in value:
            yield from flatten(item)
    else:
        yield value


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def excel_number(value: Any) -> float:
    """Convertește o valoare la număr după aritmetica Excel (blank → 0)."""
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    raise XLException("VALUE")


def excel_text(value: Any) -> str:
    if value is None:
        return ""
    if is_number(value):
        return str(int(value)) if value == int(value) else str(value)
    return str(value)


def criteria_match(value: Any, criteria: Any) -> bool:
    """Potrivire COUNTIF/COUNTIFS/SUMIFS, fără sensibilitate la majuscule."""
    if isinstance(criteria, str):
        for op in (">=", "<=", "<>", ">", "<", "="):
            if criteria.startswith(op):
                rest = criteria[len(op) :]
                try:
                    right: Any = float(rest)
                except ValueError:
                    right = rest
                if is_number(right) and not is_number(value):
                    return False
                return excel_compare(value, right, op)
        return excel_compare(value, criteria, "=")
    if is_number(criteria):
        return is_number(value) and float(value) == float(criteria)
    return excel_compare(value, criteria, "=")


def excel_compare(left: Any, right: Any, op: str) -> bool:
    if left is None:
        left = "" if isinstance(right, str) else 0
    if right is None:
        right = "" if isinstance(left, str) else 0
    key_left = (1, left.casefold()) if isinstance(left, str) else (0, left)
    key_right = (1, right.casefold()) if isinstance(right, str) else (0, right)
    ops = {
        "=": lambda: key_left == key_right,
        "<>": lambda: key_left != key_right,
        "<": lambda: key_left < key_right,
        ">": lambda: key_left > key_right,
        "<=": lambda: key_left <= key_right,
        ">=": lambda: key_left >= key_right,
    }
    return ops[op]()


class WorkbookEngine:
    """Evaluează formulele unui workbook, cu override-uri pe celule de input."""

    def __init__(self, workbook: Workbook, overrides: dict[tuple[str, str], Any] | None = None) -> None:
        self.wb = workbook
        self.overrides = overrides or {}
        self.memo: dict[tuple[str, str], Any] = {}
        self.visiting: set[tuple[str, str]] = set()

    def cell(self, sheet: str, coord: str) -> Any:
        coord = coord.replace("$", "")
        key = (sheet, coord)
        if key in self.overrides:
            return self.overrides[key]
        if key in self.memo:
            return self.memo[key]
        if key in self.visiting:
            raise XLException("CYCLE")
        raw = self.wb[sheet][coord].value
        if not (isinstance(raw, str) and raw.startswith("=")):
            return raw
        self.visiting.add(key)
        try:
            result = self.eval_ast(parse_formula(raw), sheet)
        finally:
            self.visiting.remove(key)
        self.memo[key] = result
        return result

    def ref(self, ref: str, sheet: str) -> Any:
        if "!" in ref:
            sheet, ref = ref.rsplit("!", 1)
            sheet = sheet.strip("'").replace("''", "'")
        ref = ref.replace("$", "")
        if ":" not in ref:
            return self.cell(sheet, ref)
        min_col, min_row, max_col, max_row = range_boundaries(ref)
        return [
            self.cell(sheet, f"{get_column_letter(col)}{row}")
            for row in range(min_row, max_row + 1)
            for col in range(min_col, max_col + 1)
        ]

    def eval_ast(self, ast: tuple, sheet: str) -> Any:
        kind = ast[0]
        if kind == "lit":
            return ast[1]
        if kind == "ref":
            return self.ref(ast[1], sheet)
        if kind == "unary":
            return excel_number(self.eval_ast(ast[2], sheet)) * (1 if ast[1] == "+" else -1)
        if kind == "op":
            op = ast[1]
            left = self.eval_ast(ast[2], sheet)
            right = self.eval_ast(ast[3], sheet)
            if op in {"=", "<>", "<", ">", "<=", ">="}:
                return excel_compare(left, right, op)
            if op == "&":
                return excel_text(left) + excel_text(right)
            x = excel_number(left)
            y = excel_number(right)
            return {
                "+": lambda: x + y,
                "-": lambda: x - y,
                "*": lambda: x * y,
                "/": lambda: x / y,
                "^": lambda: x**y,
            }[op]()

        name, args = ast[1], ast[2]
        if name == "IF":
            return self.eval_ast(args[1] if self.eval_ast(args[0], sheet) else args[2], sheet)
        if name == "IFERROR":
            try:
                return self.eval_ast(args[0], sheet)
            except (XLException, ZeroDivisionError, ValueError, OverflowError):
                return self.eval_ast(args[1], sheet)

        values = [self.eval_ast(arg, sheet) for arg in args]
        numbers = [item for item in flatten(values) if is_number(item)]
        if name == "COUNT":
            return len(numbers)
        if name == "COUNTBLANK":
            return sum(1 for item in flatten(values) if item is None or item == "")
        if name == "COUNTIF":
            return sum(1 for item in flatten(values[0]) if criteria_match(item, values[1]))
        if name == "COUNTIFS":
            ranges = [list(flatten(values[i])) for i in range(0, len(values), 2)]
            crits = [values[i] for i in range(1, len(values), 2)]
            return sum(
                1
                for idx in range(len(ranges[0]))
                if all(criteria_match(ranges[j][idx], crits[j]) for j in range(len(ranges)))
            )
        if name == "SUMIFS":
            summed = list(flatten(values[0]))
            ranges = [list(flatten(values[i])) for i in range(1, len(values), 2)]
            crits = [values[i] for i in range(2, len(values), 2)]
            total = 0.0
            for idx, item in enumerate(summed):
                if all(criteria_match(ranges[j][idx], crits[j]) for j in range(len(ranges))):
                    if is_number(item):
                        total += float(item)
            return total
        if name == "ISNUMBER":
            return is_number(values[0])
        if name == "NOT":
            flag = values[0]
            if isinstance(flag, bool):
                return not flag
            if is_number(flag):
                return float(flag) == 0.0
            raise XLException("VALUE")
        if name == "MOD":
            numerator = excel_number(values[0])
            denominator = excel_number(values[1])
            return numerator - denominator * math.floor(numerator / denominator)
        if name == "SUM":
            return sum(numbers)
        if name == "AVERAGE":
            return sum(numbers) / len(numbers)
        if name == "MIN":
            return min(numbers) if numbers else 0
        if name == "MAX":
            return max(numbers) if numbers else 0
        if name == "AND":
            return all(values)
        if name == "OR":
            return any(values)
        if name == "ABS":
            return abs(excel_number(values[0]))
        if name == "SQRT":
            return math.sqrt(excel_number(values[0]))
        if name == "EXP":
            return math.exp(excel_number(values[0]))
        if name == "LN":
            return math.log(excel_number(values[0]))
        if name == "POWER":
            return excel_number(values[0]) ** excel_number(values[1])
        if name == "ROUND":
            return float(
                Decimal(str(values[0])).quantize(
                    Decimal(1).scaleb(-int(values[1])),
                    rounding=ROUND_HALF_UP,
                )
            )
        if name == "MATCH":
            for i, item in enumerate(values[1], 1):
                if excel_compare(values[0], item, "="):
                    return i
            raise XLException("NA")
        if name == "INDEX":
            return values[0][int(values[1]) - 1]
        if name == "TEXT":
            fmt = values[1]
            digits = (
                len(fmt.split(".")[1].replace("%", "").replace("x", "")) if "." in fmt else 0
            )
            z = excel_number(values[0]) * (100 if "%" in fmt else 1)
            z = Decimal(str(z)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
            suffix = "%" if "%" in fmt else ("x" if fmt.endswith("x") else "")
            return f"{z:.{digits}f}{suffix}"
        raise NotImplementedError(name)
