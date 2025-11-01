import streamlit as st
import math

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Casio fx-991EX Scientific Calculator", page_icon="🧮", layout="centered")

# ---------- CUSTOM STYLES ----------
st.markdown("""
    <style>
    body {
        background-color: #0d1117;
    }
    .main {
        background-color: #1c1c1c;
        color: #ffffff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 0px 15px rgba(0, 255, 255, 0.3);
        width: 420px;
        margin: auto;
    }
    h1 {
        text-align: center;
        color: #00fff0;
        font-family: 'Courier New', monospace;
        margin-bottom: 10px;
    }
    .display {
        background-color: #000000;
        border: 2px solid #00fff0;
        border-radius: 10px;
        padding: 10px;
        color: #00fff0;
        font-family: 'Digital-7 Mono', monospace;
        font-size: 22px;
        text-align: right;
        margin-bottom: 2px;
    }
    .result {
        color: #b3ffb3;
        font-size: 18px;
        text-align: right;
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 85px;
        height: 55px;
        font-size: 16px;
        font-weight:
