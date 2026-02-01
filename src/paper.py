# src/paper.py
import streamlit as st
from datetime import datetime
import pandas as pd

class PaperTradingPortfolio:
    def __init__(self, initial_cash=10000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = []           # list of dicts
        self.closed_trades = []       # history
        self.trade_count = 0

    def open_position(self, setup, quantity=1):
        """Open a new Iron Condor paper trade"""
        if not setup:
            return False, "No valid setup provided"

        credit = setup['max_profit'] * quantity
        margin = setup['max_loss'] * quantity

        if self.cash < margin:
            return False, f"Insufficient cash (need ${margin:,.2f}, have ${self.cash:,.2f})"

        position = {
            'id': self.trade_count + 1,
            'entry_date': datetime.now(),
            'expiration': setup['expiration'],
            'quantity': quantity,
            'setup': setup,
            'entry_credit': credit,
            'max_loss': margin,
            'status': 'open'
        }

        self.positions.append(position)
        self.cash -= margin
        self.trade_count += 1
        return True, f"Opened trade #{position['id']} – Credit ${credit:,.2f}"

    def close_position(self, position_id, current_value):
        """Close position and realize P&L"""
        for i, pos in enumerate(self.positions):
            if pos['id'] == position_id:
                pnl = current_value + pos['entry_credit'] * pos['quantity']
                closed = pos.copy()
                closed.update({
                    'close_date': datetime.now(),
                    'final_pnl': pnl,
                    'status': 'closed'
                })
                self.closed_trades.append(closed)
                self.cash += pos['max_loss'] + pnl  # return margin + pnl
                del self.positions[i]
                return True, f"Closed trade #{pos['id']} – P&L ${pnl:,.2f}"
        return False, "Position not found"

    def get_stats(self):
        total_value = self.cash
        unrealized = 0
        for pos in self.positions:
            # Placeholder current value calculation – improve with real pricing later
            current_val = pos['entry_credit'] * pos['quantity'] * 0.5  # demo
            unrealized += current_val
            total_value += pos['max_loss'] + current_val

        return {
            'account_value': total_value,
            'cash': self.cash,
            'total_pnl': total_value - self.initial_cash,
            'open_positions': len(self.positions),
            'unrealized_pnl': unrealized
        }
