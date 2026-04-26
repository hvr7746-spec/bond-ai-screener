import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bond AI Screener", layout="wide")

# Load data from the CSV file
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    # Convert numeric columns and handle empty values
   df["SPREAD (bps)"] = (df["YTM (%)"] - df["G-SEC YIELD (%)"]) * 100
   df["DELTA (bps)"] = (df["YTM (%)"] - df["LAST CUT-OFF (%)"]) * 100
    return df

df = load_data()

# Sidebar for sorting
st.sidebar.header("Filter & Sort")
sort_by = st.sidebar.selectbox("Sort By", ["SCORE", "SPREAD (bps)", "YTM (%)"])
df = df.sort_values(by=sort_by, ascending=False)

# Valuation Logic
def valuation(row):
    if row["SPREAD (bps)"] > 80:
        return "CHEAP 🟢"
    elif row["SPREAD (bps)"] > 60:
        return "FAIR 🟡"
    else:
        return "EXPENSIVE 🔴"

df["VALUATION"] = df.apply(valuation, axis=1)

# App UI
st.title("📊 Bond AI Screener")

st.subheader("Top Opportunities")
st.dataframe(df.head(5), use_container_width=True)

st.subheader("Full Market View")
st.dataframe(df, use_container_width=True)
