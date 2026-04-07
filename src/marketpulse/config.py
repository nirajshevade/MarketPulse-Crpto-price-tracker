from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


COIN_IDS = ["bitcoin", "ethereum", "solana", "dogecoin"]
COIN_LABELS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "solana": "Solana",
    "dogecoin": "Dogecoin",
}


@dataclass(frozen=True)
class AppConfig:
    base_dir: Path
    data_dir: Path
    charts_dir: Path
    logs_dir: Path
    json_path: Path
    csv_path: Path
    readme_path: Path
    log_path: Path
    vs_currency: str
    price_change_threshold: float
    telegram_bot_token: str
    telegram_chat_id: str
    email_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    email_from: str
    email_to: str

    @classmethod
    def from_env(cls, base_dir: Path | None = None) -> "AppConfig":
        resolved_base = base_dir or Path.cwd()
        data_dir = resolved_base / "data"
        charts_dir = resolved_base / "charts"
        logs_dir = resolved_base / "logs"

        return cls(
            base_dir=resolved_base,
            data_dir=data_dir,
            charts_dir=charts_dir,
            logs_dir=logs_dir,
            json_path=data_dir / "historical_prices.json",
            csv_path=data_dir / "historical_prices.csv",
            readme_path=resolved_base / "README.md",
            log_path=logs_dir / "marketpulse.log",
            vs_currency=os.getenv("VS_CURRENCY", "usd"),
            price_change_threshold=float(os.getenv("PRICE_CHANGE_THRESHOLD", "5")),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
            email_enabled=os.getenv("EMAIL_ENABLED", "false").strip().lower() == "true",
            smtp_host=os.getenv("SMTP_HOST", "").strip(),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME", "").strip(),
            smtp_password=os.getenv("SMTP_PASSWORD", "").strip(),
            email_from=os.getenv("EMAIL_FROM", "").strip(),
            email_to=os.getenv("EMAIL_TO", "").strip(),
        )

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
