"""The BAIT integration."""
from __future__ import annotations

import firebase_admin

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .const import (
    CONF_SERVICE_ACCOUNT,
    DATA_ENTRIES,
    DATA_VIEWS_REGISTERED,
    DOMAIN,
)
from .http_api import RegisterView, UnregisterView
from .notify import NOTIFY_DOMAIN, async_register_device_services
from .push import BaitPush, build_firebase_app
from .store import BaitDeviceStore


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BAIT from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    entries = domain_data.setdefault(DATA_ENTRIES, {})

    store = BaitDeviceStore(hass)
    await store.async_load()

    app = await hass.async_add_executor_job(
        build_firebase_app, entry.data[CONF_SERVICE_ACCOUNT], entry.entry_id
    )

    async def _prune(token: str) -> None:
        await store.async_prune_token(token)

    def _prune_sync(token: str) -> None:
        # Called from a firebase executor thread: schedule the async store write
        # on the event loop in a thread-safe way.
        hass.add_job(_prune, token)

    push = BaitPush(hass, app, prune=_prune_sync)

    entries[entry.entry_id] = {
        "store": store,
        "push": push,
        "entry_id": entry.entry_id,
        "app": app,
    }

    if not domain_data.get(DATA_VIEWS_REGISTERED):
        hass.http.register_view(RegisterView())
        hass.http.register_view(UnregisterView())
        domain_data[DATA_VIEWS_REGISTERED] = True

    for record in store.all():
        async_register_device_services(hass, store, push, record)

    return True


def _service_names_for(store: BaitDeviceStore) -> set[str]:
    """All notify service names derived from this store's device records."""
    names: set[str] = set()
    for record in store.all():
        names.add(f"bait_{slugify(record['name'])}")
        names.add(f"bait_{slugify(record['user_id'])}")
    return names


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a BAIT config entry: remove notify services and the firebase app."""
    ctx = hass.data.get(DOMAIN, {}).get(DATA_ENTRIES, {}).pop(entry.entry_id, None)
    if ctx is None:
        return True

    for name in _service_names_for(ctx["store"]):
        if hass.services.has_service(NOTIFY_DOMAIN, name):
            hass.services.async_remove(NOTIFY_DOMAIN, name)

    app = ctx.get("app")
    if app is not None:
        await hass.async_add_executor_job(firebase_admin.delete_app, app)

    return True
