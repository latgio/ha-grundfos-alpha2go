"""BLE client for Grundfos ALPHA2 GO."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from bleak import BleakClient
from bleak_retry_connector import establish_connection

from .diagnostics import log_ble_packet
from .recorder import record_ble_packet

_LOGGER = logging.getLogger(__name__)

DEVICE_INFO_SERVICE = "0000180a-0000-1000-8000-00805f9b34fb"
CHAR_MODEL_NUMBER = "00002a24-0000-1000-8000-00805f9b34fb"
CHAR_FIRMWARE = "00002a26-0000-1000-8000-00805f9b34fb"
CHAR_DEVICE_NAME = "00002a00-0000-1000-8000-00805f9b34fb"

GRUNDFOS_SERVICE_UUID = "0000fe5d-0000-1000-8000-00805f9b34fb"
GENI_SERVICE_UUID = GRUNDFOS_SERVICE_UUID
GRUNDFOS_CHAR_UUID = "859cffd1-036e-432a-aa28-1a0085b87ba9"


@dataclass
class PumpData:
    """Pump state read from Bluetooth."""

    model: str | None = None
    firmware: str | None = None
    device_name: str | None = None
    connected: bool = False
    rssi: int | None = None
    notifications: int = 0


class Alpha2GoClient:
    """BLE client for a Grundfos ALPHA2 GO pump."""

    def __init__(self, address: str) -> None:
        self._address = address
        self._client: BleakClient | None = None
        self._notification_count = 0

    async def connect(self) -> None:
        """Connect to the pump and subscribe to proprietary notifications."""
        _LOGGER.debug("Connecting to ALPHA2 GO at %s", self._address)
        self._client = await establish_connection(
            BleakClient,
            self._address,
            self._address,
            disconnected_callback=self._on_disconnect,
            timeout=20.0,
        )
        _LOGGER.info("Connected to ALPHA2 GO %s", self._address)

        try:
            await self._client.start_notify(GRUNDFOS_CHAR_UUID, self._on_notify)
            _LOGGER.debug("Notifications enabled on Grundfos characteristic")
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("Could not enable notifications: %s", exc)

    async def disconnect(self) -> None:
        """Disconnect from the pump."""
        if self._client and self._client.is_connected:
            await self._client.disconnect()
        self._client = None

    def _on_disconnect(self, _client: BleakClient) -> None:
        _LOGGER.warning("ALPHA2 GO %s disconnected", self._address)
        self._client = None

    def _on_notify(self, _handle: int, data: bytes) -> None:
        """Handle a BLE notification from the pump."""
        self._notification_count += 1
        log_ble_packet(self._address, data, self._notification_count)
        record_ble_packet(self._address, data, self._notification_count)

    @property
    def is_connected(self) -> bool:
        """Return whether the client is currently connected."""
        return self._client is not None and self._client.is_connected

    async def _read_char(self, uuid: str) -> str | None:
        if self._client is None:
            return None
        try:
            data = await self._client.read_gatt_char(uuid)
            return data.decode("utf-8", errors="ignore").strip("\x00").strip()
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug("Cannot read %s from %s: %s", uuid, self._address, exc)
            return None

    async def poll(self, timeout: float = 15.0) -> PumpData | None:
        """Connect if needed and read all currently available pump information."""
        if not self.is_connected:
            try:
                await asyncio.wait_for(self.connect(), timeout=timeout)
            except Exception as exc:  # noqa: BLE001
                _LOGGER.error("Cannot connect to pump %s: %s", self._address, exc)
                return None

        data = PumpData(
            connected=self.is_connected,
            notifications=self._notification_count,
        )
        data.device_name = await self._read_char(CHAR_DEVICE_NAME)
        data.model = await self._read_char(CHAR_MODEL_NUMBER)
        data.firmware = await self._read_char(CHAR_FIRMWARE)

        _LOGGER.debug(
            "Pump %s name=%s model=%s firmware=%s notifications=%d",
            self._address,
            data.device_name,
            data.model,
            data.firmware,
            data.notifications,
        )

        return data
