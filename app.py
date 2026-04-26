import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bond AI Screener", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_excel("data.xlsx")

df = load_data()

# -----------------------------
# Sorting
# -----------------------------
sort_by = st.sidebar.selectbox(
    "Sort By",
    ["SCORE", "SPREAD (bps)", "YTM (%)"]
)

df = df.sort_values(by=sort_by, ascending=False)

# -----------------------------
# Valuation Tag
# -----------------------------
def valuation(row):
    if row["SPREAD (bps)"] > 80:
        return "CHEAP 🟢"
    elif row["SPREAD (bps)"] > 60:
        return "FAIR 🟡"
    else:
        return "EXPENSIVE 🔴"

df["VALUATION"] = df.apply(valuation, axis=1)

# -----------------------------
# UI
# -----------------------------
st.title("📊 Bond AI Screener (Dealer View)")

# Top trades
st.subheader("🔥 Top 5 Opportunities")
st.dataframe(
    df[[
        "SECURITY NAME",
        "PRICE",
        "YTM (%)",
        "SPREAD (bps)",
        "DELTA (bps)",
        "SCORE",
        "VALUATION"
    ]].head(5),
    use_container_width=True
)

# Full table
st.subheader("📊 Full Market View")
st.dataframe(
    df[[
        "SECURITY NAME",
        "PRICE",
        "YTM (%)",
        "SPREAD (bps)",
        "DELTA (bps)",
        "VOLUME",
        "SCORE",
        "VALUATION"
    ]],
    use_container_width=True
)

# -----------------------------
# Filter
# -----------------------------
st.sidebar.header("Filter")

security_filter = st.sidebar.multiselect(
    "Select Security",
    df["SECURITY NAME"].unique()
)

if security_filter:
    filtered = df[df["SECURITY NAME"].isin(security_filter)]
    st.subheader("Filtered Data")
    st.dataframe(filtered, use_container_width=True)

# -----------------------------
# Chart
# -----------------------------
st.subheader("📈 Spread Comparison")
st.bar_chart(df.set_index("SECURITY NAME")["SPREAD (bps)"])

# -----------------------------
# Best Trade Insight
# -----------------------------
best = df.iloc[0]

st.subheader("🧠 Dealer Insight")

st.success(f"""
Best Trade: {best['SECURITY NAME']}

Price: {best['PRICE']}
YTM: {best['YTM (%)']}%
Spread: {best['SPREAD (bps)']} bps

Why:
- High spread vs G-Sec
- Positive auction delta
- Good relative value
""")
