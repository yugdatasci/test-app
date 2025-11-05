import streamlit as st
import ast
import math
from typing import Dict, Any

# ---------------- Page Setup ----------------
st.set_page_config(page_title="⚡ Advanced Scientific Calculator", page_icon="🧮", layout="centered")

# ---------------- CSS Styling ----------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #141e30, #243b55);
        color: #fff;
        font-family: 'Poppins', sans-serif;
    }
    .display-box {
        text-align: right;
        background: rgba(0, 0, 0, 0.85);
        color: #00ffb3;
        font-size: 2.2em;
        padding: 12px 18px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: inset 0 0 12px #00ffb3;
        word-break: break-all;
        font-family: 'Consolas', monospace;
    }
    .preview-box {
        text-align: right;
        color: #aaa;
        font-size: 1em;
        margin-top: -5px;
        margin-bottom: 10px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #1e1e1e, #3a3a3a);
        border: none;
        color: #00ffc3;
        font-weight: 600;
        font-size: 1.1em;
        border-radius: 10px;
        width: 100%;
        height: 55px;
        transition: all 0.15s ease-in-out;
        box-shadow: 0px 3px 8px rgba(0,255,180,0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00ffb3, #00b36b);
        color: black;
        transform: scale(1.05);
        box-shadow: 0px 4px 12px rgba(0,255,180,0.5);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- State ----------------
if "display" not in st.session_state:
    st.session_state.display = ""
if "last_ans" not in st.session_state:
    st.session_state.last_ans = None
if "deg_mode" not in st.session_state:
    st.session_state.deg_mode = False

# ---------------- AST Safe Eval ----------------
ALLOWED_NODES = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Name, ast.Load,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.USub, ast.UAdd, ast.Constant, ast.Tuple, ast.List,
}

def validate_ast(node, allowed_names):
    for n in ast.walk(node):
        if type(n) not in ALLOWED_NODES:
            raise ValueError(f"Invalid syntax or operation: {type(n).__name__}")
        if isinstance(n, ast.Call) and (
            not isinstance(n.func, ast.Name) or n.func.id not in allowed_names
        ):
            raise ValueError(f"Function not allowed: {getattr(n.func, 'id', None)}")
        if isinstance(n, ast.Name) and n.id not in allowed_names:
            raise ValueError(f"Variable not allowed: {n.id}")

def make_allowed_names() -> Dict[str, Any]:
    deg = st.session_state.deg_mode
    A = {"pi": math.pi, "e": math.e, "abs": abs, "round": round, "pow": pow, "int": int, "float": float,
         "log": math.log, "log10": math.log10, "sqrt": math.sqrt, "exp": math.exp}
    # factorial
    def fact(n):
        if not isinstance(n, int) or n < 0:
            raise ValueError("factorial() requires non-negative integer")
        return math.factorial(n)
    A["fact"] = A["factorial"] = fact
    # trig
    if deg:
        A.update({
            "sin": lambda x: math.sin(math.radians(x)),
            "cos": lambda x: math.cos(math.radians(x)),
            "tan": lambda x: math.tan(math.radians(x)),
            "asin": lambda x: math.degrees(math.asin(x)),
            "acos": lambda x: math.degrees(math.acos(x)),
            "atan": lambda x: math.degrees(math.atan(x)),
        })
    else:
        A.update({
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "asin": math.asin, "acos": math.acos, "atan": math.atan
        })
    # Ans
    A["Ans"] = st.session_state.last_ans
    return A

def safe_eval(expr: str, names: Dict[str, Any]):
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace("π", "pi")
    node = ast.parse(expr, mode="eval")
    validate_ast(node, names)
    return eval(compile(node, "<safe>", "eval"), {"__builtins__": None}, names)

# ---------------- Expression Evaluation ----------------
def evaluate(expr: str):
    try:
        result = safe_eval(expr, make_allowed_names())
        st.session_state.last_ans = result
        return result
    except Exception as e:
        return f"Error: {e}"

# ---------------- UI: Top Controls ----------------
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    st.session_state.deg_mode = st.toggle("Degrees", value=st.session_state.deg_mode)
with col3:
    if st.button("C"):
        st.session_state.display = ""
    if st.button("⌫"):
        st.session_state.display = st.session_state.display[:-1]

# ---------------- Display ----------------
display = st.text_input("Expression", st.session_state.display, label_visibility="collapsed")
st.session_state.display = display.strip()

# Show live result (preview)
if display:
    preview = evaluate(display)
    if isinstance(preview, (int, float)):
        st.markdown(f"<div class='preview-box'>= {preview}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='preview-box' style='color:#f55;'>⚠️ {preview}</div>", unsafe_allow_html=True)

# ---------------- Buttons Layout ----------------
buttons = [
    ["7", "8", "9", "÷", "C"],
    ["4", "5", "6", "×", "("],
    ["1", "2", "3", "-", ")"],
    ["0", ".", "^", "+", "="],
]
scientific = [
    ["sin", "cos", "tan", "log", "ln"],
    ["sqrt", "exp", "abs", "fact", "Ans"],
    ["π", "e", "deg→rad", "rad→deg", "clear"]
]

# ---------------- Button Handler ----------------
def handle_input(label):
    d = st.session_state.display
    if label == "=":
        result = evaluate(d)
        st.session_state.display = str(result if not isinstance(result, str) else "")
    elif label in {"C", "clear"}:
        st.session_state.display = ""
    elif label == "Ans" and st.session_state.last_ans is not None:
        st.session_state.display += str(st.session_state.last_ans)
    elif label == "⌫":
        st.session_state.display = d[:-1]
    elif label == "π":
        st.session_state.display += "pi"
    elif label == "e":
        st.session_state.display += "e"
    elif label == "deg→rad":
        try:
            val = float(evaluate(d))
            st.session_state.display = str(math.radians(val))
        except Exception:
            st.session_state.display = "Error"
    elif label == "rad→deg":
        try:
            val = float(evaluate(d))
            st.session_state.display = str(math.degrees(val))
        except Exception:
            st.session_state.display = "Error"
    elif label in {"sin", "cos", "tan", "log", "ln", "sqrt", "exp", "abs", "fact"}:
        st.session_state.display += f"{label}("
    else:
        st.session_state.display += label

# ---------------- Render Scientific Buttons ----------------
st.markdown("### 🔬 Scientific Functions")
for row in scientific:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, key=f"sci_{label}"):
                handle_input(label)

# ---------------- Render Numeric Buttons ----------------
st.markdown("### 🔢 Basic Operations")
for row in buttons:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, key=f"btn_{label}"):
                handle_input(label)

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#bbb; font-size:0.9em;'>
Built with ⚡ <b>Streamlit</b><br>
Supports <code>sin(30)</code>, <code>sqrt(16)</code>, <code>fact(5)</code>, <code>ln(e)</code>, etc.<br>
Switch between Degrees/Radians anytime — secure AST evaluation ensures no code injection.
</div>
""", unsafe_allow_html=True)
