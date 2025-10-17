# ==========================================================
# Portfolio Risk & Performance Dashboard (Dan Li)
# ==========================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------------
# 1. Page setup
# ----------------------------------------------------------
st.set_page_config(
    page_title="Portfolio Risk Dashboard",
    layout="wide",
    page_icon="📊"
)

st.title("Portfolio Risk & Performance Dashboard")
st.markdown("Automated risk analytics powered by **Python + yFinance**.")

# ----------------------------------------------------------
# 2. Load Excel data
# ----------------------------------------------------------
FILE_PATH = "reports/Portfolio_Analysis_Advanced.xlsx"

@st.cache_data
def load_excel(path):
    data = pd.read_excel(path, sheet_name=None)
    return data

data = load_excel(FILE_PATH)

summary = data.get("Summary Metrics")
portfolio_value = data.get("Portfolio Value")
returns = data.get("Daily Returns")
drawdown = data.get("Drawdown")
rolling_sharpe = data.get("Rolling Sharpe")
price_data = data.get("Price Data")

# ----------------------------------------------------------
# 3. Helper to clean Excel data
# ----------------------------------------------------------
def clean_for_chart(df):
    """Ensure clean numeric columns and datetime index."""
    df = df.copy()
    if "Unnamed: 0" in df.columns:
        df.rename(columns={"Unnamed: 0": "Date"}, inplace=True)
    if "Date" not in df.columns:
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.set_index("Date")
    df = df.select_dtypes(include=["number"])
    df.columns = df.columns.map(str)  # convert all col names to strings
    return df.dropna()

# ----------------------------------------------------------
# 4. Sidebar date range filter
# ----------------------------------------------------------
pv = clean_for_chart(portfolio_value)
min_date, max_date = pv.index.min(), pv.index.max()
st.sidebar.header("🔍 Date Filter")
start_date, end_date = st.sidebar.date_input(
    "Select date range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)
pv_filtered = pv.loc[str(start_date):str(end_date)]

# ----------------------------------------------------------
# 5. Summary Metrics
# ----------------------------------------------------------
st.header("Key Portfolio Metrics")

metrics = {}
if summary is not None and not summary.empty:
    for _, row in summary.iterrows():
        metrics[row["Metric"]] = row["Value"]

cols = st.columns(4)
cols[0].metric("💰 Final Value", f"${metrics.get('Final Value', 0):,.0f}")
cols[1].metric("📆 CAGR", f"{metrics.get('Annualized Return (CAGR)', 0)*100:.2f}%")
cols[2].metric("📊 Volatility", f"{metrics.get('Volatility (Annualized)', 0)*100:.2f}%")
cols[3].metric("⚖️ Sharpe Ratio", f"{metrics.get('Sharpe Ratio', 0):.2f}")

st.divider()

# ----------------------------------------------------------
# 6. Portfolio Value Chart
# ----------------------------------------------------------
st.header("Portfolio Value Over Time")
st.line_chart(pv_filtered, y=pv_filtered.columns[0], use_container_width=True)

# ----------------------------------------------------------
# 7. Drawdown Chart
# ----------------------------------------------------------
st.header("Maximum Drawdown")
dd = clean_for_chart(drawdown)
dd_filtered = dd.loc[str(start_date):str(end_date)]
st.area_chart(dd_filtered, y=dd_filtered.columns[0], height=250, use_container_width=True)

# ----------------------------------------------------------
# 8. Rolling Sharpe Ratio
# ----------------------------------------------------------
st.header("Rolling Sharpe Ratio (90-day Window)")
rs = clean_for_chart(rolling_sharpe)
rs_filtered = rs.loc[str(start_date):str(end_date)]
st.line_chart(rs_filtered, y=rs_filtered.columns[0], height=250, use_container_width=True)

# ----------------------------------------------------------
# 9. Data Explorer Tabs
# ----------------------------------------------------------
st.divider()
st.header("Detailed Data Explorer")

tab1, tab2, tab3 = st.tabs(["Summary Metrics", "Daily Returns", "Price Data"])
with tab1:
    st.dataframe(summary, use_container_width=True)
with tab2:
    st.dataframe(returns.tail(10), use_container_width=True)
with tab3:
    st.dataframe(price_data.tail(10), use_container_width=True)

st.markdown("✅ **Data Source:** Yahoo Finance | Auto-updated via RiskAnalysis_Advanced.py")
