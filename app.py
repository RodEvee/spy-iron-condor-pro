# app.py
import streamlit as st
import time
from datetime import datetime

# ── Imports from modular structure ────────────────────────────────
from src.data import get_spy_data, get_yahoo_options_chain, generate_demo_options_data
from src.analysis import calculate_indicators, calculate_iron_condor_score, find_iron_condor_strikes
from src.paper import init_paper_trading, display_paper_trading_panel
from ui.components import display_header, display_signal_box, display_current_metrics, display_expiry_selector
from ui.professional_chart import display_professional_chart

st.set_page_config(
    page_title="SPY Iron Condor Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS – keep only what's actually used
st.markdown("""
<style>
    .main-header { font-size: 42px; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 10px; }
    .signal-strong-entry { background: linear-gradient(135deg, #11998e, #38ef7d); padding: 20px; border-radius: 10px; color: white; font-size: 24px; text-align: center; }
    .signal-exit { background: linear-gradient(135deg, #ee0979, #ff6a00); padding: 20px; border-radius: 10px; color: white; font-size: 24px; text-align: center; }
    .signal-neutral { background: linear-gradient(135deg, #f2994a, #f2c94c); padding: 20px; border-radius: 10px; color: white; font-size: 24px; text-align: center; }
    .expiry-badge { background: #e3f2fd; color: #1976d2; padding: 5px 12px; border-radius: 15px; font-weight: 600; display: inline-block; }
</style>
""", unsafe_allow_html=True)

def main():
    display_header()

    # ── Sidebar settings ───────────────────────────────────────────
    with st.sidebar:
        st.header("Settings")
        data_source = st.radio("Data Source", ["Demo Mode", "Yahoo Finance"], index=1)
        timeframe_label = st.selectbox("Timeframe", ["Daily (5d)", "Hourly (5d)", "30 min (2d)", "15 min (1d)"])
        auto_refresh = st.checkbox("Auto-refresh every 60s", value=False)

        period, interval = {
            "Daily (5d)":   ("5d", "1d"),
            "Hourly (5d)":  ("5d", "1h"),
            "30 min (2d)":  ("2d", "30m"),
            "15 min (1d)":  ("1d", "15m"),
        }[timeframe_label]

    # ── Data loading ───────────────────────────────────────────────
    with st.spinner("Loading market & options data..."):
        df = get_spy_data(period=period, interval=interval)
        if df.empty:
            st.error("Could not load price data")
            st.stop()

        df = calculate_indicators(df)
        current_price = float(df['Close'].iloc[-1])

        if data_source == "Yahoo Finance":
            options_data = get_yahoo_options_chain("SPY")
        else:
            options_data = generate_demo_options_data()

        if not options_data:
            st.warning("Using demo options data")
            options_data = generate_demo_options_data()

    expirations = sorted(options_data.keys())
    selected_expiry = display_expiry_selector(expirations)

    # ── Analysis & signal ──────────────────────────────────────────
    entry_score, risk_score, signal = calculate_iron_condor_score(df, current_price)

    display_current_metrics(df, current_price, entry_score, risk_score, signal)
    st.markdown("---")
    display_signal_box(signal)
    st.markdown("---")

    # ── Chart ──────────────────────────────────────────────────────
    display_professional_chart(df, current_price, entry_score, risk_score)
    st.markdown("---")

    # ── Paper trading panel (placeholder integration) ──────────────
    display_paper_trading_panel(options_data, current_price, selected_expiry)

    # Auto-refresh
    if auto_refresh:
        time.sleep(60)
        st.rerun()

if __name__ == "__main__":
    init_paper_trading()
    main()
