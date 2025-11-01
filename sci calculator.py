import streamlit as st
import math
import ast

# --- Page Config ---
st.set_page_config(page_title="Advanced Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS (Eye-Catching Style) ---
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
        transform: scale(1.05);
        box-shadow: 0px 3px 15px rgba(0,255,180,0.5);
    }
    .small-btn>button {
        height: 45px !important;
        font-size: 1em !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🧮 Advanced Scientific Calculator (Clean & Safe)")

# --- Session State ---
if "display" not in st.session_state:
    st.session_state.display = ""
if "last_ans" not in st.session_state:
    st.session_state.last_ans = None
if "deg_mode" not in st.session_state:
    st.session_state.deg_mode = False  # False means trig uses radians

# --- Safe evaluation using ast ---
ALLOWED_NODE_TYPES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Num,         # Python <3.8
    ast.Constant,    # Python >=3.8
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Tuple,
    ast.List,
    ast.Subscript,
    ast.Index,
    ast.Slice,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.USub,
    ast.UAdd,
    ast.FloorDiv,
)

def _validate_ast(node, allowed_names):
    """Recursively validate AST nodes and names."""
    for child in ast.walk(node):
        if not isinstance(child, ALLOWED_NODE_TYPES):
            raise ValueError(f"Disallowed expression: {type(child).__name__}")
        # If it's a call, ensure the function is a Name (no attribute access)
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                func_name = child.func.id
                if func_name not in allowed_names:
                    raise ValueError(f"Use of function '{func_name}' is not allowed.")
            else:
                raise ValueError("Only direct function names are allowed (no attribute access).")
        # If it's a Name, ensure it's allowed (constants, variables)
        if isinstance(child, ast.Name):
            if child.id not in allowed_names:
                raise ValueError(f"Use of name '{child.id}' is not allowed.")

def safe_eval(expr: str, names: dict):
    """
    Evaluate `expr` safely using ast parsing and a whitelist of names.
    `names` is a dict mapping allowed names to callables/constants.
    """
    # Normalize some common unicode operators
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    # Parse to AST
    try:
        node = ast.parse(expr, mode="eval")
    except Exception as e:
        raise ValueError("Invalid expression syntax.") from e
    # Validate AST
    _validate_ast(node, names.keys())
    # Evaluate in a restricted environment
    try:
        return eval(compile(node, "<string>", "eval"), {"__builtins__": None}, names)
    except Exception as e:
        # Re-raise with a friendlier message
        raise ValueError(f"Error evaluating expression: {e}") from e

# --- Build allowed names / functions depending on degree/radian mode ---
def make_allowed_names(deg_mode: bool):
    allowed = {}

    # Basic math constants
    allowed["pi"] = math.pi
    allowed["π"] = math.pi
    allowed["e"] = math.e

    # Numeric constructors
    allowed["int"] = int
    allowed["float"] = float
    allowed["abs"] = abs
    allowed["round"] = round

    # pow is allowed but we also have '**' in expression
    allowed["pow"] = pow

    # factorial wrapper — validate at call time
    def fact(n):
        if not (isinstance(n, (int,))):
            raise ValueError("factorial() only accepts integers.")
        if n < 0:
            raise ValueError("factorial() only accepts non-negative integers.")
        return math.factorial(n)
    allowed["fact"] = fact
    allowed["factorial"] = fact
    allowed["!"] = fact  # user convenience but will only work if they write fact(...)

    # logarithms: log (natural), log10
    allowed["ln"] = math.log
    allowed["log"] = math.log  # natural log
    allowed["log10"] = math.log10

    # exp and sqrt
    allowed["exp"] = math.exp
    allowed["sqrt"] = math.sqrt

    # Trigonometric wrappers that respect degree/radian mode
    if deg_mode:
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

    # include last answer variable 'Ans' and 'ans'
    allowed["Ans"] = st.session_state.get("last_ans", None)
    allowed["ans"] = st.session_state.get("last_ans", None)

    return allowed

# --- Helper to format result ---
