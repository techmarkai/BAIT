"""Dynamic notify services for BAIT devices."""
from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.util import slugify

from .push import BaitPush
from .store import BaitDeviceStore

NOTIFY_DOMAIN = "notify"


@callback
def async_register_device_services(
    hass: HomeAssistant,
    store: BaitDeviceStore,
    push: BaitPush,
    record: dict,
) -> None:
    """Register notify.bait_<device> and notify.bait_<user> for a device."""

    device_service = f"bait_{slugify(record['name'])}"
    user_service = f"bait_{slugify(record['user_id'])}"

    async def _send(tokens: list[str], call: ServiceCall) -> None:
        await push.async_send(
            tokens,
            title=call.data.get("title"),
            body=call.data.get("message"),
            data=call.data.get("data") or {},
        )

    async def _device_handler(call: ServiceCall) -> None:
        rec = store.by_device(record["device_id"])
        if rec:
            await _send([rec["push_token"]], call)

    async def _user_handler(call: ServiceCall) -> None:
        tokens = [r["push_token"] for r in store.by_user(record["user_id"])]
        if tokens:
            await _send(tokens, call)

    hass.services.async_register(NOTIFY_DOMAIN, device_service, _device_handler)
    hass.services.async_register(NOTIFY_DOMAIN, user_service, _user_handler)
