# ui/paper_trading_ui.py
import streamlit as st
import pandas as pd
from datetime import datetime
from src.paper import PaperTradingPortfolio


def display_paper_trading_dashboard(portfolio: PaperTradingPortfolio):
    """Main dashboard overview"""
    if not portfolio:
        st.error("Portfolio not initialized")
        return

    stats = portfolio.get_stats()

    st.markdown("## 📈 Paper Trading Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Account Value", f"${stats['account_value']:,.2f}",
                  delta=f"{stats['total_pnl']:,.2f}", delta_color="normal")

    with col2:
        st.metric("Cash Balance", f"${stats['cash']:,.2f}")

    with col3:
        pnl_color = "normal" if stats['total_pnl'] >= 0 else "inverse"
        st.metric("Total P&L", f"${stats['total_pnl']:,.2f}", delta_color=pnl_color)

    with col4:
        st.metric("Open Positions", stats['open_positions'])

    # Trade history summary
    if stats['closed_trades'] > 0:
        st.markdown("---")
        st.caption(f"📊 {stats['closed_trades']} closed trades | {stats['total_trades']} total trades")

    st.markdown("---")


def display_open_position_form(options_data, current_price, selected_expiry, ic_setups):
    """Form to open new Iron Condor paper trade"""
    st.subheader("Open New Iron Condor Position")

    if not ic_setups:
        st.warning("No valid Iron Condor setups available yet.")
        return

    setup_options = [f"{i+1}: {s['pop']}% POP — Δ {s['target_delta']}" for i, s in enumerate(ic_setups)]
    choice = st.selectbox("Select Setup", setup_options)

    if choice:
        idx = int(choice.split(":")[0]) - 1
        selected_setup = ic_setups[idx]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Call Spread**")
            st.write(f"Short: {selected_setup['short_call']['strike']} @ {selected_setup['short_call']['bid']:.2f}")
            st.write(f"Long:  {selected_setup['long_call']['strike']} @ {selected_setup['long_call']['ask']:.2f}")

        with col2:
            st.markdown("**Put Spread**")
            st.write(f"Short: {selected_setup['short_put']['strike']} @ {selected_setup['short_put']['bid']:.2f}")
            st.write(f"Long:  {selected_setup['long_put']['strike']} @ {selected_setup['long_put']['ask']:.2f}")

        quantity = st.number_input("Contracts (quantity)", min_value=1, max_value=20, value=1)

        credit = selected_setup['max_profit'] * quantity
        risk = selected_setup['max_loss'] * quantity

        st.metric("Expected Credit", f"${credit:,.2f}")
        st.metric("Max Risk / Margin", f"${risk:,.2f}")

        if st.button("Open Paper Trade", type="primary"):
            success, msg = st.session_state.paper_portfolio.open_position(selected_setup, quantity)
            if success:
                st.success(msg)
            else:
                st.error(msg)


def display_positions_table(portfolio: PaperTradingPortfolio, options_data, current_price):
    """Detailed view of open positions with strike info"""
    if not portfolio.positions:
        st.info("No open positions yet.")
        return

    st.subheader("Open Positions")

    data = []
    for pos in portfolio.positions:
        setup = pos['setup']
        row = {
            'ID': pos['id'],
            'Expiration': pos['expiration'],
            'Qty': pos['quantity'],
            'Short Call': setup['short_call']['strike'],
            'Long Call': setup['long_call']['strike'],
            'Short Put': setup['short_put']['strike'],
            'Long Put': setup['long_put']['strike'],
            'Entry Credit': f"${pos['entry_credit']:,.2f}",
            'Max Risk': f"${pos['max_loss']:,.2f}",
            'Status': pos['status']
        }
        data.append(row)

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Close position buttons
    st.markdown("---")
    st.subheader("Close a Position")
    if portfolio.positions:
        pos_choice = st.selectbox("Select Position to Close",
                                  [f"#{p['id']} — Credit ${p['entry_credit']:,.2f}" for p in portfolio.positions])
        close_pct = st.slider("Close at % of max profit", 0, 100, 50) / 100
        if st.button("Close Position", type="secondary"):
            pos_id = int(pos_choice.split("#")[1].split(" ")[0])
            success, msg = portfolio.close_position(pos_id, close_pct)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def display_paper_trading_panel(options_data, current_price, selected_expiry):
    """Main entry point – call this from app.py"""
    from src.paper import initialize_paper_trading
    initialize_paper_trading()

    portfolio = st.session_state.paper_portfolio

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Open Positions", "New Trade"])

    with tab1:
        display_paper_trading_dashboard(portfolio)

    with tab2:
        display_positions_table(portfolio, options_data, current_price)

    with tab3:
        from src.analysis import find_iron_condor_strikes
        ic_setups = []
        for delta in [0.16, 0.20, 0.30]:
            setup = find_iron_condor_strikes(options_data, selected_expiry, current_price, delta)
            if setup:
                setup['target_delta'] = delta
                ic_setups.append(setup)
        display_open_position_form(options_data, current_price, selected_expiry, ic_setups)
