# app.py
import streamlit as st
import time
import pandas as pd
from datetime import datetime

# ── Modular imports ────────────────────────────────────────────────────────
from src.data import get_spy_data, get_yahoo_options_chain, generate_demo_options_data
from src.analysis import calculate_indicators, calculate_iron_condor_score, find_iron_condor_strikes
from src.greeks import calculate_delta  # only delta used right now, others available
from src.paper import initialize_paper_trading
from ui.components import (
    display_header,
    display_signal_box,
    display_current_metrics,
    display_expiry_selector
)
from ui.professional_chart import display_professional_chart
from ui.paper_trading_ui import display_paper_trading_panel

# ── Page config & CSS ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPY Iron Condor Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 42px; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 10px; }
    .signal-strong-entry { background: linear-gradient(135deg, #11998e, #38ef7d); padding: 20px; border-radius: 10px; color: white; font-size: 24px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .signal-exit { background: linear-gradient(135deg, #ee0979, #ff6a00); padding: 20px; border-radius: 10px; color: white; font-size: 24px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .signal-neutral { background: linear-gradient(135deg, #f2994a, #f2c94c); padding: 20px; border-radius: 10px; color: white; font-size: 24px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .expiry-badge { background: #e3f2fd; color: #1976d2; padding: 6px 14px; border-radius: 20px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

def main():
    display_header()

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Controls")
        data_source = st.radio("Data Source", ["Demo Mode", "Yahoo Finance (real)"], index=1)
        timeframe_label = st.selectbox("Chart Timeframe", [
            "Daily (5d)", "Hourly (5d)", "30 min (2d)", "15 min (1d)"
        ])
        paper_enabled = st.checkbox("Enable Paper Trading", value=False)
        auto_refresh = st.checkbox("Auto-refresh every 60s", value=False)

        period, interval = {
            "Daily (5d)":   ("5d", "1d"),
            "Hourly (5d)":  ("5d", "1h"),
            "30 min (2d)":  ("2d", "30m"),
            "15 min (1d)":  ("1d", "15m"),
        }[timeframe_label]

    # ── Data loading ───────────────────────────────────────────────────────────
    with st.spinner("Fetching market & options data..."):
        df = get_spy_data(period=period, interval=interval)
        if df.empty:
            st.error("Could not load price data – using minimal fallback")
            df = pd.DataFrame({'Close': [580.0]}, index=[datetime.now()])

        df = calculate_indicators(df)
        current_price = float(df['Close'].iloc[-1]) if not df.empty else 580.0

        if data_source == "Yahoo Finance (real)":
            options_data = get_yahoo_options_chain("SPY")
        else:
            options_data = generate_demo_options_data()

        if not options_data:
            st.warning("No options data – falling back to demo")
            options_data = generate_demo_options_data()

    expirations = sorted(options_data.keys())
    selected_expiry = display_expiry_selector(expirations)

    # ── Core analysis ──────────────────────────────────────────────────────────
    entry_score, risk_score, signal = calculate_iron_condor_score(df, current_price)

    display_current_metrics(df, current_price, entry_score, risk_score, signal)
    st.markdown("---")
    display_signal_box(signal)
    st.markdown("---")

    # ── Main chart ─────────────────────────────────────────────────────────────
    display_professional_chart(df, current_price, entry_score, risk_score)
    st.markdown("---")

    # ── Paper Trading ──────────────────────────────────────────────────────────
    if paper_enabled:
        display_paper_trading_panel(
            options_data=options_data,
            current_price=current_price,
            selected_expiry=selected_expiry
        )
        st.markdown("---")

    # ── Optional: Recommended Iron Condor setups (expandable cards) ────────────
    st.subheader("🎯 Recommended Iron Condor Setups")
    col_setup = st.columns(3)

    deltas = [0.16, 0.20, 0.30]
    labels = ["Conservative (16Δ)", "Balanced (20Δ)", "Aggressive (30Δ)"]

    for i, (delta, label) in enumerate(zip(deltas, labels)):
        with col_setup[i]:
            with st.expander(label, expanded=(delta == 0.20)):
                setup = find_iron_condor_strikes(
                    options_data, selected_expiry, current_price, target_delta=delta
                )
                if setup:
                    st.markdown(f"**POP estimate:** {setup['pop']}%")
                    st.markdown(f"**Max Profit:** ${setup['max_profit']:.2f}")
                    st.markdown(f"**Max Loss:** ${setup['max_loss']:.2f}")

                    st.markdown("**Call Spread**")
                    st.write(f"Short: {setup['short_call']['strike']} @ {setup['short_call']['bid']:.2f}")
                    st.write(f"Long:  {setup['long_call']['strike']} @ {setup['long_call']['ask']:.2f}")

                    st.markdown("**Put Spread**")
                    st.write(f"Short: {setup['short_put']['strike']} @ {setup['short_put']['bid']:.2f}")
                    st.write(f"Long:  {setup['long_put']['strike']} @ {setup['long_put']['ask']:.2f}")
                else:
                    st.info("No valid setup for this delta")

    # ── Auto-refresh ───────────────────────────────────────────────────────────
    if auto_refresh:
        time.sleep(60)
        st.rerun()

if __name__ == "__main__":
    initialize_paper_trading()
    main()
