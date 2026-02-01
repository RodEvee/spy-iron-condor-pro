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
            dte = max(0, (datetime.strptime(exp_date, '%Y-%m-%d') - datetime.now()).days + 1/24)

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
    # very simplified placeholder – you can keep your original if preferred
    current_price = 580.0
    expirations = [(datetime.now() + timedelta(days=d)).strftime('%Y-%m-%d') for d in [7,14,21,30,45,60]]
    data = {}
    for exp in expirations:
        dte = max(1, (datetime.strptime(exp, '%Y-%m-%d') - datetime.now()).days)
        opts = []
        for strike in np.arange(current_price-40, current_price+45, 5):
            iv = 0.18 + abs(strike - current_price)/current_price * 0.4
            delta = 0.5 + (current_price - strike)/(current_price*2)
            opts.append({
                'strike': strike,
                'type': 'call' if strike > current_price else 'put',
                'bid': max(0.05, abs(current_price - strike)*0.4 + iv*5),
                'ask': max(0.10, abs(current_price - strike)*0.4 + iv*5 + 0.05),
                'greeks': {'delta': round(delta if strike > current_price else delta-1, 4)},
                'iv': round(iv, 4)
            })
        data[exp] = opts
    return data
