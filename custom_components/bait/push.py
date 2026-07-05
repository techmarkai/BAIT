"""Sending push notifications via the Firebase Admin SDK."""
from __future__ import annotations

import json
import logging
from collections.abc import Callable

import firebase_admin
from firebase_admin import credentials, messaging

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


def build_firebase_app(service_account_json: str, name: str):
    """Initialize (or return) a named firebase_admin app from a JSON string."""
    cred = credentials.Certificate(json.loads(service_account_json))
    try:
        return firebase_admin.get_app(name)
    except ValueError:
        return firebase_admin.initialize_app(cred, name=name)


def build_message(
    token: str,
    title: str | None,
    body: str | None,
    data: dict,
) -> messaging.Message:
    """Build a fully-configured FCM message for one token.

    Adds a high-priority Android config on the payload's per-category channel
    (falling back to "other"), a big-picture image when provided, and an APNs
    config enabling rich media (mutable-content) + action categories on iOS.
    The `data` map is forwarded verbatim (string-coerced, as FCM requires).
    """
    str_data = {k: str(v) for k, v in (data or {}).items()}
    category = str_data.get("category") or "other"
    image = str_data.get("image")

    return messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body, image=image),
        data=str_data,
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                channel_id=category,
                image=image,
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default",
                    mutable_content=True,
                    category=category,
                ),
            ),
        ),
    )


class BaitPush:
    """Sends FCM messages for stored device tokens.

    `app` is the initialized firebase_admin app. `prune` is called with a token
    string when FCM reports it is no longer registered.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        app,
        prune: Callable[[str], object],
    ) -> None:
        self._hass = hass
        self._app = app
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

        messages = [build_message(token, title, body, data) for token in tokens]
        try:
            batch = await self._hass.async_add_executor_job(self._send_each, messages)
        except Exception:  # noqa: BLE001 - whole-batch failure: log, no prune, not fatal
            _LOGGER.exception("BAIT push batch send failed")
            return

        for token, response in zip(tokens, batch.responses):
            if response.success:
                continue
            exc = response.exception
            if isinstance(exc, messaging.UnregisteredError):
                _LOGGER.info("Pruning unregistered BAIT push token")
                self._prune(token)
            else:
                _LOGGER.error("BAIT push send failed for a token: %s", exc)

    def _send_each(self, messages: list[messaging.Message]):
        return messaging.send_each(messages, app=self._app)
