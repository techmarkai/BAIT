"""Config flow for the BAIT integration."""
from __future__ import annotations

import json
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow

from .const import CONF_SERVICE_ACCOUNT, DOMAIN


def validate_service_account(raw: str) -> None:
    """Raise ValueError if `raw` is not a plausible service-account JSON."""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as err:
        raise ValueError("not json") from err
    if parsed.get("type") != "service_account":
        raise ValueError("not a service account")


class BaitConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the BAIT config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self.hass.async_add_executor_job(
                    validate_service_account, user_input[CONF_SERVICE_ACCOUNT]
                )
            except ValueError:
                errors["base"] = "invalid_credentials"
            else:
                return self.async_create_entry(title="BAIT", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_SERVICE_ACCOUNT): str}),
            errors=errors,
        )
