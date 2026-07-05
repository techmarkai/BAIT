"""Device Registry integration for BAIT devices."""
from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN


@callback
def async_upsert_device(hass: HomeAssistant, entry_id: str, record: dict) -> None:
    """Create or update the Device Registry entry for a BAIT device."""
    registry = dr.async_get(hass)
    registry.async_get_or_create(
        config_entry_id=entry_id,
        identifiers={(DOMAIN, record["device_id"])},
        manufacturer="BAIT",
        name=record["name"],
        model=record["platform"],
        sw_version=record["app_version"],
    )
