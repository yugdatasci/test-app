import streamlit as st
import math

# --- Page Config ---
st.set_page_config(page_title="Advanced Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS (Eye-Catching Style) ---
st.markdown("""
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
""", unsafe_allow_html=True)

st.title("🧮 Advanced Scientific Calculator")

# --- Session State ---
if "display" not in st.session_state:
    st.session_state.display = ""

# --- Calculator Logic ---
def calculate(expression):
    try:
        expr = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
        result = eval(expr, {"__builtins__": None}, math.__dict__)
        return result
    except Exception:
        return "Error"

# --- Display Screen ---
st.markdown(f"<div class='calc-display'>{st.session_state.display or '0'}</div>", unsafe_allow_html=True)

# --- Buttons Layout ---
buttons = [
    ["7", "8", "9", "÷", "C"],
    ["4", "5", "6", "×", "("],
    ["1", "2", "3", "-", ")"],
    ["0", ".", "^", "+", "="],
]

scientific = [
    ["sin", "cos", "tan", "log", "ln"],
    ["sqrt", "exp", "abs", "!", "⌫"],
    ["π", "e", "deg", "rad", "Ans"]
]

# --- Handle Buttons ---
def press(label):
    if label == "C":
        st.session_state.display = ""
    elif label == "⌫":
        st.session_state.display = st.session_state.display[:-1]
    elif label == "=":
        res = calculate(st.session_state.display)
        st.session_state.display = str(res)
        st.session_state.last_ans = res
    elif label == "Ans":
        if "last_ans" in st.session_state:
            st.session_state.display += str(st.session_state.last_ans)
    elif label in ["sin", "cos", "tan", "log", "ln", "sqrt", "exp", "abs"]:
        func = {"ln": "log"}.get(label, label)
        st.session_state.display += f"math.{func}("
    elif label == "!":
        st.session_state.display += "math.factorial("
    elif label == "π":
        st.session_state.display += "math.pi"
    elif label == "e":
        st.session_state.display += "math.e"
    elif label == "deg":
        st.session_state.display = str(math.degrees(eval(st.session_state.display)))
    elif label == "rad":
        st.session_state.display = str(math.radians(eval(st.session_state.display)))
    else:
        st.session_state.display += label

# --- Scientific Buttons ---
st.markdown("### 🔬 Scientific Functions")
for row in scientific:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, key=f"sci_{label}"):
                press(label)

# --- Numeric Buttons ---
st.markdown("### 🔢 Basic Operations")
for row in buttons:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, key=f"btn_{label}"):
                press(label)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:gray; font-size:0.9em;'>
Built with ❤️ using <b>Streamlit</b> <br>
Supports sin, cos, tan, log, ln, sqrt, factorial, exp, π, e, degree↔radian conversion.
</div>
""", unsafe_allow_html=True)
