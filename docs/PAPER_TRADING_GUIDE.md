# 📈 PAPER TRADING GUIDE - SPY Iron Condor Pro

## 🎯 What is Paper Trading?

Paper trading lets you **test Iron Condor strategies with VIRTUAL MONEY** - no risk, all learning!

- **Starting Balance:** $10,000 virtual cash
- **Real Market Data:** Uses actual SPY options prices from Yahoo Finance
- **Full P&L Tracking:** See exactly how your trades perform
- **Portfolio Management:** Open, monitor, and close positions just like real trading
- **Performance Analytics:** Win rate, ROI, equity curve, and more

---

## 🚀 Quick Start (3 Steps)

### Step 1: Enable Paper Trading
1. Open your SPY Iron Condor Pro app
2. Look at the **Sidebar** (left side)
3. Find **"📈 Paper Trading"** section
4. **Check the box**: "Enable Paper Trading"

### Step 2: Open Your First Position
1. Scroll down to **"🎯 Iron Condor Strike Recommendations"**
2. Choose a setup:
   - **CONSERVATIVE** (16Δ) - Safest, ~75% win rate
   - **BALANCED** (20Δ) - Optimal risk/reward, ~70% win rate ⭐ RECOMMENDED
   - **AGGRESSIVE** (30Δ) - Higher premiums, ~65% win rate
3. Click **"🚀 Open Position"** button
4. Select number of contracts (start with 1)
5. Add notes (optional)
6. Click **"🚀 Open Position"** again to confirm
7. 🎉 **You're in!** Position is now active

### Step 3: Monitor & Close
1. Click **"📊 View Full Dashboard"** in sidebar
2. See all open positions with live P&L
3. When ready to close:
   - Click **"Close Position #X"**
   - Enter closing price (or use suggested)
   - Click **"✅ Confirm"**
4. Position closed! P&L added to account

---

## 📊 Dashboard Features

### Account Overview (Top Metrics)
- **Account Value:** Total portfolio value
- **Available Cash:** Cash available for new trades
- **ROI:** Return on investment percentage
- **Win Rate:** Percentage of winning trades
- **Open Positions:** Number of active trades

### Tabs

#### 📊 Open Positions
- See all active Iron Condor positions
- Real-time P&L updates
- Detailed strike information
- One-click close functionality
- Current SPY price vs entry price

#### 📝 Trade History
- Complete record of closed positions
- Entry/exit dates and prices
- P&L for each trade
- Win/loss statistics
- Downloadable CSV export

#### 📈 Performance
- **Equity Curve:** Visual chart of account growth
- **Trade P&L Chart:** Individual trade results
- **Starting Balance Line:** Reference point

#### ⚙️ Settings
- Reset account (start fresh with $10,000)
- Export trading history
- Account statistics

---

## 💡 How to Use Paper Trading Effectively

### For Beginners (Learning Mode)
1. **Start with Demo Mode** to understand the interface
2. **Switch to Yahoo Finance** for real market data
3. **Enable Paper Trading**
4. **Open 1 contract** of BALANCED (20Δ) setup
5. **Watch for 1-3 days** to see how P&L changes with SPY movement
6. **Close at 50% profit** or when Risk Score ≥ 5
7. **Repeat 10 times** before considering real money

### For Practice Trading (Test Strategies)
1. **Use real signals** from the Entry/Risk Score
2. **Only enter** when Entry Score ≥ 6 and Risk ≤ 3
3. **Follow exit rules:**
   - 50% profit target (close early!)
   - Risk Score ≥ 5 (exit immediately)
   - 21 DTE or less (roll or close)
   - Volatility spike (ATR > 2%)
4. **Track your results** for 20-30 trades
5. **Calculate your win rate** (aim for 65%+)
6. **If consistent wins**, consider real trading

### For Strategy Testing (Advanced)
1. **Test different setups:**
   - Week 1: Only CONSERVATIVE (16Δ)
   - Week 2: Only BALANCED (20Δ)
   - Week 3: Only AGGRESSIVE (30Δ)
2. **Compare results:**
   - Which has best win rate?
   - Which has best ROI?
   - Which feels most comfortable?
3. **Test entry timing:**
   - Entry Score = 6 vs 7 vs 8
   - Different RSI levels (45-50 vs 40-60)
   - Low volatility (ATR < 0.8%) vs medium (0.8-1.2%)
4. **Test exit strategies:**
   - 30% profit vs 50% vs 70%
   - Risk Score 4 vs 5 vs 6
   - Different DTE thresholds (21 vs 14 vs 7)

---

## 📋 Step-by-Step Example Trade

### Opening the Trade

**Scenario:** Entry Score is 8/9, Risk Score is 2/9

1. **Check the Setup**
   ```
   SPY Price: $580.00
   Selected Expiration: 2026-02-28 (28 days)
   Setup: BALANCED (20Δ)
   ```

2. **Review the Strikes**
   ```
   CALL SPREAD:
   - Short Call: $595 (Sell) - Delta 0.20, $2.50
   - Long Call: $600 (Buy) - Delta 0.12, $1.00
   - Credit: $1.50

   PUT SPREAD:
   - Short Put: $565 (Sell) - Delta -0.20, $2.40
   - Long Put: $560 (Buy) - Delta -0.12, $0.90
   - Credit: $1.50

   Total Credit: $3.00 ($300 per contract)
   Max Profit: $300
   Max Loss: $200
   ```

3. **Open Position**
   - Contracts: 1
   - Notes: "Entry 8/9, RSI 52, ATR 0.7%"
   - Click "🚀 Open Position"
   - ✅ Position #1 opened!

4. **Check Dashboard**
   ```
   Account Value: $10,300 (credit received)
   Cash: $9,800 (margin held)
   Open Positions: 1
   ```

### Monitoring the Trade

**Day 1-3:** SPY stays at $580-$582
- P&L: +$50 to +$100
- Status: Good! Theta decay working in your favor

**Day 4-7:** SPY moves to $575
- P&L: +$30 (closer to put side, but still profitable)
- Risk Score: 3/9 (still OK)
- Action: Hold

**Day 8:** SPY at $580
- P&L: +$150 (50% of max profit!)
- Entry Score: 7/9 (still good)
- **Action: CLOSE for 50% profit** ✅

### Closing the Trade

1. **Click "Close Position #1"**
2. **Closing Cost:** $150 (to buy back spreads)
3. **Confirm close**
4. **Final P&L:** +$150 (50% profit)
5. **New Account Value:** $10,150

**Result:**
- Win! 50% profit in 8 days
- ROI: +1.5% on account
- Win Rate: 100% (1/1)

---

## 🎓 Learning Checkpoints

### After 5 Trades
- [ ] Can you open a position without help?
- [ ] Do you understand the P&L calculation?
- [ ] Can you identify good entry signals?
- [ ] Do you know when to close?

### After 10 Trades
- [ ] Win rate above 50%?
- [ ] Positive total P&L?
- [ ] Following the exit rules consistently?
- [ ] Comfortable with the process?

### After 20 Trades
- [ ] Win rate above 65%?
- [ ] ROI positive?
- [ ] Understanding which setups work best?
- [ ] Ready for real trading? (if yes, start with 1 contract)

---

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T:
- **Trade without signals:** Only enter when Entry ≥ 6
- **Hold winners too long:** Take 50% profit, don't be greedy
- **Ignore risk signals:** Exit when Risk ≥ 5
- **Overtrade:** Quality over quantity
- **Skip the learning:** Paper trade 20+ times first
- **Trade too large:** Start with 1 contract
- **Ignore stops:** Close losing trades at max loss
- **Trade near earnings:** Check SPY earnings dates

### ✅ DO:
- **Use the signals:** Entry and Risk Scores are your guide
- **Take profits early:** 50% is excellent!
- **Close bad trades:** Don't hope for recovery
- **Track your results:** Learn from every trade
- **Be patient:** Wait for good setups
- **Start small:** 1 contract until consistent
- **Use stop losses:** Know your max loss
- **Check expiration:** Close or roll at 21 DTE

---

## 📊 Performance Tracking

### Key Metrics to Track
- **Win Rate:** % of profitable trades (target: 65%+)
- **Average Win:** Average profit per winning trade
- **Average Loss:** Average loss per losing trade
- **Profit Factor:** Total wins / Total losses (target: 1.5+)
- **ROI:** % return on starting capital
- **Max Drawdown:** Largest peak-to-valley loss

### How to Review Your Trading
1. **Export your trade history** (Settings tab)
2. **Calculate metrics** in Excel/Google Sheets
3. **Look for patterns:**
   - Which setups win most?
   - What entry scores work best?
   - When do you close winners?
   - When do you close losers?
4. **Adjust your strategy** based on data

---

## 🚀 Graduating to Real Trading

### Before You Go Live
- [ ] 20+ paper trades completed
- [ ] Win rate consistently 65%+
- [ ] Positive ROI for last 10 trades
- [ ] Can identify good setups quickly
- [ ] Follow rules consistently
- [ ] Understand all Greeks
- [ ] Comfortable with risk management
- [ ] Emotionally ready for real money

### Your First Real Trade
1. **Start with 1 contract** (not more!)
2. **Use the BALANCED (20Δ) setup**
3. **Only enter when Entry ≥ 7, Risk ≤ 3**
4. **Set alerts** for Risk Score changes
5. **Take 50% profit** (no exceptions!)
6. **Review after 3 days**
7. **Wait 1 week** before next trade

### Scaling Up
- After 5 winning trades: Try 2 contracts
- After 10 winning trades: Try different setups
- After 20 winning trades: Consider 3-5 contracts
- **Never risk more than 5% of account** on one trade

---

## 💻 Technical Details

### Position Calculations
```
Credit Received = Call Credit + Put Credit
Max Profit = Credit Received × 100 × Contracts
Max Loss = (Strike Width × 100 × Contracts) - Credit Received
Margin Required = Max Loss
Breakeven Upper = Short Call Strike + (Credit / 100)
Breakeven Lower = Short Put Strike - (Credit / 100)
```

### P&L Updates
- P&L updates when you view the dashboard
- Based on current bid/ask spreads
- Uses real-time Yahoo Finance data
- Reflects time decay (theta) and price movement

### Account Management
- Starting capital: $10,000
- Margin held per position: Max Loss amount
- Available cash = Total Cash - Sum of Margins
- Account Value = Cash + Unrealized P&L

---

## 🔧 Troubleshooting

### "Insufficient Cash" Error
- **Cause:** Not enough cash for margin
- **Solution:** Close open positions or reset account

### P&L Not Updating
- **Cause:** Market closed or data delay
- **Solution:** Refresh page or wait for market hours

### Can't Open Position
- **Cause:** Paper trading not enabled
- **Solution:** Check "Enable Paper Trading" in sidebar

### Lost Positions
- **Cause:** App refreshed
- **Solution:** Positions are saved in session; check dashboard

---

## 📚 Additional Resources

### In the App
- **START_HERE.md:** Complete app guide
- **QUICK_REFERENCE.md:** Quick tips
- **DEPLOYMENT_GUIDE.md:** Setup instructions

### Recommended Learning
1. **Iron Condor Strategy:** Tastytrade, projectoption
2. **Options Greeks:** Khan Academy, Investopedia
3. **Risk Management:** Options Alpha podcast
4. **SPY Trading:** SPY ETF options strategies

---

## 🎯 Summary

Paper trading is your **RISK-FREE TRAINING GROUND**:

1. **Enable paper trading** in sidebar
2. **Open positions** from the recommended setups
3. **Monitor in dashboard** with real-time P&L
4. **Close for profit** or when risk increases
5. **Track your performance** over 20+ trades
6. **Learn and improve** before risking real money

**Remember:** The goal is not to make paper money - it's to **build skills, test strategies, and gain confidence** for real trading!

---

## 📞 Need Help?

- **Check the Dashboard:** Most answers are in the UI
- **Review Docs:** START_HERE.md and QUICK_REFERENCE.md
- **Test in Demo Mode:** Safe environment to experiment
- **Track Your Trades:** Learn from the data

---

**Good luck with your paper trading! 🚀📈**

*Remember: Paper trading is practice, but treat it like real money. The habits you build here will carry over to live trading.*
