# 📊 QUICK REFERENCE - SPY Iron Condor Pro

## ⚡ 60-Second Quick Start

### Run Locally
```bash
cd spy-iron-condor-pro
./run.sh  # Mac/Linux
run.bat   # Windows
```
→ Opens at **http://localhost:8501**

### Deploy Online
1. Upload to GitHub (public repo)
2. Deploy on **share.streamlit.io**
3. Main file: **app.py**

---

## 🎯 Reading the App (30 seconds)

### Top Bar (5 Metrics)
| Metric | Good | Bad |
|--------|------|-----|
| **Entry Score** | ≥6/9 | ≤4/9 |
| **Risk Score** | ≤3/9 | ≥5/9 |
| **RSI** | 40-60 | <30 or >70 |
| **Volatility** | <1% | >2% |

### Signal Box
- 🟢 **Green** = Enter
- 🟡 **Yellow** = Wait
- 🔴 **Red** = Exit

---

## 📋 The 3 Setups

| Setup | Delta | Win Rate | Premium | Risk |
|-------|-------|----------|---------|------|
| **Conservative** | 16Δ | ~75% | Low | Lowest |
| **Balanced ⭐** | 20Δ | ~70% | Medium | Medium |
| **Aggressive** | 30Δ | ~65% | High | Higher |

**Recommendation**: Start with **Balanced (20Δ)**

---

## 🎓 Greeks Cheat Sheet

| Greek | What It Means | What You Want |
|-------|---------------|---------------|
| **Delta (Δ)** | Directional risk | Low (0.16-0.30) |
| **Gamma (Γ)** | Delta change rate | Low & stable |
| **Theta (Θ)** | Daily profit | High (negative #) |
| **Vega (V)** | IV sensitivity | Low |
| **Rho (ρ)** | Rate impact | Ignore (minimal) |

---

## 📅 Expiration Guide

| DTE | Type | Best For |
|-----|------|----------|
| **30-45** | Monthly | ⭐ Optimal |
| **21-30** | Weekly | Active traders |
| **14-21** | Weekly | High risk |
| **<14** | Short-term | Avoid |

**Exit at 21 DTE** regardless of P&L

---

## 🎯 Entry Rules (Checklist)

- ✅ Entry Score ≥ 6
- ✅ Risk Score ≤ 3
- ✅ RSI 40-60
- ✅ ATR < 1%
- ✅ 30-45 DTE
- ✅ Green signal

**All must be true!**

---

## 🚪 Exit Rules (Any One)

- ✅ 50% profit reached
- ✅ Risk Score ≥ 5
- ✅ 21 DTE
- ✅ 2x max loss
- ✅ Red signal

**Exit immediately!**

---

## 💰 Position Sizing

| Account Size | Max Per Trade | Max Open Positions |
|--------------|---------------|-------------------|
| $5,000 | $250 (5%) | 1-2 |
| $10,000 | $500 (5%) | 2-3 |
| $25,000 | $1,250 (5%) | 3-4 |
| $50,000+ | $2,500 (5%) | 4-5 |

**Never exceed 5% per trade!**

---

## 📊 Example Trade

### Setup: Balanced (20Δ), 35 DTE

**Market Conditions:**
- SPY: $580
- Entry Score: 7/9 ✅
- Risk Score: 2/9 ✅
- Signal: STRONG ENTRY 🟢

**Strikes Selected:**
- Short Call: $595 (Δ 0.20)
- Long Call: $600 (Δ 0.14)
- Short Put: $565 (Δ -0.20)
- Long Put: $560 (Δ -0.14)

**P&L:**
- Max Profit: $200
- Max Loss: $300
- POP: 70%
- Breakevens: $563/$597

**Exit Plan:**
- Take profit @ $100 (50%)
- Stop loss @ $600
- Time stop @ 21 DTE
- Monitor Risk Score daily

---

## 🔑 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Refresh data | `R` |
| Expand all | `E` |
| Scroll to top | `Home` |
| Open sidebar | `S` |

---

## 🛠️ Troubleshooting (30 seconds)

| Problem | Solution |
|---------|----------|
| App won't start | `pip install -r requirements.txt` |
| No data | Use demo mode (works offline) |
| Slow performance | Use Daily timeframe |
| GitHub upload fail | Show hidden files (Cmd+Shift+.) |
| Streamlit error | Check main file is `app.py` |

---

## 📱 Files You Need

### Essential (3 files)
1. ✅ app.py
2. ✅ requirements.txt
3. ✅ .streamlit/config.toml

### Documentation (5 files)
4. START_HERE.md
5. DEPLOYMENT_GUIDE.md
6. README.md
7. PACKAGE_SUMMARY.md
8. QUICK_REFERENCE.md (this file)

### Optional (2 files)
9. run.sh
10. run.bat

---

## ⚠️ Remember

### Do's ✅
- Paper trade first
- Start with 1 contract
- Follow your rules
- Log every trade
- Exit at 50% profit

### Don'ts ❌
- Don't over-leverage
- Don't skip stops
- Don't trade on tilt
- Don't hold to expiration
- Don't ignore Risk Score

---

## 🎯 Daily Workflow

### Morning (2 min)
1. Open app
2. Check Entry/Risk scores
3. Review existing positions

### Midday (1 min)
1. Check Risk Score
2. Monitor for spikes

### Evening (2 min)
1. Review P&L
2. Plan tomorrow
3. Update journal

---

## 📈 Monthly Goals

| Month | Goal |
|-------|------|
| **1** | 10+ paper trades |
| **2** | Go live with 1 contract |
| **3** | 5-10% profit |
| **4+** | 10-20% profit |

**Be patient. Build slowly.**

---

## 🔗 Important Links

- **Tradier API**: https://developer.tradier.com
- **Streamlit Cloud**: https://share.streamlit.io
- **GitHub**: https://github.com

---

## 📞 Quick Help

**Can't figure something out?**

1. Read **START_HERE.md**
2. Check **DEPLOYMENT_GUIDE.md**
3. Review **README.md**

---

**Print this page and keep it next to your monitor! 📄**

**Version 2.0 | January 2026**
