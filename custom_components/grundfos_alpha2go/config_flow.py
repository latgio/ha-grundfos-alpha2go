"""Config flow for Grundfos ALPHA2 GO."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_ADDRESS, CONF_NAME, DEFAULT_NAME, DEVICE_NAME_PREFIX, DOMAIN
from .genibus import GRUNDFOS_SERVICE_UUID

_LOGGER = logging.getLogger(__name__)

MANUAL_OPTION = "__manual__"


class Alpha2GoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grundfos ALPHA2 GO."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_address: str = ""
        self._discovered_name: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial user step."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]

            if address == MANUAL_OPTION:
                return await self.async_step_manual()

            name = user_input.get(CONF_NAME, DEFAULT_NAME)
            return await self._create_entry(address, name)

        discovered = self._find_discovered_pumps()

        if discovered:
            device_options = {
                address: f"{name} ({address})" for address, name in discovered.items()
            }
            device_options[MANUAL_OPTION] = "Saisir une adresse manuellement"

            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_ADDRESS): vol.In(device_options),
                        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    }
                ),
                errors={},
            )

        return await self.async_step_manual()

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual Bluetooth address entry."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip().upper()
            name = user_input.get(CONF_NAME, DEFAULT_NAME)
            return await self._create_entry(address, name)

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors={},
        )

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle Bluetooth discovery."""
        if not self._is_alpha2go(discovery_info):
            return self.async_abort(reason="not_alpha2go")

        address = discovery_info.address
        name = discovery_info.name or DEFAULT_NAME

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {"name": name, "address": address}
        self._discovered_address = address
        self._discovered_name = name

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm Bluetooth-discovered pump."""
        if user_input is not None:
            return await self._create_entry(
                self._discovered_address,
                self._discovered_name,
            )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": self._discovered_name,
                "address": self._discovered_address,
            },
            errors={},
        )

    def _find_discovered_pumps(self) -> dict[str, str]:
        """Return known Bluetooth discoveries that look like ALPHA2 GO pumps."""
        discovered: dict[str, str] = {}

        for info in async_discovered_service_info(self.hass):
            if not self._is_alpha2go(info):
                continue

            discovered[info.address] = info.name or DEFAULT_NAME

        _LOGGER.debug("Discovered ALPHA2 GO candidates: %s", discovered)
        return discovered

    def _is_alpha2go(self, info: BluetoothServiceInfoBleak) -> bool:
        """Return whether a Bluetooth advertisement looks like an ALPHA2 GO."""
        service_uuids = {service.lower() for service in info.service_uuids}
        name = info.name or ""

        return GRUNDFOS_SERVICE_UUID.lower() in service_uuids or name.startswith(
            DEVICE_NAME_PREFIX
        )

    async def _create_entry(self, address: str, name: str) -> FlowResult:
        """Create a config entry."""
        address = address.strip().upper()
        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=name,
            data={
                CONF_ADDRESS: address,
                CONF_NAME: name,
            },
        )
