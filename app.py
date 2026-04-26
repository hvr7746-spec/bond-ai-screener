import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bond AI Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
}

.main-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.main-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 4px;
    font-family: 'DM Mono', monospace;
}

.metric-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
}

.metric-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.signal-buy {
    background: linear-gradient(135deg, #052e16, #14532d);
    border: 1px solid #16a34a;
    color: #4ade80;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    font-family: 'DM Mono', monospace;
}

.signal-sell {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    border: 1px solid #dc2626;
    color: #f87171;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    font-family: 'DM Mono', monospace;
}

.signal-hold {
    background: linear-gradient(135deg, #1c1917, #292524);
    border: 1px solid #78716c;
    color: #d6d3d1;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    font-family: 'DM Mono', monospace;
}

.signal-watch {
    background: linear-gradient(135deg, #1c1400, #3b2800);
    border: 1px solid #d97706;
    color: #fbbf24;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    font-family: 'DM Mono', monospace;
}

.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #94a3b8;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 8px;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'DM Mono', monospace;
}

.insight-box {
    background: #0f172a;
    border-left: 3px solid #38bdf8;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.88rem;
    color: #cbd5e1;
}

.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

div[data-testid="stSidebar"] {
    background: #0a0e1a;
    border-right: 1px solid #1e293b;
}

.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #4f46e5);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.2s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4);
}

.stFileUploader {
    border-radius: 10px;
}

.stSelectbox > div, .stNumberInput > div {
    background: #0f172a;
    border-color: #1e293b;
}

.tooltip-text {
    font-size: 0.75rem;
    color: #475569;
    font-style: italic;
}

.banner-good { background: #052e16; border: 1px solid #16a34a; color: #4ade80; border-radius: 8px; padding: 10px 16px; }
.banner-avg  { background: #1c1400; border: 1px solid #d97706; color: #fbbf24; border-radius: 8px; padding: 10px 16px; }
.banner-bad  { background: #450a0a; border: 1px solid #dc2626; color: #f87171; border-radius: 8px; padding: 10px 16px; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
SPREAD_NORMS = {
    "Normal":      (40, 50),
    "Attractive":  (50, 70),
    "Very Cheap":  (70, 999),
    "Expensive":   (0, 40),
}

HIGH_RISK_STATES = ["Andhra Pradesh", "Punjab", "Rajasthan", "Himachal Pradesh"]
LOW_RISK_STATES  = ["Maharashtra", "Gujarat", "Karnataka", "Tamil Nadu"]

SAMPLE_DATA = {
    "ISIN":             ["IN0020220128", "IN0020210079", "IN0020220201", "IN0020200045", "IN0020230044",
                         "IN0020210152", "IN0020220315", "IN0020200118", "IN0020230117", "IN0020210225"],
    "SECURITY NAME":    ["MH SDL 2034", "GJ SDL 2033", "AP SDL 2030", "PB SDL 2032", "KA SDL 2035",
                         "TN SDL 2031", "UP SDL 2033", "RJ SDL 2034", "MH SDL 2029", "GJ SDL 2036"],
    "STATE":            ["Maharashtra", "Gujarat", "Andhra Pradesh", "Punjab", "Karnataka",
                         "Tamil Nadu", "Uttar Pradesh", "Rajasthan", "Maharashtra", "Gujarat"],
    "MATURITY":         [2034, 2033, 2030, 2032, 2035, 2031, 2033, 2034, 2029, 2036],
    "YTM (%)":          [7.64, 7.58, 7.89, 7.95, 7.72, 7.61, 7.81, 7.92, 7.52, 7.61],
    "G-SEC YIELD (%)":  [7.10, 7.10, 7.10, 7.10, 7.10, 7.10, 7.10, 7.10, 7.05, 7.15],
    "LAST CUT-OFF (%)": [7.58, 7.55, 7.82, 7.88, 7.68, 7.57, 7.75, 7.85, 7.49, 7.57],
    "LIQUIDITY":        ["High", "High", "Low", "Low", "Medium", "Medium", "Low", "Low", "High", "High"],
    "FACE VALUE":       [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
}

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────
def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["SPREAD (bps)"]    = (df["YTM (%)"] - df["G-SEC YIELD (%)"]).round(4) * 100
    df["DELTA (bps)"]     = (df["YTM (%)"] - df["LAST CUT-OFF (%)"]).round(4) * 100
    df["SCORE"]           = 0

    # Spread scoring
    df.loc[df["SPREAD (bps)"] >= 70, "SCORE"] += 3
    df.loc[(df["SPREAD (bps)"] >= 50) & (df["SPREAD (bps)"] < 70), "SCORE"] += 2
    df.loc[(df["SPREAD (bps)"] >= 40) & (df["SPREAD (bps)"] < 50), "SCORE"] += 1
    df.loc[df["SPREAD (bps)"] < 40, "SCORE"] -= 1

    # Delta (vs last auction) scoring
    df.loc[df["DELTA (bps)"] > 0, "SCORE"] += 2
    df.loc[df["DELTA (bps)"] == 0, "SCORE"] += 0
    df.loc[df["DELTA (bps)"] < 0, "SCORE"] -= 1

    # Liquidity scoring
    if "LIQUIDITY" in df.columns:
        df.loc[df["LIQUIDITY"] == "High",   "SCORE"] += 2
        df.loc[df["LIQUIDITY"] == "Medium", "SCORE"] += 1
        df.loc[df["LIQUIDITY"] == "Low",    "SCORE"] -= 1

    # State risk (if STATE column exists)
    if "STATE" in df.columns:
        df.loc[df["STATE"].isin(HIGH_RISK_STATES), "SCORE"] -= 1
        df.loc[df["STATE"].isin(LOW_RISK_STATES),  "SCORE"] += 1

    # Signal
    def map_signal(s):
        if s >= 6: return "🟢 STRONG BUY"
        if s >= 4: return "🔵 BUY"
        if s >= 2: return "🟡 WATCH"
        if s >= 0: return "⚪ HOLD"
        return "🔴 AVOID"

    df["SIGNAL"] = df["SCORE"].apply(map_signal)
    df["SPREAD (bps)"]  = df["SPREAD (bps)"].round(1)
    df["DELTA (bps)"]   = df["DELTA (bps)"].round(1)
    return df


def spread_label(spread):
    if spread >= 70:   return "Very Cheap", "good"
    if spread >= 50:   return "Attractive", "good"
    if spread >= 40:   return "Normal", "avg"
    return "Expensive", "bad"


def color_signal(val):
    colors = {
        "🟢 STRONG BUY": "color:#4ade80;font-weight:700",
        "🔵 BUY":        "color:#60a5fa;font-weight:700",
        "🟡 WATCH":      "color:#fbbf24;font-weight:700",
        "⚪ HOLD":        "color:#94a3b8",
        "🔴 AVOID":      "color:#f87171;font-weight:700",
    }
    return colors.get(val, "")


def color_spread(val):
    if val >= 70:  return "color:#4ade80"
    if val >= 50:  return "color:#60a5fa"
    if val >= 40:  return "color:#fbbf24"
    return "color:#f87171"


def color_delta(val):
    if val > 0:  return "color:#4ade80"
    if val == 0: return "color:#94a3b8"
    return "color:#f87171"


@st.cache_data
def load_sample():
    return pd.DataFrame(SAMPLE_DATA)


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 Data Source")
    data_source = st.radio("", ["Use Sample Data", "Upload Excel / CSV"], label_visibility="collapsed")

    uploaded_file = None
    if data_source == "Upload Excel / CSV":
        uploaded_file = st.file_uploader("Upload your bond data file", type=["xlsx", "xls", "csv"])
        with st.expander("📋 Required Columns"):
            st.code("""SECURITY NAME
YTM (%)
G-SEC YIELD (%)
LAST CUT-OFF (%)
LIQUIDITY        ← optional
STATE            ← optional
ISIN             ← optional
MATURITY         ← optional""")

    st.markdown("---")
    st.markdown("### 🎛️ Filters")

    min_spread = st.slider("Min Spread (bps)", 0, 100, 0, 5)
    signal_filter = st.multiselect(
        "Show Signals",
        ["🟢 STRONG BUY", "🔵 BUY", "🟡 WATCH", "⚪ HOLD", "🔴 AVOID"],
        default=["🟢 STRONG BUY", "🔵 BUY", "🟡 WATCH"],
    )
    if "MATURITY" in pd.DataFrame(SAMPLE_DATA).columns:
        maturity_range = st.slider("Maturity Year", 2025, 2045, (2028, 2038))
    else:
        maturity_range = (2025, 2045)

    st.markdown("---")
    st.markdown("### 📖 Spread Guide")
    st.markdown("""
| Spread | Status |
|--------|--------|
| ≥ 70 bps | 🟢 Very Cheap |
| 50–70 bps | 🔵 Attractive |
| 40–50 bps | 🟡 Normal |
| < 40 bps | 🔴 Expensive |
""")

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)

        # Try to auto-rename common column variants
        rename_map = {}
        for col in raw_df.columns:
            c = col.strip()
            if c.upper() in ["YTM", "YIELD TO MATURITY"]:
                rename_map[col] = "YTM (%)"
            elif "G-SEC" in c.upper() or "GSEC" in c.upper():
                rename_map[col] = "G-SEC YIELD (%)"
            elif "CUT" in c.upper():
                rename_map[col] = "LAST CUT-OFF (%)"
        raw_df.rename(columns=rename_map, inplace=True)

        required = ["YTM (%)", "G-SEC YIELD (%)", "LAST CUT-OFF (%)"]
        missing = [r for r in required if r not in raw_df.columns]
        if missing:
            st.error(f"❌ Missing columns: {missing}\n\nFound columns: {list(raw_df.columns)}")
            st.info("Tip: Rename your Excel columns to match the required names above.")
            st.stop()

        df = raw_df.copy()
        st.sidebar.success(f"✅ Loaded {len(df)} bonds")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    df = load_sample()
    st.sidebar.info("ℹ️ Using sample data")

# ─── COMPUTE ──────────────────────────────────────────────────────────────────
df = compute_signals(df)

# Apply filters
filtered = df[df["SPREAD (bps)"] >= min_spread].copy()
if signal_filter:
    filtered = filtered[filtered["SIGNAL"].isin(signal_filter)]
if "MATURITY" in filtered.columns:
    filtered = filtered[
        (filtered["MATURITY"] >= maturity_range[0]) &
        (filtered["MATURITY"] <= maturity_range[1])
    ]

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <p class="main-title">📊 Bond AI Screener</p>
  <p class="main-subtitle">SDL & G-Sec Intelligence Platform · Real-time Spread Analysis · AI-Powered Signals</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI ROW ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

buys  = len(df[df["SIGNAL"].isin(["🟢 STRONG BUY", "🔵 BUY"])])
watches = len(df[df["SIGNAL"] == "🟡 WATCH"])
avoids  = len(df[df["SIGNAL"] == "🔴 AVOID"])
avg_spread = df["SPREAD (bps)"].mean()
best_bond  = df.loc[df["SPREAD (bps)"].idxmax(), "SECURITY NAME"] if len(df) else "-"

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:#4ade80">{buys}</div>
        <div class="metric-label">BUY Signals</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:#fbbf24">{watches}</div>
        <div class="metric-label">WATCH</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:#f87171">{avoids}</div>
        <div class="metric-label">AVOID</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:#60a5fa">{avg_spread:.1f}</div>
        <div class="metric-label">Avg Spread (bps)</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="font-size:1rem;color:#38bdf8;padding-top:8px">{best_bond[:12]}</div>
        <div class="metric-label">Widest Spread</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Screener", "📈 Charts", "🧮 Single Bond Analyzer", "📤 Export", "❓ How It Works"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: SCREENER TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<p class="section-header">Bond Screener · {len(filtered)} bonds shown</p>', unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No bonds match the current filters. Try relaxing the filters in the sidebar.")
    else:
        display_cols = ["SECURITY NAME", "YTM (%)", "G-SEC YIELD (%)", "SPREAD (bps)",
                        "LAST CUT-OFF (%)", "DELTA (bps)", "SIGNAL", "SCORE"]
        if "STATE" in filtered.columns:      display_cols.insert(1, "STATE")
        if "MATURITY" in filtered.columns:   display_cols.insert(2, "MATURITY")
        if "LIQUIDITY" in filtered.columns:  display_cols.append("LIQUIDITY")

        display_cols = [c for c in display_cols if c in filtered.columns]
        show_df = filtered[display_cols].sort_values("SCORE", ascending=False).reset_index(drop=True)

        def style_table(df_s):
            styles = pd.DataFrame("", index=df_s.index, columns=df_s.columns)
            if "SIGNAL" in df_s.columns:
                for idx, val in df_s["SIGNAL"].items():
                    styles.at[idx, "SIGNAL"] = color_signal(val)
            if "SPREAD (bps)" in df_s.columns:
                for idx, val in df_s["SPREAD (bps)"].items():
                    styles.at[idx, "SPREAD (bps)"] = color_spread(val)
            if "DELTA (bps)" in df_s.columns:
                for idx, val in df_s["DELTA (bps)"].items():
                    styles.at[idx, "DELTA (bps)"] = color_delta(val)
            return styles

        styled = show_df.style.apply(style_table, axis=None).format({
            "YTM (%)":          "{:.2f}%",
            "G-SEC YIELD (%)":  "{:.2f}%",
            "LAST CUT-OFF (%)": "{:.2f}%",
            "SPREAD (bps)":     "{:.1f}",
            "DELTA (bps)":      "{:+.1f}",
        })

        st.dataframe(styled, use_container_width=True, height=420)

        # Insights
        st.markdown("---")
        st.markdown('<p class="section-header">💡 AI Insights</p>', unsafe_allow_html=True)

        strong_buys = filtered[filtered["SIGNAL"] == "🟢 STRONG BUY"]
        if not strong_buys.empty:
            top = strong_buys.iloc[0]
            st.markdown(f"""<div class="insight-box">
                🟢 <b>Top Pick:</b> <b>{top['SECURITY NAME']}</b> is trading at <b>{top['SPREAD (bps)']:.1f} bps</b> over G-Sec —
                {'+' if top['DELTA (bps)'] > 0 else ''}{top['DELTA (bps)']:.1f} bps vs last auction cut-off.
                Score: {top['SCORE']}/7. Strong buying opportunity.
            </div>""", unsafe_allow_html=True)

        high_spread = filtered[filtered["SPREAD (bps)"] >= 70]
        if not high_spread.empty:
            st.markdown(f"""<div class="insight-box">
                📌 <b>{len(high_spread)} bond(s)</b> are trading at <b>≥70 bps spread</b> — classified as <b>Very Cheap</b>.
                These offer exceptional value relative to benchmark G-Secs.
            </div>""", unsafe_allow_html=True)

        neg_delta = filtered[filtered["DELTA (bps)"] < 0]
        if not neg_delta.empty:
            st.markdown(f"""<div class="insight-box">
                ⚠️ <b>{len(neg_delta)} bond(s)</b> are trading <b>below their last auction cut-off</b> —
                these look relatively expensive versus where they were issued.
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: CHARTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-header">Spread Distribution</p>', unsafe_allow_html=True)
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df["SPREAD (bps)"],
            nbinsx=15,
            marker=dict(
                color=df["SPREAD (bps)"],
                colorscale=[[0,"#f87171"],[0.4,"#fbbf24"],[0.7,"#60a5fa"],[1,"#4ade80"]],
                showscale=False,
            ),
            name="Spread",
        ))
        fig_hist.add_vline(x=40, line_dash="dash", line_color="#f87171", annotation_text="40 bps (floor)")
        fig_hist.add_vline(x=50, line_dash="dash", line_color="#60a5fa", annotation_text="50 bps (attractive)")
        fig_hist.add_vline(x=70, line_dash="dash", line_color="#4ade80", annotation_text="70 bps (very cheap)")
        fig_hist.update_layout(
            plot_bgcolor="#0f172a", paper_bgcolor="#0a0e1a",
            font_color="#94a3b8", height=340,
            xaxis_title="Spread (bps)", yaxis_title="Count",
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.markdown('<p class="section-header">Signal Breakdown</p>', unsafe_allow_html=True)
        sig_counts = df["SIGNAL"].value_counts()
        colors_pie = {"🟢 STRONG BUY":"#4ade80","🔵 BUY":"#60a5fa","🟡 WATCH":"#fbbf24","⚪ HOLD":"#94a3b8","🔴 AVOID":"#f87171"}
        fig_pie = go.Figure(go.Pie(
            labels=sig_counts.index,
            values=sig_counts.values,
            marker=dict(colors=[colors_pie.get(l, "#64748b") for l in sig_counts.index]),
            hole=0.4,
        ))
        fig_pie.update_layout(
            plot_bgcolor="#0f172a", paper_bgcolor="#0a0e1a",
            font_color="#94a3b8", height=340,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color="#94a3b8")),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Spread vs YTM Scatter
    st.markdown('<p class="section-header">Spread vs YTM — Opportunity Map</p>', unsafe_allow_html=True)
    color_map = {"🟢 STRONG BUY":"#4ade80","🔵 BUY":"#60a5fa","🟡 WATCH":"#fbbf24","⚪ HOLD":"#94a3b8","🔴 AVOID":"#f87171"}
    fig_scatter = go.Figure()
    for sig, grp in df.groupby("SIGNAL"):
        hover_text = grp.apply(
            lambda r: f"<b>{r['SECURITY NAME']}</b><br>YTM: {r['YTM (%)']:.2f}%<br>Spread: {r['SPREAD (bps)']:.1f}bps<br>Score: {r['SCORE']}",
            axis=1
        )
        fig_scatter.add_trace(go.Scatter(
            x=grp["YTM (%)"],
            y=grp["SPREAD (bps)"],
            mode="markers+text",
            name=sig,
            marker=dict(color=color_map.get(sig,"#64748b"), size=14, opacity=0.85),
            text=grp["SECURITY NAME"].str[:8] if "SECURITY NAME" in grp.columns else "",
            textposition="top center",
            textfont=dict(size=9, color="#94a3b8"),
            hovertext=hover_text,
            hoverinfo="text",
        ))
    fig_scatter.add_hrect(y0=50, y1=70, fillcolor="#1d4ed8", opacity=0.06, annotation_text="Attractive zone")
    fig_scatter.add_hrect(y0=70, y1=120, fillcolor="#16a34a", opacity=0.06, annotation_text="Very Cheap zone")
    fig_scatter.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="#0a0e1a",
        font_color="#94a3b8", height=420,
        xaxis_title="YTM (%)", yaxis_title="Spread over G-Sec (bps)",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(font=dict(color="#94a3b8")),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Yield curve if MATURITY exists
    if "MATURITY" in df.columns:
        st.markdown('<p class="section-header">SDL Yield Curve</p>', unsafe_allow_html=True)
        curve_df = df.sort_values("MATURITY")
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=curve_df["MATURITY"], y=curve_df["YTM (%)"],
            mode="lines+markers", name="SDL YTM",
            line=dict(color="#60a5fa", width=2),
            marker=dict(size=8),
        ))
        fig_curve.add_trace(go.Scatter(
            x=curve_df["MATURITY"], y=curve_df["G-SEC YIELD (%)"],
            mode="lines+markers", name="G-Sec Yield",
            line=dict(color="#f87171", width=2, dash="dot"),
            marker=dict(size=6),
        ))
        fig_curve.update_layout(
            plot_bgcolor="#0f172a", paper_bgcolor="#0a0e1a",
            font_color="#94a3b8", height=340,
            xaxis_title="Maturity Year", yaxis_title="Yield (%)",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color="#94a3b8")),
        )
        st.plotly_chart(fig_curve, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: SINGLE BOND ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">Single Bond Deep-Dive Analyzer</p>', unsafe_allow_html=True)
    st.markdown("Enter any SDL or G-Sec details to get an instant professional assessment.")

    col_a, col_b = st.columns(2)
    with col_a:
        bond_name     = st.text_input("Bond / Security Name", "MH SDL 2034")
        ytm_input     = st.number_input("YTM (%)", 6.0, 12.0, 7.64, 0.01, format="%.2f")
        gsec_input    = st.number_input("Benchmark G-Sec Yield (%)", 5.0, 12.0, 7.10, 0.01, format="%.2f")
    with col_b:
        cutoff_input  = st.number_input("Last Auction Cut-off (%)", 5.0, 12.0, 7.58, 0.01, format="%.2f")
        liq_input     = st.selectbox("Liquidity", ["High", "Medium", "Low"])
        state_input   = st.selectbox("State", ["Maharashtra", "Gujarat", "Karnataka", "Tamil Nadu",
                                                 "Andhra Pradesh", "Punjab", "Rajasthan", "Uttar Pradesh", "Other"])

    if st.button("🔍 Analyze Bond", use_container_width=True):
        spread = round((ytm_input - gsec_input) * 100, 2)
        delta  = round((ytm_input - cutoff_input) * 100, 2)

        score = 0
        reasons = []

        # Spread
        if spread >= 70:
            score += 3; reasons.append(("✅", f"Spread is {spread} bps — Very Cheap (≥70 bps). Strong value."))
        elif spread >= 50:
            score += 2; reasons.append(("✅", f"Spread is {spread} bps — Attractive (50–70 bps). Good opportunity."))
        elif spread >= 40:
            score += 1; reasons.append(("🟡", f"Spread is {spread} bps — Normal range (40–50 bps). Fair value."))
        else:
            score -= 1; reasons.append(("❌", f"Spread is {spread} bps — Expensive (<40 bps). Avoid buying."))

        # Delta
        if delta > 0:
            score += 2; reasons.append(("✅", f"Yield is +{delta} bps above last auction — bond is cheaper than issuance."))
        elif delta == 0:
            reasons.append(("🟡", "Yield is at par with last auction cut-off."))
        else:
            score -= 1; reasons.append(("❌", f"Yield is {delta} bps below last auction — more expensive than issue price."))

        # Liquidity
        if liq_input == "High":
            score += 2; reasons.append(("✅", "Liquidity is High — easy to exit position."))
        elif liq_input == "Medium":
            score += 1; reasons.append(("🟡", "Liquidity is Medium — moderate exit risk."))
        else:
            score -= 1; reasons.append(("❌", "Liquidity is Low — hard to sell, illiquidity premium exists."))

        # State
        if state_input in LOW_RISK_STATES:
            score += 1; reasons.append(("✅", f"{state_input} has strong fiscal reputation — lower credit risk."))
        elif state_input in HIGH_RISK_STATES:
            score -= 1; reasons.append(("⚠️", f"{state_input} carries higher fiscal risk — factor in state premium."))
        else:
            reasons.append(("🟡", f"{state_input} — neutral state risk assessment."))

        # Final signal
        if score >= 6:   final_signal, cls = "🟢 STRONG BUY",  "banner-good"
        elif score >= 4: final_signal, cls = "🔵 BUY",         "banner-good"
        elif score >= 2: final_signal, cls = "🟡 WATCH",       "banner-avg"
        elif score >= 0: final_signal, cls = "⚪ HOLD",         "banner-avg"
        else:            final_signal, cls = "🔴 AVOID",        "banner-bad"

        st.markdown("---")
        st.markdown(f'<div class="{cls}"><b>{bond_name}</b> &nbsp;→&nbsp; {final_signal} &nbsp; | &nbsp; Score: {score}/8 &nbsp; | &nbsp; Spread: {spread} bps &nbsp; | &nbsp; Δ vs auction: {delta:+.1f} bps</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**Analysis Breakdown:**")
        for icon, txt in reasons:
            st.markdown(f"{icon} {txt}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Mini gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Bond Score", "font": {"color": "#94a3b8"}},
            gauge={
                "axis":  {"range": [-3, 8], "tickcolor": "#475569"},
                "bar":   {"color": "#38bdf8"},
                "steps": [
                    {"range": [-3, 0], "color": "#450a0a"},
                    {"range": [0, 2],  "color": "#292524"},
                    {"range": [2, 4],  "color": "#1c1400"},
                    {"range": [4, 6],  "color": "#052e16"},
                    {"range": [6, 8],  "color": "#14532d"},
                ],
                "threshold": {"line": {"color": "#4ade80", "width": 3}, "value": 6},
            },
            number={"font": {"color": "#e2e8f0"}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#0a0e1a", font_color="#94a3b8", height=260,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">Export Screener Data</p>', unsafe_allow_html=True)
    st.markdown("Download the full screened & analyzed data as Excel or CSV.")

    export_df = df.copy()

    c1, c2 = st.columns(2)
    with c1:
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name=f"bond_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Bond Screener")
        xlsx_data = output.getvalue()
        st.download_button(
            "⬇️ Download Excel",
            data=xlsx_data,
            file_name=f"bond_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("**Preview of export data:**")
    st.dataframe(export_df.head(10), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: HOW IT WORKS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-header">Methodology — How the AI Scoring Works</p>', unsafe_allow_html=True)

    st.markdown("""
<div class="insight-box">
The Bond AI Screener uses a <b>multi-factor scoring model</b> used by professional fixed-income dealers to quickly rank SDL and G-Sec securities by attractiveness.
</div>
""", unsafe_allow_html=True)

    st.markdown("### 📐 Scoring Model (Max 8 Points)")

    scoring_data = {
        "Factor": ["Spread vs G-Sec", "Spread vs G-Sec", "Spread vs G-Sec", "Spread vs G-Sec",
                   "Delta vs Auction", "Delta vs Auction", "Delta vs Auction",
                   "Liquidity", "Liquidity", "Liquidity",
                   "State Risk", "State Risk"],
        "Condition": [
            "≥ 70 bps (Very Cheap)", "50–70 bps (Attractive)", "40–50 bps (Normal)", "< 40 bps (Expensive)",
            "YTM > Last Cut-off", "YTM = Last Cut-off", "YTM < Last Cut-off",
            "High", "Medium", "Low",
            "Strong fiscal state (MH, GJ, KA, TN)", "High-risk state (AP, PB, RJ, HP)",
        ],
        "Points": ["+3", "+2", "+1", "-1", "+2", "0", "-1", "+2", "+1", "-1", "+1", "-1"],
    }
    st.dataframe(pd.DataFrame(scoring_data), use_container_width=True, hide_index=True)

    st.markdown("### 🏷️ Signal Thresholds")
    signal_data = {
        "Score": ["6–8", "4–5", "2–3", "0–1", "< 0"],
        "Signal": ["🟢 STRONG BUY", "🔵 BUY", "🟡 WATCH", "⚪ HOLD", "🔴 AVOID"],
        "Meaning": [
            "All criteria met — very attractive entry point",
            "Most criteria met — good opportunity",
            "Some criteria met — monitor closely",
            "Neutral — no strong case to buy",
            "Overpriced or illiquid — avoid",
        ],
    }
    st.dataframe(pd.DataFrame(signal_data), use_container_width=True, hide_index=True)

    st.markdown("### 💡 Pro Tips from the Desk")
    tips = [
        "Always compare same-state SDLs — don't compare MH SDL vs AP SDL directly.",
        "High yield ≠ good. Check liquidity first — illiquid bonds can be a trap.",
        "A spread above 70 bps is rare and usually a strong buying opportunity.",
        "Delta vs last auction is often more important than absolute spread.",
        "In a rate-cutting cycle, even 'Hold' rated bonds can appreciate.",
        "For SDLs, auction dates drive pricing — follow the auction calendar.",
    ]
    for tip in tips:
        st.markdown(f"<div class='insight-box'>💬 {tip}</div>", unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#334155;font-size:0.75rem;font-family:DM Mono,monospace'>"
    "Bond AI Screener · For professional use · Not financial advice · "
    f"Last refreshed: {datetime.now().strftime('%d %b %Y %H:%M')}"
    "</p>",
    unsafe_allow_html=True,
)
