# 📊 Bond Trading Terminal v2

A professional **SDL & G-Sec Trading Intelligence Platform** — maturity-matched spread analysis, FIBIL pricing, AI signals, price calculator, and comparative analytics.

---

## 🚀 Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub  
2. Go to [share.streamlit.io](https://share.streamlit.io)  
3. New app → select repo → `app.py` → Deploy ✅

---

## ✨ Features (v2)

| Tab | What it does |
|---|---|
| 🏆 **Top Picks** | Top 5 Best Value · Top 5 Highest Yield · Top 5 Discounted+Yield · Widest Spread chart |
| 🔍 **Full Screener** | All bonds with maturity-matched spread, FIBIL gap, signals, color coding |
| 📈 **Charts** | Yield curve (state-wise) · Opportunity map · Spread histogram · Price vs FIBIL chart |
| 🧮 **Price Calculator** | Exact DCF price from yield · Yield from price · DV01 sensitivity table |
| 🔬 **Single Bond Analyzer** | Deep-dive + **comparative analysis** of all same-maturity bonds across states |
| 📤 **Export** | Download as CSV or Excel |
| ❓ **How It Works** | Scoring methodology + dealer tips |

---

## 🧠 Key Upgrade: Maturity-Matched G-Sec

> Every SDL is now compared against the G-Sec of the **same maturity year**, not a common 10Y benchmark.

**You need 2 sheets in your Excel:**

### Sheet 1: `BONDS`
| Column | Required? | Notes |
|--------|-----------|-------|
| SECURITY NAME | ✅ | e.g. "MH SDL 2034" |
| MATURITY | ✅ | e.g. 2034 |
| YTM (%) | ✅ | Current yield |
| LAST CUT-OFF (%) | ✅ | Last auction yield |
| COUPON (%) | Recommended | For price calculation |
| PRICE | Recommended | Market price |
| FIBIL YIELD (%) | Recommended | FIBIL fair yield |
| STATE | Optional | For risk scoring |
| LIQUIDITY | Optional | High / Medium / Low |
| VOLUME (Cr) | Optional | Trading volume |
| ISIN | Optional | Reference |

### Sheet 2: `GSEC_CURVE`
| MATURITY | GSEC YIELD (%) |
|----------|----------------|
| 2029 | 6.90 |
| 2030 | 6.95 |
| 2034 | 7.10 |
| 2035 | 7.13 |

---

## 🖥️ Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/bond-ai-screener.git
cd bond-ai-screener
pip install -r requirements.txt
streamlit run app.py
```

---

## ⚠️ Disclaimer

For professional reference only. Not financial advice.
