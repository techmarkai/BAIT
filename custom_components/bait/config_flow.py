"""Zero-config config flow for the BAIT integration.

Setup takes no user input: it registers this Home Assistant instance with the
central BAIT push relay and stores the returned per-install credentials.
"""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.instance_id import async_get as async_get_instance_id

from .const import (
    CONF_INSTANCE_ID,
    CONF_INSTANCE_KEY,
    DOMAIN,
    RELAY_URL,
)


class CannotConnect(Exception):
    """Raised when the BAIT relay cannot be reached."""


class BaitConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the BAIT config flow."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                creds = await self._register_instance()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="BAIT", data=creds)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({}), errors=errors
        )

    async def _register_instance(self) -> dict[str, str]:
        """Register this HA instance with the relay; return its credentials."""
        session = async_get_clientsession(self.hass)
        ha_uuid = await async_get_instance_id(self.hass)
        name = self.hass.config.location_name or "Home Assistant"
        try:
            resp = await session.post(
                f"{RELAY_URL}/register",
                json={"ha_uuid": ha_uuid, "name": name},
                timeout=aiohttp.ClientTimeout(total=10),
            )
            resp.raise_for_status()
            body = await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise CannotConnect from err
        return {
            CONF_INSTANCE_ID: body["instance_id"],
            CONF_INSTANCE_KEY: body["instance_key"],
        }
