# 📊 Bond AI Screener

A professional **SDL & G-Sec Intelligence Platform** built with Streamlit. Instantly screen Indian government bonds using dealer-grade spread analysis and AI-powered buy/sell signals.

---

## 🚀 Live Demo

Deploy instantly on [Streamlit Cloud](https://streamlit.io/cloud) — free, no server needed.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Bond Screener** | Multi-factor scoring table with color-coded signals |
| 📈 **Charts** | Spread histogram, signal pie chart, YTM scatter map, yield curve |
| 🧮 **Single Bond Analyzer** | Enter any bond manually and get instant deep-dive analysis |
| 📤 **Export** | Download results as CSV or Excel |
| ❓ **Methodology** | Full explanation of the scoring model and pro tips |

---

## 📐 Scoring Model

Each bond is scored out of 8 points across 4 factors:

### 1. Spread vs Benchmark G-Sec
| Spread | Score | Status |
|--------|-------|--------|
| ≥ 70 bps | +3 | Very Cheap 🟢 |
| 50–70 bps | +2 | Attractive 🔵 |
| 40–50 bps | +1 | Normal 🟡 |
| < 40 bps | -1 | Expensive 🔴 |

### 2. Delta vs Last Auction Cut-off
| Condition | Score |
|-----------|-------|
| YTM > Cut-off | +2 (bond is cheaper now) |
| YTM = Cut-off | 0 |
| YTM < Cut-off | -1 (more expensive) |

### 3. Liquidity
| Liquidity | Score |
|-----------|-------|
| High | +2 |
| Medium | +1 |
| Low | -1 |

### 4. State Risk
| State Type | Score |
|------------|-------|
| Strong fiscal (MH, GJ, KA, TN) | +1 |
| High risk (AP, PB, RJ, HP) | -1 |

### Signal Thresholds
| Score | Signal |
|-------|--------|
| 6–8 | 🟢 STRONG BUY |
| 4–5 | 🔵 BUY |
| 2–3 | 🟡 WATCH |
| 0–1 | ⚪ HOLD |
| < 0 | 🔴 AVOID |

---

## 📁 Excel Upload Format

Your Excel file **must** have these columns (exact names):

```
YTM (%)
G-SEC YIELD (%)
LAST CUT-OFF (%)
```

Optional columns (add for richer analysis):
```
ISIN
SECURITY NAME
STATE
MATURITY
LIQUIDITY       ← values: High / Medium / Low
FACE VALUE
```

Run `python generate_sample.py` to create a ready-to-use template.

---

## 🖥️ Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/bond-ai-screener.git
cd bond-ai-screener
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → Select your repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** ✅

---

## 📖 How to Read the Screener

> **"Good level = High spread + Better than last auction + Good liquidity"**

- **Spread** tells you how cheap/expensive vs central govt bonds
- **Delta** tells you if it's cheaper or costlier than where it was issued
- **Liquidity** tells you if you can actually exit the trade
- **State** tells you the credit risk premium you're taking

---

## ⚠️ Disclaimer

This tool is for **professional reference only** and does not constitute financial advice. Always do your own due diligence before trading.

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io) — UI framework
- [Pandas](https://pandas.pydata.org) — Data processing
- [Plotly](https://plotly.com) — Interactive charts
- [OpenPyXL](https://openpyxl.readthedocs.io) — Excel support
