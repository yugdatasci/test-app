scientific-calculator/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# --- CUSTOM STYLING (Casio look) ---
st.markdown("""
    <style>
    .main {
        background-color: #1a1a1a;
        color: white;
        border-radius: 10px;
        padding: 20px;
    }
    .stButton>button {
        width: 70px;
        height: 50px;
        margin: 3px;
        border-radius: 8px;
        background-color: #333;
        color: #00ffcc;
        border: 1px solid #00ffcc;
        font-size: 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00ffcc;
        color: black;
    }
    .display-box {
        background-color: #000;
        color: #00ffcc;
        font-size: 24px;
        text-align: right;
        padding: 10px;
        border-radius: 5px;
        border: 2px solid #00ffcc;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- APP TITLE ---
st.title("🧮 Scientific Calculator (Casio fx-911 Style)")
st.write("### Made with Streamlit")

# --- CALCULATOR LOGIC ---
if "expression" not in st.session_state:
    st.session_state.expression = ""

def press_button(symbol):
    """Handles button press logic"""
    if symbol == "C":
        st.session_state.expression = ""
    elif symbol == "=":
        try:
            # Replace scientific functions with math equivalents
            expr = st.session_state.expression.replace("^", "**")
            expr = expr.replace("π", str(math.pi)).replace("e", str(math.e))
            result = eval(expr, {"__builtins__": None}, vars(math))
            st.session_state.expression = str(result)
        except Exception:
            st.session_state.expression = "Error"
    else:
        st.session_state.expression += symbol

# --- DISPLAY SCREEN ---
st.markdown(f'<div class="display-box">{st.session_state.expression}</div>', unsafe_allow_html=True)

# --- BUTTON LAYOUT ---
buttons = [
    ["sin(", "cos(", "tan(", "log("],
    ["√(", "^", "π", "e"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "(", "+)"],
    ["C", "(", ")", "="]
]

# --- DISPLAY BUTTONS ---
for row in buttons:
    cols = st.columns(4)
    for i, symbol in enumerate(row):
        with cols[i]:
            st.button(symbol, on_click=press_button, args=(symbol,))

# --- FOOTER ---
st.markdown("---")
st.caption("🔹 Casio-style Scientific Calculator built with Streamlit by [Your Name]")
