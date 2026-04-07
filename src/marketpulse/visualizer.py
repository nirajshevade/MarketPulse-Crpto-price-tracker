from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _read_dataframe(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df = df.sort_values("timestamp")
    return df


def generate_trend_chart(csv_path: Path, output_path: Path) -> None:
    df = _read_dataframe(csv_path)

    fig, ax = plt.subplots(figsize=(11, 6))

    if df.empty or len(df.columns) <= 1:
        ax.text(0.5, 0.5, "No historical data yet", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
    else:
        for coin in [col for col in df.columns if col != "timestamp"]:
            ax.plot(df["timestamp"], df[coin], marker="o", linewidth=2, label=coin.title())

        ax.set_title("Crypto Price Trend (USD)", fontsize=14)
        ax.set_xlabel("Timestamp (UTC)")
        ax.set_ylabel("Price (USD)")
        ax.grid(alpha=0.3)
        ax.legend(loc="best")
        fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def generate_latest_bar_chart(csv_path: Path, output_path: Path) -> None:
    df = _read_dataframe(csv_path)

    fig, ax = plt.subplots(figsize=(9, 5))

    if df.empty:
        ax.text(0.5, 0.5, "No historical data yet", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
    else:
        latest_row = df.iloc[-1]
        coins = [col for col in df.columns if col != "timestamp"]
        values = [float(latest_row[c]) for c in coins]

        bars = ax.bar([coin.title() for coin in coins], values)
        ax.set_title("Latest Snapshot (USD)", fontsize=14)
        ax.set_xlabel("Coin")
        ax.set_ylabel("Price (USD)")
        ax.bar_label(bars, fmt="%.2f")

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
