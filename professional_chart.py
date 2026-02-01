"""
Professional Iron Condor Chart System
- ONE main price chart with signal arrows
- Clear indicator displays with current values
- Dropdown help section
- Entry AND Exit signals
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def display_professional_chart(df, current_price, entry_score, risk_score):
    """
    Display ONE comprehensive chart with all indicators and signals
    """
    
    # Calculate signals
    entry_signal = entry_score >= 6 and risk_score <= 3
    exit_signal = risk_score >= 5
    
    # Create expandable "How to Read" section
    with st.expander("📖 How to Read This Chart", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📈 Price Action**
            - **Candlesticks**: Green = up, Red = down
            - **Bollinger Bands**: Gray bands show volatility
            - **SMA20**: Orange line = 20-day average
            
            **For Iron Condors:**
            ✅ Price in middle of bands = GOOD
            ❌ Price touching bands = AVOID
            """)
        
        with col2:
            st.markdown("""
            **📊 Technical Indicators**
            - **RSI**: Momentum (0-100)
              - 40-60 = Ideal range
              - >70 = Overbought
              - <30 = Oversold
            - **MACD**: Trend strength
              - Positive = Bullish
              - Negative = Bearish
            """)
        
        with col3:
            st.markdown("""
            **🎯 Entry/Exit Signals**
            - **🟢 Green UP Arrow** = ENTRY SIGNAL
              - Entry Score ≥ 6
              - Risk Score ≤ 3
            - **🔴 Red DOWN Arrow** = EXIT SIGNAL
              - Risk Score ≥ 5
            - **ATR%**: Volatility measure
              - <2% = Low vol (good)
              - >3% = High vol (avoid)
            """)
    
    # Display current indicator values at the top
    st.markdown("### 📊 Current Technical Readings")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get latest values
    latest = df.iloc[-1]
    rsi = latest.get('RSI', 0)
    macd = latest.get('MACD', 0)
    atr_pct = latest.get('ATR_pct', 0)
    volume = latest.get('Volume', 0)
    bb_position = ((current_price - latest.get('BB_lower', current_price)) / 
                   (latest.get('BB_upper', current_price) - latest.get('BB_lower', current_price)) * 100)
    
    with col1:
        rsi_color = "🟢" if 40 <= rsi <= 60 else "🔴" if rsi > 70 or rsi < 30 else "🟡"
        st.metric("RSI", f"{rsi:.1f}", delta=None)
        st.caption(f"{rsi_color} {'Neutral' if 40 <= rsi <= 60 else 'Extreme'}")
    
    with col2:
        macd_color = "🟢" if abs(macd) < 2 else "🔴"
        st.metric("MACD", f"{macd:.2f}", delta=None)
        st.caption(f"{macd_color} {'Weak trend' if abs(macd) < 2 else 'Strong trend'}")
    
    with col3:
        atr_color = "🟢" if atr_pct < 2 else "🔴" if atr_pct > 3 else "🟡"
        st.metric("ATR%", f"{atr_pct:.2f}%", delta=None)
        st.caption(f"{atr_color} {'Low vol' if atr_pct < 2 else 'High vol'}")
    
    with col4:
        bb_color = "🟢" if 30 <= bb_position <= 70 else "🔴"
        st.metric("BB Position", f"{bb_position:.0f}%", delta=None)
        st.caption(f"{bb_color} {'Middle' if 30 <= bb_position <= 70 else 'Edge'}")
    
    with col5:
        vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
        vol_color = "🟢" if volume < vol_ma * 1.2 else "🟡"
        st.metric("Volume", f"{volume/1e6:.1f}M", delta=None)
        st.caption(f"{vol_color} {'Normal' if volume < vol_ma * 1.2 else 'High'}")
    
    # Create the main chart with subplots
    fig = make_subplots(
        rows=5, cols=1,
        row_heights=[0.4, 0.15, 0.15, 0.15, 0.15],
        vertical_spacing=0.03,
        subplot_titles=('SPY Price with Signals', 'RSI (14)', 'MACD', 'ATR % Volatility', 'Volume'),
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # Row 1: Price chart with Bollinger Bands
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='SPY',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ), row=1, col=1)
    
    # Add Bollinger Bands
    if 'BB_upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_upper'],
            name='BB Upper',
            line=dict(color='rgba(128,128,128,0.5)', dash='dash'),
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_lower'],
            name='BB Lower',
            line=dict(color='rgba(128,128,128,0.5)', dash='dash'),
            fill='tonexty',
            fillcolor='rgba(128,128,128,0.1)',
            showlegend=False
        ), row=1, col=1)
    
    # Add SMA20
    if 'SMA20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA20'],
            name='SMA20',
            line=dict(color='orange', width=2, dash='dash'),
            showlegend=True
        ), row=1, col=1)
    
    # Add ENTRY signals (Green UP arrows)
    if entry_signal:
        # Add arrow at current price
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[current_price * 0.98],  # Slightly below price
            mode='markers+text',
            marker=dict(
                symbol='triangle-up',
                size=20,
                color='#00FF00',
                line=dict(color='darkgreen', width=2)
            ),
            text=['ENTER'],
            textposition='bottom center',
            textfont=dict(size=12, color='darkgreen', family='Arial Black'),
            name='Entry Signal',
            showlegend=False
        ), row=1, col=1)
    
    # Add EXIT signals (Red DOWN arrows)
    if exit_signal:
        # Add arrow at current price
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[current_price * 1.02],  # Slightly above price
            mode='markers+text',
            marker=dict(
                symbol='triangle-down',
                size=20,
                color='#FF0000',
                line=dict(color='darkred', width=2)
            ),
            text=['EXIT'],
            textposition='top center',
            textfont=dict(size=12, color='darkred', family='Arial Black'),
            name='Exit Signal',
            showlegend=False
        ), row=1, col=1)
    
    # Row 2: RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['RSI'],
            name='RSI',
            line=dict(color='purple', width=2),
            showlegend=False
        ), row=2, col=1)
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
        
        # Shade ideal zone
        fig.add_hrect(y0=40, y1=60, fillcolor="green", opacity=0.1, row=2, col=1)
    
    # Row 3: MACD
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD'],
            name='MACD',
            line=dict(color='blue', width=2),
            showlegend=False
        ), row=3, col=1)
        
        if 'MACD_signal' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD_signal'],
                name='Signal',
                line=dict(color='red', width=1),
                showlegend=False
            ), row=3, col=1)
        
        # MACD histogram
        if 'MACD_hist' in df.columns:
            colors = ['green' if val >= 0 else 'red' for val in df['MACD_hist']]
            fig.add_trace(go.Bar(
                x=df.index, y=df['MACD_hist'],
                name='Histogram',
                marker_color=colors,
                opacity=0.3,
                showlegend=False
            ), row=3, col=1)
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=3, col=1)
    
    # Row 4: ATR %
    if 'ATR_pct' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ATR_pct'],
            name='ATR%',
            line=dict(color='red', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,0,0,0.1)',
            showlegend=False
        ), row=4, col=1)
        
        # Add volatility zones
        fig.add_hline(y=2, line_dash="dash", line_color="green", opacity=0.5, row=4, col=1)
        fig.add_hline(y=3, line_dash="dash", line_color="red", opacity=0.5, row=4, col=1)
        fig.add_hrect(y0=0, y1=2, fillcolor="green", opacity=0.05, row=4, col=1)
    
    # Row 5: Volume
    if 'Volume' in df.columns:
        colors = ['green' if df.iloc[i]['Close'] >= df.iloc[i]['Open'] 
                 else 'red' for i in range(len(df))]
        
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.6,
            showlegend=False
        ), row=5, col=1)
        
        # Add volume MA
        vol_ma = df['Volume'].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=vol_ma,
            name='Vol MA',
            line=dict(color='blue', width=1, dash='dash'),
            showlegend=False
        ), row=5, col=1)
    
    # Update layout
    fig.update_layout(
        height=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified',
        template='plotly_white',
        margin=dict(t=100, b=50, l=50, r=50)
    )
    
    # Update x-axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    # Update y-axes
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Overall Signal Assessment
    st.markdown("---")
    st.markdown("### 🎯 Overall Iron Condor Signal Assessment")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Count favorable conditions
        conditions = []
        if 40 <= rsi <= 60:
            conditions.append("✅ RSI in neutral zone")
        else:
            conditions.append("❌ RSI extreme")
        
        if atr_pct < 2:
            conditions.append("✅ Low volatility")
        elif atr_pct < 3:
            conditions.append("🟡 Moderate volatility")
        else:
            conditions.append("❌ High volatility")
        
        if 30 <= bb_position <= 70:
            conditions.append("✅ Price in BB middle")
        else:
            conditions.append("❌ Price at BB edge")
        
        if abs(macd) < 2:
            conditions.append("✅ Weak trend")
        else:
            conditions.append("❌ Strong trend")
        
        if volume < vol_ma * 1.2:
            conditions.append("✅ Normal volume")
        else:
            conditions.append("🟡 High volume")
        
        green_count = sum(1 for c in conditions if c.startswith("✅"))
        
        st.markdown(f"**Score: {green_count}/5 Favorable**")
        
        for condition in conditions:
            st.markdown(condition)
    
    with col2:
        if green_count >= 4:
            st.success(f"""
            **🟢 STRONG ENTRY SIGNAL**
            
            **Recommendation:** Open Iron Condor position now
            
            **Setup:** Use the BALANCED (20Δ) setup below
            - Conservative: 16Δ for higher win rate
            - Aggressive: 30Δ for more premium
            
            **Entry Score:** {entry_score}/10
            **Risk Score:** {risk_score}/10
            """)
        elif green_count >= 3:
            st.warning(f"""
            **🟡 MODERATE SIGNAL**
            
            **Recommendation:** Consider waiting for better conditions
            
            **What to watch:**
            - Wait for RSI to reach 40-60
            - Watch for volatility to drop below 2%
            - Ensure price moves to middle of Bollinger Bands
            
            **Entry Score:** {entry_score}/10
            **Risk Score:** {risk_score}/10
            """)
        else:
            st.error(f"""
            **🔴 AVOID / EXIT**
            
            **Recommendation:** Do NOT enter new positions
            
            **Issues:**
            - Too many unfavorable conditions
            - High risk environment for Iron Condors
            - If holding positions, consider closing
            
            **Entry Score:** {entry_score}/10
            **Risk Score:** {risk_score}/10
            """)
