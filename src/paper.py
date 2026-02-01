# src/paper.py – minimal version to fix import error

import streamlit as st

def initialize_paper_trading():
    """Initialize paper trading session state if not present"""
    if 'paper_portfolio' not in st.session_state:
        st.session_state.paper_portfolio = {
            'cash': 10000.0,
            'positions': [],
            'total_pl': 0.0,
            'trade_count': 0
        }
    if 'paper_trading_enabled' not in st.session_state:
        st.session_state.paper_trading_enabled = False
