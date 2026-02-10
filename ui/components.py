# ui/components.py
import streamlit as st
from datetime import datetime

def display_header():
    """Main app title and subtitle"""
    st.markdown(
        '<div class="main-header">📊 SPY IRON CONDOR PRO</div>'
        '<div class="sub-header">'
        'Real-time signals • Multiple expirations • Full Greeks • Paper Trading'
        '</div>',
        unsafe_allow_html=True
    )


def display_signal_box(signal: str):
    """Large colored signal indicator"""
    if "STRONG" in signal or "ENTRY" in signal:
        st.markdown(
            f'<div class="signal-strong-entry">🟢 {signal}</div>',
            unsafe_allow_html=True
        )
    elif "EXIT" in signal or "AVOID" in signal or "CAUTION" in signal:
        st.markdown(
            f'<div class="signal-exit">🔴 {signal}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="signal-neutral">🟡 {signal}</div>',
            unsafe_allow_html=True
        )


def display_current_metrics(df, current_price: float, entry_score: int, risk_score: int, signal: str):
    """Key metrics row"""
    col1, col2, col3, col4, col5 = st.columns(5)

    price_change = 0
    if len(df) >= 2:
        price_change = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100

    with col1:
        st.metric("SPY Price", f"${current_price:.2f}", f"{price_change:+.2f}%")

    with col2:
        st.metric("Entry Score", f"{entry_score}/9", "Good" if entry_score >= 5 else "Low")

    with col3:
        st.metric("Risk Score", f"{risk_score}/9", "High" if risk_score >= 5 else "Low")

    with col4:
        rsi = df.iloc[-1].get('RSI', 50)
        st.metric("RSI", f"{rsi:.1f}", "Neutral" if 40 <= rsi <= 60 else "Extreme")

    with col5:
        atr_pct = df.iloc[-1].get('ATR_pct', 1.0) if 'ATR_pct' in df.columns else 1.0
        st.metric("ATR %", f"{atr_pct:.2f}%", "Low Vol ✅" if atr_pct < 1.5 else "High Vol ⚠️")


def display_expiry_selector(expirations: list):
    """Compact dropdown for expiration selection"""
    if not expirations:
        st.warning("No expirations available")
        return None

    selected = st.session_state.get("selected_expiry", expirations[0])
    if selected not in expirations:
        selected = expirations[0]

    # Build labels with DTE
    options = []
    for exp in expirations[:12]:
        dte = (datetime.strptime(exp, '%Y-%m-%d') - datetime.now()).days
        options.append(f"{exp}  ({dte}d)")

    default_idx = 0
    for i, opt in enumerate(options):
        if selected in opt:
            default_idx = i
            break

    choice = st.selectbox("📅 Expiration", options, index=default_idx, key="expiry_dropdown")

    # Extract date from the label
    chosen_date = choice.split("  ")[0]
    if chosen_date != selected:
        st.session_state.selected_expiry = chosen_date

    return chosen_date

