"""Diagnostics helpers."""

from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)


def log_ble_packet(address: str, payload: bytes) -> None:
    """Log a BLE packet in a readable format."""
    _LOGGER.debug(
        "BLE RX | pump=%s | len=%d | hex=%s",
        address,
        len(payload),
        payload.hex(" "),
    )
