# app.py
import streamlit as st
import time
import pandas as pd
from datetime import datetime

# ── Modular imports ────────────────────────────────────────────────────────
from src.data import get_spy_data, get_yahoo_options_chain, generate_demo_options_data
from src.analysis import calculate_indicators, calculate_iron_condor_score, find_iron_condor_strikes
from src.paper import initialize_paper_trading
from ui.components import (
    display_header,
    display_signal_box,
    display_current_metrics,
    display_expiry_selector
)
from ui.paper_trading_ui import display_paper_trading_panel
from ui.professional_chart import display_professional_chart

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPY Iron Condor Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark Professional Theme CSS ────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Base Dark Theme ────────────────────────────────────── */
    .stApp {
        background: linear-gradient(180deg, #0a0e17 0%, #111827 100%);
        color: #e2e8f0;
    }

    /* ── Header ──────────────────────────────────────────────── */
    .main-header {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 16px;
        color: #64748b;
        text-align: center;
        margin-bottom: 30px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Signal Boxes ────────────────────────────────────────── */
    .signal-strong-entry {
        background: linear-gradient(135deg, #064e3b, #059669);
        padding: 22px;
        border-radius: 12px;
        color: #ecfdf5;
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 0 30px rgba(5, 150, 105, 0.3);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .signal-exit {
        background: linear-gradient(135deg, #7f1d1d, #dc2626);
        padding: 22px;
        border-radius: 12px;
        color: #fef2f2;
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 0 30px rgba(220, 38, 38, 0.3);
        border: 1px solid rgba(248, 113, 113, 0.3);
    }
    .signal-neutral {
        background: linear-gradient(135deg, #78350f, #d97706);
        padding: 22px;
        border-radius: 12px;
        color: #fffbeb;
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 0 30px rgba(217, 119, 6, 0.3);
        border: 1px solid rgba(251, 191, 36, 0.3);
    }

    /* ── Expiry Badge ────────────────────────────────────────── */
    .expiry-badge {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* ── Cards / Containers ──────────────────────────────────── */
    .stExpander {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(100, 116, 139, 0.2) !important;
        border-radius: 12px !important;
    }

    /* ── Metrics ─────────────────────────────────────────────── */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stMetricDelta"] > div {
        font-size: 14px !important;
    }

    /* ── Sidebar ─────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(100, 116, 139, 0.2) !important;
    }

    /* ── Tabs ────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom-color: #3b82f6 !important;
    }

    /* ── Buttons ─────────────────────────────────────────────── */
    .stButton > button {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(100, 116, 139, 0.3) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: rgba(59, 130, 246, 0.2) !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.15) !important;
    }

    /* ── Dividers ─────────────────────────────────────────────── */
    hr {
        border-color: rgba(100, 116, 139, 0.2) !important;
    }

    /* ── Disclaimer bar ──────────────────────────────────────── */
    .disclaimer {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(100, 116, 139, 0.15);
        border-radius: 8px;
        padding: 10px 16px;
        text-align: center;
        color: #64748b;
        font-size: 12px;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    display_header()

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Controls")
        data_source = st.radio("Data Source", ["Demo Mode", "Yahoo Finance (real)"], index=1)
        timeframe_label = st.selectbox("Timeframe (for indicators)", [
            "Daily (5d)", "Hourly (5d)", "30 min (2d)", "15 min (1d)"
        ])
        paper_enabled = st.checkbox("Enable Paper Trading", value=False)
        show_chart = st.checkbox("Show Professional Chart", value=True)
        auto_refresh = st.checkbox("Auto-refresh every 60s", value=False)

        period, interval = {
            "Daily (5d)":   ("5d", "1d"),
            "Hourly (5d)":  ("5d", "1h"),
            "30 min (2d)":  ("2d", "30m"),
            "15 min (1d)":  ("1d", "15m"),
        }[timeframe_label]

        st.markdown("---")
        st.caption("📊 SPY Iron Condor Pro v2.1")
        st.caption("⚠️ Educational tool — not financial advice")

    # ── Data loading ───────────────────────────────────────────────────────────
    with st.spinner("Fetching market & options data..."):
        df = get_spy_data(period=period, interval=interval)
        if df.empty:
            st.warning("No price data loaded — using fallback price")
            current_price = 580.0
        else:
            df = calculate_indicators(df)
            current_price = float(df['Close'].iloc[-1]) if not df.empty else 580.0

        if data_source == "Yahoo Finance (real)":
            options_data = get_yahoo_options_chain("SPY")
        else:
            options_data = generate_demo_options_data()

        if not options_data:
            st.warning("No options chain loaded — using demo chain")
            options_data = generate_demo_options_data()

    expirations = sorted(options_data.keys())
    selected_expiry = display_expiry_selector(expirations)

    # ── Core analysis ──────────────────────────────────────────────────────────
    entry_score, risk_score, signal = calculate_iron_condor_score(df, current_price)

    display_current_metrics(df, current_price, entry_score, risk_score, signal)
    st.markdown("---")
    display_signal_box(signal)
    st.markdown("---")

    # ── Professional Chart ─────────────────────────────────────────────────────
    if show_chart and not df.empty:
        display_professional_chart(df, current_price, entry_score, risk_score)
        st.markdown("---")

    # ── Recommended Iron Condor setups ─────────────────────────────────────────
    st.subheader("🎯 Recommended Iron Condor Setups")
    col1, col2, col3 = st.columns(3)

    deltas = [0.16, 0.20, 0.30]
    labels = ["Conservative (16Δ)", "Balanced (20Δ) ⭐", "Aggressive (30Δ)"]
    columns = [col1, col2, col3]

    for col, delta, label in zip(columns, deltas, labels):
        with col:
            with st.expander(label, expanded=(delta == 0.20)):
                setup = find_iron_condor_strikes(
                    options_data, selected_expiry, current_price, target_delta=delta
                )
                if setup:
                    st.metric("POP estimate", f"{setup['pop']}%")
                    st.metric("Max Profit", f"${setup['max_profit']:.2f}")
                    st.metric("Max Loss", f"${setup['max_loss']:.2f}")

                    st.markdown("**Call Spread**")
                    st.write(f"Short: **{setup['short_call']['strike']}** @ {setup['short_call']['bid']:.2f}")
                    st.write(f"Long:  {setup['long_call']['strike']} @ {setup['long_call']['ask']:.2f}")

                    st.markdown("**Put Spread**")
                    st.write(f"Short: **{setup['short_put']['strike']}** @ {setup['short_put']['bid']:.2f}")
                    st.write(f"Long:  {setup['long_put']['strike']} @ {setup['long_put']['ask']:.2f}")

                    st.info(f"Breakevens: {setup['breakeven_lower']:.1f} – {setup['breakeven_upper']:.1f}")
                else:
                    st.info("No valid strikes found for this delta")

    st.markdown("---")

    # ── Paper Trading ──────────────────────────────────────────────────────────
    if paper_enabled:
        st.subheader("💼 Paper Trading")
        display_paper_trading_panel(
            options_data=options_data,
            current_price=current_price,
            selected_expiry=selected_expiry
        )

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="disclaimer">'
        '⚠️ This tool is for educational & informational purposes only. '
        'It does not constitute financial advice. Trade at your own risk.'
        '</div>',
        unsafe_allow_html=True
    )

    # ── Auto-refresh ───────────────────────────────────────────────────────────
    if auto_refresh:
        time.sleep(60)
        st.rerun()

if __name__ == "__main__":
    initialize_paper_trading()
    main()
