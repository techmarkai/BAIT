"""HTTP endpoints for BAIT device registration."""
from __future__ import annotations

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DATA_ENTRIES, DOMAIN, REGISTER_URL, UNREGISTER_URL
from .device import async_upsert_device
from .notify import async_register_device_services

_REQUIRED = ("device_id", "device_name", "push_token", "platform", "app_version")


def _active_entry(hass: HomeAssistant) -> dict | None:
    """Return the single active BAIT entry context (single-instance integration)."""
    entries = hass.data.get(DOMAIN, {}).get(DATA_ENTRIES, {})
    return next(iter(entries.values()), None)


class RegisterView(HomeAssistantView):
    """POST /api/bait/register — register or update a device's push token."""

    url = REGISTER_URL
    name = "api:bait:register"
    requires_auth = True

    async def post(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        ctx = _active_entry(hass)
        if ctx is None:
            return self.json_message("BAIT not set up", status_code=503)

        try:
            body = await request.json()
        except ValueError:
            return self.json_message("Invalid JSON", status_code=400)

        if not isinstance(body, dict):
            return self.json_message("Invalid body", status_code=400)

        if any(not body.get(field) for field in _REQUIRED):
            return self.json_message("Missing fields", status_code=400)

        record = {
            "device_id": body["device_id"],
            "user_id": request["hass_user"].id,
            "push_token": body["push_token"],
            "platform": body["platform"],
            "app_version": body["app_version"],
            "name": body["device_name"],
        }
        await ctx["store"].async_upsert(record)
        async_upsert_device(hass, ctx["entry_id"], record)
        async_register_device_services(hass, ctx["store"], ctx["push"], record)
        return self.json({"device_id": record["device_id"]})


class UnregisterView(HomeAssistantView):
    """POST /api/bait/unregister — remove a device."""

    url = UNREGISTER_URL
    name = "api:bait:unregister"
    requires_auth = True

    async def post(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        ctx = _active_entry(hass)
        if ctx is None:
            return self.json_message("BAIT not set up", status_code=503)

        try:
            body = await request.json()
        except ValueError:
            return self.json_message("Invalid JSON", status_code=400)

        if not isinstance(body, dict):
            return self.json_message("Invalid body", status_code=400)

        device_id = body.get("device_id")
        if not device_id:
            return self.json_message("Missing device_id", status_code=400)
        await ctx["store"].async_remove(device_id)
        return self.json({"device_id": device_id})
