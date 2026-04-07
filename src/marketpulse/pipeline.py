from __future__ import annotations

from pathlib import Path

from .api_fetcher import CoinGeckoClient
from .config import AppConfig, COIN_IDS
from .data_processor import build_record, load_history, persist_history, utc_now_iso
from .logger import configure_logger
from .notifier import send_threshold_alerts
from .readme_updater import update_readme
from .visualizer import generate_latest_bar_chart, generate_trend_chart


def run_pipeline(base_dir: Path | None = None) -> int:
    config = AppConfig.from_env(base_dir=base_dir)
    config.ensure_directories()

    logger = configure_logger(config.log_path)
    logger.info("MarketPulse pipeline started")

    try:
        client = CoinGeckoClient()
        payload = client.fetch_prices(COIN_IDS, vs_currency=config.vs_currency)

        history = load_history(config.json_path)
        previous_record = history[-1] if history else None

        timestamp = utc_now_iso()
        processed = build_record(
            coin_ids=COIN_IDS,
            api_payload=payload,
            timestamp=timestamp,
            vs_currency=config.vs_currency,
            previous_record=previous_record,
        )

        persist_history(
            history=history,
            new_data=processed,
            json_path=config.json_path,
            csv_path=config.csv_path,
        )

        generate_trend_chart(config.csv_path, config.charts_dir / "price_trends.png")
        generate_latest_bar_chart(config.csv_path, config.charts_dir / "latest_snapshot.png")

        send_threshold_alerts(
            config=config,
            timestamp=processed.timestamp,
            run_to_run_changes=processed.run_to_run_changes,
            logger=logger,
        )

        update_readme(
            readme_path=config.readme_path,
            timestamp=processed.timestamp,
            current_prices=processed.current_prices,
            api_24h_changes=processed.api_24h_changes,
            run_to_run_changes=processed.run_to_run_changes,
            threshold=config.price_change_threshold,
        )

        logger.info("Pipeline completed successfully")
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline failed: %s", exc)
        return 1
