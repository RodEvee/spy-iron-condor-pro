# src/greeks.py
from math import log, sqrt, exp, pi
from scipy.stats import norm
import numpy as np

def calculate_delta(S: float, K: float, T: float, sigma: float, option_type: str = 'call') -> float:
    """Delta: Rate of change of option price with respect to underlying price"""
    if T <= 0:
        if option_type == 'call':
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0

    try:
        r = 0.045  # Approximate 2026 short-term risk-free rate
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * (T / 365)) / (sigma * sqrt(T / 365))
        if option_type == 'call':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1
    except:
        return 0.5 if option_type == 'call' else -0.5


def calculate_gamma(S: float, K: float, T: float, sigma: float) -> float:
    """Gamma: Rate of change of delta with respect to underlying price"""
    if T <= 0:
        return 0.0

    try:
        r = 0.045
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * (T / 365)) / (sigma * sqrt(T / 365))
        return norm.pdf(d1) / (S * sigma * sqrt(T / 365))
    except:
        return 0.01


def calculate_theta(S: float, K: float, T: float, sigma: float, option_type: str = 'call') -> float:
    """Theta: Daily time decay (negative for long options)"""
    if T <= 0:
        return 0.0

    try:
        r = 0.045
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * (T / 365)) / (sigma * sqrt(T / 365))
        d2 = d1 - sigma * sqrt(T / 365)

        if option_type == 'call':
            theta = (
                -S * norm.pdf(d1) * sigma / (2 * sqrt(T / 365)) -
                r * K * exp(-r * T / 365) * norm.cdf(d2)
            )
        else:
            theta = (
                -S * norm.pdf(d1) * sigma / (2 * sqrt(T / 365)) +
                r * K * exp(-r * T / 365) * norm.cdf(-d2)
            )

        return theta / 365  # Per day
    except:
        return -0.05


def calculate_vega(S: float, K: float, T: float, sigma: float) -> float:
    """Vega: Sensitivity to volatility (same for call & put)"""
    if T <= 0:
        return 0.0

    try:
        r = 0.045
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * (T / 365)) / (sigma * sqrt(T / 365))
        return S * norm.pdf(d1) * sqrt(T / 365) / 100  # Per 1% change
    except:
        return 0.15


def calculate_rho(S: float, K: float, T: float, sigma: float, option_type: str = 'call') -> float:
    """Rho: Sensitivity to interest rates"""
    if T <= 0:
        return 0.0

    try:
        r = 0.045
        d1 = (log(S / K) + (r + 0.5 * sigma**2) * (T / 365)) / (sigma * sqrt(T / 365))
        d2 = d1 - sigma * sqrt(T / 365)

        if option_type == 'call':
            return K * (T / 365) * exp(-r * T / 365) * norm.cdf(d2) / 100
        else:
            return -K * (T / 365) * exp(-r * T / 365) * norm.cdf(-d2) / 100
    except:
        return 0.01
