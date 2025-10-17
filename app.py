# ==========================================================
# Portfolio Risk & Performance Dashboard (Dan Li)
# ==========================================================

import streamlit as st
import pandas as pd
import subprocess
import datetime

# ----------------------------------------------------------
# 1. Page setup
# ----------------------------------------------------------
st.set_page_config(
    page_title="Portfolio Risk Dashboard",
    layout="wide",
    page_icon="📊"
)

# --- Custom CSS styling ---
st.markdown("""
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #2b2b2b;
        }
        .stButton button {
            background-color: #3F4DCB;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 600;
            transition: 0.2s;
        }
        .stButton button:hover {
            background-color: #2f3cb8;
        }
        .metric-card {
            background-color: #f7f8ff;
            border-radius: 12px;
            padding: 10px 16px;
            text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }
        h3 {
            color: #3F4DCB;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# 2. Header section
# ----------------------------------------------------------
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("<div class='main-title'>📊 Portfolio Risk & Performance Dashboard</div>", unsafe_allow_html=True)
    st.markdown("Automated risk analytics powered by **Python + yFinance + GitHub Actions**.")
with col2:
    if st.button("🔄 Refresh Data"):
        with st.spinner("Fetching latest market data..."):
            try:
                subprocess.run(["python3", "RiskAnalysis_Advanced.py"], check=True)
                st.success("✅ Data refreshed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to refresh data: {e}")

# Timestamp
st.caption(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

st.divider()

# ----------------------------------------------------------
# 3. Load Excel data
# ----------------------------------------------------------
FILE_PATH = "reports/Portfolio_Analysis_Advanced.xlsx"

@st.cache_data
def load_excel(path):
    data = pd.read_excel(path, sheet_name=None)
    return data

try:
    data = load_excel(FILE_PATH)
except FileNotFoundError:
    st.error("❌ Portfolio_Analysis_Advanced.xlsx not found. Please run RiskAnalysis_Advanced.py first.")
    st.stop()

summary = data.get("Summary Metrics")
portfolio_value = data.get("Portfolio Value")
returns = data.get("Daily Returns")
drawdown = data.get("Drawdown")
rolling_sharpe = data.get("Rolling Sharpe")
price_data = data.get("Price Data")

# ----------------------------------------------------------
# 4. Helper to clean Excel data
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
# 5. Sidebar date filter (persistent via query params)
# ----------------------------------------------------------
st.sidebar.header("📅 Date Filter")

pv = clean_for_chart(portfolio_value)
min_date, max_date = pv.index.min(), pv.index.max()

# Get query params safely
query_params = st.query_params

def safe_parse_date(value, fallback):
    """Try parsing a date string, otherwise return fallback."""
    try:
        return pd.to_datetime(value)
    except Exception:
        return fallback

start_q = query_params.get("start", [str(min_date)])[0]
end_q = query_params.get("end", [str(max_date)])[0]

start_date = safe_parse_date(start_q, min_date)
end_date = safe_parse_date(end_q, max_date)

# Sidebar selector (user can override)
start_date, end_date = st.sidebar.date_input(
    "Select date range",
    [start_date, end_date],
    min_value=min_date,
    max_value=max_date
)

# Update query params for sharing
st.query_params["start"] = str(start_date)
st.query_params["end"] = str(end_date)

# Filter portfolio
pv_filtered = pv.loc[str(start_date):str(end_date)]


# ----------------------------------------------------------
# 6. Summary metrics (cards)
# ----------------------------------------------------------
st.subheader("📈 Key Portfolio Metrics")

metrics = {}
if summary is not None and not summary.empty:
    for _, row in summary.iterrows():
        metrics[row["Metric"]] = row["Value"]

cols = st.columns(4)
with cols[0]:
    st.markdown("<div class='metric-card'>💰 **Final Value**<br>" +
                f"<h3>${metrics.get('Final Value', 0):,.0f}</h3></div>", unsafe_allow_html=True)
with cols[1]:
    st.markdown("<div class='metric-card'>📆 **CAGR**<br>" +
                f"<h3>{metrics.get('Annualized Return (CAGR)', 0)*100:.2f}%</h3></div>", unsafe_allow_html=True)
with cols[2]:
    st.markdown("<div class='metric-card'>📊 **Volatility**<br>" +
                f"<h3>{metrics.get('Volatility (Annualized)', 0)*100:.2f}%</h3></div>", unsafe_allow_html=True)
with cols[3]:
    st.markdown("<div class='metric-card'>⚖️ **Sharpe Ratio**<br>" +
                f"<h3>{metrics.get('Sharpe Ratio', 0):.2f}</h3></div>", unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------------
# 7. Charts
# ----------------------------------------------------------
st.subheader("💼 Portfolio Value Over Time")
st.line_chart(pv_filtered, y=pv_filtered.columns[0], use_container_width=True)

st.subheader("📉 Maximum Drawdown")
dd = clean_for_chart(drawdown)
dd_filtered = dd.loc[str(start_date):str(end_date)]
st.area_chart(dd_filtered, y=dd_filtered.columns[0], height=250, use_container_width=True)

st.subheader("📊 Rolling Sharpe Ratio (90-day Window)")
rs = clean_for_chart(rolling_sharpe)
rs_filtered = rs.loc[str(start_date):str(end_date)]
st.line_chart(rs_filtered, y=rs_filtered.columns[0], height=250, use_container_width=True)

# ----------------------------------------------------------
# 8. Data explorer
# ----------------------------------------------------------
st.divider()
st.subheader("📂 Detailed Data Explorer")
tab1, tab2, tab3 = st.tabs(["Summary Metrics", "Daily Returns", "Price Data"])
with tab1:
    st.dataframe(summary, use_container_width=True)
with tab2:
    st.dataframe(returns.tail(10), use_container_width=True)
with tab3:
    st.dataframe(price_data.tail(10), use_container_width=True)

st.markdown("✅ **Data Source:** Yahoo Finance | Auto-updated via GitHub Actions")
