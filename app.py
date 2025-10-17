# ==========================================================
# Portfolio Risk & Performance Dashboard (Dan Li)
# ==========================================================
import streamlit as st
import pandas as pd
import datetime
from importlib import reload
import RiskAnalysis_Advanced as risk

# ----------------------------------------------------------
# 1. Page setup
# ----------------------------------------------------------
st.set_page_config(page_title="Portfolio Risk Dashboard", layout="wide", page_icon="📊")

st.markdown(
    """
    <style>
    .stApp {background-color: #f8f9ff;}
    .main-title {font-size: 32px; color: #3f4dcb; font-weight: 700;}
    .metric-label {color: #3f4dcb;}
    </style>
    """, unsafe_allow_html=True
)

col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.markdown("<div class='main-title'>📊 Portfolio Risk & Performance Dashboard</div>", unsafe_allow_html=True)
    st.markdown("Automated risk analytics powered by **Python + yFinance**.")
with col2:
    if st.button("🔄 Refresh Data", key="refresh_main"):
        with st.spinner("Fetching latest market data..."):
            try:
                reload(risk)
                risk.generate_report()
                st.success("✅ Data refreshed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to refresh data: {e}")

# ----------------------------------------------------------
# 2. Load Excel data
# ----------------------------------------------------------
FILE_PATH = "reports/Portfolio_Analysis_Advanced.xlsx"

@st.cache_data
def load_excel(path):
    return pd.read_excel(path, sheet_name=None)

try:
    data = load_excel(FILE_PATH)
except FileNotFoundError:
    st.warning("No report found yet. Click 🔄 **Refresh Data** to generate the first dataset.")
    st.stop()

summary = data.get("Summary Metrics")
portfolio_value = data.get("Portfolio Value")
returns = data.get("Daily Returns")
drawdown = data.get("Drawdown")
rolling_sharpe = data.get("Rolling Sharpe")
price_data = data.get("Price Data")

# ----------------------------------------------------------
# 3. Clean function
# ----------------------------------------------------------
def clean_for_chart(df):
    df = df.copy()
    if "Unnamed: 0" in df.columns:
        df.rename(columns={"Unnamed: 0": "Date"}, inplace=True)
    if "Date" not in df.columns:
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.set_index("Date")
    df = df.select_dtypes(include=["number"])
    df.columns = df.columns.map(str)
    return df.dropna()

# ----------------------------------------------------------
# 4. Sidebar filters
# ----------------------------------------------------------
st.sidebar.header("📅 Date Filter")
pv = clean_for_chart(portfolio_value)
min_date, max_date = pv.index.min(), pv.index.max()
start_date, end_date = st.sidebar.date_input(
    "Select date range", [min_date, max_date], min_value=min_date, max_value=max_date
)
pv_filtered = pv.loc[str(start_date):str(end_date)]

# ----------------------------------------------------------
# 5. Key metrics
# ----------------------------------------------------------
st.header("📈 Key Portfolio Metrics")

metrics = {row["Metric"]: row["Value"] for _, row in summary.iterrows()}

cols = st.columns(4)
cols[0].metric("💰 Final Value", f"${metrics.get('Final Value', 0):,.0f}")
cols[1].metric("📆 CAGR", f"{metrics.get('Annualized Return (CAGR)', 0)*100:.2f}%")
cols[2].metric("📊 Volatility", f"{metrics.get('Volatility (Annualized)', 0)*100:.2f}%")
cols[3].metric("⚖️ Sharpe Ratio", f"{metrics.get('Sharpe Ratio', 0):.2f}")

st.divider()

# ----------------------------------------------------------
# 6. Charts
# ----------------------------------------------------------
st.header("💼 Portfolio Value Over Time")
st.line_chart(pv_filtered, y=pv_filtered.columns[0], width='stretch')

st.header("📉 Maximum Drawdown")
dd = clean_for_chart(drawdown)
st.area_chart(dd, y=dd.columns[0], height=250, width='stretch')

st.header("📊 Rolling Sharpe Ratio (90-day Window)")
rs = clean_for_chart(rolling_sharpe)
st.line_chart(rs, y=rs.columns[0], height=250, width='stretch')

# ----------------------------------------------------------
# 7. Data explorer
# ----------------------------------------------------------
st.divider()
st.header("📂 Detailed Data Explorer")
tab1, tab2, tab3 = st.tabs(["Summary Metrics", "Daily Returns", "Price Data"])
with tab1:
    st.dataframe(summary, use_container_width=True)
with tab2:
    st.dataframe(returns.tail(10), use_container_width=True)
with tab3:
    st.dataframe(price_data.tail(10), use_container_width=True)

st.caption("✅ **Data Source:** Yahoo Finance | Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
