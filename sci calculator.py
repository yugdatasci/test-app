# app.py
import streamlit as st
import math
import operator
import ast

st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# ---- Safe evaluator using AST ----
# Allowed operators and functions
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Map of allowed names -> functions/constants
MATH_FUNCS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'exp': math.exp,
    'ln': math.log,        # natural log
    'log': lambda x, b=10: math.log(x, b) if b != 10 else math.log10(x),  # log(x) default base 10
    'log10': math.log10,
    'sqrt': math.sqrt,
    'abs': abs,
    'floor': math.floor,
    'ceil': math.ceil,
    'factorial': math.factorial,
    'pi': math.pi,
    'e': math.e,
}

# Helper to parse factorial postfix '!' (like 5!)
def replace_factorial(expr: str) -> str:
    # Simple replacement: convert "n!" into "factorial(n)". Handles basic expressions.
    # This is not a full parser — works for typical uses like 5!, (3+2)!, etc.
    out = []
    i = 0
    while i < len(expr):
        if expr[i] == '!':
            # find start of previous token (number or ) )
            j = len(out) - 1
            # gather token backwards
            token = ''
            if j >= 0 and out[j] == ')':
                # find matching '('
                cnt = 0
                while j >= 0:
                    ch = out[j]
                    token = ch + token
                    if ch == ')':
                        cnt += 1
                    elif ch == '(':
                        cnt -= 1
                        if cnt == 0:
                            break
                    j -= 1
                # remove the token
                out = out[:j]
                out.append(f'factorial{token}')
            else:
                # number or name — gather digits/letters/decimal/dots
                while j >= 0 and (out[j].isalnum() or out[j] in '._'):
                    token = out[j] + token
                    j -= 1
                out = out[: j+1]
                out.append(f'factorial({token})')
            i += 1
        else:
            out.append(expr[i])
            i += 1
    return ''.join(out)

def safe_eval(expr: str):
    """
    Safely evaluate a mathematical expression using AST.
    Supports numbers, parentheses, + - * / ** %, unary +/-, function calls from MATH_FUNCS.
    """
    # Replace common symbols: '^' -> '**'
    expr = expr.replace('^', '**')
    expr = expr.replace('×', '*').replace('÷', '/')
    expr = replace_factorial(expr)
    try:
        node = ast.parse(expr, mode='eval')
    except Exception as e:
        raise ValueError(f"Parse error: {e}")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):  # for Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Unsupported constant type")
        if isinstance(node, ast.Num):  # older py
            return node.n
        if isinstance(node, ast.BinOp):
            op = type(node.op)
            if op in ALLOWED_OPERATORS:
                left = _eval(node.left)
                right = _eval(node.right)
                return ALLOWED_OPERATORS[op](left, right)
            else:
                raise ValueError("Operator not allowed")
        if isinstance(node, ast.UnaryOp):
            op = type(node.op)
            if op in ALLOWED_OPERATORS:
                operand = _eval(node.operand)
                return ALLOWED_OPERATORS[op](operand)
            else:
                raise ValueError("Unary operator not allowed")
        if isinstance(node, ast.Call):
            # function call
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in MATH_FUNCS:
                    func = MATH_FUNCS[func_name]
                    args = [_eval(a) for a in node.args]
                    # support optional kwargs only for log base, but ignore keywords for safety
                    return func(*args)
            raise ValueError(f"Function '{getattr(node.func, 'id', 'unknown')}' not allowed")
        if isinstance(node, ast.Name):
            if node.id in MATH_FUNCS:
                val = MATH_FUNCS[node.id]
                if isinstance(val, (int, float)):
                    return val
            raise ValueError(f"Name '{node.id}' is not allowed as a value")
        if isinstance(node, ast.Expr):
            return _eval(node.value)
        raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    return _eval(node)

# ---- UI ----
st.title("🧮 Scientific Calculator (Streamlit)")
st.write("Type an expression (examples: `2+3*4`, `sin(pi/2)`, `sqrt(2)`, `5!`, `log(100)`, `2^8`)")

if 'history' not in st.session_state:
    st
