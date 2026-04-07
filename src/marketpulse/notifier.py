from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Dict, List

import requests

from .config import AppConfig, COIN_LABELS


def _format_alert_lines(changes: Dict[str, float], threshold: float) -> List[str]:
    exceeded = []
    for coin, change in changes.items():
        if abs(change) >= threshold:
            direction = "up" if change > 0 else "down"
            exceeded.append(f"- {COIN_LABELS.get(coin, coin)}: {change:.2f}% ({direction})")
    return exceeded


def _build_message(timestamp: str, lines: List[str], threshold: float) -> str:
    joined = "\n".join(lines)
    return (
        "MarketPulse Alert\n"
        f"Timestamp: {timestamp}\n"
        f"Threshold: +/-{threshold:.2f}%\n\n"
        f"Coins exceeding threshold:\n{joined}"
    )


def _send_telegram(config: AppConfig, message: str) -> None:
    if not config.telegram_bot_token or not config.telegram_chat_id:
        return

    endpoint = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    payload = {"chat_id": config.telegram_chat_id, "text": message}
    response = requests.post(endpoint, data=payload, timeout=20)
    response.raise_for_status()


def _send_email(config: AppConfig, message: str) -> None:
    if not config.email_enabled:
        return

    required = [
        config.smtp_host,
        config.smtp_username,
        config.smtp_password,
        config.email_from,
        config.email_to,
    ]
    if not all(required):
        return

    email_message = EmailMessage()
    email_message["Subject"] = "MarketPulse Price Alert"
    email_message["From"] = config.email_from
    email_message["To"] = config.email_to
    email_message.set_content(message)

    with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(config.smtp_username, config.smtp_password)
        smtp.send_message(email_message)


def send_threshold_alerts(
    config: AppConfig,
    timestamp: str,
    run_to_run_changes: Dict[str, float],
    logger: logging.Logger,
) -> List[str]:
    lines = _format_alert_lines(run_to_run_changes, config.price_change_threshold)
    if not lines:
        logger.info("No threshold alerts triggered")
        return []

    message = _build_message(timestamp, lines, config.price_change_threshold)
    channels: List[str] = []

    try:
        _send_telegram(config, message)
        if config.telegram_bot_token and config.telegram_chat_id:
            channels.append("telegram")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Telegram alert failed: %s", exc)

    try:
        _send_email(config, message)
        if config.email_enabled:
            channels.append("email")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Email alert failed: %s", exc)

    if channels:
        logger.info("Alerts sent via: %s", ", ".join(channels))
    else:
        logger.warning("Alert condition met but no notifier channel configured")

    return lines
