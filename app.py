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
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📈 Portfolio Allocation")
            pie = px.pie(
                values=[equity, debt, gold],
                names=["Equity", "Debt", "Gold"],
                color_discrete_sequence=["#002B5C", "#D4AF37", "#8B0000"]
            )
            st.plotly_chart(pie, use_container_width=True)

        st.success(f"Your Risk Category: *{category}*")

# -----------------------------------------------------------
#        2️⃣ INTEREST RATE CALCULATOR (ADVANCED)
# -----------------------------------------------------------
elif page == "Interest Rate Calculator":
    st.title("💰 Interest Rate & EMI Calculator")

    principal = st.number_input("Loan Amount (₹)", 1000, 100000000, 100000)
    tenure = st.number_input("Tenure (Months)", 1, 360, 12)
    rate = st.number_input("Interest Rate (% per year)", 0.0, 50.0, 8.0)

    monthly_rate = rate / 12 / 100

    if st.button("Calculate EMI"):
        if monthly_rate == 0:
            # No interest case
            emi = principal / tenure
        else:
            # ✅ Correct EMI formula with exponent
            r = monthly_rate
            n = tenure
            emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

        st.subheader(f"📌 Monthly EMI: ₹ {emi:,.2f}")

        # Amortization table
        balance = principal
        rows = []

        for i in range(1, tenure + 1):
            if monthly_rate == 0:
                interest = 0
            else:
                interest = balance * monthly_rate
            principal_paid = emi - interest
            balance -= principal_paid
            rows.append([i, emi, principal_paid, interest, max(balance, 0)])

        df = pd.DataFrame(rows, columns=["Month", "EMI", "Principal", "Interest", "Balance"])

        st.write("### 📄 Amortization Schedule")
        st.dataframe(df, use_container_width=True)

        st.write("### 📈 Loan Balance Over Time")
        fig = px.line(df, x="Month", y="Balance", title="Loan Balance Over Time")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
#            3️⃣ USA CPI DASHBOARD (ADVANCED)
# -----------------------------------------------------------
elif page == "USA CPI Dashboard":
    st.title("🇺🇸 USA CPI Dashboard – Inflation Trends")

    # sample dataset
    cpi = pd.DataFrame({
        "Year": list(range(2010, 2025)),
        "CPI": [218, 224, 229, 232, 236, 237, 240, 245, 251, 255, 258, 262, 268, 277, 292]
    })

    st.write("### 📈 CPI Trend (USA)")
    fig = px.line(cpi, x="Year", y="CPI", markers=True, title="USA CPI Index")
    st.plotly_chart(fig, use_container_width=True)

    # YoY inflation
    cpi["Inflation"] = cpi["CPI"].pct_change() * 100
    st.write("### 📉 Year-on-Year Inflation")
    fig2 = px.bar(cpi, x="Year", y="Inflation", title="USA YoY CPI Inflation (%)")
    st.plotly_chart(fig2, use_container_width=True)

    st.info("Federal Reserve Inflation Target: **2%**")

# -----------------------------------------------------------
#     4️⃣ WORLD INFLATION DASHBOARD (ADVANCED + FORECAST)
# -----------------------------------------------------------
elif page == "World Inflation Dashboard":
    st.title("🌍 World Inflation Dashboard")

    st.write("Select countries to compare:")

    data = {
        "Year": list(range(2010, 2025)),
        "India": [10, 8, 7, 6, 5.5, 5, 4.8, 3.6, 4.9, 6.3, 5.1, 6.7, 7.2, 6.4, 5.8],
        "USA":   [1.6, 3.2, 2.1, 1.5, 1.6, 0.1, 2.1, 2.4, 1.8, 2.3, 1.4, 7.0, 6.5, 4.1, 3.2],
        "UK":    [3.3, 4.5, 2.8, 2.6, 1.5, 0.1, 0.8, 2.1, 2.5, 1.7, 2.2, 6.2, 7.3, 5.6, 3.8]
    }

    df = pd.DataFrame(data)

    countries = st.multiselect("Countries", ["India", "USA", "UK"], ["India", "USA"])

    if countries:
        st.write("### 📈 Historical Inflation Comparison")
        fig = px.line(df, x="Year", y=countries, title="Inflation Rate by Country (%)")
        st.plotly_chart(fig, use_container_width=True)

        # Forecast (ARIMA simple)
        st.write("### 🔮 Forecast Next-Year Inflation")

        for c in countries:
            series = df[c]

            try:
                model = ARIMA(series, order=(1, 1, 1))
                model_fit = model.fit()
                forecast = model_fit.forecast(1)[0]

                st.success(f"{c} – Forecast Inflation (Next Year): {forecast:.2f}%")
            except Exception as e:
                st.error(f"Could not forecast for {c}: {e}")
