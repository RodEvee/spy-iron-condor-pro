"""
Paper Trading UI Components for SPY Iron Condor Bot
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from paper_trading import PaperTradingPortfolio

def initialize_paper_trading():
    """Initialize paper trading portfolio in session state"""
    if 'paper_portfolio' not in st.session_state:
        st.session_state.paper_portfolio = PaperTradingPortfolio(initial_cash=10000.0)
    if 'paper_trading_enabled' not in st.session_state:
        st.session_state.paper_trading_enabled = False

def display_paper_trading_dashboard(portfolio: PaperTradingPortfolio):
    """Display main paper trading dashboard"""
    
    stats = portfolio.get_stats()
    
    st.markdown("## 📈 Paper Trading Dashboard")
    
    # Account Overview
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        pnl_color = "green" if stats['total_pnl'] >= 0 else "red"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center;">
            <div style="color: white; font-size: 14px;">Account Value</div>
            <div style="color: white; font-size: 24px; font-weight: bold;">${stats['account_value']:,.2f}</div>
            <div style="color: {pnl_color}; font-size: 16px; font-weight: bold;">
                {'+' if stats['total_pnl'] >= 0 else ''}{stats['total_pnl']:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; text-align: center;">
            <div style="color: white; font-size: 14px;">Available Cash</div>
            <div style="color: white; font-size: 24px; font-weight: bold;">${stats['cash']:,.2f}</div>
            <div style="color: white; font-size: 12px;">Buying Power</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        roi_color = "green" if stats['roi'] >= 0 else "red"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; text-align: center;">
            <div style="color: white; font-size: 14px;">ROI</div>
            <div style="color: {roi_color}; font-size: 24px; font-weight: bold;">{stats['roi']:+.2f}%</div>
            <div style="color: white; font-size: 12px;">Total Return</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; border-radius: 10px; text-align: center;">
            <div style="color: white; font-size: 14px;">Win Rate</div>
            <div style="color: white; font-size: 24px; font-weight: bold;">{stats['win_rate']:.1f}%</div>
            <div style="color: white; font-size: 12px;">{stats['winning_trades']}W/{stats['losing_trades']}L</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 10px; text-align: center;">
            <div style="color: white; font-size: 14px;">Open Positions</div>
            <div style="color: white; font-size: 24px; font-weight: bold;">{stats['open_positions']}</div>
            <div style="color: white; font-size: 12px;">Active Trades</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Open Positions", "📝 Trade History", "📈 Performance", "⚙️ Settings"])
    
    with tab1:
        display_open_positions(portfolio)
    
    with tab2:
        display_closed_positions(portfolio)
    
    with tab3:
        display_performance_charts(portfolio)
    
    with tab4:
        display_paper_trading_settings(portfolio)

def display_open_positions(portfolio: PaperTradingPortfolio):
    """Display open positions table"""
    
    if not portfolio.positions:
        st.info("📭 No open positions. Use the 'Open Iron Condor' section below to start trading!")
        return
    
    st.markdown("### Open Positions")
    
    for pos in portfolio.positions:
        # Calculate days to expiry
        exp_date = datetime.strptime(pos['expiration'], '%Y-%m-%d')
        days_left = (exp_date - datetime.now()).days
        
        # P&L color
        pnl_color = "green" if pos['current_pnl'] >= 0 else "red"
        pnl_pct = (pos['current_pnl'] / pos['max_profit'] * 100) if pos['max_profit'] > 0 else 0
        
        with st.expander(f"**Position #{pos['id']}** | {pos['expiration']} ({days_left}d) | P&L: ${pos['current_pnl']:,.2f}", expanded=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                **Entry Details:**
                - Entry Date: {pos['entry_date']}
                - SPY @ Entry: ${pos['spy_price_entry']:.2f}
                - Current SPY: ${pos.get('current_spy_price', pos['spy_price_entry']):.2f}
                - Contracts: {pos['contracts']}
                """)
                
                st.markdown(f"""
                **Iron Condor Setup:**
                - Call Spread: ${pos['call_short']:.0f} / ${pos['call_long']:.0f} (${pos['call_spread_credit']:.2f} credit)
                - Put Spread: ${pos['put_short']:.0f} / ${pos['put_long']:.0f} (${pos['put_spread_credit']:.2f} credit)
                """)
            
            with col2:
                st.markdown(f"""
                **P&L Metrics:**
                - Total Credit: ${pos['total_credit']:.2f}
                - Max Profit: ${pos['max_profit']:.2f}
                - Max Loss: ${pos['max_loss']:.2f}
                - Current P&L: <span style='color:{pnl_color}; font-weight:bold; font-size:18px;'>${pos['current_pnl']:,.2f} ({pnl_pct:+.1f}%)</span>
                
                **Risk Metrics:**
                - Margin Used: ${pos['margin_required']:,.2f}
                - Risk/Reward: {abs(pos['max_loss']/pos['max_profit']):.2f}
                """, unsafe_allow_html=True)
            
            with col3:
                # Close position button
                if st.button(f"Close Position #{pos['id']}", key=f"close_{pos['id']}"):
                    st.session_state[f'closing_position_{pos['id']}'] = True
                
                # If closing, show confirmation
                if st.session_state.get(f'closing_position_{pos['id']}', False):
                    st.markdown("**Close at:**")
                    closing_price = st.number_input(
                        "Closing Cost ($)", 
                        value=float(pos['total_credit'] - pos['current_pnl']),
                        key=f"close_price_{pos['id']}"
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Confirm", key=f"confirm_close_{pos['id']}"):
                            portfolio.close_position(
                                pos['id'],
                                datetime.now().strftime('%Y-%m-%d'),
                                pos.get('current_spy_price', pos['spy_price_entry']),
                                closing_price
                            )
                            st.session_state[f'closing_position_{pos['id']}'] = False
                            st.success(f"✅ Position #{pos['id']} closed!")
                            st.rerun()
                    
                    with col_b:
                        if st.button("❌ Cancel", key=f"cancel_close_{pos['id']}"):
                            st.session_state[f'closing_position_{pos['id']}'] = False
                            st.rerun()
            
            if pos.get('notes'):
                st.markdown(f"**Notes:** {pos['notes']}")

def display_closed_positions(portfolio: PaperTradingPortfolio):
    """Display trade history"""
    
    if not portfolio.closed_positions:
        st.info("📭 No closed positions yet.")
        return
    
    st.markdown("### Closed Positions")
    
    # Create dataframe
    trades_data = []
    for pos in portfolio.closed_positions:
        trades_data.append({
            'ID': pos['id'],
            'Entry': pos['entry_date'],
            'Exit': pos['exit_date'],
            'Expiry': pos['expiration'],
            'SPY Entry': f"${pos['spy_price_entry']:.2f}",
            'SPY Exit': f"${pos['exit_spy_price']:.2f}",
            'Contracts': pos['contracts'],
            'Credit': f"${pos['total_credit']:.2f}",
            'P&L': f"${pos['exit_pnl']:.2f}",
            'Result': '✅ Win' if pos['exit_pnl'] > 0 else '❌ Loss'
        })
    
    df = pd.DataFrame(trades_data)
    st.dataframe(df, use_container_width=True)
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    stats = portfolio.get_stats()
    
    with col1:
        st.metric("Total Trades", stats['total_trades'])
    with col2:
        st.metric("Avg Win", f"${stats['avg_win']:.2f}")
    with col3:
        st.metric("Avg Loss", f"${stats['avg_loss']:.2f}")
    with col4:
        st.metric("Win Rate", f"{stats['win_rate']:.1f}%")

def display_performance_charts(portfolio: PaperTradingPortfolio):
    """Display performance charts"""
    
    if not portfolio.trade_history:
        st.info("📊 No trading history yet.")
        return
    
    st.markdown("### Performance Over Time")
    
    # Build equity curve
    equity_data = []
    running_balance = portfolio.initial_cash
    
    for trade in portfolio.trade_history:
        if trade['action'] == 'CLOSE':
            # Find the position
            pos = next((p for p in portfolio.closed_positions if p['id'] == trade['position_id']), None)
            if pos:
                running_balance += pos['exit_pnl']
                equity_data.append({
                    'date': trade['date'],
                    'balance': running_balance,
                    'pnl': pos['exit_pnl']
                })
    
    if equity_data:
        df = pd.DataFrame(equity_data)
        
        # Equity curve
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['balance'],
            mode='lines+markers',
            name='Account Balance',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        # Add starting balance line
        fig.add_hline(
            y=portfolio.initial_cash,
            line_dash="dash",
            line_color="gray",
            annotation_text="Starting Balance"
        )
        
        fig.update_layout(
            title="Account Equity Curve",
            xaxis_title="Date",
            yaxis_title="Account Balance ($)",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # P&L Distribution
        fig2 = go.Figure()
        colors = ['green' if pnl > 0 else 'red' for pnl in df['pnl']]
        
        fig2.add_trace(go.Bar(
            x=df['date'],
            y=df['pnl'],
            marker_color=colors,
            name='Trade P&L'
        ))
        
        fig2.update_layout(
            title="Individual Trade P&L",
            xaxis_title="Date",
            yaxis_title="P&L ($)",
            template="plotly_white",
            height=300
        )
        
        st.plotly_chart(fig2, use_container_width=True)

def display_paper_trading_settings(portfolio: PaperTradingPortfolio):
    """Display paper trading settings"""
    
    st.markdown("### Paper Trading Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Account Actions")
        
        if st.button("🔄 Reset Account", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                st.session_state.paper_portfolio = PaperTradingPortfolio(initial_cash=10000.0)
                st.session_state.confirm_reset = False
                st.success("✅ Account reset!")
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Click again to confirm reset")
        
        if st.button("💾 Export Trading History", use_container_width=True):
            if portfolio.trade_history:
                df = pd.DataFrame(portfolio.trade_history)
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "spy_paper_trading_history.csv",
                    "text/csv",
                    use_container_width=True
                )
            else:
                st.info("No trading history to export")
    
    with col2:
        st.markdown("#### Statistics")
        stats = portfolio.get_stats()
        
        st.metric("Initial Capital", f"${portfolio.initial_cash:,.2f}")
        st.metric("Current Value", f"${stats['account_value']:,.2f}")
        st.metric("Total Return", f"${stats['total_pnl']:,.2f}")
        st.metric("ROI", f"{stats['roi']:+.2f}%")

def display_open_position_form(portfolio: PaperTradingPortfolio, 
                                current_price: float,
                                selected_expiry: str,
                                setup_name: str,
                                call_short: float,
                                call_long: float,
                                put_short: float,
                                put_long: float,
                                call_credit: float,
                                put_credit: float):
    """Display form to open a new position from a setup"""
    
    st.markdown("### 📝 Open This Iron Condor Position")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"""
        **Setup: {setup_name}**
        
        **Strikes:**
        - Call Spread: ${call_short:.0f} / ${call_long:.0f}
        - Put Spread: ${put_short:.0f} / ${put_long:.0f}
        
        **Credits:**
        - Call: ${call_credit:.2f}
        - Put: ${put_credit:.2f}
        - **Total: ${call_credit + put_credit:.2f}**
        """)
    
    with col2:
        contracts = st.number_input(
            "Number of Contracts",
            min_value=1,
            max_value=10,
            value=1,
            help="Each contract = 100 shares"
        )
        
        total_credit = (call_credit + put_credit) * 100 * contracts
        max_loss = max(
            (call_long - call_short) * 100 * contracts - total_credit,
            (put_short - put_long) * 100 * contracts - total_credit
        )
        
        st.markdown(f"""
        **Position Size:**
        - Total Credit: ${total_credit:.2f}
        - Max Profit: ${total_credit:.2f}
        - Max Loss: ${abs(max_loss):.2f}
        - Margin Required: ${abs(max_loss):.2f}
        """)
    
    with col3:
        notes = st.text_area(
            "Notes (optional)",
            placeholder="e.g., Entry Score 8/9, Low IV",
            height=100
        )
        
        if st.button("🚀 Open Position", type="primary", use_container_width=True):
            # Check if enough cash
            if abs(max_loss) > portfolio.cash:
                st.error(f"❌ Insufficient cash! Need ${abs(max_loss):.2f}, have ${portfolio.cash:.2f}")
            else:
                position = portfolio.open_iron_condor(
                    entry_date=datetime.now().strftime('%Y-%m-%d'),
                    expiration=selected_expiry,
                    spy_price=current_price,
                    call_short_strike=call_short,
                    call_long_strike=call_long,
                    put_short_strike=put_short,
                    put_long_strike=put_long,
                    call_spread_credit=call_credit,
                    put_spread_credit=put_credit,
                    contracts=contracts,
                    notes=notes
                )
                
                if position:
                    st.success(f"✅ Position #{position['id']} opened successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to open position")
