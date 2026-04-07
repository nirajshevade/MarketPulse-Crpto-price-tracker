from __future__ import annotations

from typing import Dict, Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class CoinGeckoClient:
    """Client wrapper around CoinGecko simple price endpoint with retries."""

    BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

    def __init__(self, timeout_seconds: int = 30) -> None:
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_prices(self, coin_ids: Iterable[str], vs_currency: str = "usd") -> Dict[str, Dict[str, float]]:
        ids = list(coin_ids)
        if not ids:
            raise ValueError("coin_ids cannot be empty")

        params = {
            "ids": ",".join(ids),
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
        }

        response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout_seconds)
        response.raise_for_status()
        payload = response.json()

        missing = [coin for coin in ids if coin not in payload]
        if missing:
            raise RuntimeError(f"Missing coins in API response: {', '.join(missing)}")

        return payload
