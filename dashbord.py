pip install streamlit yfinance plotly pandas

# Filename: stock_dashboard.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Dashboard title
st.title("📊 Stock Market Dashboard (NIFTY & Stocks)")

# Sidebar for user input
st.sidebar.header("Select Stock & Date Range")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., ^NSEI for NIFTY 50, HDFCBANK.NS for HDFC Bank):", "^NSEI")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2025-11-01"))

# Fetch stock data
data = yf.download(ticker, start=start_date, end=end_date)
data.reset_index(inplace=True)

# Display basic statistics
st.subheader(f"Basic Stats for {ticker}")
st.write(data.describe())

# Closing price plot
st.subheader("Closing Price Chart 📈")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Close'))
fig.update_layout(title=f"{ticker} Closing Price", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig)

# Moving Averages
st.subheader("Moving Averages")
data['SMA_20'] = data['Close'].rolling(20).mean()
data['SMA_50'] = data['Close'].rolling(50).mean()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Close'))
fig2.add_trace(go.Scatter(x=data['Date'], y=data['SMA_20'], mode='lines', name='SMA 20'))
fig2.add_trace(go.Scatter(x=data['Date'], y=data['SMA_50'], mode='lines', name='SMA 50'))
fig2.update_layout(title=f"{ticker} with Moving Averages", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig2)

# Daily Returns
st.subheader("Daily Returns")
data['Returns'] = data['Close'].pct_change()
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=data['Date'], y=data['Returns'], mode='lines', name='Returns'))
fig3.update_layout(title=f"{ticker} Daily Returns", xaxis_title="Date", yaxis_title="Return")
st.plotly_chart(fig3)

