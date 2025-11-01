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
