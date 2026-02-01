# -*- coding: utf-8 -*-
"""
ALL-IN-ONE Mega Chart for SPY Iron Condor Pro
Shows everything on a single comprehensive view
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

def create_mega_chart(df, current_price, entry_score, risk_score):
    """
    Create ONE comprehensive chart with ALL indicators and visual signals
    
    Layout:
    - Row 1: Price + Bollinger Bands (with entry/exit arrows)
    - Row 2: RSI
    - Row 3: MACD
    - Row 4: ATR %
    - Row 5: Volume
    """
    
    # Create subplots
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.4, 0.15, 0.15, 0.15, 0.15],
        subplot_titles=(
            '📊 SPY Price with Bollinger Bands & ENTRY/EXIT SIGNALS',
            '📈 RSI (14) - Momentum',
            '📉 MACD - Trend Strength',
            '📊 ATR % - Volatility (KEY for Iron Condors!)',
            '📊 Volume'
        )
    )
    
    # =====================
    # ROW 1: PRICE + BOLLINGER BANDS + SIGNALS
    # =====================
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='SPY Price',
        increasing_line_color='green',
        decreasing_line_color='red',
        showlegend=True
    ), row=1, col=1)
    
    # Bollinger Bands
    if 'BB_upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_upper'],
            name='Upper BB',
            line=dict(color='rgba(255,0,0,0.5)', width=1, dash='dash'),
            showlegend=True
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_lower'],
            name='Lower BB',
            line=dict(color='rgba(0,255,0,0.5)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(100,100,100,0.1)',
            showlegend=True
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA20'],
            name='SMA 20',
            line=dict(color='orange', width=2, dash='dot'),
            showlegend=True
        ), row=1, col=1)
    
    # 50-day MA
    if len(df) >= 50:
        sma50 = df['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=sma50,
            name='SMA 50',
            line=dict(color='blue', width=2),
            showlegend=True
        ), row=1, col=1)
    
    # ENTRY/EXIT SIGNALS - GREEN UP ARROWS & RED DOWN ARROWS
    # Entry points: Entry Score >= 6 AND Risk Score <= 3
    entry_mask = (entry_score >= 6) & (risk_score <= 3)
    if entry_mask and len(df) > 0:
        # Get last few entry points
        entry_indices = df.index[-min(50, len(df)):]
        entry_prices = df.loc[entry_indices, 'Close'] * 0.995  # Slightly below
        
        # Add green up arrows for entries
        fig.add_trace(go.Scatter(
            x=entry_indices[::5],  # Show every 5th point
            y=entry_prices[::5],
            mode='markers+text',
            name='🟢 ENTRY Signal',
            marker=dict(
                symbol='triangle-up',
                size=20,
                color='lime',
                line=dict(color='darkgreen', width=3)
            ),
            text='ENTER',
            textposition='bottom center',
            textfont=dict(size=10, color='lime', family='Arial Black'),
            showlegend=True
        ), row=1, col=1)
    
    # Exit points: Risk Score >= 5
    exit_mask = risk_score >= 5
    if exit_mask and len(df) > 0:
        exit_indices = df.index[-min(50, len(df)):]
        exit_prices = df.loc[exit_indices, 'Close'] * 1.005  # Slightly above
        
        # Add red down arrows for exits
        fig.add_trace(go.Scatter(
            x=exit_indices[::5],
            y=exit_prices[::5],
            mode='markers+text',
            name='🔴 EXIT Signal',
            marker=dict(
                symbol='triangle-down',
                size=20,
                color='red',
                line=dict(color='darkred', width=3)
            ),
            text='EXIT',
            textposition='top center',
            textfont=dict(size=10, color='red', family='Arial Black'),
            showlegend=True
        ), row=1, col=1)
    
    # Current price line
    fig.add_hline(
        y=current_price,
        line_dash="solid",
        line_color="yellow",
        line_width=3,
        annotation_text=f"Current: ${current_price:.2f}",
        annotation_position="right",
        row=1, col=1
    )
    
    # =====================
    # ROW 2: RSI
    # =====================
    
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['RSI'],
            name='RSI',
            line=dict(color='purple', width=3),
            showlegend=False
        ), row=2, col=1)
        
        # RSI zones
        fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, line_width=0, row=2, col=1)
        fig.add_hrect(y0=40, y1=60, fillcolor="green", opacity=0.15, line_width=0, row=2, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="red", opacity=0.1, line_width=0, row=2, col=1)
        
        # RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
        
        # Current RSI marker
        current_rsi = df['RSI'].iloc[-1]
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[current_rsi],
            mode='markers+text',
            name='Current RSI',
            marker=dict(size=15, color='yellow', symbol='diamond'),
            text=f'{current_rsi:.0f}',
            textposition='middle right',
            showlegend=False
        ), row=2, col=1)
    
    # =====================
    # ROW 3: MACD
    # =====================
    
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD'],
            name='MACD',
            line=dict(color='blue', width=2),
            showlegend=False
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD_signal'],
            name='Signal',
            line=dict(color='red', width=2),
            showlegend=False
        ), row=3, col=1)
        
        # Histogram
        macd_hist = df['MACD'] - df['MACD_signal']
        colors = ['green' if x > 0 else 'red' for x in macd_hist]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=macd_hist,
            name='Histogram',
            marker_color=colors,
            opacity=0.4,
            showlegend=False
        ), row=3, col=1)
        
        # Zero line
        fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.5, row=3, col=1)
    
    # =====================
    # ROW 4: ATR %
    # =====================
    
    if 'ATR_pct' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['ATR_pct'],
            name='ATR %',
            line=dict(color='darkred', width=3),
            fill='tozeroy',
            fillcolor='rgba(139,0,0,0.2)',
            showlegend=False
        ), row=4, col=1)
        
        # ATR zones
        fig.add_hrect(y0=0, y1=0.8, fillcolor="green", opacity=0.15, line_width=0, row=4, col=1)
        fig.add_hrect(y0=2.0, y1=10, fillcolor="red", opacity=0.15, line_width=0, row=4, col=1)
        
        # Reference lines
        fig.add_hline(y=0.8, line_dash="dash", line_color="green", line_width=2, row=4, col=1)
        fig.add_hline(y=2.0, line_dash="dash", line_color="red", line_width=2, row=4, col=1)
        
        # Current ATR marker
        current_atr = df['ATR_pct'].iloc[-1]
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[current_atr],
            mode='markers+text',
            name='Current ATR',
            marker=dict(size=15, color='yellow', symbol='diamond'),
            text=f'{current_atr:.2f}%',
            textposition='middle right',
            showlegend=False
        ), row=4, col=1)
    
    # =====================
    # ROW 5: VOLUME
    # =====================
    
    if 'Volume' in df.columns:
        colors = ['green' if df['Close'].iloc[i] >= df['Close'].iloc[i-1] else 'red' 
                 for i in range(1, len(df))]
        colors = ['gray'] + colors
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7,
            showlegend=False
        ), row=5, col=1)
        
        # Volume MA
        if len(df) >= 20:
            vol_ma = df['Volume'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=vol_ma,
                name='Vol MA(20)',
                line=dict(color='blue', width=2),
                showlegend=False
            ), row=5, col=1)
    
    # =====================
    # LAYOUT & STYLING
    # =====================
    
    fig.update_layout(
        height=1400,  # Tall chart to fit everything
        template='plotly_dark',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time", row=5, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="ATR %", row=4, col=1)
    fig.update_yaxes(title_text="Volume", row=5, col=1)
    
    # Remove rangeslider
    fig.update_xaxes(rangeslider_visible=False)
    
    return fig

def display_mega_chart_with_explanations(df, current_price, entry_score, risk_score):
    """Display the mega chart with comprehensive explanations"""
    
    st.markdown("## 📊 ALL-IN-ONE COMPREHENSIVE CHART")
    st.markdown("### Every Indicator on One Screen with Visual Entry/Exit Signals")
    
    if df.empty or len(df) < 20:
        st.warning("Not enough data to display chart")
        return
    
    # Create the mega chart
    fig = create_mega_chart(df, current_price, entry_score, risk_score)
    
    # Display it
    st.plotly_chart(fig, use_container_width=True)
    
    # =====================
    # LEGEND & HOW TO READ
    # =====================
    
    st.markdown("---")
    st.markdown("### 🎯 HOW TO READ THIS CHART")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📊 SECTION 1: PRICE
        
        **Candlesticks:**
        - Green = Up day
        - Red = Down day
        
        **Lines:**
        - Orange dots = 20-day average
        - Blue solid = 50-day trend
        - Gray shading = Bollinger Bands
        - Yellow = Current price
        
        **🟢 Green UP Arrows:**
        - ENTRY signals
        - Entry Score ≥ 6
        - Risk Score ≤ 3
        - **Action: OPEN Iron Condor**
        
        **🔴 Red DOWN Arrows:**
        - EXIT signals
        - Risk Score ≥ 5
        - **Action: CLOSE positions**
        """)
    
    with col2:
        st.markdown("""
        #### 📈 SECTIONS 2-4: MOMENTUM & TREND
        
        **RSI (Purple line):**
        - Green zone (40-60) = OPTIMAL
        - Red zones = AVOID
        - Target: 45-55 for entries
        
        **MACD (Blue/Red lines):**
        - Near zero = WEAK trend (good!)
        - Far from zero = STRONG trend (bad!)
        - Histogram = Trend strength
        
        **ATR % (Red area):**
        - Green zone (<0.8%) = LOW VOL ✅
        - Red zone (>2.0%) = HIGH VOL ❌
        - **Most important for Iron Condors!**
        """)
    
    with col3:
        st.markdown("""
        #### 📊 SECTION 5: VOLUME
        
        **Bar colors:**
        - Green = Up day
        - Red = Down day
        - Blue line = 20-day average
        
        **Good signs:**
        - Volume near average
        - No huge spikes
        
        **Warning signs:**
        - Volume spike (>2x avg)
        - Signals big move coming
        
        **Why it matters:**
        - Confirms price moves
        - Low volume = stable
        - Spikes = breakout risk
        """)
    
    # =====================
    # CURRENT READINGS
    # =====================
    
    st.markdown("---")
    st.markdown("### 📊 CURRENT READINGS")
    
    latest = df.iloc[-1]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        rsi = latest.get('RSI', 50)
        rsi_color = "green" if 40 <= rsi <= 60 else "red"
        st.markdown(f"""
        <div style="background: {rsi_color}22; padding: 15px; border-radius: 10px; border-left: 4px solid {rsi_color};">
            <h4 style="color: {rsi_color}; margin: 0;">RSI</h4>
            <p style="font-size: 24px; margin: 5px 0;">{rsi:.1f}</p>
            <p style="margin: 0;">{'✅ Neutral' if 40 <= rsi <= 60 else '⚠️ Extreme'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        macd = latest.get('MACD', 0)
        macd_strength = abs(macd / current_price * 100)
        macd_color = "green" if macd_strength < 0.5 else "red"
        st.markdown(f"""
        <div style="background: {macd_color}22; padding: 15px; border-radius: 10px; border-left: 4px solid {macd_color};">
            <h4 style="color: {macd_color}; margin: 0;">MACD</h4>
            <p style="font-size: 24px; margin: 5px 0;">{macd:.2f}</p>
            <p style="margin: 0;">{'✅ Weak trend' if macd_strength < 0.5 else '⚠️ Strong trend'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        atr = latest.get('ATR_pct', 1.0)
        atr_color = "green" if atr < 0.8 else ("yellow" if atr < 2.0 else "red")
        st.markdown(f"""
        <div style="background: {atr_color}22; padding: 15px; border-radius: 10px; border-left: 4px solid {atr_color};">
            <h4 style="color: {atr_color}; margin: 0;">ATR %</h4>
            <p style="font-size: 24px; margin: 5px 0;">{atr:.2f}%</p>
            <p style="margin: 0;">{'✅ LOW VOL' if atr < 0.8 else ('OK' if atr < 2.0 else '⚠️ HIGH VOL')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if 'BB_upper' in df.columns:
            bb_pos = (current_price - latest['BB_lower']) / (latest['BB_upper'] - latest['BB_lower'])
            bb_color = "green" if 0.4 <= bb_pos <= 0.6 else "yellow"
            st.markdown(f"""
            <div style="background: {bb_color}22; padding: 15px; border-radius: 10px; border-left: 4px solid {bb_color};">
                <h4 style="color: {bb_color}; margin: 0;">BB Position</h4>
                <p style="font-size: 24px; margin: 5px 0;">{bb_pos*100:.0f}%</p>
                <p style="margin: 0;">{'✅ Centered' if 0.4 <= bb_pos <= 0.6 else '⚠️ Near edge'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        vol = latest.get('Volume', 0)
        avg_vol = df['Volume'].tail(20).mean() if len(df) >= 20 else vol
        vol_ratio = vol / avg_vol if avg_vol > 0 else 1
        vol_color = "green" if vol_ratio < 1.5 else "red"
        st.markdown(f"""
        <div style="background: {vol_color}22; padding: 15px; border-radius: 10px; border-left: 4px solid {vol_color};">
            <h4 style="color: {vol_color}; margin: 0;">Volume</h4>
            <p style="font-size: 24px; margin: 5px 0;">{vol_ratio:.1f}x</p>
            <p style="margin: 0;">{'✅ Normal' if vol_ratio < 1.5 else '⚠️ Elevated'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # =====================
    # OVERALL SIGNAL
    # =====================
    
    st.markdown("---")
    st.markdown("### 🎯 OVERALL IRON CONDOR SIGNAL")
    
    # Calculate score
    score = 0
    signals = []
    
    if 40 <= rsi <= 60:
        score += 1
        signals.append("✅ RSI neutral")
    if macd_strength < 0.5:
        score += 1
        signals.append("✅ Weak trend")
    if atr < 0.8:
        score += 1
        signals.append("✅ Low volatility")
    if 'BB_upper' in df.columns and 0.4 <= bb_pos <= 0.6:
        score += 1
        signals.append("✅ Price centered")
    if vol_ratio < 1.5:
        score += 1
        signals.append("✅ Normal volume")
    
    # Overall assessment
    if score >= 4:
        signal_color = "green"
        signal_text = "🟢 EXCELLENT - STRONG ENTRY"
        action = "✅ Open Iron Condor positions now!"
    elif score >= 3:
        signal_color = "yellow"
        signal_text = "🟡 NEUTRAL - WAIT FOR BETTER"
        action = "⏸️ Monitor for improvement"
    else:
        signal_color = "red"
        signal_text = "🔴 POOR - AVOID"
        action = "❌ Do NOT enter new positions"
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style="background: {signal_color}44; padding: 40px; border-radius: 15px; text-align: center; border: 4px solid {signal_color};">
            <h1 style="color: {signal_color}; margin: 0;">{score}/5</h1>
            <p style="font-size: 18px; margin: 10px 0;">Indicators Green</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: {signal_color}44; padding: 30px; border-radius: 15px; border: 4px solid {signal_color};">
            <h2 style="color: {signal_color}; margin: 0 0 15px 0; text-align: center;">{signal_text}</h2>
            <p style="text-align: center; font-size: 20px; margin: 0 0 15px 0;"><strong>{action}</strong></p>
            <hr style="border-color: {signal_color};">
            <div style="font-size: 16px;">
                {'<br>'.join(signals)}
            </div>
        </div>
        """, unsafe_allow_html=True)
