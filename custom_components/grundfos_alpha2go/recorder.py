"""BLE capture recorder for reverse engineering."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

CAPTURE_DIR = Path("/config/grundfos_alpha2go")
CAPTURE_FILE = CAPTURE_DIR / "ble_capture.jsonl"


def record_ble_packet(address: str, payload: bytes, count: int) -> None:
    """Append a BLE packet to a JSONL capture file."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(timespec="milliseconds"),
        "pump": address,
        "count": count,
        "len": len(payload),
        "payload": payload.hex(" "),
    }

    try:
        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        with CAPTURE_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry) + "\n")
    except OSError as exc:
        _LOGGER.warning("Could not write BLE capture: %s", exc)
