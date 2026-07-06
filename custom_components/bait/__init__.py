"""The BAIT integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .const import (
    CONF_INSTANCE_ID,
    CONF_INSTANCE_KEY,
    DATA_ENTRIES,
    DATA_VIEWS_REGISTERED,
    DOMAIN,
)
from .http_api import RegisterView, UnregisterView
from .notify import NOTIFY_DOMAIN, async_register_device_services
from .push import BaitPush
from .store import BaitDeviceStore


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle migration of an old config entry.

    v1 entries stored a Firebase service-account JSON; the relay model (v2)
    stores per-install relay credentials instead. There is no data path from
    one to the other, so we fail migration cleanly — Home Assistant then
    surfaces a "reconfigure" state and the user removes and re-adds BAIT (the
    documented breaking-change upgrade), rather than a raw MIGRATION_ERROR.
    """
    return False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BAIT from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    entries = domain_data.setdefault(DATA_ENTRIES, {})

    store = BaitDeviceStore(hass)
    await store.async_load()

    push = BaitPush(
        hass,
        entry.data[CONF_INSTANCE_ID],
        entry.data[CONF_INSTANCE_KEY],
        prune=store.async_prune_token,
    )

    entries[entry.entry_id] = {
        "store": store,
        "push": push,
        "entry_id": entry.entry_id,
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
    """Unload a BAIT config entry: remove its notify services."""
    ctx = hass.data.get(DOMAIN, {}).get(DATA_ENTRIES, {}).pop(entry.entry_id, None)
    if ctx is None:
        return True

    for name in _service_names_for(ctx["store"]):
        if hass.services.has_service(NOTIFY_DOMAIN, name):
            hass.services.async_remove(NOTIFY_DOMAIN, name)

    return True
