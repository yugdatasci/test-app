import streamlit as st
import math

st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Scientific Calculator")

# Initialize session state for display
if "display" not in st.session_state:
    st.session_state.display = ""

# Function to safely evaluate expression
def calculate(expression):
    try:
        expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
        result = eval(expression, {"__builtins__": None}, math.__dict__)
        return result
    except Exception:
        return "Error"

# Display area
st.markdown(f"""
<div style="text-align:center; background-color:#222; color:#0f0; font-size:30px; padding:10px; border-radius:10px;">
{st.session_state.display or "0"}
</div>
""", unsafe_allow_html=True)

# Button layout
buttons = [
    ["7", "8", "9", "÷", "C"],
    ["4", "5", "6", "×", "("],
    ["1", "2", "3", "-", ")"],
    ["0", ".", "^", "+", "="],
    ["sin", "cos", "tan", "sqrt", "log"]
]

# Handle button clicks
for row in buttons:
    cols = st.columns(5)
    for i, label in enumerate(row):
        if cols[i].button(label):
            if label == "C":
                st.session_state.display = ""
            elif label == "=":
                st.session_state.display = str(calculate(st.session_state.display))
            elif label in ["sin", "cos", "tan", "sqrt", "log"]:
                st.session_state.display += f"math.{label}("
            else:
                st.session_state.display += label

# Additional buttons for constants
col1, col2, col3 = st.columns(3)
if col1.button("π"):
    st.session_state.display += "math.pi"
if col2.button("e"):
    st.session_state.display += "math.e"
if col3.button("⌫"):  # Backspace
    st.session_state.display = st.session_state.display[:-1]

st.markdown("---")
st.caption("Supports: +, -, ×, ÷, ^, sin, cos, tan, sqrt, log, π, e")
