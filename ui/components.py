# ui/components.py
import streamlit as st
from datetime import datetime

def display_header():
    """Main app title and subtitle"""
    st.markdown(
        '<div class="main-header">📊 SPY IRON CONDOR PRO</div>'
        '<div style="font-size:18px; color:#666; text-align:center; margin-bottom:30px;">'
        'Real-time signals • Multiple expirations • Full Greeks</div>',
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
        st.metric("Vol %", f"{atr_pct:.2f}%", "Low" if atr_pct < 1.0 else "High")


def display_expiry_selector(expirations: list[str]):
    """Horizontal buttons for expiration selection"""
    st.subheader("📅 Select Expiration")

    if not expirations:
        st.warning("No expirations available")
        return expirations[0] if expirations else None

    cols = st.columns(min(6, len(expirations)))
    selected = st.session_state.get("selected_expiry", expirations[0])

    for i, exp in enumerate(expirations[:12]):
        dte = (datetime.strptime(exp, '%Y-%m-%d') - datetime.now()).days
        label = f"{exp}\n({dte}d)"
        key = f"exp_select_{exp}"

        if cols[i % len(cols)].button(label, key=key, use_container_width=True):
            st.session_state.selected_expiry = exp
            st.rerun()

    st.markdown(f"**Active:** <span class='expiry-badge'>{selected}</span>", unsafe_allow_html=True)
    return selected
