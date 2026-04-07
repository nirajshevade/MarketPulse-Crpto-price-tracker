from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from marketpulse.config import COIN_LABELS


st.set_page_config(page_title="MarketPulse Dashboard", page_icon="MP", layout="wide")
st.title("MarketPulse - Crypto Price Tracker")
st.caption("Live-style dashboard from repository historical data")

csv_path = ROOT_DIR / "data" / "historical_prices.csv"
if not csv_path.exists():
    st.warning("No data found yet. Run: python scripts/run_pipeline.py")
    st.stop()


df = pd.read_csv(csv_path)
if df.empty:
    st.warning("Data file is empty. Run the pipeline to fetch the first snapshot.")
    st.stop()


df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
df = df.sort_values("timestamp")
latest = df.iloc[-1]

st.subheader("Latest Prices")
cols = st.columns(4)
coins = [coin for coin in df.columns if coin != "timestamp"]
for index, coin in enumerate(coins):
    value = float(latest[coin])
    label = COIN_LABELS.get(coin, coin.title())

    delta = 0.0
    if len(df) >= 2:
        prev = float(df.iloc[-2][coin])
        if prev != 0:
            delta = ((value - prev) / prev) * 100

    cols[index % 4].metric(label=label, value=f"${value:,.4f}", delta=f"{delta:+.2f}%")

st.subheader("Historical Trends")
plot_df = df.set_index("timestamp")
st.line_chart(plot_df[coins])

left, right = st.columns(2)
trend_chart_path = ROOT_DIR / "charts" / "price_trends.png"
snapshot_chart_path = ROOT_DIR / "charts" / "latest_snapshot.png"

with left:
    st.subheader("Generated Trend Chart")
    if trend_chart_path.exists():
        st.image(str(trend_chart_path), use_container_width=True)
    else:
        st.info("Trend chart not generated yet.")

with right:
    st.subheader("Generated Snapshot Chart")
    if snapshot_chart_path.exists():
        st.image(str(snapshot_chart_path), use_container_width=True)
    else:
        st.info("Snapshot chart not generated yet.")

st.caption(f"Last updated: {latest['timestamp']}")
