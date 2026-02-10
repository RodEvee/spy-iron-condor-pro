# src/paper.py – Paper Trading Portfolio System
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any


class PaperTradingPortfolio:
    """Simulated portfolio for paper trading Iron Condors"""

    def __init__(self, initial_cash: float = 10000.0):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: List[Dict[str, Any]] = []
        self.closed_positions: List[Dict[str, Any]] = []
        self.trade_count = 0
        self.total_pnl = 0.0

    def open_position(self, setup: Dict, quantity: int = 1) -> Tuple[bool, str]:
        """Open a new Iron Condor paper trade"""
        credit = setup['max_profit'] * quantity
        max_loss = setup['max_loss'] * quantity
        margin_required = max_loss  # Simplified margin

        if margin_required > self.cash:
            return False, f"Insufficient margin. Need ${margin_required:,.2f}, have ${self.cash:,.2f}"

        self.trade_count += 1
        position = {
            'id': self.trade_count,
            'setup': setup,
            'quantity': quantity,
            'entry_credit': credit,
            'max_loss': max_loss,
            'margin_held': margin_required,
            'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'expiration': setup.get('short_call', {}).get('expiration_date', 'N/A'),
            'status': 'open',
            'current_pnl': 0.0
        }

        self.cash -= margin_required
        self.positions.append(position)
        return True, f"Opened IC #{self.trade_count} for ${credit:,.2f} credit"

    def close_position(self, position_id: int, pnl_pct: float = 0.5) -> Tuple[bool, str]:
        """Close a position at a given P&L percentage of max profit"""
        pos = next((p for p in self.positions if p['id'] == position_id), None)
        if not pos:
            return False, f"Position #{position_id} not found"

        realized_pnl = pos['entry_credit'] * pnl_pct
        self.cash += pos['margin_held'] + realized_pnl
        self.total_pnl += realized_pnl

        pos['status'] = 'closed'
        pos['close_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        pos['realized_pnl'] = realized_pnl

        self.positions.remove(pos)
        self.closed_positions.append(pos)
        return True, f"Closed IC #{position_id} for ${realized_pnl:+,.2f}"

    def get_stats(self) -> Dict[str, Any]:
        """Get portfolio statistics"""
        margin_in_use = sum(p['margin_held'] for p in self.positions)
        account_value = self.cash + margin_in_use
        return {
            'cash': self.cash,
            'margin_in_use': margin_in_use,
            'account_value': account_value,
            'total_pnl': account_value - self.initial_cash,
            'open_positions': len(self.positions),
            'closed_trades': len(self.closed_positions),
            'total_trades': self.trade_count
        }


def initialize_paper_trading():
    """Initialize paper trading session state if not present"""
    if 'paper_portfolio' not in st.session_state:
        st.session_state.paper_portfolio = PaperTradingPortfolio(initial_cash=10000.0)
    if 'paper_trading_enabled' not in st.session_state:
        st.session_state.paper_trading_enabled = False
