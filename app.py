import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bond AI Screener", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("data.xlsx")

df = load_data()

df["Spread"] = (df["Yield"] - df["GSec Yield"]) * 100
df["Delta"] = (df["Yield"] - df["Last Cut-off"]) * 100

def calculate_score(row):
    score = 0
    if row["Spread"] > 80:
        score += 3
    elif row["Spread"] > 60:
        score += 2
    else:
        score += 1

    if row["Delta"] > 5:
        score += 3
    elif row["Delta"] > 0:
        score += 2
    else:
        score += 1

    if row["Volume"] > 200:
        score += 2
    else:
        score += 1

    return score

df["Score"] = df.apply(calculate_score, axis=1)
df = df.sort_values(by="Score", ascending=False)

st.title("📊 Bond AI Screener")

st.subheader("Top Opportunities")
st.dataframe(df.head(5), use_container_width=True)

st.subheader("Full Market View")
st.dataframe(df, use_container_width=True)

st.sidebar.header("Filter")
states = st.sidebar.multiselect("Select State", df["State"].unique())

if states:
    filtered = df[df["State"].isin(states)]
    st.subheader("Filtered Data")
    st.dataframe(filtered, use_container_width=True)

best = df.iloc[0]
st.subheader("Best Opportunity")
st.write(f"{best['ISIN']} ({best['State']})")
st.write(f"Spread: {best['Spread']:.2f} bps")
st.write(f"Score: {best['Score']}")
