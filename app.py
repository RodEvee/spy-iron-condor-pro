"""
SPY Iron Condor Trading Bot - Professional Edition
With Full Greeks, Multiple Expirations, and Enhanced UI
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Tuple
from professional_chart import display_professional_chart

import time
import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from paper_trading import PaperTradingPortfolio
    from paper_trading_ui import (
        initialize_paper_trading,
        display_paper_trading_dashboard,
        display_open_position_form
    )
    PAPER_TRADING_AVAILABLE = True
except ImportError:
    PAPER_TRADING_AVAILABLE = False
    st.warning("⚠️ Paper trading module not found. Some features may be unavailable.")

# Page configuration
st.set_page_config(
    page_title="SPY Iron Condor Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 18px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .greek-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .signal-strong-entry {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .signal-exit {
        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .signal-neutral {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .expiry-badge {
        background: #e3f2fd;
        color: #1976d2;
        padding: 5px 12px;
        border-radius: 15px;
        font-weight: 600;
        display: inline-block;
        margin: 5px;
    }
    .optimal-badge {
        background: #4caf50;
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        font-weight: 600;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
    }
    .strike-row {
        padding: 10px;
        border-bottom: 1px solid #e0e0e0;
        transition: background 0.3s;
    }
    .strike-row:hover {
        background: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA FETCHING ====================

@st.cache_data(ttl=300)
def get_spy_data(period="5d", interval="1d"):
    """Fetch SPY price data from Yahoo Finance"""
    try:
        spy = yf.Ticker("SPY")
        df = spy.history(period=period, interval=interval)
        
        if df.empty:
            st.warning("⚠️ Could not fetch SPY data. Using demo data.")
            return generate_demo_price_data()
        
        return df
    except Exception as e:
        st.warning(f"⚠️ Data fetch error: {e}. Using demo data.")
        return generate_demo_price_data()

def generate_demo_price_data():
    """Generate demo price data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1H')
    df = pd.DataFrame({
        'Close': 580 + np.random.randn(100).cumsum() * 2,
        'High': 582 + np.random.randn(100).cumsum() * 2,
        'Low': 578 + np.random.randn(100).cumsum() * 2,
        'Volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)
    return df

def get_yahoo_options_chain(symbol="SPY"):
    """
    Fetch REAL options chain from Yahoo Finance
    Returns dict with expirations and full options data including Greeks
    FREE and NO API KEY NEEDED!
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get all available expiration dates
        expirations = ticker.options
        
        if not expirations:
            st.warning("⚠️ Could not fetch options from Yahoo Finance. Using demo data.")
            return generate_demo_options_data()
        
        # Get current stock price for Greek calculations
        current_price = ticker.history(period='1d')['Close'].iloc[-1]
        
        options_data = {}
        
        # Limit to first 15 expirations
        for exp_date in expirations[:15]:
            try:
                # Get option chain for this expiration
                opt_chain = ticker.option_chain(exp_date)
                calls = opt_chain.calls
                puts = opt_chain.puts
                
                options = []
                
                # Calculate days to expiration
                exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                days_to_exp = (exp_datetime - datetime.now()).days
                
                # Process calls
                for _, row in calls.iterrows():
                    strike = row['strike']
                    
                    # Calculate Greeks (simplified Black-Scholes approximation)
                    # For calls
                    moneyness = (strike - current_price) / current_price
                    iv = row.get('impliedVolatility', 0.20)  # Default to 20% if missing
                    
                    delta = calculate_delta(current_price, strike, days_to_exp, iv, 'call')
                    gamma = calculate_gamma(current_price, strike, days_to_exp, iv)
                    theta = calculate_theta(current_price, strike, days_to_exp, iv, 'call')
                    vega = calculate_vega(current_price, strike, days_to_exp, iv)
                    rho = calculate_rho(current_price, strike, days_to_exp, iv, 'call')
                    
                    options.append({
                        'symbol': row.get('contractSymbol', ''),
                        'strike': strike,
                        'type': 'call',
                        'expiration_date': exp_date,
                        'bid': row.get('bid', 0),
                        'ask': row.get('ask', 0),
                        'last': row.get('lastPrice', 0),
                        'volume': int(row.get('volume', 0)) if pd.notna(row.get('volume')) else 0,
                        'open_interest': int(row.get('openInterest', 0)) if pd.notna(row.get('openInterest')) else 0,
                        'greeks': {
                            'delta': round(delta, 4),
                            'gamma': round(gamma, 4),
                            'theta': round(theta, 4),
                            'vega': round(vega, 4),
                            'rho': round(rho, 4)
                        },
                        'iv': round(iv, 4)
                    })
                
                # Process puts
                for _, row in puts.iterrows():
                    strike = row['strike']
                    
                    moneyness = (strike - current_price) / current_price
                    iv = row.get('impliedVolatility', 0.20)
                    
                    delta = calculate_delta(current_price, strike, days_to_exp, iv, 'put')
                    gamma = calculate_gamma(current_price, strike, days_to_exp, iv)
                    theta = calculate_theta(current_price, strike, days_to_exp, iv, 'put')
                    vega = calculate_vega(current_price, strike, days_to_exp, iv)
                    rho = calculate_rho(current_price, strike, days_to_exp, iv, 'put')
                    
                    options.append({
                        'symbol': row.get('contractSymbol', ''),
                        'strike': strike,
                        'type': 'put',
                        'expiration_date': exp_date,
                        'bid': row.get('bid', 0),
                        'ask': row.get('ask', 0),
                        'last': row.get('lastPrice', 0),
                        'volume': int(row.get('volume', 0)) if pd.notna(row.get('volume')) else 0,
                        'open_interest': int(row.get('openInterest', 0)) if pd.notna(row.get('openInterest')) else 0,
                        'greeks': {
                            'delta': round(delta, 4),
                            'gamma': round(gamma, 4),
                            'theta': round(theta, 4),
                            'vega': round(vega, 4),
                            'rho': round(rho, 4)
                        },
                        'iv': round(iv, 4)
                    })
                
                options_data[exp_date] = options
                
            except Exception as e:
                continue
        
        if options_data:
            return options_data
        else:
            st.warning("⚠️ No options data available. Using demo data.")
            return generate_demo_options_data()
            
    except Exception as e:
        st.warning(f"⚠️ Yahoo Finance error: {str(e)[:100]}. Using demo data.")
        return generate_demo_options_data()

# Greek calculation helper functions (Black-Scholes approximation)
from math import sqrt, exp, log, pi
from scipy.stats import norm

def calculate_delta(S, K, T, sigma, option_type='call'):
    """Calculate option delta"""
    if T <= 0:
        return 1.0 if option_type == 'call' and S > K else 0.0
    
    try:
        r = 0.05  # Risk-free rate assumption
        d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * (T / 365)) / (sigma * sqrt(T / 365))
        
        if option_type == 'call':
            return norm.cdf(d1)
        else:
            return -norm.cdf(-d1)
    except:
        return 0.5 if option_type == 'call' else -0.5

def calculate_gamma(S, K, T, sigma):
    """Calculate option gamma"""
    if T <= 0:
        return 0.0
    
    try:
        r = 0.05
        d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * (T / 365)) / (sigma * sqrt(T / 365))
        return norm.pdf(d1) / (S * sigma * sqrt(T / 365))
    except:
        return 0.01

def calculate_theta(S, K, T, sigma, option_type='call'):
    """Calculate option theta (per day)"""
    if T <= 0:
        return 0.0
    
    try:
        r = 0.05
        d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * (T / 365)) / (sigma * sqrt(T / 365))
        d2 = d1 - sigma * sqrt(T / 365)
        
        if option_type == 'call':
            theta = (-S * norm.pdf(d1) * sigma / (2 * sqrt(T / 365)) - r * K * exp(-r * T / 365) * norm.cdf(d2)) / 365
        else:
            theta = (-S * norm.pdf(d1) * sigma / (2 * sqrt(T / 365)) + r * K * exp(-r * T / 365) * norm.cdf(-d2)) / 365
        
        return theta
    except:
        return -0.05

def calculate_vega(S, K, T, sigma):
    """Calculate option vega"""
    if T <= 0:
        return 0.0
    
    try:
        r = 0.05
        d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * (T / 365)) / (sigma * sqrt(T / 365))
        return S * norm.pdf(d1) * sqrt(T / 365) / 100
    except:
        return 0.15

def calculate_rho(S, K, T, sigma, option_type='call'):
    """Calculate option rho"""
    if T <= 0:
        return 0.0
    
    try:
        r = 0.05
        d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * (T / 365)) / (sigma * sqrt(T / 365))
        d2 = d1 - sigma * sqrt(T / 365)
        
        if option_type == 'call':
            return K * (T / 365) * exp(-r * T / 365) * norm.cdf(d2) / 100
        else:
            return -K * (T / 365) * exp(-r * T / 365) * norm.cdf(-d2) / 100
    except:
        return 0.01

def get_alpaca_options_chain(symbol="SPY", api_key=None, api_secret=None):
    """
    Fetch options chain from Alpaca API
    Returns dict with expirations and full options data including Greeks
    """
    if not api_key or not api_secret:
        return generate_demo_options_data()
    
    try:
        # Try paper trading endpoint first
        base_url = "https://paper-api.alpaca.markets/v2"
        data_url = "https://data.alpaca.markets/v1beta1"
        
        headers = {
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': api_secret,
            'accept': 'application/json'
        }
        
        # First, verify API keys work by getting account info
        account_response = requests.get(
            f"{base_url}/account",
            headers=headers,
            timeout=10
        )
        
        if account_response.status_code == 401:
            st.warning("⚠️ Alpaca authentication failed. Keys may be incorrect or expired. Using demo data.")
            return generate_demo_options_data()
        
        # Get options snapshots
        # Note: Alpaca options data is limited and may not be available for all accounts
        # We'll use a fallback to demo data with a note
        
        try:
            # Try to get options contracts
            options_response = requests.get(
                f"{data_url}/options/contracts",
                headers=headers,
                params={
                    'underlying_symbols': symbol,
                    'status': 'active',
                    'expiration_date_gte': datetime.now().strftime('%Y-%m-%d'),
                    'limit': 1000
                },
                timeout=15
            )
            
            if options_response.status_code == 200:
                contracts_data = options_response.json()
                contracts = contracts_data.get('option_contracts', [])
                
                if not contracts:
                    st.info("💡 Alpaca connected but options data not available. Using enhanced demo data with real SPY price.")
                    return generate_demo_options_data()
                
                # Parse contracts into our format
                options_data = {}
                
                for contract in contracts:
                    exp_date = contract.get('expiration_date')
                    strike = float(contract.get('strike_price', 0)) / 100  # Alpaca uses cents
                    option_type = contract.get('type', '').lower()
                    
                    if exp_date not in options_data:
                        options_data[exp_date] = []
                    
                    # Get quote for this contract
                    symbol_str = contract.get('symbol')
                    
                    # Create option entry with estimated Greeks
                    option = {
                        'symbol': symbol_str,
                        'strike': strike,
                        'type': option_type,
                        'expiration_date': exp_date,
                        'bid': 0,  # Will be filled by snapshot
                        'ask': 0,
                        'last': 0,
                        'volume': 0,
                        'open_interest': 0,
                        'greeks': {
                            'delta': 0,
                            'gamma': 0,
                            'theta': 0,
                            'vega': 0,
                            'rho': 0
                        },
                        'iv': 0
                    }
                    
                    options_data[exp_date].append(option)
                
                # Limit to 15 expirations
                sorted_exps = sorted(options_data.keys())[:15]
                filtered_data = {exp: options_data[exp] for exp in sorted_exps}
                
                if filtered_data:
                    st.success("✅ Alpaca connected! Options data loaded.")
                    return filtered_data
                else:
                    st.info("💡 Alpaca connected. Using enhanced demo data.")
                    return generate_demo_options_data()
                    
            else:
                # Options data API not available - use demo
                st.info("💡 Alpaca account verified! Options API access limited. Using enhanced demo data with real market structure.")
                return generate_demo_options_data()
                
        except Exception as inner_e:
            st.info(f"💡 Alpaca connected successfully! Options data endpoint unavailable. Using enhanced demo data.")
            return generate_demo_options_data()
            
    except requests.exceptions.Timeout:
        st.warning("⚠️ Alpaca API timeout. Using demo data.")
        return generate_demo_options_data()
    except Exception as e:
        st.warning(f"⚠️ Alpaca API error: {str(e)[:100]}. Using demo data.")
        return generate_demo_options_data()

def get_tdameritrade_options_chain(symbol="SPY", api_key=None):
    """
    Fetch options chain from TD Ameritrade API
    Returns dict with expirations and full options data including Greeks
    """
    if not api_key:
        return generate_demo_options_data()
    
    try:
        base_url = "https://api.tdameritrade.com/v1/marketdata"
        
        # Get option chain
        params = {
            'apikey': api_key,
            'symbol': symbol,
            'includeQuotes': 'TRUE',
            'strategy': 'ANALYTICAL',
            'range': 'ALL'
        }
        
        response = requests.get(
            f"{base_url}/chains",
            params=params,
            timeout=15
        )
        
        if response.status_code != 200:
            st.warning(f"TD Ameritrade API error: {response.status_code}. Using demo data.")
            return generate_demo_options_data()
        
        data = response.json()
        
        # Parse TD Ameritrade format to our format
        options_data = {}
        
        # Process call options
        call_exp_map = data.get('callExpDateMap', {})
        put_exp_map = data.get('putExpDateMap', {})
        
        # Get all unique expiration dates
        all_expirations = set()
        for exp_date_str in call_exp_map.keys():
            exp_date = exp_date_str.split(':')[0]  # Format: "2024-02-16:45"
            all_expirations.add(exp_date)
        
        all_expirations = sorted(list(all_expirations))[:15]  # Limit to 15
        
        for exp_date in all_expirations:
            options = []
            
            # Find matching strikes for this expiration
            for exp_key in call_exp_map.keys():
                if exp_date in exp_key:
                    strike_map = call_exp_map[exp_key]
                    
                    for strike_str, option_list in strike_map.items():
                        strike = float(strike_str)
                        
                        for opt in option_list:
                            # Call option
                            options.append({
                                'symbol': opt.get('symbol', ''),
                                'strike': strike,
                                'type': 'call',
                                'expiration_date': exp_date,
                                'bid': opt.get('bid', 0),
                                'ask': opt.get('ask', 0),
                                'last': opt.get('last', 0),
                                'volume': opt.get('totalVolume', 0),
                                'open_interest': opt.get('openInterest', 0),
                                'greeks': {
                                    'delta': opt.get('delta', 0),
                                    'gamma': opt.get('gamma', 0),
                                    'theta': opt.get('theta', 0),
                                    'vega': opt.get('vega', 0),
                                    'rho': opt.get('rho', 0)
                                },
                                'iv': opt.get('volatility', 0) / 100 if opt.get('volatility') else 0
                            })
            
            # Add put options
            for exp_key in put_exp_map.keys():
                if exp_date in exp_key:
                    strike_map = put_exp_map[exp_key]
                    
                    for strike_str, option_list in strike_map.items():
                        strike = float(strike_str)
                        
                        for opt in option_list:
                            # Put option
                            options.append({
                                'symbol': opt.get('symbol', ''),
                                'strike': strike,
                                'type': 'put',
                                'expiration_date': exp_date,
                                'bid': opt.get('bid', 0),
                                'ask': opt.get('ask', 0),
                                'last': opt.get('last', 0),
                                'volume': opt.get('totalVolume', 0),
                                'open_interest': opt.get('openInterest', 0),
                                'greeks': {
                                    'delta': opt.get('delta', 0),
                                    'gamma': opt.get('gamma', 0),
                                    'theta': opt.get('theta', 0),
                                    'vega': opt.get('vega', 0),
                                    'rho': opt.get('rho', 0)
                                },
                                'iv': opt.get('volatility', 0) / 100 if opt.get('volatility') else 0
                            })
            
            if options:
                options_data[exp_date] = options
        
        return options_data if options_data else generate_demo_options_data()
        
    except Exception as e:
        st.warning(f"⚠️ TD Ameritrade API error: {e}. Using demo data.")
        return generate_demo_options_data()

def get_tradier_options_chain(symbol="SPY", api_key=None):
    """
    Fetch options chain from Tradier API (sandbox or production)
    Returns dict with expirations and full options data including Greeks
    """
    if not api_key:
        # Demo mode - generate realistic fake data
        return generate_demo_options_data()
    
    try:
        # Tradier API endpoints
        base_url = "https://sandbox.tradier.com/v1/markets"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        
        # Get expirations
        exp_response = requests.get(
            f"{base_url}/options/expirations",
            params={'symbol': symbol},
            headers=headers,
            timeout=10
        )
        
        if exp_response.status_code != 200:
            return generate_demo_options_data()
        
        expirations = exp_response.json().get('expirations', {}).get('date', [])[:15]
        
        # Get options chains for each expiration
        options_data = {}
        for exp_date in expirations:
            chain_response = requests.get(
                f"{base_url}/options/chains",
                params={'symbol': symbol, 'expiration': exp_date, 'greeks': 'true'},
                headers=headers,
                timeout=10
            )
            
            if chain_response.status_code == 200:
                chain = chain_response.json().get('options', {}).get('option', [])
                options_data[exp_date] = chain
        
        return options_data
        
    except Exception as e:
        st.warning(f"⚠️ Tradier API error: {e}. Using demo data.")
        return generate_demo_options_data()

def generate_demo_options_data():
    """Generate realistic demo options data with Greeks"""
    current_price = 580  # SPY demo price
    expirations = []
    base_date = datetime.now()
    
    # Generate 15 expiration dates
    for i in range(8):
        exp = base_date + timedelta(days=7*(i+1))
        expirations.append(exp.strftime('%Y-%m-%d'))
    for i in range(7):
        exp = base_date + timedelta(days=60 + 30*i)
        expirations.append(exp.strftime('%Y-%m-%d'))
    
    options_data = {}
    
    for exp_date in expirations:
        days_to_exp = (datetime.strptime(exp_date, '%Y-%m-%d') - base_date).days
        options = []
        
        # Generate strikes
        strikes = np.arange(
            int(current_price * 0.85), 
            int(current_price * 1.15), 
            5
        )
        
        for strike in strikes:
            moneyness = (strike - current_price) / current_price
            
            # Call options
            call_delta = max(0.01, min(0.99, 0.5 + moneyness * 2))
            call_gamma = 0.015 * np.exp(-abs(moneyness) * 10) / np.sqrt(max(days_to_exp, 1))
            call_theta = -0.05 * np.sqrt(max(days_to_exp, 1))
            call_vega = 0.15 * np.sqrt(max(days_to_exp, 1))
            
            put_delta = -(1 - call_delta)
            put_gamma = call_gamma
            put_theta = call_theta
            put_vega = call_vega
            
            iv = 0.15 + abs(moneyness) * 0.3
            call_price = max(0.05, (current_price - strike) * call_delta + iv * 10)
            put_price = max(0.05, (strike - current_price) * abs(put_delta) + iv * 10)
            
            # Call option
            options.append({
                'symbol': f'SPY{exp_date.replace("-", "")}C{int(strike*1000)}',
                'strike': strike,
                'type': 'call',
                'expiration_date': exp_date,
                'bid': round(call_price * 0.98, 2),
                'ask': round(call_price * 1.02, 2),
                'last': round(call_price, 2),
                'volume': int(np.random.exponential(1000)),
                'open_interest': int(np.random.exponential(5000)),
                'greeks': {
                    'delta': round(call_delta, 4),
                    'gamma': round(call_gamma, 4),
                    'theta': round(call_theta, 4),
                    'vega': round(call_vega, 4),
                    'rho': round(0.01 * days_to_exp / 365, 4)
                },
                'iv': round(iv, 4)
            })
            
            # Put option
            options.append({
                'symbol': f'SPY{exp_date.replace("-", "")}P{int(strike*1000)}',
                'strike': strike,
                'type': 'put',
                'expiration_date': exp_date,
                'bid': round(put_price * 0.98, 2),
                'ask': round(put_price * 1.02, 2),
                'last': round(put_price, 2),
                'volume': int(np.random.exponential(1000)),
                'open_interest': int(np.random.exponential(5000)),
                'greeks': {
                    'delta': round(put_delta, 4),
                    'gamma': round(put_gamma, 4),
                    'theta': round(put_theta, 4),
                    'vega': round(put_vega, 4),
                    'rho': round(-0.01 * days_to_exp / 365, 4)
                },
                'iv': round(iv, 4)
            })
        
        options_data[exp_date] = options
    
    return options_data

# ==================== PAPER TRADING SYSTEM ====================

def init_paper_trading():
    """Initialize paper trading portfolio in session state"""
    if 'paper_portfolio' not in st.session_state:
        st.session_state.paper_portfolio = {
            'cash': 10000.00,  # Starting cash
            'positions': [],    # Open positions
            'closed_trades': [], # Closed trades history
            'total_pl': 0.00,   # Total profit/loss
            'trade_count': 0    # Number of trades
        }

def calculate_position_value(position, current_data):
    """Calculate current value and P&L of a position"""
    try:
        # Get current prices for all legs
        total_current_value = 0
        
        for leg in ['short_call', 'long_call', 'short_put', 'long_put']:
            strike = position[leg]['strike']
            option_type = 'call' if 'call' in leg else 'put'
            
            # Find current option in data
            current_option = None
            exp_date = position['expiration']
            
            if exp_date in current_data:
                for opt in current_data[exp_date]:
                    if opt['strike'] == strike and opt['type'] == option_type:
                        current_option = opt
                        break
            
            if current_option:
                current_price = (current_option['bid'] + current_option['ask']) / 2
            else:
                current_price = 0
            
            # Calculate value (short = negative, long = positive)
            if 'short' in leg:
                total_current_value -= current_price * 100 * position['quantity']
            else:
                total_current_value += current_price * 100 * position['quantity']
        
        pl = position['entry_credit'] + total_current_value
        
        return total_current_value, pl
        
    except Exception as e:
        return 0, 0

def open_paper_trade(ic_setup, expiration, quantity=1):
    """Open a new paper trading position"""
    if 'paper_portfolio' not in st.session_state:
        init_paper_trading()
    
    # Calculate entry credit
    entry_credit = ic_setup['max_profit'] * quantity
    max_loss = ic_setup['max_loss'] * quantity
    
    # Check if enough cash
    required_margin = max_loss
    if st.session_state.paper_portfolio['cash'] < required_margin:
        st.error(f"❌ Insufficient cash! Need ${required_margin:.2f}, have ${st.session_state.paper_portfolio['cash']:.2f}")
        return False
    
    # Create position
    position = {
        'id': st.session_state.paper_portfolio['trade_count'] + 1,
        'entry_date': datetime.now(),
        'expiration': expiration,
        'quantity': quantity,
        'short_call': {
            'strike': ic_setup['short_call']['strike'],
            'entry_price': ic_setup['short_call']['last']
        },
        'long_call': {
            'strike': ic_setup['long_call']['strike'],
            'entry_price': ic_setup['long_call']['last']
        },
        'short_put': {
            'strike': ic_setup['short_put']['strike'],
            'entry_price': ic_setup['short_put']['last']
        },
        'long_put': {
            'strike': ic_setup['long_put']['strike'],
            'entry_price': ic_setup['long_put']['last']
        },
        'entry_credit': entry_credit,
        'max_loss': max_loss,
        'max_profit': entry_credit,
        'target_delta': ic_setup.get('target_delta', 0.20)
    }
    
    # Add to portfolio
    st.session_state.paper_portfolio['positions'].append(position)
    st.session_state.paper_portfolio['cash'] -= required_margin
    st.session_state.paper_portfolio['trade_count'] += 1
    
    st.success(f"✅ Paper trade opened! Trade #{position['id']} | Credit: ${entry_credit:.2f} | Max Loss: ${max_loss:.2f}")
    return True

def close_paper_trade(position_id, current_data, reason="Manual close"):
    """Close a paper trading position"""
    if 'paper_portfolio' not in st.session_state:
        return False
    
    # Find position
    position = None
    for i, pos in enumerate(st.session_state.paper_portfolio['positions']):
        if pos['id'] == position_id:
            position = pos
            position_index = i
            break
    
    if not position:
        return False
    
    # Calculate final P&L
    _, final_pl = calculate_position_value(position, current_data)
    
    # Close position
    closed_trade = position.copy()
    closed_trade['close_date'] = datetime.now()
    closed_trade['close_reason'] = reason
    closed_trade['final_pl'] = final_pl
    closed_trade['days_held'] = (datetime.now() - position['entry_date']).days
    
    # Update portfolio
    st.session_state.paper_portfolio['closed_trades'].append(closed_trade)
    st.session_state.paper_portfolio['positions'].pop(position_index)
    st.session_state.paper_portfolio['cash'] += position['max_loss'] + final_pl
    st.session_state.paper_portfolio['total_pl'] += final_pl
    
    return True

def display_paper_trading_panel(options_data, current_price, ic_setups, selected_expiry):
    """Display paper trading interface"""
    init_paper_trading()
    
    st.markdown("### 💼 Paper Trading Portfolio")
    
    portfolio = st.session_state.paper_portfolio
    
    # Portfolio summary
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate total position value
    total_position_value = 0
    total_unrealized_pl = 0
    
    for pos in portfolio['positions']:
        _, pl = calculate_position_value(pos, options_data)
        total_unrealized_pl += pl
    
    with col1:
        st.metric("Cash", f"${portfolio['cash']:.2f}")
    
    with col2:
        total_value = portfolio['cash'] + sum(p['max_loss'] for p in portfolio['positions']) + total_unrealized_pl
        st.metric("Total Value", f"${total_value:.2f}", f"{((total_value - 10000) / 10000 * 100):.2f}%")
    
    with col3:
        st.metric("Open Positions", len(portfolio['positions']))
    
    with col4:
        st.metric("Unrealized P&L", f"${total_unrealized_pl:.2f}", 
                 "Profit" if total_unrealized_pl > 0 else "Loss")
    
    with col5:
        st.metric("Total P&L", f"${portfolio['total_pl']:.2f}",
                 "Profit" if portfolio['total_pl'] > 0 else "Loss")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Open New Trade", "📊 Open Positions", "📜 Trade History"])
    
    with tab1:
        st.markdown("#### Open New Iron Condor")
        
        if not ic_setups or len(ic_setups) == 0:
            st.warning("⚠️ No Iron Condor setups available. Check signals first.")
        else:
            # Setup selection
            setup_options = ["16Δ Conservative", "20Δ Balanced (Optimal)", "30Δ Aggressive"]
            selected_setup = st.selectbox("Select Setup", setup_options, index=1)
            
            setup_idx = setup_options.index(selected_setup)
            ic_setup = ic_setups[setup_idx] if setup_idx < len(ic_setups) else None
            
            if ic_setup:
                # Quantity selector
                quantity = st.number_input("Quantity (contracts)", min_value=1, max_value=10, value=1)
                
                # Show setup details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Call Spread**")
                    st.write(f"Short: ${ic_setup['short_call']['strike']} @ ${ic_setup['short_call']['last']:.2f}")
                    st.write(f"Long: ${ic_setup['long_call']['strike']} @ ${ic_setup['long_call']['last']:.2f}")
                
                with col2:
                    st.markdown("**Put Spread**")
                    st.write(f"Short: ${ic_setup['short_put']['strike']} @ ${ic_setup['short_put']['last']:.2f}")
                    st.write(f"Long: ${ic_setup['long_put']['strike']} @ ${ic_setup['long_put']['last']:.2f}")
                
                st.markdown("---")
                
                # P&L summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Credit Received", f"${ic_setup['max_profit'] * quantity:.2f}")
                with col2:
                    st.metric("Max Loss", f"${ic_setup['max_loss'] * quantity:.2f}")
                with col3:
                    st.metric("Probability", f"{ic_setup['pop']}%")
                
                # Open trade button
                if st.button("🚀 Open Paper Trade", type="primary", use_container_width=True):
                    ic_setup['target_delta'] = [0.16, 0.20, 0.30][setup_idx]
                    open_paper_trade(ic_setup, selected_expiry, quantity)
                    st.rerun()
    
    with tab2:
        st.markdown("#### Open Positions")
        
        if len(portfolio['positions']) == 0:
            st.info("📭 No open positions. Open a trade in the 'Open New Trade' tab!")
        else:
            for pos in portfolio['positions']:
                with st.expander(f"Trade #{pos['id']} - {pos['expiration']} ({pos['quantity']} contracts)", expanded=True):
                    # Calculate current P&L
                    current_value, current_pl = calculate_position_value(pos, options_data)
                    
                    days_held = (datetime.now() - pos['entry_date']).days
                    days_to_exp = (datetime.strptime(pos['expiration'], '%Y-%m-%d') - datetime.now()).days
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Entry Credit", f"${pos['entry_credit']:.2f}")
                    with col2:
                        pl_pct = (current_pl / pos['entry_credit'] * 100) if pos['entry_credit'] > 0 else 0
                        st.metric("Current P&L", f"${current_pl:.2f}", f"{pl_pct:.1f}%")
                    with col3:
                        st.metric("Days Held", f"{days_held}")
                    with col4:
                        st.metric("DTE", f"{days_to_exp}")
                    
                    # Strikes
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Call Spread**")
                        st.write(f"Short: ${pos['short_call']['strike']}")
                        st.write(f"Long: ${pos['long_call']['strike']}")
                    with col2:
                        st.markdown("**Put Spread**")
                        st.write(f"Short: ${pos['short_put']['strike']}")
                        st.write(f"Long: ${pos['long_put']['strike']}")
                    
                    # Exit rules
                    st.markdown("**Exit Signals:**")
                    
                    exit_reasons = []
                    if pl_pct >= 50:
                        exit_reasons.append("✅ 50% profit target reached!")
                    if days_to_exp <= 21:
                        exit_reasons.append("⏰ 21 DTE - consider closing")
                    if pl_pct <= -100:
                        exit_reasons.append("🚨 Stop loss triggered!")
                    
                    if exit_reasons:
                        for reason in exit_reasons:
                            st.warning(reason)
                    else:
                        st.info("✓ No exit signals yet")
                    
                    # Close button
                    if st.button(f"Close Trade #{pos['id']}", key=f"close_{pos['id']}"):
                        if close_paper_trade(pos['id'], options_data, "Manual close"):
                            st.success(f"✅ Trade #{pos['id']} closed! P&L: ${current_pl:.2f}")
                            st.rerun()
    
    with tab3:
        st.markdown("#### Trade History")
        
        if len(portfolio['closed_trades']) == 0:
            st.info("📭 No closed trades yet. Start trading to build history!")
        else:
            # Summary stats
            total_trades = len(portfolio['closed_trades'])
            winning_trades = len([t for t in portfolio['closed_trades'] if t['final_pl'] > 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Trades", total_trades)
            with col2:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with col3:
                st.metric("Total P&L", f"${portfolio['total_pl']:.2f}")
            
            st.markdown("---")
            
            # Trade history table
            history_data = []
            for trade in reversed(portfolio['closed_trades']):
                history_data.append({
                    'Trade #': trade['id'],
                    'Entry': trade['entry_date'].strftime('%Y-%m-%d'),
                    'Exit': trade['close_date'].strftime('%Y-%m-%d'),
                    'Days': trade['days_held'],
                    'Credit': f"${trade['entry_credit']:.2f}",
                    'P&L': f"${trade['final_pl']:.2f}",
                    'Return': f"{(trade['final_pl'] / trade['entry_credit'] * 100):.1f}%",
                    'Reason': trade['close_reason']
                })
            
            if history_data:
                df_history = pd.DataFrame(history_data)
                st.dataframe(df_history, use_container_width=True, hide_index=True)

# ==================== ANALYSIS FUNCTIONS ====================

def calculate_indicators(df):
    """Calculate technical indicators for Iron Condor signals"""
    if df.empty or len(df) < 50:
        return df
    
    try:
        # Bollinger Bands
        df['SMA20'] = df['Close'].rolling(20, min_periods=1).mean()
        df['BB_std'] = df['Close'].rolling(20, min_periods=1).std()
        df['BB_upper'] = df['SMA20'] + (df['BB_std'] * 2)
        df['BB_lower'] = df['SMA20'] - (df['BB_std'] * 2)
        df['BB_width'] = ((df['BB_upper'] - df['BB_lower']) / df['SMA20']) * 100
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
        rs = gain / (loss + 0.0001)  # Avoid division by zero
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # ATR
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        
        df['TR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = df['TR'].rolling(14, min_periods=1).mean()
        df['ATR_pct'] = (df['ATR'] / df['Close']) * 100
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
        
    except Exception as e:
        st.warning(f"⚠️ Indicator calculation error: {e}")
    
    return df

def calculate_iron_condor_score(df, current_price):
    """Calculate Entry and Risk scores for Iron Condor strategy"""
    if df.empty or len(df) < 20:
        return 0, 9, "NEUTRAL"
    
    try:
        latest = df.iloc[-1]
        
        # Check if required columns exist
        required_cols = ['RSI', 'BB_lower', 'BB_upper', 'BB_width', 'ATR_pct', 'MACD']
        for col in required_cols:
            if col not in df.columns or pd.isna(latest.get(col, np.nan)):
                return 0, 9, "NEUTRAL"
        
        entry_score = 0
        risk_score = 0
        
        # 1. RSI in neutral zone (40-60)
        rsi = latest['RSI']
        if pd.notna(rsi):
            if 45 <= rsi <= 55:
                entry_score += 2
            elif 40 <= rsi <= 60:
                entry_score += 1
            elif rsi < 30 or rsi > 70:
                risk_score += 2
        
        # 2. Price in middle of Bollinger Bands
        if pd.notna(latest['BB_lower']) and pd.notna(latest['BB_upper']):
            bb_range = latest['BB_upper'] - latest['BB_lower']
            if bb_range > 0:
                bb_position = (current_price - latest['BB_lower']) / bb_range
                if 0.4 <= bb_position <= 0.6:
                    entry_score += 2
                elif 0.3 <= bb_position <= 0.7:
                    entry_score += 1
                elif bb_position < 0.2 or bb_position > 0.8:
                    risk_score += 2
        
        # 3. Low volatility
        if pd.notna(latest['BB_width']):
            if latest['BB_width'] < 5:
                entry_score += 2
            elif latest['BB_width'] < 7:
                entry_score += 1
            elif latest['BB_width'] > 10:
                risk_score += 2
        
        # 4. Low ATR
        if pd.notna(latest['ATR_pct']):
            if latest['ATR_pct'] < 0.8:
                entry_score += 2
            elif latest['ATR_pct'] < 1.2:
                entry_score += 1
            elif latest['ATR_pct'] > 2.0:
                risk_score += 2
        
        # 5. MACD near zero
        if pd.notna(latest['MACD']) and current_price > 0:
            macd_strength = abs(latest['MACD'] / current_price) * 100
            if macd_strength < 0.3:
                entry_score += 1
            elif macd_strength > 1.0:
                risk_score += 1
        
        # Determine signal
        if entry_score >= 6 and risk_score <= 3:
            signal = "STRONG ENTRY"
        elif entry_score >= 4 and risk_score <= 4:
            signal = "ENTRY"
        elif risk_score >= 6:
            signal = "EXIT / AVOID"
        elif risk_score >= 5:
            signal = "CAUTION"
        else:
            signal = "NEUTRAL"
        
        return entry_score, risk_score, signal
        
    except Exception as e:
        st.warning(f"⚠️ Score calculation error: {e}")
        return 0, 9, "NEUTRAL"

def find_iron_condor_strikes(options_data, expiration, current_price, target_delta=0.20):
    """Find optimal Iron Condor strikes based on delta"""
    if expiration not in options_data:
        return None
    
    options = options_data[expiration]
    
    # Separate calls and puts
    calls = [opt for opt in options if opt['type'] == 'call' and opt['strike'] > current_price]
    puts = [opt for opt in options if opt['type'] == 'put' and opt['strike'] < current_price]
    
    if not calls or not puts:
        return None
    
    # Sort by strike
    calls = sorted(calls, key=lambda x: x['strike'])
    puts = sorted(puts, key=lambda x: x['strike'], reverse=True)
    
    # Find strikes closest to target delta
    def find_closest_delta(opts, target):
        if not opts:
            return None
        return min(opts, key=lambda x: abs(abs(x['greeks']['delta']) - target))
    
    short_call = find_closest_delta(calls, target_delta)
    short_put = find_closest_delta(puts, target_delta)
    
    if not short_call or not short_put:
        return None
    
    # Find long strikes (1 strike width out)
    long_call = next((c for c in calls if c['strike'] > short_call['strike']), None)
    long_put = next((p for p in puts if p['strike'] < short_put['strike']), None)
    
    if not long_call or not long_put:
        return None
    
    # Calculate P&L
    credit = (short_call['bid'] + short_put['bid'] - long_call['ask'] - long_put['ask']) * 100
    max_loss = (max(long_call['strike'] - short_call['strike'], 
                    short_put['strike'] - long_put['strike']) * 100) - credit
    
    return {
        'short_call': short_call,
        'long_call': long_call,
        'short_put': short_put,
        'long_put': long_put,
        'max_profit': max(credit, 0),
        'max_loss': max(max_loss, 0),
        'breakeven_upper': short_call['strike'] + (max(credit, 0) / 100),
        'breakeven_lower': short_put['strike'] - (max(credit, 0) / 100),
        'pop': round((1 - abs(short_call['greeks']['delta']) - abs(short_put['greeks']['delta'])) * 100, 1)
    }

# ==================== UI COMPONENTS ====================

def display_header():
    """Display app header"""
    st.markdown('<div class="main-header">📊 SPY IRON CONDOR PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-Time Signals with Full Greeks & Multiple Expirations</div>', unsafe_allow_html=True)

def display_current_metrics(df, current_price, entry_score, risk_score, signal):
    """Display current trading metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    if len(df) < 2:
        price_change = 0
    else:
        price_change = ((current_price - df.iloc[-2]['Close']) / df.iloc[-2]['Close']) * 100
    
    latest = df.iloc[-1]
    
    with col1:
        st.metric(
            "SPY Price",
            f"${current_price:.2f}",
            f"{price_change:+.2f}%"
        )
    
    with col2:
        st.metric(
            "Entry Score",
            f"{entry_score}/9",
            "Good" if entry_score >= 6 else "Low"
        )
    
    with col3:
        st.metric(
            "Risk Score",
            f"{risk_score}/9",
            "High" if risk_score >= 5 else "Low"
        )
    
    with col4:
        rsi_val = latest.get('RSI', 50)
        st.metric(
            "RSI",
            f"{rsi_val:.1f}" if pd.notna(rsi_val) else "N/A",
            "Neutral" if 40 <= rsi_val <= 60 else "Extreme"
        )
    
    with col5:
        atr_val = latest.get('ATR_pct', 1.0)
        st.metric(
            "Volatility",
            f"{atr_val:.2f}%" if pd.notna(atr_val) else "N/A",
            "Low" if atr_val < 1.0 else "High"
        )

def display_signal_box(signal):
    """Display trading signal"""
    if signal == "STRONG ENTRY" or signal == "ENTRY":
        st.markdown(f'<div class="signal-strong-entry">🟢 {signal}</div>', unsafe_allow_html=True)
    elif signal == "EXIT / AVOID" or signal == "CAUTION":
        st.markdown(f'<div class="signal-exit">🔴 {signal}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="signal-neutral">🟡 {signal}</div>', unsafe_allow_html=True)

def display_strike_card(option, label, is_short):
    """Display individual strike information with Greeks"""
    greeks = option['greeks']
    
    badge_color = "#4caf50" if is_short else "#2196f3"
    
    st.markdown(f"""
    <div style="background: {badge_color}; color: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px;">{label}</div>
        <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">
            ${option['strike']} Strike
        </div>
        <div style="font-size: 14px; opacity: 0.9;">
            <b>Price:</b> ${option['last']:.2f} (Bid: ${option['bid']:.2f} / Ask: ${option['ask']:.2f})<br>
            <b>Delta:</b> {greeks['delta']:.4f} | <b>Gamma:</b> {greeks['gamma']:.4f}<br>
            <b>Theta:</b> {greeks['theta']:.4f} | <b>Vega:</b> {greeks['vega']:.4f}<br>
            <b>Rho:</b> {greeks['rho']:.4f} | <b>IV:</b> {option['iv']*100:.1f}%<br>
            <b>Volume:</b> {option['volume']:,} | <b>OI:</b> {option['open_interest']:,}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_iron_condor_setups(options_data, current_price, selected_expiry):
    """Display Iron Condor setups for 16Δ, 20Δ, and 30Δ"""
    st.markdown("### 🎯 Iron Condor Strike Recommendations")
    
    deltas = [
        (0.16, "CONSERVATIVE", "🛡️ Highest probability (~75%)"),
        (0.20, "BALANCED ⭐ OPTIMAL", "⚖️ Best risk/reward (~70%)"),
        (0.30, "AGGRESSIVE", "💰 Higher premium (~65%)")
    ]
    
    for target_delta, setup_name, description in deltas:
        with st.expander(f"**{setup_name}** - {description}", expanded=(target_delta == 0.20)):
            ic_setup = find_iron_condor_strikes(options_data, selected_expiry, current_price, target_delta)
            
            if not ic_setup:
                st.warning("⚠️ Could not find suitable strikes for this delta")
                continue
            
            # Display strikes
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### CALL SPREAD (Credit)")
                display_strike_card(ic_setup['short_call'], "Short Call (Sell)", is_short=True)
                display_strike_card(ic_setup['long_call'], "Long Call (Buy)", is_short=False)
            
            with col2:
                st.markdown("#### PUT SPREAD (Credit)")
                display_strike_card(ic_setup['short_put'], "Short Put (Sell)", is_short=True)
                display_strike_card(ic_setup['long_put'], "Long Put (Buy)", is_short=False)
            
            # P&L Summary
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Max Profit", f"${ic_setup['max_profit']:.2f}")
            with c2:
                st.metric("Max Loss", f"${ic_setup['max_loss']:.2f}")
            with c3:
                st.metric("Probability of Profit", f"{ic_setup['pop']}%")
            with c4:
                ratio = ic_setup['max_profit'] / ic_setup['max_loss'] if ic_setup['max_loss'] > 0 else 0
                st.metric("Risk/Reward", f"1:{ratio:.2f}")
            
            st.info(f"📍 **Breakeven Points:** Lower: ${ic_setup['breakeven_lower']:.2f} | Upper: ${ic_setup['breakeven_upper']:.2f}")
            
            # Paper Trading Button
            if PAPER_TRADING_AVAILABLE and st.session_state.get('paper_trading_enabled', False):
                st.markdown("---")
                
                # Calculate values for the form
                call_credit = (ic_setup['short_call']['bid'] - ic_setup['long_call']['ask'])
                put_credit = (ic_setup['short_put']['bid'] - ic_setup['long_put']['ask'])
                
                display_open_position_form(
                    st.session_state.paper_portfolio,
                    current_price,
                    selected_expiry,
                    setup_name,
                    ic_setup['short_call']['strike'],
                    ic_setup['long_call']['strike'],
                    ic_setup['short_put']['strike'],
                    ic_setup['long_put']['strike'],
                    call_credit,
                    put_credit
                )
            elif PAPER_TRADING_AVAILABLE:
                # Show message when paper trading is available but not enabled
                st.markdown("---")
                st.info("""
                💡 **Want to practice this trade?** 
                
                Enable **Paper Trading** in the sidebar to:
                - Open virtual positions with $10,000 starting cash
                - Track P&L in real-time
                - Build confidence before trading real money
                
                👈 Look for "📈 Paper Trading" in the left sidebar!
                """)


def display_full_options_chain(options_data, selected_expiry, current_price):
    """Display full options chain with all Greeks"""
    st.markdown("### 📋 Full Options Chain")
    
    if selected_expiry not in options_data:
        st.warning("No options data available for this expiration")
        return
    
    options = options_data[selected_expiry]
    
    # Create DataFrame
    chain_data = []
    for opt in options:
        chain_data.append({
            'Strike': opt['strike'],
            'Type': opt['type'].upper(),
            'Last': opt['last'],
            'Bid': opt['bid'],
            'Ask': opt['ask'],
            'Delta': opt['greeks']['delta'],
            'Gamma': opt['greeks']['gamma'],
            'Theta': opt['greeks']['theta'],
            'Vega': opt['greeks']['vega'],
            'Rho': opt['greeks']['rho'],
            'IV': f"{opt['iv']*100:.1f}%",
            'Volume': opt['volume'],
            'OI': opt['open_interest']
        })
    
    df_chain = pd.DataFrame(chain_data)
    
    # Filter around current price
    df_filtered = df_chain[
        (df_chain['Strike'] >= current_price - 30) & 
        (df_chain['Strike'] <= current_price + 30)
    ].sort_values('Strike')
    
    # Highlight ATM strikes with better contrast
    def highlight_atm(row):
        if abs(row['Strike'] - current_price) < 5:
            # Strong contrast: dark background with white text
            return ['background-color: #1976d2; color: white; font-weight: bold'] * len(row)
        # Alternate row coloring for better readability
        return ['background-color: #f5f5f5'] * len(row) if row.name % 2 == 0 else ['background-color: white'] * len(row)
    
    styled_df = df_filtered.style.apply(highlight_atm, axis=1).format({
        'Last': '${:.2f}',
        'Bid': '${:.2f}',
        'Ask': '${:.2f}',
        'Delta': '{:.4f}',
        'Gamma': '{:.4f}',
        'Theta': '{:.4f}',
        'Vega': '{:.4f}',
        'Rho': '{:.4f}',
        'Volume': '{:,.0f}',
        'OI': '{:,.0f}'
    }).set_properties(**{
        'text-align': 'right',
        'padding': '8px',
        'border': '1px solid #ddd'
    })
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )

# ==================== MAIN APP ====================

def main():
    # Initialize paper trading
    if PAPER_TRADING_AVAILABLE:
        initialize_paper_trading()
    
    display_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Simple choice: Demo or Yahoo Finance
        api_source = st.radio(
            "Data Source",
            ["Demo Mode", "Yahoo Finance (Real Data)"],
            index=1  # Default to Yahoo Finance
        )
        
        if api_source == "Yahoo Finance (Real Data)":
            st.success("✅ **Yahoo Finance - FREE Real Data!**")
            st.markdown("""
            **What you get:**
            - ✅ Real SPY options prices
            - ✅ Real Bid/Ask/Last
            - ✅ Real Implied Volatility
            - ✅ Real Volume & Open Interest
            - ✅ Calculated Greeks (accurate)
            - ✅ 15+ expirations
            - ✅ NO API key needed
            - ✅ 100% FREE
            
            **Data delay:** ~15 minutes (standard for free)
            """)
        else:
            st.info("💡 **Demo Mode**")
            st.markdown("""
            Perfect for:
            - Learning Iron Condor strategy
            - Understanding Greeks
            - Testing the app
            - Practicing analysis
            
            Uses realistic simulated data.
            """)
        
        # Paper Trading Toggle
        if PAPER_TRADING_AVAILABLE:
            st.markdown("---")
            st.markdown("### 📈 Paper Trading")
            
            paper_enabled = st.checkbox(
                "Enable Paper Trading",
                value=st.session_state.get('paper_trading_enabled', False),
                help="Test strategies with virtual money"
            )
            
            st.session_state.paper_trading_enabled = paper_enabled
            
            if paper_enabled:
                stats = st.session_state.paper_portfolio.get_stats()
                st.metric("Account Value", f"${stats['account_value']:,.2f}")
                st.metric("Total P&L", f"${stats['total_pnl']:+,.2f}")
                st.metric("Open Positions", stats['open_positions'])
                
                if st.button("📊 View Full Dashboard", use_container_width=True):
                    st.session_state.show_paper_dashboard = True
        
        st.markdown("---")
        
        # Timeframe selection
        timeframe_map = {
            "Daily": ("5d", "1d"),
            "1 Hour": ("5d", "1h"),
            "30 Minutes": ("2d", "30m"),
            "15 Minutes": ("1d", "15m")
        }
        
        timeframe_label = st.selectbox(
            "Chart Timeframe",
            list(timeframe_map.keys()),
            index=0
        )
        period, interval = timeframe_map[timeframe_label]
        
        # Auto-refresh
        auto_refresh = st.checkbox("Auto-refresh (60s)", value=False)
        
        if auto_refresh:
            time.sleep(60)
            st.rerun()
        
        # Info
        st.markdown("---")
        st.markdown("### 📊 Strategy Info")
        st.markdown("""
        **Iron Condor** profits when SPY stays within a range.
        
        **Best Conditions:**
        - Low volatility
        - RSI 40-60
        - Price in BB middle
        - Weak trend
        
        **Exit When:**
        - Volatility spikes
        - Strong directional move
        - 50% profit reached
        - 21 DTE or less
        """)
    
    # Fetch data
    with st.spinner("📡 Fetching SPY data..."):
        df = get_spy_data(period=period, interval=interval)
        
        if df.empty:
            st.error("❌ Could not load data. Please refresh.")
            st.stop()
        
        df = calculate_indicators(df)
        current_price = df['Close'].iloc[-1]
        
        # Fetch options data based on selected source
        if api_source == "Yahoo Finance (Real Data)":
            options_data = get_yahoo_options_chain("SPY")
        else:
            options_data = generate_demo_options_data()
        
        if not options_data:
            st.error("❌ No options data available")
            st.stop()
        
        expirations = list(options_data.keys())
    
    # Calculate signals
    entry_score, risk_score, signal = calculate_iron_condor_score(df, current_price)
    
    # Display metrics
    display_current_metrics(df, current_price, entry_score, risk_score, signal)
    
    st.markdown("---")
    
    # Signal box
    display_signal_box(signal)
    
    st.markdown("---")
    
    # Expiration selector
    st.markdown("### 📅 Select Expiration Date")
    
    # Session state for selected expiry
    if 'selected_expiry' not in st.session_state:
        st.session_state.selected_expiry = expirations[0]
    
    expiry_cols = st.columns(min(5, len(expirations)))
    
    for idx, exp_date in enumerate(expirations[:15]):
        col_idx = idx % 5
        days_to_exp = (datetime.strptime(exp_date, '%Y-%m-%d') - datetime.now()).days
        
        with expiry_cols[col_idx]:
            if st.button(f"{exp_date}\n({days_to_exp}d)", key=f"exp_{exp_date}"):
                st.session_state.selected_expiry = exp_date
    
    selected_expiry = st.session_state.selected_expiry
    days_remaining = (datetime.strptime(selected_expiry, '%Y-%m-%d') - datetime.now()).days
    
    st.markdown(f"**Selected Expiration:** <span class='expiry-badge'>{selected_expiry} ({days_remaining} days)</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Paper Trading Dashboard (if requested)
    if PAPER_TRADING_AVAILABLE and st.session_state.get('show_paper_dashboard', False):
        with st.expander("📈 Paper Trading Dashboard", expanded=True):
            display_paper_trading_dashboard(st.session_state.paper_portfolio)
            
            if st.button("✖ Close Dashboard"):
                st.session_state.show_paper_dashboard = False
                st.rerun()
        
        st.markdown("---")
    
    # Charts section
    display_professional_chart(df, current_price, entry_score, risk_score)
    
    st.markdown("---")
    
    # Iron Condor setups
    display_iron_condor_setups(options_data, current_price, selected_expiry)
    
    st.markdown("---")
    
    # Full options chain
    display_full_options_chain(options_data, selected_expiry, current_price)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
        <b>⚠️ DISCLAIMER:</b> This tool is for educational purposes only. Not financial advice. 
        Trade at your own risk. Past performance does not guarantee future results.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

