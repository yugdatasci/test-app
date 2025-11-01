import streamlit as st
import ast
import math
from typing import Dict, Any

# --- Page config ---
st.set_page_config(page_title="Advanced Scientific Calculator", page_icon="🧮", layout="centered")

# --- CSS ---
st.markdown(
    """
<style>
    .stApp {
        background: radial-gradient(circle at top, #1e1e2e, #111);
        color: white;
        font-family: 'Poppins', sans-serif;
    }
    .calc-display {
        text-align: right;
        background: rgba(0, 0, 0, 0.8);
        color: #00ffb3;
        font-size: 2em;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: inset 0 0 10px #00ffb3;
        word-break: break-all;
    }
    .stButton>button {
        background: linear-gradient(145deg, #202020, #3a3a3a);
        border: none;
        color: #00ffc3;
        font-size: 1.1em;
        font-weight: bold;
        border-radius: 10px;
        height: 55px;
        width: 100%;
        transition: all 0.15s ease-in-out;
        box-shadow: 0px 3px 10px rgba(0,255,200,0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(145deg, #00ffb3, #00b36b);
        color: black;
        transform: scale(1.03);
        box-shadow: 0px 3px 15px rgba(0,255,180,0.5);
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🧮 Advanced Scientific Calculator")

# --- Session state defaults ---
if "display" not in st.session_state:
    st.session_state.display = ""
if "last_ans" not in st.session_state:
    st.session_state.last_ans = None
if "deg_mode" not in st.session_state:
    st.session_state.deg_mode = False

# --- Safe AST evaluator ---
ALLOWED_NODES = (
    ast.Expression, ast.Call, ast.Name, ast.Load, ast.BinOp, ast.UnaryOp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.USub, ast.UAdd,
    ast.Num, ast.Constant, ast.Tuple, ast.List, ast.Subscript, ast.Index, ast.Slice,
)

def validate_ast(node: ast.AST, allowed_names: Dict[str, Any]):
    for n in ast.walk(node):
        if not isinstance(n, ALLOWED_NODES):
            raise ValueError(f"Disallowed AST node: {type(n).__name__}")
        # Disallow attribute access (no math.sin with dot)
        if isinstance(n, ast.Attribute):
            raise ValueError("Attribute access is not allowed.")
        # Calls: function must be a Name and allowed
        if isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name):
                raise ValueError("Only direct function names are allowed.")
            if n.func.id not in allowed_names:
                raise ValueError(f"Function '{n.func.id}' is not allowed.")
        if isinstance(n, ast.Name):
            if n.id not in allowed_names:
                raise ValueError(f"Name '{n.id}' is not allowed.")

def safe_eval(expr: str, names: Dict[str, Any]):
    # Normalize common tokens
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    # Quick replace for pi symbol
    expr = expr.replace("π", "pi")
    # Parse AST
    try:
        node = ast.parse(expr, mode="eval")
    except Exception as e:
        raise ValueError("Invalid expression syntax.") from e
    validate_ast(node, names)
    try:
        return eval(compile(node, "<safe>", "eval"), {"__builtins__": None}, names)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}") from e

# --- Allowed names generator (respects degree/radian mode) ---
def make_allowed_names():
    allowed = {}
    # constants
    allowed["pi"] = math.pi
    allowed["e"] = math.e
    # basic
    allowed["abs"] = abs
    allowed["round"] = round
    allowed["int"] = int
    allowed["float"] = float
    allowed["pow"] = pow
    # ln/log
    allowed["ln"] = math.log
    allowed["log"] = math.log  # natural log
    allowed["log10"] = math.log10
    # sqrt/exp
    allowed["sqrt"] = math.sqrt
    allowed["exp"] = math.exp
    # factorial wrapper
    def fact(n):
        if not isinstance(n, int):
            raise ValueError("factorial requires integer")
        if n < 0:
            raise ValueError("factorial requires non-negative integer")
        return math.factorial(n)
    allowed["fact"] = fact
    allowed["factorial"] = fact

    # trig functions: respect deg_mode
    if st.session_state.deg_mode:
        allowed["sin"] = lambda x: math.sin(math.radians(x))
        allowed["cos"] = lambda x: math.cos(math.radians(x))
        allowed["tan"] = lambda x: math.tan(math.radians(x))
        allowed["asin"] = lambda x: math.degrees(math.asin(x))
        allowed["acos"] = lambda x: math.degrees(math.acos(x))
        allowed["atan"] = lambda x: math.degrees(math.atan(x))
    else:
        allowed["sin"] = math.sin
        allowed["cos"] = math.cos
        allowed["tan"] = math.tan
        allowed["asin"] = math.asin
        allowed["acos"] = math.acos
        allowed["atan"] = math.atan

    # last answer
    allowed["Ans"] = st.session_state.last_ans
    allowed["ans"] = st.session_state.last_ans

    return allowed

# --- Helpers ---
def format_result(val):
    if isinstance(val, float):
        if abs(val - round(val)) < 1e-12:
            return str(int(round(val)))
        return f"{val:.12g}"
    return str(val)

def evaluate_expression(expr: str):
    names = make_allowed_names()
    return safe_eval(expr, names)

# --- UI: top controls ---
left, center, right = st.columns([2, 6, 2])
with left:
    deg_toggle = st.checkbox("Degrees mode", value=st.session_state.deg_mode)
    st.session_state.deg_mode = deg_toggle

with center:
    st.markdown(f"<div class='calc-display'>{st.session_state.display or '0'}</div>", unsafe_allow_html=True)

with right:
    if st.button("C", key="top_clear"):
        st.session_state.display = ""
    if st.button("⌫", key="top_back"):
        st.session_state.display = st.session_state.display[:-1]

# --- Button layout ---
buttons = [
    ["7", "8", "9", "÷", "C"],
    ["4", "5", "6", "×", "("],
    ["1", "2", "3", "-", ")"],
    ["0", ".", "^", "+", "="],
]

scientific = [
    ["sin", "cos", "tan", "log", "ln"],
    ["sqrt", "exp", "abs", "fact", "⌫"],
    ["π", "e", "deg→rad", "rad→deg", "Ans"]
]

def press(label: str):
    try:
        if label == "C":
            st.session_state.display = ""
            return
        if label == "⌫":
            st.session_state.display = st.session_state.display[:-1]
            return
        if label == "=":
            expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("^", "**")
            # allow users to type common factorial like fact(5). postfix '5!' not implemented here.
            # Evaluate
            result = evaluate_expression(expr)
            st.session_state.last_ans = result
            st.session_state.display = format_result(result)
            return
        if label == "Ans":
            if st.session_state.last_ans is not None:
                st.session_state.display += str(format_result(st.session_state.last_ans))
            return
        if label == "π":
            st.session_state.display += "pi"
            return
        if label == "e":
            st.session_state.display += "e"
            return
        if label == "deg→rad":
            if st.session_state.display:
                try:
                    v = float(evaluate_expression(st.session_state.display))
                    st.session_state.display = format_result(math.radians(v))
                except Exception as e:
                    st.session_state.display = f"Error: {e}"
            return
        if label == "rad→deg":
            if st.session_state.display:
                try:
                    v = float(evaluate_expression(st.session_state.display))
                    st.session_state.display = format_result(math.degrees(v))
                except Exception as e:
                    st.session_state.display = f"Error: {e}"
            return
        if label in {"sin", "cos", "tan", "log", "ln", "sqrt", "exp", "abs", "fact"}:
            # append function and opening paren
            fn = "ln" if label == "ln" else ("fact" if label == "fact" else label)
            st.session_state.display += f"{fn}("
            return
        # default: append label
        st.session_state.display += label
    except Exception as e:
        st.session_state.display = f"Error: {e}"

# --- Draw scientific buttons ---
st.markdown("### 🔬 Scientific Functions")
for row in scientific:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, key=f"sci_{label}"):
                press(label)

# --- Draw numeric buttons ---
st.markdown("### 🔢 Basic Operations")
for row in buttons:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, key=f"btn_{label}"):
                press(label)

# --- Footer ---
st.markdown("---")
st.markdown(
    """
<div style='text-align:center; color:gray; font-size:0.9em;'>
Built with ❤️ using <b>Streamlit</b>.<br>
Usage tips: use functions like <code>sin(30)</code>, <code>sqrt(16)</code>, <code>fact(5)</code>, <code>ln(2.718)</code>. Toggle Degrees mode for trig.<br>
This app uses a safe AST-based evaluator — arbitrary code execution is prevented.
</div>
""",
    unsafe_allow_html=True,
)
