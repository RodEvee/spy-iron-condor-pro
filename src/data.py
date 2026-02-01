# src/data.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_spy_data(period="5d", interval="1d"):
    try:
        spy = yf.Ticker("SPY")
        df = spy.history(period=period, interval=interval)
        if df.empty:
            return generate_demo_price_data()
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception:
        return generate_demo_price_data()

def generate_demo_price_data():
    dates = pd.date_range(end=datetime.now(), periods=120, freq='1h')
    prices = 580 + np.cumsum(np.random.randn(120) * 1.2)
    return pd.DataFrame({
        'Open': prices,
        'High': prices + np.random.uniform(0.5, 2, 120),
        'Low': prices - np.random.uniform(0.5, 2, 120),
        'Close': prices + np.random.uniform(-0.8, 0.8, 120),
        'Volume': np.random.randint(800000, 6000000, 120)
    }, index=dates)

def get_yahoo_options_chain(symbol="SPY"):
    try:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options[:15]
        if not expirations:
            return None

        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        options_data = {}

        for exp_date in expirations:
            chain = ticker.option_chain(exp_date)
            calls = chain.calls
            puts = chain.puts

            opts = []
            dte = (datetime.strptime(exp_date, '%Y-%m-%d') - datetime.now()).days

            for df_opt, opt_type in [(calls, 'call'), (puts, 'put')]:
                for _, row in df_opt.iterrows():
                    iv = row.get('impliedVolatility', 0.20)
                    delta = calculate_delta(current_price, row['strike'], dte, iv, opt_type)
                    opts.append({
                        'strike': row['strike'],
                        'type': opt_type,
                        'expiration_date': exp_date,
                        'bid': row.get('bid', 0),
                        'ask': row.get('ask', 0),
                        'last': row.get('lastPrice', 0),
                        'greeks': {'delta': round(delta, 4)},
                        'iv': round(iv, 4)
                    })

            options_data[exp_date] = opts

        return options_data
    except Exception:
        return None

# Minimal Greeks (only delta for speed – expand later)
from scipy.stats import norm
from math import log, sqrt, exp

def calculate_delta(S, K, T, sigma, option_type='call'):
    if T <= 0:
        return 1.0 if option_type == 'call' and S > K else 0.0
    try:
        r = 0.045  # 2026 realistic short-term rate
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * (T/365)) / (sigma * sqrt(T/365))
        return norm.cdf(d1) if option_type == 'call' else norm.cdf(-d1) - 1
    except:
        return 0.5 if option_type == 'call' else -0.5
