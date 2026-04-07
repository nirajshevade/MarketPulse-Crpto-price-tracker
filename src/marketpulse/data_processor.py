from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


@dataclass
class ProcessedPriceData:
    timestamp: str
    current_prices: Dict[str, float]
    api_24h_changes: Dict[str, float]
    run_to_run_changes: Dict[str, float]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_history(json_path: Path) -> List[Dict[str, float | str]]:
    if not json_path.exists():
        return []
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _calculate_change_percent(previous: float, current: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def build_record(
    coin_ids: list[str],
    api_payload: Dict[str, Dict[str, float]],
    timestamp: str,
    vs_currency: str,
    previous_record: Dict[str, float | str] | None,
) -> ProcessedPriceData:
    current_prices: Dict[str, float] = {}
    api_24h_changes: Dict[str, float] = {}
    run_to_run_changes: Dict[str, float] = {}

    for coin_id in coin_ids:
        details = api_payload[coin_id]
        currency_key = vs_currency.lower()
        change_key = f"{currency_key}_24h_change"

        current_price = float(details.get(currency_key, 0.0))
        api_change = float(details.get(change_key, 0.0) or 0.0)

        current_prices[coin_id] = current_price
        api_24h_changes[coin_id] = api_change

        if previous_record is None:
            run_to_run_changes[coin_id] = 0.0
        else:
            prev_value = float(previous_record.get(coin_id, 0.0) or 0.0)
            run_to_run_changes[coin_id] = _calculate_change_percent(prev_value, current_price)

    return ProcessedPriceData(
        timestamp=timestamp,
        current_prices=current_prices,
        api_24h_changes=api_24h_changes,
        run_to_run_changes=run_to_run_changes,
    )


def persist_history(
    history: List[Dict[str, float | str]],
    new_data: ProcessedPriceData,
    json_path: Path,
    csv_path: Path,
) -> None:
    json_row: Dict[str, float | str] = {"timestamp": new_data.timestamp}
    json_row.update(new_data.current_prices)
    history.append(json_row)

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)

    fieldnames = ["timestamp", *new_data.current_prices.keys()]
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(history)
