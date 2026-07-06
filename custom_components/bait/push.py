"""Send push notifications by POSTing to the central BAIT relay."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import RELAY_URL

_LOGGER = logging.getLogger(__name__)


class BaitPush:
    """Relay client. Sends each token's notification to the BAIT relay.

    `prune` is an awaitable called with a token when the relay reports it is no
    longer registered.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        instance_id: str,
        instance_key: str,
        prune: Callable[[str], Awaitable[None]],
    ) -> None:
        self._hass = hass
        self._instance_id = instance_id
        self._instance_key = instance_key
        self._prune = prune

    async def async_send(
        self,
        tokens: list[str],
        *,
        title: str | None,
        body: str | None,
        data: dict,
    ) -> None:
        if not tokens:
            return

        session = async_get_clientsession(self._hass)
        for token in tokens:
            payload = {
                "instance_id": self._instance_id,
                "instance_key": self._instance_key,
                "token": token,
                "title": title,
                "body": body,
                "data": data or {},
            }
            try:
                resp = await session.post(
                    f"{RELAY_URL}/send",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                )
                result = await resp.json()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                _LOGGER.exception("BAIT relay send failed")
                continue

            if result.get("error") == "unregistered":
                _LOGGER.info("Pruning unregistered BAIT push token")
                await self._prune(token)
            elif not result.get("success"):
                _LOGGER.error("BAIT relay send error: %s", result.get("error"))
