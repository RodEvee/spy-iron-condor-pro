# 📊 SPY Iron Condor Pro - With Full Greeks

**Professional SPY Iron Condor trading signals with complete options analysis**

## ✨ Features

### 🎯 **Complete Options Analysis**
- ✅ **All 5 Greeks displayed**: Delta, Gamma, Theta, Vega, Rho
- ✅ **15+ Expiration dates** with full options chains
- ✅ **Real-time options pricing** (Tradier API or demo mode)
- ✅ **Implied Volatility (IV)** for every strike
- ✅ **Volume & Open Interest** data

### 📈 **Iron Condor Setups**
Three pre-configured setups optimized for different risk profiles:

1. **CONSERVATIVE (16Δ)** - ~75% probability of profit
2. **BALANCED (20Δ) ⭐ OPTIMAL** - ~70% probability, best risk/reward
3. **AGGRESSIVE (30Δ)** - ~65% probability, higher premium

Each setup shows:
- Short Call & Long Call strikes with full Greeks
- Short Put & Long Put strikes with full Greeks
- Max Profit / Max Loss
- Probability of Profit (POP)
- Risk/Reward ratio
- Breakeven points

### 🎨 **Beautiful Modern UI**
- Gradient cards with shadows
- Color-coded signals (Green=Entry, Red=Exit, Yellow=Neutral)
- Animated optimal setup badge
- Interactive expiration selector
- Hover effects on options chains
- Mobile-responsive design

### 📊 **Technical Analysis**
- RSI (Relative Strength Index)
- Bollinger Bands with width calculation
- MACD (Moving Average Convergence Divergence)
- ATR (Average True Range) for volatility
- Entry Score (0-9): Higher = better entry
- Risk Score (0-9): Lower = safer

### 🔔 **Trading Signals**
- **STRONG ENTRY**: Entry Score ≥6, Risk Score ≤3
- **ENTRY**: Entry Score ≥4, Risk Score ≤4
- **NEUTRAL**: Moderate scores
- **CAUTION**: Risk Score = 5
- **EXIT / AVOID**: Risk Score ≥6

## 🚀 Quick Start

### Option 1: Run Locally (2 minutes)

**Mac/Linux:**
```bash
cd spy-iron-condor-pro
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
cd spy-iron-condor-pro
run.bat
```

**Manual:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

App opens at: **http://localhost:8501**

### Option 2: Deploy to Streamlit Cloud (10 minutes)

1. **Upload to GitHub:**
   - Create public repo: `spy-iron-condor-pro`
   - Upload all files from this folder

2. **Deploy on Streamlit:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repo
   - Main file: `app.py`
   - Deploy

3. **Your app will be live at:**
   `https://your-app-name.streamlit.app`

## 🔑 Optional: Add Real-Time Options Data

**Free Tradier Sandbox API:**
1. Sign up at [developer.tradier.com](https://developer.tradier.com)
2. Get free sandbox API key
3. Enter in app sidebar
4. Enjoy real-time options data with Greeks!

**Without API key:** App uses realistic demo data (still fully functional for learning)

## 📖 How to Use

1. **Check Signal**
   - Green = Enter Iron Condor
   - Red = Exit or avoid
   - Look for Entry Score ≥6, Risk Score ≤3

2. **Select Expiration**
   - Choose 30-45 DTE for best results
   - Click any expiration button to update

3. **Choose Setup**
   - **20Δ OPTIMAL** is recommended (balanced)
   - Expand each setup to see strikes and Greeks
   - All 5 Greeks shown for every leg

4. **Review Greeks**
   - **Delta**: Directional risk (closer to 0 = safer)
   - **Gamma**: Rate of delta change
   - **Theta**: Daily time decay (your friend!)
   - **Vega**: Volatility sensitivity
   - **Rho**: Interest rate sensitivity

5. **View Full Chain**
   - Scroll down for complete options chain
   - All strikes with all Greeks
   - Filter around current SPY price

6. **Execute Trade**
   - Use your broker (TD Ameritrade, IBKR, etc.)
   - Enter suggested strikes
   - Monitor with app daily

## 📊 Strategy Guide

### Best Entry Conditions
- ✅ Low volatility (ATR < 1%)
- ✅ RSI between 40-60
- ✅ Price in middle of Bollinger Bands
- ✅ Weak trend (low MACD)
- ✅ Entry Score ≥ 6
- ✅ Risk Score ≤ 3

### When to Exit
- ❌ Volatility spike (ATR > 2%)
- ❌ Strong directional move
- ❌ RSI extremes (<30 or >70)
- ❌ Price near short strikes
- ❌ Risk Score ≥ 5
- ✅ 50% profit reached (recommended)
- ✅ 21 DTE or less

### Delta Selection
- **16Δ**: Most conservative, ~75% win rate
- **20Δ**: Best balance, ~70% win rate ⭐
- **30Δ**: Higher premium, ~65% win rate

## 🎓 Understanding the Greeks

### Delta (Δ)
- **What it means**: How much option price changes per $1 move in SPY
- **For Iron Condor**: Lower delta = further from current price = safer
- **Target**: 0.16 to 0.30 for short strikes

### Gamma (Γ)
- **What it means**: How fast delta changes
- **For Iron Condor**: Lower gamma = more stable position
- **Watch**: Gamma increases near expiration

### Theta (Θ)
- **What it means**: Daily time decay (profit for sellers!)
- **For Iron Condor**: Positive theta = you earn money daily
- **Best**: Higher theta = faster profit

### Vega (V)
- **What it means**: Sensitivity to volatility changes
- **For Iron Condor**: Negative vega = you profit when IV drops
- **Risk**: IV spike can hurt your position

### Rho (ρ)
- **What it means**: Sensitivity to interest rate changes
- **For Iron Condor**: Usually minimal impact
- **Note**: More relevant for longer-dated options

## 📱 Features by Section

### Top Metrics Bar
- SPY current price with % change
- Entry Score (0-9)
- Risk Score (0-9)
- Current RSI
- Current Volatility (ATR %)

### Signal Box
- Large, color-coded trading signal
- STRONG ENTRY / ENTRY / NEUTRAL / CAUTION / EXIT

### Expiration Selector
- 15 expiration dates
- Days to expiration shown
- Click to switch between expirations

### Iron Condor Setups (3 cards)
Each setup shows:
- Setup name and description
- Call spread (Short + Long) with Greeks
- Put spread (Short + Long) with Greeks
- Max Profit, Max Loss, POP, Risk/Reward
- Breakeven points

### Full Options Chain
- All strikes around current price
- Calls and Puts
- Complete Greeks for every strike
- IV, Volume, Open Interest
- Sortable and scrollable

## 🛠️ Customization

Edit `app.py` to customize:
- Delta targets (line ~350): Change 0.16, 0.20, 0.30
- Entry/Risk score thresholds (line ~180-230)
- RSI ranges (line ~189)
- Volatility thresholds (line ~207)
- Number of expirations shown (line ~124)

## ⚠️ Important Notes

- **Not Financial Advice**: Educational tool only
- **Paper Trade First**: Test with fake money
- **Risk Management**: Never risk more than 5% per trade
- **Max Positions**: Keep 2-3 Iron Condors open max
- **Track Results**: Log every trade
- **Real Data**: Add Tradier API for production use

## 📊 System Requirements

- Python 3.8+
- Internet connection (for data)
- Modern browser (Chrome, Firefox, Safari, Edge)

## 🆘 Troubleshooting

**App won't start:**
```bash
pip install --upgrade streamlit yfinance pandas numpy plotly
```

**No options data:**
- Add Tradier API key in sidebar
- Or use demo mode (works offline)

**Slow performance:**
- Close other apps
- Use Daily timeframe
- Disable auto-refresh

**GitHub upload issues:**
- Show hidden files (Command+Shift+. on Mac)
- Ensure `.streamlit/config.toml` is included
- Check file structure matches README

## 📈 Version History

- **v2.0** (Current)
  - ✅ All 5 Greeks displayed
  - ✅ 15+ expirations
  - ✅ Beautiful modern UI
  - ✅ Full options chains
  - ✅ 16Δ/20Δ/30Δ setups
  - ✅ Tradier API integration
  - ✅ Probability of Profit

- **v1.0**
  - Basic signals
  - Strike suggestions
  - Yahoo Finance data

## 📞 Support

- **Issues**: Check troubleshooting section
- **Feature requests**: Let me know!
- **Questions**: Review Strategy Guide

## 📄 License

MIT License - Free to use and modify

---

**Built with ❤️ for SPY Iron Condor traders**

**Remember**: Practice with paper trading first. Trade responsibly. 🚀
