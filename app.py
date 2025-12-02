import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA

# -----------------------------------------------------------
#                    GLOBAL STYLING (RBI THEME)
# -----------------------------------------------------------
st.set_page_config(
    page_title="RBI Financial Dashboard",
    layout="wide",
    page_icon="🏦"
)

st.markdown("""
<style>
/* Main background */
body {
    background-color: #F5F7FA;
}

/* App background */
[data-testid="stAppViewContainer"] {
    background-color: #F5F7FA;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #002B5C !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Headers */
h1, h2, h3 {
    color: #002B5C !important;
}

/* Buttons */
.stButton>button {
    background-color: #002B5C !important;
    color: white !important;
    border-radius: 8px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
#                     SIDEBAR NAVIGATION
# -----------------------------------------------------------
st.sidebar.title("🏦 RBI Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "RISCO Meter", "Interest Rate Calculator", "USA CPI Dashboard", "World Inflation Dashboard"]
)

# -----------------------------------------------------------
#                         HOME PAGE
# -----------------------------------------------------------
if page == "Home":
    st.title("🏦 RBI Financial Analytics Dashboard")
    st.subheader("A unified platform for risk scoring, interest analysis, CPI trends, and global inflation forecasting.")

    st.markdown("""
    ### 🔍 Modules Included:
    - *RISCO Meter (Advanced)* – Risk scoring, gauge meter, profiling  
    - *Interest Rate Calculator (Advanced)* – EMI chart & amortization  
    - *USA CPI Dashboard (Advanced)* – Trends, graphs, inflation target comparison  
    - *World Inflation Dashboard (Advanced)* – Multi-country trends + forecast  

    *Designed with an RBI-style blue/gold theme for professional use.*
    """)

# -----------------------------------------------------------
#                 1️⃣ RISCO METER (ADVANCED)
# -----------------------------------------------------------
elif page == "RISCO Meter":
    st.title("📊 RISCO Meter – Advanced Risk Analyzer")

    st.write("Enter your portfolio allocation (%)")

    equity = st.slider("Equity (%)", 0, 100, 40)
    debt = st.slider("Debt (%)", 0, 100, 40)
    gold = st.slider("Gold (%)", 0, 100, 20)
    total = equity + debt + gold

    if total != 100:
        st.warning("Total allocation must be 100%.")
    else:
        # Risk score formula
        risk_score = (equity * 0.8) + (gold * 0.4) + (debt * 0.1)

        # Risk category
        if risk_score <= 30:
            category = "Low Risk"
            color = "green"
        elif risk_score <= 55:
            category = "Moderate Risk"
            color = "orange"
        else:
            category = "High Risk"
            color = "red"

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 Risk Gauge")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 60], 'color': "yellow"},
                        {'range': [60, 100], 'color': "lightcoral"},
                    ],
                },
                title={'text': "Overall Risk Score"}
            ))
            st.plotly_chart(fig, use_containe
