"""Persistence of BAIT device/token records."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION


class BaitDeviceStore:
    """A Store-backed registry of device -> token records, keyed by device_id."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._devices: dict[str, dict] = {}

    async def async_load(self) -> None:
        data = await self._store.async_load()
        self._devices = dict(data or {})

    async def _async_save(self) -> None:
        await self._store.async_save(self._devices)

    async def async_upsert(self, record: dict) -> None:
        self._devices[record["device_id"]] = record
        await self._async_save()

    async def async_remove(self, device_id: str) -> None:
        if self._devices.pop(device_id, None) is not None:
            await self._async_save()

    async def async_prune_token(self, token: str) -> None:
        removed = [d for d, r in self._devices.items() if r.get("push_token") == token]
        for device_id in removed:
            self._devices.pop(device_id, None)
        if removed:
            await self._async_save()

    def by_device(self, device_id: str) -> dict | None:
        return self._devices.get(device_id)

    def by_user(self, user_id: str) -> list[dict]:
        return [r for r in self._devices.values() if r.get("user_id") == user_id]

    def all(self) -> list[dict]:
        return list(self._devices.values())
