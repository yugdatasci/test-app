import streamlit as st
import math

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Casio fx-991EX Calculator", page_icon="🧮", layout="centered")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background-color: #0d1117;
}
.main {
    background-color: #1e1e1e;
    padding: 20px;
    border-radius: 15px;
    color: #f5f5f5;
    box-shadow: 0px 0px 15px #00ffcc33;
    width: 400px;
    margin: auto;
}
h1 {
    text-align: center;
    color: #00ffe0;
    font-family: 'Courier New', monospace;
    margin-bottom: 10px;
}
.display {
    background-color: #000000;
    border: 2px solid #00ffe0;
    border-radius: 10px;
    padding: 10px;
    color: #00ffe0;
    font-family: 'Digital-7 Mono', monospace;
    font-size: 24px;
    text-align: right;
    margin-bottom: 5px;
}
.result {
    color: #b3ffb3;
    font-size: 18px;
    text-align: right;
    margin-bottom: 10px;
}
.stButton>button {
    width: 70px;
    height: 55px;
    margin: 3px;
    font-size: 16px;
    font-weight: bold;
    border-radius: 10px;
    border: none;
}
.num {background-color: #333; color: #fff;}
.op {background-color: #0ef; color: #000;}
.func {background-color: #1e90ff; color: white;}
.ctrl {background-color: #ff3c3c; color: white;}
.eq {background-color: #00ff88; color: black;}
.stButton>button:hover {
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# ---------- INITIALIZE SESSION STATE ----------
if "expression" not in st.session_state:
    st.session_state.expression = ""
if "result" not in st.session_state:
    st.session_state.result = ""

# ---------- CALCULATION FUNCTION ----------
def press_button(symbol):
    if symbol == "C":
        st.session_state.expression = ""
        st.session_state.result = ""
    elif symbol == "=":
        try:
            expr = st.session_state.expression.replace("^", "**")
            expr = expr.replace("√", "math.sqrt").replace("π", str(math.pi)).replace("e", str(math.e))
            expr = expr.replace("ln", "math.log").replace("log", "math.log10")
            expr = expr.replace("sin", "math.sin").replace("cos", "math.cos").replace("tan", "math.tan")
            expr = expr.replace("!", "math.factorial")
            result = eval(expr, {"math": math, "__builtins__": None})
            st.session_state.result = str(result)
        except Exception:
            st.session_state.result = "Error"
    else:
        st.session_state.expression += symbol

# ---------- DISPLAY ----------
st.markdown("<h1>Casio fx-991EX</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='display'>{st.session_state.expression}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='result'>{st.session_state.result}</div>", unsafe_allow_html=True)

# ---------- BUTTON LAYOUT ----------
layout = [
    ["C", "(", ")", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "^", "="],
    ["sin(", "cos(", "tan(", "√("],
    ["log(", "ln(", "π", "e"],
    ["x!", "%", "", ""]
]

# ---------- RENDER BUTTONS ----------
for row in layout:
    cols = st.columns(4)
    for i, symbol in enumerate(row):
        if symbol:
            css_class = "num"
            if symbol in ["+", "-", "×", "÷", "^"]:
                css_class = "op"
            elif symbol in ["sin(", "cos(", "tan(", "√(", "log(", "ln(", "π", "e", "x!"]:
                css_class = "func"
            elif symbol == "C":
                css_class = "ctrl"
            elif symbol == "=":
                css_class = "eq"

            # Convert symbols for internal computation
            display_symbol = symbol.replace("×", "*").replace("÷", "/").replace("x!", "!")
            st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
            st.button(symbol, key=symbol, on_click=press_button, args=(display_symbol,))
            st.markdown("</div>", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("<hr><center>🧮 Casio-style Scientific Calculator built with Streamlit</center>", unsafe_allow_html=True)
