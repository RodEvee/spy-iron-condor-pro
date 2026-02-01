import pandas as pd
import numpy as np

def calculate_indicators(df):
    if len(df) < 20:
        return df

    # Bollinger Bands
    df['SMA20'] = df['Close'].rolling(20, min_periods=1).mean()
    df['BB_std'] = df['Close'].rolling(20, min_periods=1).std()
    df['BB_upper'] = df['SMA20'] + df['BB_std'] * 2
    df['BB_lower'] = df['SMA20'] - df['BB_std'] * 2
    df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['SMA20'] * 100

    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14, min_periods=1).mean()
    loss = -delta.where(delta < 0, 0).rolling(14, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan).fillna(0.0001)
    df['RSI'] = 100 - (100 / (1 + rs))

    # Fill NaNs safely
    df = df.bfill().ffill().fillna(0)

    return df


def calculate_iron_condor_score(df, current_price):
    if len(df) < 20:
        return 0, 9, "NEUTRAL"

    latest = df.iloc[-1]

    entry = 0
    risk = 0

    # RSI neutral
    rsi = latest.get('RSI', 50)
    if 45 <= rsi <= 55: entry += 2
    elif 40 <= rsi <= 60: entry += 1
    elif rsi < 35 or rsi > 65: risk += 2

    # BB position
    if 'BB_lower' in latest and 'BB_upper' in latest:
        bb_range = latest['BB_upper'] - latest['BB_lower']
        if bb_range > 0:
            pos = (current_price - latest['BB_lower']) / bb_range
            if 0.4 <= pos <= 0.6: entry += 2
            elif 0.3 <= pos <= 0.7: entry += 1
            elif pos < 0.25 or pos > 0.75: risk += 2

    # Low vol
    if 'BB_width' in latest:
        if latest['BB_width'] < 5: entry += 2
        elif latest['BB_width'] > 10: risk += 2

    signal = "NEUTRAL"
    if entry >= 5 and risk <= 3:
        signal = "STRONG ENTRY"
    elif entry >= 3:
        signal = "ENTRY"
    elif risk >= 5:
        signal = "CAUTION / AVOID"

    return entry, risk, signal


def find_iron_condor_strikes(options_data, expiration, current_price, target_delta=0.20):
    if expiration not in options_data:
        return None

    opts = options_data[expiration]
    calls = [o for o in opts if o['type'] == 'call' and o['strike'] > current_price]
    puts  = [o for o in opts if o['type'] == 'put'  and o['strike'] < current_price]

    if not calls or not puts:
        return None

    calls = sorted(calls, key=lambda x: x['strike'])
    puts  = sorted(puts,  key=lambda x: x['strike'], reverse=True)

    def closest_delta(items, target):
        if not items: return None
        return min(items, key=lambda x: abs(abs(x.get('greeks', {}).get('delta', 0)) - target))

    short_call = closest_delta(calls, target_delta)
    short_put  = closest_delta(puts,  target_delta)

    if not short_call or not short_put:
        return None

    # Simple long legs (next strike)
    long_call = next((c for c in calls if c['strike'] > short_call['strike']), None)
    long_put  = next((p for p in puts  if p['strike'] < short_put['strike']),  None)

    if not long_call or not long_put:
        return None

    credit = (short_call['bid'] + short_put['bid'] - long_call['ask'] - long_put['ask']) * 100
    width = max(long_call['strike'] - short_call['strike'], short_put['strike'] - long_put['strike'])
    max_loss = width * 100 - credit

    pop = round((1 - abs(short_call.get('greeks', {}).get('delta', 0.3)) - abs(short_put.get('greeks', {}).get('delta', 0.3))) * 100, 1)

    return {
        'short_call': short_call,
        'long_call': long_call,
        'short_put': short_put,
        'long_put': long_put,
        'max_profit': max(credit, 0),
        'max_loss': max(max_loss, 0),
        'pop': pop
    }
