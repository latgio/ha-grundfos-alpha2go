"""Diagnostics helpers for Grundfos ALPHA2 GO."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

_LOGGER = logging.getLogger(__name__)


def log_ble_packet(address: str, payload: bytes, count: int) -> None:
    """Log a BLE packet in a compact, analysis-friendly format."""
    timestamp = datetime.now(UTC).isoformat(timespec="milliseconds")
    _LOGGER.debug(
        "BLE_RX timestamp=%s pump=%s count=%d len=%d payload=%s",
        timestamp,
        address,
        count,
        len(payload),
        payload.hex(" "),
    )
