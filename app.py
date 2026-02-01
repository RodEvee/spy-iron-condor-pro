# app.py
import streamlit as st
from datetime import datetime
from src.greeks import calculate_delta, calculate_gamma, calculate_theta, calculate_vega, calculate_rho
from ui.components import display_header, display_signal_box, display_current_metrics, display_expiry_selector
from src.data import get_spy_data, get_yahoo_options_chain, generate_demo_options_data
from src.analysis import calculate_indicators, calculate_iron_condor_score, find_iron_condor_strikes
from src.paper import init_paper_trading, display_paper_trading_panel
from ui.components import (
    display_header, display_current_metrics, display_signal_box,
    display_iron_condor_setups, display_full_options_chain
)
from ui.professional_chart import display_professional_chart

st.set_page_config(
    page_title="SPY Iron Condor Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (kept minimal – move to separate file later if grows)
st.markdown("""
<style>
    .main-header { font-size: 42px; font-weight: bold; color: #1f77b4; text-align: center; }
    .signal-strong-entry { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 24px; }
    .signal-exit { background: linear-gradient(135deg, #ee0979, #ff6a00); color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 24px; }
    .expiry-badge { background: #e3f2fd; color: #1976d2; padding: 5px 12px; border-radius: 15px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

def main():
    display_header()

    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        data_mode = st.radio("Data Source", ["Demo Mode", "Yahoo Finance (Real)"], index=1)
        timeframe = st.selectbox("Timeframe", ["Daily (5d)", "1h (5d)", "30m (2d)", "15m (1d)"])
        auto_refresh = st.checkbox("Auto-refresh every 60s", False)

        period, interval = {
            "Daily (5d)": ("5d", "1d"),
            "1h (5d)": ("5d", "1h"),
            "30m (2d)": ("2d", "30m"),
            "15m (1d)": ("1d", "15m"),
        }[timeframe]

    # Data loading
    with st.spinner("Loading market data..."):
        df = get_spy_data(period=period, interval=interval)
        df = calculate_indicators(df)
        current_price = float(df['Close'].iloc[-1])

        options_data = (
            get_yahoo_options_chain("SPY")
            if data_mode == "Yahoo Finance (Real)"
            else generate_demo_options_data()
        )

    if not options_data:
        st.error("No options data available. Try again later.")
        st.stop()

    expirations = sorted(options_data.keys())
    selected_expiry = st.session_state.get("selected_expiry", expirations[0])

    # Signal & score
    entry_score, risk_score, signal = calculate_iron_condor_score(df, current_price)

    # UI layout
    display_current_metrics(df, current_price, entry_score, risk_score, signal)
    st.markdown("---")
    display_signal_box(signal)
    st.markdown("---")

    # Expiration selector (horizontal buttons)
    st.subheader("📅 Expiration")
    cols = st.columns(min(6, len(expirations)))
    for i, exp in enumerate(expirations[:12]):
        days = (datetime.strptime(exp, '%Y-%m-%d') - datetime.now()).days
        label = f"{exp} ({days}d)"
        if cols[i % len(cols)].button(label, key=f"exp_{exp}", use_container_width=True):
            st.session_state.selected_expiry = exp
            st.rerun()

    st.markdown(f"**Selected:** <span class='expiry-badge'>{selected_expiry}</span>", unsafe_allow_html=True)

    # Core sections
    display_professional_chart(df, current_price, entry_score, risk_score)
    st.markdown("---")

    # Iron Condor setups
    display_iron_condor_setups(options_data, current_price, selected_expiry)

    # Paper trading (if enabled)
    if st.session_state.get("paper_enabled", False):
        display_paper_trading_panel(options_data, current_price, selected_expiry)
        st.markdown("---")

    # Full chain
    display_full_options_chain(options_data, selected_expiry, current_price)

    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

if __name__ == "__main__":
    # Paper trading init (always available, toggle via sidebar later)
    init_paper_trading()
    main()
