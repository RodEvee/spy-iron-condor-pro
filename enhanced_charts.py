# -*- coding: utf-8 -*-
"""
Enhanced Chart Functions for SPY Iron Condor Pro
With comprehensive technical indicators and visual entry/exit signals
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def add_signal_markers(fig, df, signal_column='Signal', entry_score_col='Entry_Score', risk_score_col='Risk_Score'):
    """Add entry/exit arrows to any chart"""
    
    # Find entry points (Entry Score >= 6, Risk <= 3)
    entry_points = df[
        (df.get(entry_score_col, 0) >= 6) & 
        (df.get(risk_score_col, 9) <= 3)
    ]
    
    # Find exit points (Risk Score >= 5)
    exit_points = df[df.get(risk_score_col, 0) >= 5]
    
    # Add green up arrows for entries
    if not entry_points.empty:
        fig.add_trace(go.Scatter(
            x=entry_points.index,
            y=entry_points['Close'] * 0.995,  # Slightly below price
            mode='markers+text',
            name='ENTRY Signal',
            marker=dict(
                symbol='triangle-up',
                size=15,
                color='lime',
                line=dict(color='darkgreen', width=2)
            ),
            text='🟢 ENTRY',
            textposition='bottom center',
            textfont=dict(size=10, color='green'),
            showlegend=True
        ))
    
    # Add red down arrows for exits
    if not exit_points.empty:
        fig.add_trace(go.Scatter(
            x=exit_points.index,
            y=exit_points['Close'] * 1.005,  # Slightly above price
            mode='markers+text',
            name='EXIT Signal',
            marker=dict(
                symbol='triangle-down',
                size=15,
                color='red',
                line=dict(color='darkred', width=2)
            ),
            text='🔴 EXIT',
            textposition='top center',
            textfont=dict(size=10, color='red'),
            showlegend=True
        ))
    
    return fig

def calculate_stochastic(df, k_period=14, d_period=3):
    """Calculate Stochastic Oscillator"""
    if len(df) < k_period:
        return df
    
    # %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    
    df['Stoch_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min + 0.0001)
    df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()
    
    return df

def calculate_ivr(df, lookback=252):
    """Calculate Implied Volatility Rank (simulated from ATR)"""
    if 'ATR' not in df.columns or len(df) < lookback:
        return df
    
    # Use ATR as proxy for IV
    current_atr = df['ATR']
    atr_min = df['ATR'].rolling(window=min(lookback, len(df))).min()
    atr_max = df['ATR'].rolling(window=min(lookback, len(df))).max()
    
    # IVR = (Current IV - Min IV) / (Max IV - Min IV) * 100
    df['IVR'] = 100 * (current_atr - atr_min) / (atr_max - atr_min + 0.0001)
    
    return df

def create_enhanced_price_chart(df, current_price, entry_score, risk_score):
    """Enhanced price chart with BB, MAs, and entry/exit signals"""
    
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='SPY Price',
        increasing_line_color='green',
        decreasing_line_color='red'
    ))
    
    # Bollinger Bands
    if 'BB_upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_upper'],
            name='Upper BB',
            line=dict(color='rgba(255,0,0,0.3)', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_lower'],
            name='Lower BB',
            line=dict(color='rgba(0,255,0,0.3)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(100,100,100,0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA20'],
            name='SMA 20 (Middle BB)',
            line=dict(color='orange', width=2, dash='dot')
        ))
    
    # 50-period MA
    if len(df) >= 50:
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA50'],
            name='SMA 50',
            line=dict(color='blue', width=2)
        ))
    
    # Add signal arrows
    df['Entry_Score'] = entry_score
    df['Risk_Score'] = risk_score
    fig = add_signal_markers(fig, df)
    
    # Current price line
    fig.add_hline(
        y=current_price,
        line_dash="solid",
        line_color="yellow",
        line_width=2,
        annotation_text=f"Current: ${current_price:.2f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='📊 Price Action with Bollinger Bands & Entry/Exit Signals',
        yaxis_title='Price ($)',
        xaxis_title='Time',
        height=500,
        hovermode='x unified',
        template='plotly_dark',
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_enhanced_rsi_chart(df):
    """Enhanced RSI with zones and signals"""
    
    if 'RSI' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # RSI line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        name='RSI (14)',
        line=dict(color='purple', width=3)
    ))
    
    # Zone shading
    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, line_width=0,
                  annotation_text="Overbought - AVOID", annotation_position="top right")
    fig.add_hrect(y0=60, y1=70, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=40, y1=60, fillcolor="green", opacity=0.15, line_width=0,
                  annotation_text="OPTIMAL ZONE", annotation_position="left")
    fig.add_hrect(y0=30, y1=40, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor="red", opacity=0.1, line_width=0,
                  annotation_text="Oversold - AVOID", annotation_position="bottom right")
    
    # Reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5)
    
    # Current RSI marker
    current_rsi = df['RSI'].iloc[-1]
    fig.add_trace(go.Scatter(
        x=[df.index[-1]],
        y=[current_rsi],
        mode='markers',
        name='Current RSI',
        marker=dict(size=12, color='yellow', symbol='diamond')
    ))
    
    fig.update_layout(
        title='📈 RSI (Relative Strength Index) - Momentum Indicator',
        yaxis_title='RSI',
        xaxis_title='Time',
        height=350,
        yaxis=dict(range=[0, 100]),
        template='plotly_dark'
    )
    
    return fig

def create_enhanced_macd_chart(df):
    """Enhanced MACD with histogram and signals"""
    
    if 'MACD' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # MACD line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD'],
        name='MACD',
        line=dict(color='blue', width=2)
    ))
    
    # Signal line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD_signal'],
        name='Signal',
        line=dict(color='red', width=2)
    ))
    
    # Histogram
    macd_hist = df['MACD'] - df['MACD_signal']
    colors = ['green' if x > 0 else 'red' for x in macd_hist]
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=macd_hist,
        name='Histogram',
        marker_color=colors,
        opacity=0.4
    ))
    
    # Zero line
    fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.5, line_width=2)
    
    # Highlight neutral zone
    max_macd = df['MACD'].max()
    min_macd = df['MACD'].min()
    neutral_threshold = (max_macd - min_macd) * 0.1
    
    fig.add_hrect(
        y0=-neutral_threshold, 
        y1=neutral_threshold, 
        fillcolor="green", 
        opacity=0.1, 
        line_width=0,
        annotation_text="OPTIMAL (Weak Trend)",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='📉 MACD - Trend Strength & Momentum',
        yaxis_title='MACD',
        xaxis_title='Time',
        height=350,
        template='plotly_dark'
    )
    
    return fig

def create_enhanced_atr_chart(df):
    """Enhanced ATR with volatility zones"""
    
    if 'ATR_pct' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # ATR line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['ATR_pct'],
        name='ATR %',
        line=dict(color='darkred', width=3),
        fill='tozeroy',
        fillcolor='rgba(139,0,0,0.2)'
    ))
    
    # Volatility zones
    fig.add_hrect(y0=0, y1=0.8, fillcolor="green", opacity=0.15, line_width=0,
                  annotation_text="LOW VOL - ENTER", annotation_position="top left")
    fig.add_hrect(y0=0.8, y1=1.5, fillcolor="yellow", opacity=0.1, line_width=0,
                  annotation_text="MEDIUM VOL", annotation_position="top left")
    fig.add_hrect(y0=1.5, y1=2.0, fillcolor="orange", opacity=0.1, line_width=0,
                  annotation_text="HIGH VOL - CAUTION", annotation_position="top left")
    fig.add_hrect(y0=2.0, y1=10, fillcolor="red", opacity=0.15, line_width=0,
                  annotation_text="EXTREME VOL - EXIT", annotation_position="top left")
    
    # Reference lines
    fig.add_hline(y=0.8, line_dash="dash", line_color="green", opacity=0.7, line_width=2)
    fig.add_hline(y=2.0, line_dash="dash", line_color="red", opacity=0.7, line_width=2)
    
    # Current ATR marker
    current_atr = df['ATR_pct'].iloc[-1]
    fig.add_trace(go.Scatter(
        x=[df.index[-1]],
        y=[current_atr],
        mode='markers',
        name='Current ATR',
        marker=dict(size=12, color='yellow', symbol='diamond')
    ))
    
    fig.update_layout(
        title='📊 ATR % - Volatility Meter (Key for Iron Condors!)',
        yaxis_title='ATR %',
        xaxis_title='Time',
        height=350,
        template='plotly_dark'
    )
    
    return fig

def create_stochastic_chart(df):
    """Stochastic Oscillator for momentum confirmation"""
    
    if 'Stoch_K' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # %K line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Stoch_K'],
        name='%K (Fast)',
        line=dict(color='blue', width=2)
    ))
    
    # %D line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Stoch_D'],
        name='%D (Slow)',
        line=dict(color='red', width=2)
    ))
    
    # Zones
    fig.add_hrect(y0=80, y1=100, fillcolor="red", opacity=0.1, line_width=0,
                  annotation_text="Overbought", annotation_position="top right")
    fig.add_hrect(y0=50, y1=80, fillcolor="green", opacity=0.1, line_width=0,
                  annotation_text="NEUTRAL ZONE", annotation_position="right")
    fig.add_hrect(y0=20, y1=50, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=0, y1=20, fillcolor="red", opacity=0.1, line_width=0,
                  annotation_text="Oversold", annotation_position="bottom right")
    
    # Reference lines
    fig.add_hline(y=80, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3)
    fig.add_hline(y=20, line_dash="dash", line_color="green", opacity=0.5)
    
    fig.update_layout(
        title='📈 Stochastic Oscillator - Momentum Confirmation',
        yaxis_title='Stochastic',
        xaxis_title='Time',
        height=350,
        yaxis=dict(range=[0, 100]),
        template='plotly_dark'
    )
    
    return fig

def create_ivr_chart(df):
    """Implied Volatility Rank - Options timing"""
    
    if 'IVR' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # IVR line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['IVR'],
        name='IVR',
        line=dict(color='purple', width=3),
        fill='tozeroy',
        fillcolor='rgba(128,0,128,0.2)'
    ))
    
    # Zones
    fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.1, line_width=0,
                  annotation_text="LOW IVR - Avoid Selling", annotation_position="top left")
    fig.add_hrect(y0=25, y1=50, fillcolor="yellow", opacity=0.1, line_width=0,
                  annotation_text="MEDIUM IVR", annotation_position="top left")
    fig.add_hrect(y0=50, y1=100, fillcolor="green", opacity=0.15, line_width=0,
                  annotation_text="HIGH IVR - SELL OPTIONS!", annotation_position="top left")
    
    # Reference lines
    fig.add_hline(y=50, line_dash="dash", line_color="green", opacity=0.7, line_width=2,
                  annotation_text="Ideal > 50%")
    
    # Current IVR marker
    current_ivr = df['IVR'].iloc[-1]
    fig.add_trace(go.Scatter(
        x=[df.index[-1]],
        y=[current_ivr],
        mode='markers',
        name='Current IVR',
        marker=dict(size=12, color='yellow', symbol='diamond')
    ))
    
    fig.update_layout(
        title='📊 IVR (Implied Volatility Rank) - Premium Levels',
        yaxis_title='IVR %',
        xaxis_title='Time',
        height=350,
        yaxis=dict(range=[0, 100]),
        template='plotly_dark'
    )
    
    return fig

def create_volume_chart(df):
    """Enhanced volume chart with trend"""
    
    if 'Volume' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # Color volume bars
    colors = ['green' if df['Close'].iloc[i] >= df['Close'].iloc[i-1] else 'red' 
             for i in range(1, len(df))]
    colors = ['gray'] + colors
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color=colors,
        opacity=0.7
    ))
    
    # Volume MA
    if len(df) >= 20:
        vol_ma = df['Volume'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=vol_ma,
            name='Vol MA(20)',
            line=dict(color='blue', width=2)
        ))
    
    fig.update_layout(
        title='📊 Volume - Confirms Price Moves',
        yaxis_title='Volume',
        xaxis_title='Time',
        height=300,
        template='plotly_dark'
    )
    
    return fig

def display_indicator_explanation(indicator_name, current_value, interpretation, 
                                   entry_rule, exit_rule):
    """Display explanation card for each indicator"""
    
    # Color based on interpretation
    if 'GOOD' in interpretation or 'ENTER' in interpretation:
        color = '#28a745'  # Green
        icon = '✅'
    elif 'EXIT' in interpretation or 'AVOID' in interpretation:
        color = '#dc3545'  # Red
        icon = '⚠️'
    else:
        color = '#ffc107'  # Yellow
        icon = '⚡'
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%); 
                padding: 15px; border-radius: 10px; border-left: 4px solid {color}; margin: 10px 0;">
        <h4 style="color: {color}; margin: 0 0 10px 0;">{icon} {indicator_name}: {current_value}</h4>
        <p style="margin: 5px 0;"><strong>Reading:</strong> {interpretation}</p>
        <p style="margin: 5px 0;"><strong>🟢 Entry:</strong> {entry_rule}</p>
        <p style="margin: 5px 0;"><strong>🔴 Exit:</strong> {exit_rule}</p>
    </div>
    """, unsafe_allow_html=True)
