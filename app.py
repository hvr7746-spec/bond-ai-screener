import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io
import math

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bond Trading Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0a0e1a; color: #e2e8f0; }

.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #1e3a5f; border-radius: 12px;
    padding: 24px 32px; margin-bottom: 24px;
}
.main-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
}
.main-subtitle { color: #64748b; font-size: 0.9rem; margin-top: 4px; font-family: 'DM Mono', monospace; }

.metric-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 10px; padding: 16px 20px; text-align: center;
}
.metric-value { font-size: 1.8rem; font-weight: 700; font-family: 'DM Mono', monospace; }
.metric-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

.top5-card {
    background: #0f172a; border: 1px solid #1e293b; border-radius: 10px;
    padding: 18px; margin-bottom: 8px;
}
.top5-rank { font-size: 1.4rem; font-weight: 800; font-family: 'DM Mono', monospace; color: #334155; }
.top5-name { font-size: 0.95rem; font-weight: 600; color: #e2e8f0; }
.top5-detail { font-size: 0.78rem; color: #64748b; font-family: 'DM Mono', monospace; margin-top: 3px; }
.top5-badge { float: right; font-size: 0.8rem; font-weight: 700; font-family: 'DM Mono', monospace; }

.section-header {
    font-size: 1rem; font-weight: 600; color: #94a3b8;
    border-bottom: 1px solid #1e293b; padding-bottom: 8px; margin-bottom: 16px;
    text-transform: uppercase; letter-spacing: 1px; font-family: 'DM Mono', monospace;
}
.insight-box {
    background: #0f172a; border-left: 3px solid #38bdf8;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 8px 0;
    font-size: 0.88rem; color: #cbd5e1;
}
.comp-row {
    background: #0f172a; border: 1px solid #1e293b; border-radius: 8px;
    padding: 12px 16px; margin: 6px 0; display: flex; justify-content: space-between; align-items: center;
}
.calc-result {
    background: linear-gradient(135deg, #0c1a2e, #0f2744);
    border: 1px solid #1d4ed8; border-radius: 12px;
    padding: 24px; text-align: center; margin-top: 16px;
}
.calc-price { font-size: 2.5rem; font-weight: 800; font-family: 'DM Mono', monospace; color: #38bdf8; }
.calc-label { color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }

.banner-good { background: #052e16; border: 1px solid #16a34a; color: #4ade80; border-radius: 8px; padding: 12px 18px; }
.banner-avg  { background: #1c1400; border: 1px solid #d97706; color: #fbbf24; border-radius: 8px; padding: 12px 18px; }
.banner-bad  { background: #450a0a; border: 1px solid #dc2626; color: #f87171; border-radius: 8px; padding: 12px 18px; }

.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #4f46e5); color: white;
    border: none; border-radius: 8px; font-weight: 600; transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(79,70,229,0.4); }

div[data-testid="stSidebar"] { background: #0a0e1a; border-right: 1px solid #1e293b; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
HIGH_RISK_STATES = ["Andhra Pradesh", "Punjab", "Rajasthan", "Himachal Pradesh"]
LOW_RISK_STATES  = ["Maharashtra", "Gujarat", "Karnataka", "Tamil Nadu"]

# ─── SAMPLE DATA ──────────────────────────────────────────────────────────────
SAMPLE_BONDS = {
    "ISIN":             ["IN0020220128","IN0020210079","IN0020220201","IN0020200045","IN0020230044",
                         "IN0020210152","IN0020220315","IN0020200118","IN0020230117","IN0020210225",
                         "IN0020220401","IN0020210310","IN0020230201"],
    "SECURITY NAME":    ["MH SDL 2034","GJ SDL 2033","AP SDL 2030","PB SDL 2032","KA SDL 2035",
                         "TN SDL 2031","UP SDL 2033","RJ SDL 2034","MH SDL 2029","GJ SDL 2036",
                         "AP SDL 2034","KA SDL 2032","TN SDL 2033"],
    "STATE":            ["Maharashtra","Gujarat","Andhra Pradesh","Punjab","Karnataka",
                         "Tamil Nadu","Uttar Pradesh","Rajasthan","Maharashtra","Gujarat",
                         "Andhra Pradesh","Karnataka","Tamil Nadu"],
    "MATURITY":         [2034,2033,2030,2032,2035,2031,2033,2034,2029,2036,2034,2032,2033],
    "COUPON (%)":       [7.48,7.42,7.65,7.72,7.55,7.44,7.60,7.75,7.38,7.50,7.80,7.58,7.45],
    "YTM (%)":          [7.64,7.58,7.89,7.95,7.72,7.61,7.81,7.92,7.52,7.61,7.88,7.78,7.60],
    "PRICE":            [99.12,99.45,98.10,97.85,98.75,99.32,98.42,97.92,99.68,99.21,98.25,98.55,99.38],
    "LAST CUT-OFF (%)": [7.58,7.55,7.82,7.88,7.68,7.57,7.75,7.85,7.49,7.57,7.80,7.70,7.56],
    "FIBIL YIELD (%)":  [7.60,7.54,7.85,7.90,7.69,7.58,7.78,7.88,7.50,7.58,7.84,7.75,7.57],
    "LIQUIDITY":        ["High","High","Low","Low","Medium","Medium","Low","Low","High","High","Low","Medium","High"],
    "VOLUME (Cr)":      [250,310,80,60,150,120,70,55,280,260,65,130,200],
}

SAMPLE_GSEC = {
    "MATURITY": [2026,2027,2028,2029,2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040],
    "GSEC YIELD (%)": [6.72,6.78,6.84,6.90,6.95,7.00,7.04,7.08,7.10,7.13,7.15,7.17,7.19,7.21,7.23],
}

# ─── CORE FUNCTIONS ───────────────────────────────────────────────────────────
def bond_price_full(coupon_pct, ytm_pct, years, face=100, freq=2):
    """Full DCF bond price calculation (semi-annual coupons)."""
    if ytm_pct <= 0 or years <= 0:
        return face
    c = (coupon_pct / 100) * face / freq
    r = (ytm_pct / 100) / freq
    n = int(years * freq)
    if r == 0:
        return c * n + face
    pv_coupons = c * (1 - (1 + r) ** -n) / r
    pv_face    = face / (1 + r) ** n
    return round(pv_coupons + pv_face, 4)

def bond_price_approx(coupon_pct, ytm_pct, years, face=100):
    """Approximation formula for quick display."""
    return round(face + (coupon_pct - ytm_pct) * years * 0.92, 2)

def fibil_price(coupon_pct, fibil_yield_pct, years, face=100):
    return bond_price_full(coupon_pct, fibil_yield_pct, years, face)

def compute_signals(df: pd.DataFrame, gsec_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    current_year = datetime.now().year

    # Merge with maturity-matched G-sec
    df = df.merge(gsec_df.rename(columns={"GSEC YIELD (%)": "GSEC YIELD (%)"}),
                  on="MATURITY", how="left")

    # If no match, fill with a default
    df["GSEC YIELD (%)"] = df["GSEC YIELD (%)"].fillna(df.get("G-SEC YIELD (%)", 7.10))

    # Years to maturity
    df["YEARS TO MAT"] = df["MATURITY"] - current_year
    df["YEARS TO MAT"] = df["YEARS TO MAT"].clip(lower=0.5)

    # Spread vs maturity-matched G-sec
    df["SPREAD (bps)"] = ((df["YTM (%)"] - df["GSEC YIELD (%)"]) * 100).round(1)
    df["DELTA (bps)"]  = ((df["YTM (%)"] - df["LAST CUT-OFF (%)"]) * 100).round(1)

    # FIBIL price and market price gap
    if "FIBIL YIELD (%)" in df.columns and "COUPON (%)" in df.columns:
        df["FIBIL PRICE"]   = df.apply(lambda r: round(fibil_price(r["COUPON (%)"], r["FIBIL YIELD (%)"], r["YEARS TO MAT"]), 2), axis=1)
        df["MARKET PRICE"]  = df.get("PRICE", 100)
        df["PRICE vs FIBIL"]= (df["MARKET PRICE"] - df["FIBIL PRICE"]).round(2)
    else:
        df["FIBIL PRICE"]   = 100.0
        df["MARKET PRICE"]  = df.get("PRICE", 100)
        df["PRICE vs FIBIL"]= 0.0

    # Score
    df["SCORE"] = 0
    df.loc[df["SPREAD (bps)"] >= 70, "SCORE"] += 3
    df.loc[(df["SPREAD (bps)"] >= 50) & (df["SPREAD (bps)"] < 70), "SCORE"] += 2
    df.loc[(df["SPREAD (bps)"] >= 40) & (df["SPREAD (bps)"] < 50), "SCORE"] += 1
    df.loc[df["SPREAD (bps)"] < 40, "SCORE"] -= 1

    df.loc[df["DELTA (bps)"] > 5,  "SCORE"] += 2
    df.loc[(df["DELTA (bps)"] >= 0) & (df["DELTA (bps)"] <= 5), "SCORE"] += 1
    df.loc[df["DELTA (bps)"] < 0,  "SCORE"] -= 1

    if "LIQUIDITY" in df.columns:
        df.loc[df["LIQUIDITY"] == "High",   "SCORE"] += 2
        df.loc[df["LIQUIDITY"] == "Medium", "SCORE"] += 1
        df.loc[df["LIQUIDITY"] == "Low",    "SCORE"] -= 1

    if "STATE" in df.columns:
        df.loc[df["STATE"].isin(LOW_RISK_STATES),  "SCORE"] += 1
        df.loc[df["STATE"].isin(HIGH_RISK_STATES), "SCORE"] -= 1

    # Price vs FIBIL bonus
    df.loc[df["PRICE vs FIBIL"] < -0.5, "SCORE"] += 1   # cheap vs fibil
    df.loc[df["PRICE vs FIBIL"] >  0.5, "SCORE"] -= 1   # rich vs fibil

    # Volume bonus
    if "VOLUME (Cr)" in df.columns:
        df.loc[df["VOLUME (Cr)"] > 200, "SCORE"] += 1

    def sig(s):
        if s >= 7: return "🟢 STRONG BUY"
        if s >= 5: return "🔵 BUY"
        if s >= 3: return "🟡 WATCH"
        if s >= 1: return "⚪ HOLD"
        return "🔴 AVOID"

    df["SIGNAL"] = df["SCORE"].apply(sig)
    return df


@st.cache_data
def load_sample():
    return pd.DataFrame(SAMPLE_BONDS), pd.DataFrame(SAMPLE_GSEC)


def color_signal(val):
    m = {"🟢 STRONG BUY":"color:#4ade80;font-weight:700","🔵 BUY":"color:#60a5fa;font-weight:700",
         "🟡 WATCH":"color:#fbbf24;font-weight:700","⚪ HOLD":"color:#94a3b8","🔴 AVOID":"color:#f87171;font-weight:700"}
    return m.get(val, "")

def color_spread(v):
    if v >= 70: return "color:#4ade80"
    if v >= 50: return "color:#60a5fa"
    if v >= 40: return "color:#fbbf24"
    return "color:#f87171"

def color_delta(v):
    if v > 0: return "color:#4ade80"
    if v == 0: return "color:#94a3b8"
    return "color:#f87171"

def color_pricefibil(v):
    if v < -0.5: return "color:#4ade80"   # cheap
    if v > 0.5: return "color:#f87171"    # rich
    return "color:#94a3b8"

def top5_signal_color(sig):
    m = {"🟢 STRONG BUY":"#4ade80","🔵 BUY":"#60a5fa","🟡 WATCH":"#fbbf24","⚪ HOLD":"#94a3b8","🔴 AVOID":"#f87171"}
    return m.get(sig, "#94a3b8")

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 Data Source")
    data_source = st.radio("", ["Use Sample Data", "Upload Excel"], label_visibility="collapsed")

    bonds_df_raw = gsec_df_raw = None

    if data_source == "Upload Excel":
        st.markdown("**Upload your Excel file**")
        st.markdown("Must have **2 sheets:**")
        st.code("Sheet 1: BONDS\nSheet 2: GSEC_CURVE")

        uploaded = st.file_uploader("Choose .xlsx file", type=["xlsx","xls"])

        with st.expander("📋 BONDS sheet columns"):
            st.code("""SECURITY NAME  ← required
YTM (%)        ← required
LAST CUT-OFF (%) ← required
MATURITY       ← required
COUPON (%)     ← for price calc
PRICE          ← market price
FIBIL YIELD (%) ← fibil fair value
ISIN, STATE, LIQUIDITY, VOLUME (Cr) ← optional""")

        with st.expander("📋 GSEC_CURVE sheet columns"):
            st.code("""MATURITY       | GSEC YIELD (%)
2033           | 7.08
2034           | 7.10
2035           | 7.13
...""")

        if uploaded:
            try:
                xl = pd.ExcelFile(uploaded)
                sheet_names = xl.sheet_names

                bonds_sheet = st.selectbox("Select BONDS sheet", sheet_names, index=0)
                gsec_sheet  = st.selectbox("Select GSEC CURVE sheet", sheet_names, index=min(1, len(sheet_names)-1))

                bonds_df_raw = pd.read_excel(uploaded, sheet_name=bonds_sheet)
                gsec_df_raw  = pd.read_excel(uploaded, sheet_name=gsec_sheet)
                bonds_df_raw.columns = bonds_df_raw.columns.str.strip()
                gsec_df_raw.columns  = gsec_df_raw.columns.str.strip()

                st.success(f"✅ {len(bonds_df_raw)} bonds loaded")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("### 🎛️ Screener Filters")
    min_spread = st.slider("Min Spread (bps)", 0, 100, 0, 5)
    signal_filter = st.multiselect(
        "Show Signals",
        ["🟢 STRONG BUY","🔵 BUY","🟡 WATCH","⚪ HOLD","🔴 AVOID"],
        default=["🟢 STRONG BUY","🔵 BUY","🟡 WATCH"],
    )
    st.markdown("---")
    st.markdown("### 📖 Spread Guide")
    st.markdown("""| Spread | Status |\n|--------|--------|\n| ≥ 70 bps | 🟢 Very Cheap |\n| 50–70 bps | 🔵 Attractive |\n| 40–50 bps | 🟡 Normal |\n| < 40 bps | 🔴 Expensive |""")

# ─── LOAD & COMPUTE ───────────────────────────────────────────────────────────
if bonds_df_raw is not None and gsec_df_raw is not None:
    bonds_raw, gsec_raw = bonds_df_raw, gsec_df_raw
else:
    bonds_raw, gsec_raw = load_sample()

df = compute_signals(bonds_raw, gsec_raw)

# Filtered view
filtered = df[df["SPREAD (bps)"] >= min_spread].copy()
if signal_filter:
    filtered = filtered[filtered["SIGNAL"].isin(signal_filter)]

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <p class="main-title">📊 Bond Trading Terminal</p>
  <p class="main-subtitle">SDL & G-Sec Intelligence · Maturity-Matched Spread · FIBIL Pricing · AI Signals</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI ROW ──────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
buys    = len(df[df["SIGNAL"].isin(["🟢 STRONG BUY","🔵 BUY"])])
watches = len(df[df["SIGNAL"] == "🟡 WATCH"])
avoids  = len(df[df["SIGNAL"] == "🔴 AVOID"])
avg_sp  = df["SPREAD (bps)"].mean()
cheap_fibil = len(df[df["PRICE vs FIBIL"] < -0.5]) if "PRICE vs FIBIL" in df.columns else 0
best    = df.loc[df["SPREAD (bps)"].idxmax(), "SECURITY NAME"] if len(df) else "-"

for col, val, label, color in [
    (k1, buys,        "BUY Signals",    "#4ade80"),
    (k2, watches,     "WATCH",          "#fbbf24"),
    (k3, avoids,      "AVOID",          "#f87171"),
    (k4, f"{avg_sp:.1f}", "Avg Spread bps","#60a5fa"),
    (k5, cheap_fibil, "Cheap vs FIBIL", "#818cf8"),
    (k6, best[:10],   "Best Spread",    "#38bdf8"),
]:
    col.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:{color};font-size:{'1.3rem' if len(str(val))>5 else '1.8rem'}">{val}</div>
        <div class="metric-label">{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏆 Top Picks",
    "🔍 Full Screener",
    "📈 Charts",
    "🧮 Price Calculator",
    "🔬 Single Bond Analyzer",
    "📤 Export",
    "❓ How It Works",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TOP PICKS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-header">🏆 Top Picks — Dealer Intelligence</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    # ── Top 5 Best Value ──────────────────────────────────────────────────────
    with c1:
        st.markdown('<p class="section-header">🔥 Best Value (Score)</p>', unsafe_allow_html=True)
        best5 = df.sort_values("SCORE", ascending=False).head(5).reset_index(drop=True)
        for i, row in best5.iterrows():
            sig_color = top5_signal_color(row["SIGNAL"])
            state_txt = f" · {row['STATE']}" if "STATE" in row and pd.notna(row.get("STATE")) else ""
            st.markdown(f"""<div class="top5-card">
                <span class="top5-rank">#{i+1}</span>
                <span class="top5-badge" style="color:{sig_color}">{row['SIGNAL']}</span><br>
                <span class="top5-name">{row['SECURITY NAME']}</span>
                <div class="top5-detail">YTM {row['YTM (%)']:.2f}% · Spread {row['SPREAD (bps)']:.1f}bps · Score {row['SCORE']}{state_txt}</div>
            </div>""", unsafe_allow_html=True)

    # ── Top 5 Highest Yield ───────────────────────────────────────────────────
    with c2:
        st.markdown('<p class="section-header">📈 Highest Yielding</p>', unsafe_allow_html=True)
        yield5 = df.sort_values("YTM (%)", ascending=False).head(5).reset_index(drop=True)
        for i, row in yield5.iterrows():
            state_txt = f" · {row['STATE']}" if "STATE" in row and pd.notna(row.get("STATE")) else ""
            delta_txt = f"Δ {row['DELTA (bps)']:+.1f} bps vs auction"
            st.markdown(f"""<div class="top5-card">
                <span class="top5-rank">#{i+1}</span>
                <span class="top5-badge" style="color:#60a5fa">{row['YTM (%)']:.2f}%</span><br>
                <span class="top5-name">{row['SECURITY NAME']}</span>
                <div class="top5-detail">{delta_txt} · Spread {row['SPREAD (bps)']:.1f}bps{state_txt}</div>
            </div>""", unsafe_allow_html=True)

    # ── Top 5 Discounted + High Yield ─────────────────────────────────────────
    with c3:
        st.markdown('<p class="section-header">💎 Discounted + High Yield</p>', unsafe_allow_html=True)
        combo_df = df.copy()
        if "PRICE vs FIBIL" in combo_df.columns:
            combo5 = combo_df[combo_df["PRICE vs FIBIL"] < 0].sort_values("YTM (%)", ascending=False).head(5).reset_index(drop=True)
            if combo5.empty:
                combo5 = combo_df.sort_values(["SPREAD (bps)","YTM (%)"], ascending=False).head(5).reset_index(drop=True)
        else:
            combo5 = combo_df.sort_values("YTM (%)", ascending=False).head(5).reset_index(drop=True)

        for i, row in combo5.iterrows():
            pfibil = row.get("PRICE vs FIBIL", 0)
            price_label = f"Price {pfibil:+.2f} vs FIBIL"
            st.markdown(f"""<div class="top5-card">
                <span class="top5-rank">#{i+1}</span>
                <span class="top5-badge" style="color:#818cf8">{row['YTM (%)']:.2f}%</span><br>
                <span class="top5-name">{row['SECURITY NAME']}</span>
                <div class="top5-detail">{price_label} · Spread {row['SPREAD (bps)']:.1f}bps</div>
            </div>""", unsafe_allow_html=True)

    # ── Top 5 Wide Spread ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-header">📡 Widest Spread vs Maturity-Matched G-Sec</p>', unsafe_allow_html=True)
    spread5 = df.sort_values("SPREAD (bps)", ascending=False).head(5)
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=spread5["SECURITY NAME"], y=spread5["SPREAD (bps)"],
        marker=dict(
            color=spread5["SPREAD (bps)"],
            colorscale=[[0,"#fbbf24"],[0.5,"#60a5fa"],[1,"#4ade80"]],
            showscale=True, colorbar=dict(title="bps", tickfont=dict(color="#94a3b8"))
        ),
        text=spread5["SPREAD (bps)"].apply(lambda x: f"{x:.1f}"),
        textposition="outside", textfont=dict(color="#e2e8f0"),
    ))
    fig_bar.add_hline(y=50, line_dash="dash", line_color="#60a5fa", annotation_text="50 bps (Attractive)")
    fig_bar.add_hline(y=70, line_dash="dash", line_color="#4ade80", annotation_text="70 bps (Very Cheap)")
    fig_bar.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="#0a0e1a",
        font_color="#94a3b8", height=320,
        xaxis_title="", yaxis_title="Spread (bps)",
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FULL SCREENER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<p class="section-header">Full Bond Screener · {len(filtered)} bonds shown</p>', unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No bonds match current filters. Relax the sidebar filters.")
    else:
        display_cols = ["SECURITY NAME","MATURITY","YTM (%)","GSEC YIELD (%)","SPREAD (bps)",
                        "LAST CUT-OFF (%)","DELTA (bps)","FIBIL PRICE","PRICE vs FIBIL","SIGNAL","SCORE"]
        if "STATE" in filtered.columns:     display_cols.insert(1, "STATE")
        if "LIQUIDITY" in filtered.columns: display_cols.append("LIQUIDITY")
        if "VOLUME (Cr)" in filtered.columns: display_cols.append("VOLUME (Cr)")

        display_cols = [c for c in display_cols if c in filtered.columns]
        show_df = filtered[display_cols].sort_values("SCORE", ascending=False).reset_index(drop=True)

        def style_tbl(s):
            styles = pd.DataFrame("", index=s.index, columns=s.columns)
            for col, fn in [("SIGNAL", color_signal), ("SPREAD (bps)", color_spread),
                            ("DELTA (bps)", color_delta), ("PRICE vs FIBIL", color_pricefibil)]:
                if col in s.columns:
                    for idx, val in s[col].items():
                        styles.at[idx, col] = fn(val)
            return styles

        fmt = {"YTM (%)":"{:.2f}%","GSEC YIELD (%)":"{:.2f}%","LAST CUT-OFF (%)":"{:.2f}%",
               "SPREAD (bps)":"{:.1f}","DELTA (bps)":"{:+.1f}",
               "FIBIL PRICE":"{:.2f}","PRICE vs FIBIL":"{:+.2f}"}
        fmt = {k:v for k,v in fmt.items() if k in show_df.columns}

        styled = show_df.style.apply(style_tbl, axis=None).format(fmt)
        st.dataframe(styled, use_container_width=True, height=440)

        # Insights
        st.markdown("---")
        st.markdown('<p class="section-header">💡 AI Insights</p>', unsafe_allow_html=True)
        strong = filtered[filtered["SIGNAL"] == "🟢 STRONG BUY"]
        if not strong.empty:
            r = strong.iloc[0]
            st.markdown(f"""<div class="insight-box">🟢 <b>Top Pick:</b> <b>{r['SECURITY NAME']}</b> — Spread {r['SPREAD (bps)']:.1f} bps over <b>maturity-matched</b> G-Sec ({r['MATURITY']} G-Sec @ {r['GSEC YIELD (%)']:.2f}%). Delta vs auction: {r['DELTA (bps)']:+.1f} bps. Score {r['SCORE']}.</div>""", unsafe_allow_html=True)

        cheap_f = filtered[filtered["PRICE vs FIBIL"] < -0.5] if "PRICE vs FIBIL" in filtered.columns else pd.DataFrame()
        if not cheap_f.empty:
            st.markdown(f"""<div class="insight-box">💎 <b>{len(cheap_f)} bond(s)</b> are trading <b>below FIBIL fair value</b> — these offer price upside in addition to yield advantage.</div>""", unsafe_allow_html=True)

        neg_d = filtered[filtered["DELTA (bps)"] < 0]
        if not neg_d.empty:
            st.markdown(f"""<div class="insight-box">⚠️ <b>{len(neg_d)} bond(s)</b> are trading below their last auction cut-off — currently more expensive than issuance level.</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHARTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-header">Spread Distribution</p>', unsafe_allow_html=True)
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=df["SPREAD (bps)"], nbinsx=15,
            marker=dict(color=df["SPREAD (bps)"], colorscale=[[0,"#f87171"],[0.4,"#fbbf24"],[0.7,"#60a5fa"],[1,"#4ade80"]])))
        for xv, lbl, clr in [(40,"40 bps floor","#f87171"),(50,"50 bps attractive","#60a5fa"),(70,"70 bps very cheap","#4ade80")]:
            fig_hist.add_vline(x=xv, line_dash="dash", line_color=clr, annotation_text=lbl, annotation_font_color=clr)
        fig_hist.update_layout(plot_bgcolor="#0f172a",paper_bgcolor="#0a0e1a",font_color="#94a3b8",height=320,margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.markdown('<p class="section-header">Signal Breakdown</p>', unsafe_allow_html=True)
        sc = df["SIGNAL"].value_counts()
        colors_pie = {"🟢 STRONG BUY":"#4ade80","🔵 BUY":"#60a5fa","🟡 WATCH":"#fbbf24","⚪ HOLD":"#94a3b8","🔴 AVOID":"#f87171"}
        fig_pie = go.Figure(go.Pie(labels=sc.index, values=sc.values, hole=0.4,
            marker=dict(colors=[colors_pie.get(l,"#64748b") for l in sc.index])))
        fig_pie.update_layout(plot_bgcolor="#0f172a",paper_bgcolor="#0a0e1a",font_color="#94a3b8",height=320,
            margin=dict(l=0,r=0,t=10,b=0),legend=dict(font=dict(color="#94a3b8")))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Yield Curve — SDL vs G-Sec
    st.markdown('<p class="section-header">SDL vs G-Sec Yield Curve (Maturity-Matched)</p>', unsafe_allow_html=True)
    curve_df = df.sort_values("MATURITY")
    fig_curve = go.Figure()
    if "STATE" in curve_df.columns:
        state_colors = {"Maharashtra":"#60a5fa","Gujarat":"#34d399","Karnataka":"#a78bfa",
                        "Tamil Nadu":"#f472b6","Andhra Pradesh":"#f87171","Punjab":"#fbbf24",
                        "Uttar Pradesh":"#fb923c","Rajasthan":"#e879f9"}
        for state, grp in curve_df.groupby("STATE"):
            fig_curve.add_trace(go.Scatter(
                x=grp["MATURITY"], y=grp["YTM (%)"], mode="markers+lines",
                name=state, marker=dict(size=9, color=state_colors.get(state,"#94a3b8")),
                line=dict(width=1.5, dash="dot", color=state_colors.get(state,"#94a3b8")),
            ))
    else:
        fig_curve.add_trace(go.Scatter(x=curve_df["MATURITY"],y=curve_df["YTM (%)"],mode="lines+markers",name="SDL YTM",line=dict(color="#60a5fa",width=2)))

    gsec_sorted = gsec_raw.sort_values("MATURITY")
    fig_curve.add_trace(go.Scatter(
        x=gsec_sorted["MATURITY"], y=gsec_sorted["GSEC YIELD (%)"],
        mode="lines", name="G-Sec Benchmark",
        line=dict(color="#f87171", width=2.5, dash="solid"),
    ))
    fig_curve.update_layout(plot_bgcolor="#0f172a",paper_bgcolor="#0a0e1a",font_color="#94a3b8",height=380,
        xaxis_title="Maturity Year",yaxis_title="Yield (%)",margin=dict(l=0,r=0,t=10,b=0),
        legend=dict(font=dict(color="#94a3b8")))
    st.plotly_chart(fig_curve, use_container_width=True)

    # Scatter: Spread vs YTM
    st.markdown('<p class="section-header">Opportunity Map — Spread vs YTM</p>', unsafe_allow_html=True)
    color_map = {"🟢 STRONG BUY":"#4ade80","🔵 BUY":"#60a5fa","🟡 WATCH":"#fbbf24","⚪ HOLD":"#94a3b8","🔴 AVOID":"#f87171"}
    fig_scatter = go.Figure()
    for sig, grp in df.groupby("SIGNAL"):
        hover = grp.apply(lambda r: f"<b>{r['SECURITY NAME']}</b><br>YTM: {r['YTM (%)']:.2f}%<br>Spread: {r['SPREAD (bps)']:.1f}bps<br>Score: {r['SCORE']}<br>FIBIL gap: {r.get('PRICE vs FIBIL',0):+.2f}", axis=1)
        fig_scatter.add_trace(go.Scatter(
            x=grp["YTM (%)"], y=grp["SPREAD (bps)"], mode="markers+text",
            name=sig, marker=dict(color=color_map.get(sig,"#64748b"), size=14, opacity=0.85),
            text=grp["SECURITY NAME"].str[:8], textposition="top center",
            textfont=dict(size=9, color="#94a3b8"),
            hovertext=hover, hoverinfo="text",
        ))
    fig_scatter.add_hrect(y0=50,y1=70,fillcolor="#1d4ed8",opacity=0.06,annotation_text="Attractive zone")
    fig_scatter.add_hrect(y0=70,y1=130,fillcolor="#16a34a",opacity=0.06,annotation_text="Very Cheap zone")
    fig_scatter.update_layout(plot_bgcolor="#0f172a",paper_bgcolor="#0a0e1a",font_color="#94a3b8",height=400,
        xaxis_title="YTM (%)",yaxis_title="Spread over Matched G-Sec (bps)",margin=dict(l=0,r=0,t=10,b=0),
        legend=dict(font=dict(color="#94a3b8")))
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Price vs FIBIL
    if "PRICE vs FIBIL" in df.columns:
        st.markdown('<p class="section-header">Market Price vs FIBIL Fair Value</p>', unsafe_allow_html=True)
        pf = df.sort_values("PRICE vs FIBIL")
        fig_pf = go.Figure()
        fig_pf.add_trace(go.Bar(
            x=pf["SECURITY NAME"], y=pf["PRICE vs FIBIL"],
            marker=dict(color=["#4ade80" if v < 0 else "#f87171" for v in pf["PRICE vs FIBIL"]]),
            text=pf["PRICE vs FIBIL"].apply(lambda x: f"{x:+.2f}"), textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        fig_pf.add_hline(y=0, line_color="#64748b")
        fig_pf.update_layout(plot_bgcolor="#0f172a",paper_bgcolor="#0a0e1a",font_color="#94a3b8",height=320,
            yaxis_title="Price vs FIBIL (₹)",xaxis_title="",margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_pf, use_container_width=True)
        st.markdown("""<div class="insight-box">🟢 Green bars = bond trading <b>below</b> FIBIL fair value (cheap, price upside)
        &nbsp;|&nbsp; 🔴 Red bars = trading <b>above</b> FIBIL (expensive, limited upside)</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRICE CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">🧮 Bond Price Calculator</p>', unsafe_allow_html=True)
    st.markdown("Calculate the exact price of any bond from its yield, or find the yield from a given price.")

    calc_mode = st.radio("Calculate:", ["Price from Yield", "Yield from Price"], horizontal=True)

    cc1, cc2 = st.columns(2)
    with cc1:
        calc_coupon = st.number_input("Coupon Rate (%)", 4.0, 15.0, 7.48, 0.01, format="%.2f")
        calc_face   = st.number_input("Face Value (₹)", 100, 10000, 100, 100)
        calc_years  = st.number_input("Years to Maturity", 0.5, 40.0, 10.0, 0.5, format="%.1f")
        calc_freq   = st.selectbox("Coupon Frequency", ["Semi-Annual (2/yr)", "Annual (1/yr)"])
        freq_n      = 2 if "Semi" in calc_freq else 1

    with cc2:
        if calc_mode == "Price from Yield":
            calc_ytm   = st.number_input("Target YTM / Desired Yield (%)", 4.0, 15.0, 7.64, 0.01, format="%.2f")
            calc_fibil = st.number_input("FIBIL Yield (%)", 4.0, 15.0, 7.60, 0.01, format="%.2f")

            price_market = bond_price_full(calc_coupon, calc_ytm,   calc_years, calc_face, freq_n)
            price_fibil  = bond_price_full(calc_coupon, calc_fibil, calc_years, calc_face, freq_n)
            gap          = price_market - price_fibil

            st.markdown(f"""<div class="calc-result">
                <div class="calc-label">Market Price (at {calc_ytm:.2f}% yield)</div>
                <div class="calc-price">₹ {price_market:.4f}</div>
                <div style="margin-top:12px">
                    <span style="color:#94a3b8;font-size:0.85rem">FIBIL Fair Price (at {calc_fibil:.2f}%): </span>
                    <span style="color:#818cf8;font-weight:700;font-family:'DM Mono',monospace">₹ {price_fibil:.4f}</span>
                </div>
                <div style="margin-top:6px">
                    <span style="color:#94a3b8;font-size:0.85rem">Price Gap vs FIBIL: </span>
                    <span style="color:{'#4ade80' if gap < 0 else '#f87171'};font-weight:700;font-family:'DM Mono',monospace">{gap:+.4f}</span>
                    <span style="color:#64748b;font-size:0.8rem"> {'(CHEAP vs FIBIL ✅)' if gap < 0 else '(RICH vs FIBIL ⚠️)'}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        else:
            calc_price_in = st.number_input("Market Price (₹)", 80.0, 130.0, 99.12, 0.01, format="%.4f")

            # Newton's method to solve for yield
            def price_fn(y): return bond_price_full(calc_coupon, y, calc_years, calc_face, freq_n)
            y_lo, y_hi = 0.01, 30.0
            for _ in range(60):
                y_mid = (y_lo + y_hi) / 2
                if price_fn(y_mid) > calc_price_in: y_lo = y_mid
                else: y_hi = y_mid
            solved_ytm = round((y_lo + y_hi) / 2, 4)

            st.markdown(f"""<div class="calc-result">
                <div class="calc-label">Yield to Maturity (at ₹{calc_price_in:.2f})</div>
                <div class="calc-price">{solved_ytm:.4f}%</div>
                <div style="margin-top:12px;color:#64748b;font-size:0.82rem">
                    Clean price entered. Yield solved by bisection method (accurate to 4 decimal places).
                </div>
            </div>""", unsafe_allow_html=True)

    # Sensitivity table
    st.markdown("---")
    st.markdown('<p class="section-header">Price Sensitivity Table (DV01)</p>', unsafe_allow_html=True)
    base_ytm = calc_ytm if calc_mode == "Price from Yield" else solved_ytm
    ytm_range = [base_ytm + d for d in [-0.50,-0.25,-0.10,-0.05,0,0.05,0.10,0.25,0.50]]
    sens_rows = []
    for y in ytm_range:
        p = bond_price_full(calc_coupon, y, calc_years, calc_face, freq_n)
        base_p = bond_price_full(calc_coupon, base_ytm, calc_years, calc_face, freq_n)
        sens_rows.append({"YTM (%)": round(y,2), "Price (₹)": round(p,4), "Chg vs Base (₹)": round(p-base_p,4)})
    sens_df = pd.DataFrame(sens_rows)

    def color_sens(v):
        if v > 0: return "color:#4ade80"
        if v < 0: return "color:#f87171"
        return "color:#94a3b8"

    styled_sens = sens_df.style.map(color_sens, subset=["Chg vs Base (₹)"])
    st.dataframe(styled_sens, use_container_width=True, hide_index=True)
    st.markdown("""<div class="insight-box">📌 When yield <b>falls</b>, price <b>rises</b> — and vice versa. Longer maturity = higher sensitivity (Duration effect).</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SINGLE BOND ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-header">🔬 Single Bond Deep-Dive + Comparative Analysis</p>', unsafe_allow_html=True)

    mode5 = st.radio("Mode", ["Pick from data", "Enter manually"], horizontal=True)

    if mode5 == "Pick from data" and len(df) > 0:
        sel_bond = st.selectbox("Select bond", df["SECURITY NAME"].tolist())
        row = df[df["SECURITY NAME"] == sel_bond].iloc[0]
        s_name    = row["SECURITY NAME"]
        s_ytm     = row["YTM (%)"]
        s_gsec    = row["GSEC YIELD (%)"]
        s_cutoff  = row["LAST CUT-OFF (%)"]
        s_mat     = int(row["MATURITY"])
        s_liq     = row.get("LIQUIDITY","Medium")
        s_state   = row.get("STATE","Other")
        s_coupon  = row.get("COUPON (%)", s_ytm)
        s_price   = row.get("PRICE", 100)
        s_fibil_y = row.get("FIBIL YIELD (%)", s_ytm - 0.04)
        s_years   = row.get("YEARS TO MAT", s_mat - datetime.now().year)
        s_score   = row["SCORE"]
        s_signal  = row["SIGNAL"]
        s_spread  = row["SPREAD (bps)"]
        s_delta   = row["DELTA (bps)"]
        s_pfibil  = row.get("PRICE vs FIBIL", 0)
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            s_name   = st.text_input("Bond Name", "MH SDL 2034")
            s_ytm    = st.number_input("YTM (%)", 4.0, 15.0, 7.64, 0.01, format="%.2f")
            s_gsec   = st.number_input("Matched G-Sec Yield (%)", 4.0, 15.0, 7.10, 0.01, format="%.2f")
            s_coupon = st.number_input("Coupon (%)", 4.0, 15.0, 7.48, 0.01, format="%.2f")
        with col_b:
            s_cutoff  = st.number_input("Last Auction Cut-off (%)", 4.0, 15.0, 7.58, 0.01, format="%.2f")
            s_fibil_y = st.number_input("FIBIL Yield (%)", 4.0, 15.0, 7.60, 0.01, format="%.2f")
            s_mat     = st.number_input("Maturity Year", 2025, 2045, 2034, 1)
            s_liq     = st.selectbox("Liquidity", ["High","Medium","Low"])
            s_state   = st.selectbox("State", ["Maharashtra","Gujarat","Karnataka","Tamil Nadu",
                                                "Andhra Pradesh","Punjab","Rajasthan","Uttar Pradesh","Other"])
        s_price = 100.0
        s_years = max(0.5, s_mat - datetime.now().year)
        s_spread = round((s_ytm - s_gsec)*100, 2)
        s_delta  = round((s_ytm - s_cutoff)*100, 2)

        # Compute score
        s_score = 0
        s_score += 3 if s_spread >= 70 else (2 if s_spread >= 50 else (1 if s_spread >= 40 else -1))
        s_score += 2 if s_delta > 5 else (1 if s_delta >= 0 else -1)
        s_score += 2 if s_liq == "High" else (1 if s_liq == "Medium" else -1)
        s_score += 1 if s_state in LOW_RISK_STATES else (-1 if s_state in HIGH_RISK_STATES else 0)

        fibil_p  = bond_price_full(s_coupon, s_fibil_y, s_years)
        s_pfibil = round(s_price - fibil_p, 2)
        s_score += 1 if s_pfibil < -0.5 else (-1 if s_pfibil > 0.5 else 0)

        if s_score >= 7: s_signal = "🟢 STRONG BUY"
        elif s_score >= 5: s_signal = "🔵 BUY"
        elif s_score >= 3: s_signal = "🟡 WATCH"
        elif s_score >= 1: s_signal = "⚪ HOLD"
        else: s_signal = "🔴 AVOID"

    # ── Metrics row ──────────────────────────────────────────────────────────
    st.markdown("---")
    sig_clr = {"🟢 STRONG BUY":"#4ade80","🔵 BUY":"#60a5fa","🟡 WATCH":"#fbbf24","⚪ HOLD":"#94a3b8","🔴 AVOID":"#f87171"}.get(s_signal,"#94a3b8")
    st.markdown(f"""<div class="banner-{'good' if 'BUY' in s_signal else ('avg' if 'WATCH' in s_signal or 'HOLD' in s_signal else 'bad')}">
        <b style="font-size:1.1rem">{s_name}</b>
        &nbsp;→&nbsp; <b style="color:{sig_clr}">{s_signal}</b>
        &nbsp;|&nbsp; Score: {s_score}
        &nbsp;|&nbsp; Spread: {s_spread:.1f} bps
        &nbsp;|&nbsp; Δ Auction: {s_delta:+.1f} bps
        &nbsp;|&nbsp; Price vs FIBIL: {s_pfibil:+.2f}
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)

    with d1:
        st.markdown('<p class="section-header">Spread Analysis</p>', unsafe_allow_html=True)
        spread_status = "Very Cheap 🟢" if s_spread >= 70 else ("Attractive 🔵" if s_spread >= 50 else ("Normal 🟡" if s_spread >= 40 else "Expensive 🔴"))
        st.markdown(f"""
        <div class="insight-box"><b>YTM:</b> {s_ytm:.2f}%</div>
        <div class="insight-box"><b>Matched G-Sec ({s_mat}):</b> {s_gsec:.2f}%</div>
        <div class="insight-box"><b>Spread:</b> {s_spread:.1f} bps → {spread_status}</div>
        """, unsafe_allow_html=True)

    with d2:
        st.markdown('<p class="section-header">Auction Comparison</p>', unsafe_allow_html=True)
        delta_status = "Cheaper than issue ✅" if s_delta > 0 else ("At par 🟡" if s_delta == 0 else "More expensive than issue ❌")
        st.markdown(f"""
        <div class="insight-box"><b>Last Cut-off:</b> {s_cutoff:.2f}%</div>
        <div class="insight-box"><b>Current YTM:</b> {s_ytm:.2f}%</div>
        <div class="insight-box"><b>Delta:</b> {s_delta:+.1f} bps → {delta_status}</div>
        """, unsafe_allow_html=True)

    with d3:
        st.markdown('<p class="section-header">FIBIL Price Analysis</p>', unsafe_allow_html=True)
        fibil_calc = bond_price_full(s_coupon, s_fibil_y, max(0.5, s_mat - datetime.now().year))
        fibil_status = "Below FIBIL (cheap, upside) ✅" if s_pfibil < -0.5 else ("Above FIBIL (expensive) ❌" if s_pfibil > 0.5 else "At par with FIBIL 🟡")
        st.markdown(f"""
        <div class="insight-box"><b>FIBIL Yield:</b> {s_fibil_y:.2f}%</div>
        <div class="insight-box"><b>FIBIL Fair Price:</b> ₹ {fibil_calc:.4f}</div>
        <div class="insight-box"><b>Gap:</b> {s_pfibil:+.2f} → {fibil_status}</div>
        """, unsafe_allow_html=True)

    # ── Gauge ─────────────────────────────────────────────────────────────────
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=s_score,
        title={"text":"Bond Score","font":{"color":"#94a3b8"}},
        gauge={"axis":{"range":[-3,10],"tickcolor":"#475569"},
               "bar":{"color":"#38bdf8"},
               "steps":[{"range":[-3,0],"color":"#450a0a"},{"range":[0,3],"color":"#292524"},
                        {"range":[3,5],"color":"#1c1400"},{"range":[5,7],"color":"#052e16"},{"range":[7,10],"color":"#14532d"}],
               "threshold":{"line":{"color":"#4ade80","width":3},"value":7}},
        number={"font":{"color":"#e2e8f0"}},
    ))
    fig_gauge.update_layout(paper_bgcolor="#0a0e1a",font_color="#94a3b8",height=240,margin=dict(l=20,r=20,t=20,b=0))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── COMPARATIVE: same maturity, all states ─────────────────────────────
    st.markdown("---")
    st.markdown(f'<p class="section-header">📊 Comparative — All States, Same Maturity ({s_mat})</p>', unsafe_allow_html=True)

    comp_df = df[df["MATURITY"] == s_mat].copy() if "MATURITY" in df.columns else pd.DataFrame()

    if not comp_df.empty:
        comp_df = comp_df.sort_values("YTM (%)", ascending=False).reset_index(drop=True)

        # Highlight current bond
        comp_cols = ["SECURITY NAME","YTM (%)","GSEC YIELD (%)","SPREAD (bps)","DELTA (bps)","FIBIL PRICE","PRICE vs FIBIL","SIGNAL"]
        comp_cols = [c for c in comp_cols if c in comp_df.columns]
        comp_show = comp_df[comp_cols]

        def style_comp(s):
            styles = pd.DataFrame("", index=s.index, columns=s.columns)
            for col, fn in [("SIGNAL",color_signal),("SPREAD (bps)",color_spread),
                            ("DELTA (bps)",color_delta),("PRICE vs FIBIL",color_pricefibil)]:
                if col in s.columns:
                    for idx, val in s[col].items():
                        styles.at[idx, col] = fn(val)
            # Highlight selected bond row
            if "SECURITY NAME" in s.columns:
                for idx, val in s["SECURITY NAME"].items():
                    if val == s_name:
                        for c in s.columns:
                            styles.at[idx, c] = styles.at[idx, c] + ";background-color:#1e3a5f"
            return styles

        fmt2 = {k:v for k,v in {"YTM (%)":"{:.2f}%","GSEC YIELD (%)":"{:.2f}%",
                "SPREAD (bps)":"{:.1f}","DELTA (bps)":"{:+.1f}",
                "FIBIL PRICE":"{:.2f}","PRICE vs FIBIL":"{:+.2f}"}.items() if k in comp_show.columns}
        st.dataframe(comp_show.style.apply(style_comp,axis=None).format(fmt2), use_container_width=True, hide_index=True)

        # Bar chart comparison
        fig_comp = go.Figure()
        bar_colors = ["#38bdf8" if n == s_name else "#334155" for n in comp_df["SECURITY NAME"]]
        fig_comp.add_trace(go.Bar(
            x=comp_df["SECURITY NAME"], y=comp_df["YTM (%)"],
            marker=dict(color=bar_colors),
            text=comp_df["YTM (%)"].apply(lambda x: f"{x:.2f}%"), textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        gsec_yield_mat = gsec_raw[gsec_raw["MATURITY"] == s_mat]["GSEC YIELD (%)"].values
        if len(gsec_yield_mat):
            fig_comp.add_hline(y=gsec_yield_mat[0], line_dash="dash", line_color="#f87171",
                               annotation_text=f"G-Sec {s_mat} @ {gsec_yield_mat[0]:.2f}%")
        fig_comp.update_layout(plot_bgcolor="#0f172a",paper_bgcolor="#0a0e1a",font_color="#94a3b8",height=320,
            yaxis_title="YTM (%)",xaxis_title="",yaxis=dict(range=[min(comp_df["YTM (%)"]) - 0.2, max(comp_df["YTM (%)"]) + 0.2]),
            margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_comp, use_container_width=True)
        st.markdown(f"""<div class="insight-box">🔵 Highlighted bar = <b>{s_name}</b>. Red dashed line = G-Sec {s_mat} benchmark. 
        Bars above the line = SDL spread over G-Sec. Taller bar = more yield = relatively cheaper.</div>""", unsafe_allow_html=True)
    else:
        st.info(f"No other bonds with maturity {s_mat} in current dataset. Add more bonds to see comparative analysis.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<p class="section-header">📤 Export Data</p>', unsafe_allow_html=True)

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Full Data (CSV)", data=csv,
            file_name=f"bond_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True)
    with col_e2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Bond Screener")
            gsec_raw.to_excel(w, index=False, sheet_name="GSEC Curve")
        st.download_button("⬇️ Download Full Data (Excel)", data=buf.getvalue(),
            file_name=f"bond_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    st.markdown("---")
    st.dataframe(df.head(10), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — HOW IT WORKS
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<p class="section-header">How the Terminal Works</p>', unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
    This terminal uses <b>maturity-matched benchmarking</b> — every SDL is compared against the G-Sec of the <b>same maturity year</b>,
    not a single common G-Sec. This is how real treasury desks analyse bonds.
    </div>""", unsafe_allow_html=True)

    scoring_data = {
        "Factor": ["Spread vs G-Sec","","","","Delta vs Auction","","","Liquidity","","","State Risk","","Price vs FIBIL",""],
        "Condition": ["≥ 70 bps","50–70 bps","40–50 bps","< 40 bps","> 5 bps above cut-off","0–5 bps above","Below cut-off",
                      "High","Medium","Low","Strong fiscal (MH/GJ/KA/TN)","High risk (AP/PB/RJ/HP)",
                      "Market < FIBIL (cheap)","Market > FIBIL (expensive)"],
        "Score": ["+3","+2","+1","−1","+2","+1","−1","+2","+1","−1","+1","−1","+1","−1"],
    }
    st.dataframe(pd.DataFrame(scoring_data), use_container_width=True, hide_index=True)

    st.markdown("### Price Calculator Method")
    st.markdown("""<div class="insight-box">
    Uses the standard <b>Discounted Cash Flow (DCF)</b> formula:
    Price = Σ [C/(1+r)^t] + [Face/(1+r)^n]
    where C = periodic coupon, r = yield per period, n = total periods.
    Accurate to 4 decimal places. Yield-from-price uses bisection method.
    </div>""", unsafe_allow_html=True)

    tips = [
        "Always compare same-state SDLs — AP vs AP, MH vs MH.",
        "FIBIL price gap is your margin of safety — cheap vs FIBIL = real value.",
        "Maturity-matched spread is the professional way. A 2034 SDL spread must be vs 2034 G-Sec, not 10Y benchmark.",
        "Delta vs last auction is often more useful than absolute yield.",
        "DV01 (rupee value of 1 bps) = Price × Duration / 10000. Use sensitivity table for this.",
        "In a rate-cut cycle, long-duration bonds benefit most — price rises more.",
    ]
    for tip in tips:
        st.markdown(f"<div class='insight-box'>💬 {tip}</div>", unsafe_allow_html=True)


# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<p style='text-align:center;color:#334155;font-size:0.75rem;font-family:DM Mono,monospace'>Bond Trading Terminal · Professional use only · Not financial advice · {datetime.now().strftime('%d %b %Y %H:%M')}</p>", unsafe_allow_html=True)
