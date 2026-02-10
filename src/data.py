# src/data.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.greeks import (
    calculate_delta, calculate_gamma, calculate_theta,
    calculate_vega, calculate_rho
)

def get_spy_data(period="5d", interval="1d"):
    try:
        spy = yf.Ticker("SPY")
        df = spy.history(period=period, interval=interval)
        if df.empty:
            return generate_demo_price_data()
        return df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    except Exception:
        return generate_demo_price_data()


def generate_demo_price_data():
    dates = pd.date_range(end=datetime.now(), periods=120, freq='H')
    base = 580 + np.cumsum(np.random.randn(120) * 1.5)
    return pd.DataFrame({
        'Open':  base + np.random.uniform(-0.5, 0.5, 120),
        'High':  base + np.random.uniform(0.3, 1.8, 120),
        'Low':   base + np.random.uniform(-1.8, -0.3, 120),
        'Close': base + np.random.uniform(-0.8, 0.8, 120),
        'Volume': np.random.randint(900_000, 7_000_000, 120)
    }, index=dates)


def get_yahoo_options_chain(symbol="SPY"):
    try:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options[:12]  # limit to avoid rate-limiting
        if not expirations:
            return None

        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        options_data = {}

        for exp_date in expirations:
            opt_chain = ticker.option_chain(exp_date)
            calls = opt_chain.calls
            puts  = opt_chain.puts

            opts = []
            dte = max(1, (datetime.strptime(exp_date, '%Y-%m-%d') - datetime.now()).days)

            for side, df_side in [('call', calls), ('put', puts)]:
                for _, row in df_side.iterrows():
                    strike = row['strike']
                    iv = row.get('impliedVolatility', 0.20)

                    delta = calculate_delta(current_price, strike, dte, iv, side)
                    gamma = calculate_gamma(current_price, strike, dte, iv)
                    theta = calculate_theta(current_price, strike, dte, iv, side)
                    vega  = calculate_vega(current_price, strike, dte, iv)
                    rho   = calculate_rho(current_price, strike, dte, iv, side)

                    opts.append({
                        'strike': strike,
                        'type': side,
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
                            'vega':  round(vega,  4),
                            'rho':   round(rho,   4)
                        },
                        'iv': round(iv, 4)
                    })

            options_data[exp_date] = opts

        return options_data

    except Exception as e:
        print(f"Yahoo options fetch failed: {e}")
        return None


def generate_demo_options_data():
    """Generate realistic demo options data with proper calls AND puts at each strike"""
    current_price = 580.0
    expirations = [(datetime.now() + timedelta(days=d)).strftime('%Y-%m-%d') for d in [7, 14, 21, 30, 45, 60]]
    data = {}

    for exp in expirations:
        dte = max(1, (datetime.strptime(exp, '%Y-%m-%d') - datetime.now()).days)
        opts = []

        for strike in np.arange(current_price - 40, current_price + 45, 5):
            iv = 0.18 + abs(strike - current_price) / current_price * 0.4

            # Generate CALL
            call_delta = calculate_delta(current_price, strike, dte, iv, 'call')
            call_theta = calculate_theta(current_price, strike, dte, iv, 'call')
            call_intrinsic = max(0, current_price - strike)
            call_price = max(0.05, call_intrinsic + iv * np.sqrt(dte / 365) * current_price * 0.1)
            opts.append({
                'strike': strike,
                'type': 'call',
                'expiration_date': exp,
                'bid': round(max(0.05, call_price - 0.03), 2),
                'ask': round(max(0.10, call_price + 0.03), 2),
                'greeks': {
                    'delta': round(call_delta, 4),
                    'gamma': round(calculate_gamma(current_price, strike, dte, iv), 4),
                    'theta': round(call_theta, 4),
                    'vega': round(calculate_vega(current_price, strike, dte, iv), 4),
                    'rho': round(calculate_rho(current_price, strike, dte, iv, 'call'), 4),
                },
                'iv': round(iv, 4)
            })

            # Generate PUT
            put_delta = calculate_delta(current_price, strike, dte, iv, 'put')
            put_theta = calculate_theta(current_price, strike, dte, iv, 'put')
            put_intrinsic = max(0, strike - current_price)
            put_price = max(0.05, put_intrinsic + iv * np.sqrt(dte / 365) * current_price * 0.1)
            opts.append({
                'strike': strike,
                'type': 'put',
                'expiration_date': exp,
                'bid': round(max(0.05, put_price - 0.03), 2),
                'ask': round(max(0.10, put_price + 0.03), 2),
                'greeks': {
                    'delta': round(put_delta, 4),
                    'gamma': round(calculate_gamma(current_price, strike, dte, iv), 4),
                    'theta': round(put_theta, 4),
                    'vega': round(calculate_vega(current_price, strike, dte, iv), 4),
                    'rho': round(calculate_rho(current_price, strike, dte, iv, 'put'), 4),
                },
                'iv': round(iv, 4)
            })

        data[exp] = opts
    return data
