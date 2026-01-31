"""
Paper Trading Module for SPY Iron Condor Bot
Simulates Iron Condor trades with P&L tracking
"""

import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

class PaperTradingPortfolio:
    """Manages paper trading portfolio and positions"""
    
    def __init__(self, initial_cash: float = 10000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = []
        self.closed_positions = []
        self.trade_history = []
        
    def open_iron_condor(self, 
                         entry_date: str,
                         expiration: str,
                         spy_price: float,
                         call_short_strike: float,
                         call_long_strike: float,
                         put_short_strike: float,
                         put_long_strike: float,
                         call_spread_credit: float,
                         put_spread_credit: float,
                         contracts: int = 1,
                         notes: str = "") -> Dict:
        """
        Open a new Iron Condor position
        
        Returns: position dict or None if insufficient funds
        """
        # Calculate requirements
        max_loss_per_contract = max(
            (call_long_strike - call_short_strike) * 100 - (call_spread_credit + put_spread_credit) * 100,
            (put_short_strike - put_long_strike) * 100 - (call_spread_credit + put_spread_credit) * 100
        )
        total_credit = (call_spread_credit + put_spread_credit) * 100 * contracts
        margin_required = abs(max_loss_per_contract) * contracts
        
        # Check if we have enough cash for margin
        if margin_required > self.cash:
            return None
        
        # Create position
        position = {
            'id': len(self.positions) + len(self.closed_positions) + 1,
            'status': 'OPEN',
            'entry_date': entry_date,
            'expiration': expiration,
            'spy_price_entry': spy_price,
            'contracts': contracts,
            'call_short': call_short_strike,
            'call_long': call_long_strike,
            'put_short': put_short_strike,
            'put_long': put_long_strike,
            'call_spread_credit': call_spread_credit,
            'put_spread_credit': put_spread_credit,
            'total_credit': total_credit,
            'margin_required': margin_required,
            'max_loss': abs(max_loss_per_contract) * contracts,
            'max_profit': total_credit,
            'notes': notes,
            'current_pnl': total_credit,  # Start with credit received
            'exit_date': None,
            'exit_spy_price': None,
            'exit_pnl': None
        }
        
        # Update cash and positions
        self.cash -= margin_required
        self.positions.append(position)
        
        # Log trade
        self.trade_history.append({
            'date': entry_date,
            'action': 'OPEN',
            'position_id': position['id'],
            'contracts': contracts,
            'credit': total_credit,
            'cash_change': -margin_required
        })
        
        return position
    
    def update_position_pnl(self, position_id: int, current_spy_price: float, 
                           current_call_spread_value: float, 
                           current_put_spread_value: float):
        """Update P&L for an open position"""
        for pos in self.positions:
            if pos['id'] == position_id:
                # Calculate current value of spreads
                current_spread_cost = (current_call_spread_value + current_put_spread_value) * 100 * pos['contracts']
                
                # P&L = Credit received - Current cost to close
                pos['current_pnl'] = pos['total_credit'] - current_spread_cost
                pos['current_spy_price'] = current_spy_price
                break
    
    def close_position(self, position_id: int, exit_date: str, 
                       exit_spy_price: float, 
                       closing_cost: float) -> Optional[Dict]:
        """
        Close an Iron Condor position
        
        Args:
            closing_cost: Total cost to buy back both spreads (in dollars)
        """
        for i, pos in enumerate(self.positions):
            if pos['id'] == position_id:
                # Calculate final P&L
                pnl = pos['total_credit'] - closing_cost
                
                # Update position
                pos['status'] = 'CLOSED'
                pos['exit_date'] = exit_date
                pos['exit_spy_price'] = exit_spy_price
                pos['exit_pnl'] = pnl
                
                # Return margin and add P&L to cash
                self.cash += pos['margin_required'] + pnl
                
                # Move to closed positions
                self.closed_positions.append(pos)
                self.positions.pop(i)
                
                # Log trade
                self.trade_history.append({
                    'date': exit_date,
                    'action': 'CLOSE',
                    'position_id': position_id,
                    'pnl': pnl,
                    'cash_change': pos['margin_required'] + pnl
                })
                
                return pos
        
        return None
    
    def get_total_pnl(self) -> float:
        """Calculate total unrealized + realized P&L"""
        unrealized = sum(pos['current_pnl'] for pos in self.positions)
        realized = sum(pos['exit_pnl'] for pos in self.closed_positions)
        return unrealized + realized
    
    def get_account_value(self) -> float:
        """Calculate total account value (cash + unrealized P&L)"""
        return self.cash + sum(pos['current_pnl'] for pos in self.positions)
    
    def get_stats(self) -> Dict:
        """Get portfolio statistics"""
        total_trades = len(self.closed_positions)
        winning_trades = sum(1 for pos in self.closed_positions if pos['exit_pnl'] > 0)
        losing_trades = sum(1 for pos in self.closed_positions if pos['exit_pnl'] < 0)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = (sum(pos['exit_pnl'] for pos in self.closed_positions if pos['exit_pnl'] > 0) / winning_trades) if winning_trades > 0 else 0
        avg_loss = (sum(pos['exit_pnl'] for pos in self.closed_positions if pos['exit_pnl'] < 0) / losing_trades) if losing_trades > 0 else 0
        
        total_realized = sum(pos['exit_pnl'] for pos in self.closed_positions)
        total_unrealized = sum(pos['current_pnl'] for pos in self.positions)
        
        return {
            'account_value': self.get_account_value(),
            'cash': self.cash,
            'total_pnl': total_realized + total_unrealized,
            'realized_pnl': total_realized,
            'unrealized_pnl': total_unrealized,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'open_positions': len(self.positions),
            'roi': ((self.get_account_value() - self.initial_cash) / self.initial_cash * 100)
        }
    
    def to_dict(self) -> Dict:
        """Serialize portfolio to dict for saving"""
        return {
            'initial_cash': self.initial_cash,
            'cash': self.cash,
            'positions': self.positions,
            'closed_positions': self.closed_positions,
            'trade_history': self.trade_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PaperTradingPortfolio':
        """Load portfolio from dict"""
        portfolio = cls(data['initial_cash'])
        portfolio.cash = data['cash']
        portfolio.positions = data['positions']
        portfolio.closed_positions = data['closed_positions']
        portfolio.trade_history = data['trade_history']
        return portfolio
