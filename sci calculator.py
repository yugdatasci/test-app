import streamlit as st
import math
import ast
import operator

# Page setup
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Scientific Calculator")
st.write("Enter a mathematical expression below and click **Calculate**")

# Allowed operators
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

# Allowed functions and constants
SAFE_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
    "pi": math.pi,
    "e": math.e,
}


# Convert factorial notation (!) to math.factorial()
def replace_factorial(expr):
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == "!":
            j = i - 1
            while j >= 0 and (expr[j].isalnum() or expr[j] in ".)"):
                j -= 1
            token = expr[j + 1:i]
            expr = expr[:j + 1] + f"factorial({token})" + expr[i + 1:]
            i = j + len(f"factorial({token})")
        else:
            i += 1
    return expr


# Safe evaluator using AST
def safe_eval(expr):
    expr = expr.replace("^", "**")
    expr = expr.replace("×", "*").replace("÷", "/")
    expr = replace_factorial(expr)

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            if type(node.op) in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[type(node.op)](
                    _eval(node.left), _eval(node.right)
                )
            else:
                raise ValueError("Operator not allowed")
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[type(node.op)](_eval(node.operand))
            else:
                raise ValueError("Unary operator not allowed")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCTIONS:
                func = SAFE_FUNCTIONS[node.func.id]
                args = [_eval(a) for a in node.args]
                return func(*args)
            else:
                raise ValueError(f"Function not allowed: {node.func.id}")
        elif isinstance(node, ast.Name):
            if node.id in SAFE_FUNCTIONS:
                return SAFE_FUNCTIONS[node.id]
            else:
                raise ValueError(f"Unknown name: {node.id}")
        else:
            raise ValueError("Invalid expression")

    try:
        parsed = ast.parse(expr, mode="eval")
        return _eval(parsed)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")


# Input field
expression = st.text_input("Expression", placeholder="Example: sin(pi/2) + sqrt(25)")

# Calculate button
if st.button("Calculate"):
    if expression.strip():
        try:
            result = safe_eval(expression)
            st.success(f"✅ Result: {result}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter an expression first.")

# Example buttons
st.markdown("### Quick Examples")
cols = st.columns(4)
examples = ["sin(pi/2)", "sqrt(16)", "5!", "log(100)"]

for i, ex in enumerate(examples):
    if cols[i].button(ex):
        try:
            st.success(f"{ex} = {safe_eval(ex)}")
        except Exception as e:
            st.error(f"Error: {e}")

# History tracking
if "history" not in st.session_state:
    st.session_state.history = []

if expression:
    try:
        res = safe_eval(expression)
        st.session_state.history.insert(0, (expression, res))
    except:
        pass

if st.session_state.history:
    st.markdown("### 🕒 History")
    for expr, result in st.session_state.history[:10]:
        st.write(f"`{expr}` = **{result}**")

st.markdown("---")
st.caption("Supports: +, -, *, /, ^, %, !, sin, cos, tan, log, sqrt, exp, factorial, pi, e, etc.")
