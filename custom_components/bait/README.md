# BAIT Home Assistant Integration

Registers BAIT mobile devices and sends push notifications via the hosted BAIT
relay (Firebase Cloud Messaging). No Firebase project or key required.

## Install
Copy `custom_components/bait/` into your Home Assistant `config/custom_components/`
directory and restart HA.

## Configure
Settings → Devices & Services → Add Integration → **BAIT**. No input is needed —
the integration registers this Home Assistant with the BAIT push service
automatically.

## Endpoints (authenticated with a normal HA token)
- `POST /api/bait/register` — `{device_id, device_name, push_token, platform, app_version}`
- `POST /api/bait/unregister` — `{device_id}`

## Notify services
- `notify.bait_<device>` — one device
- `notify.bait_<user>` — all of a user's devices

`data` in the notify call is forwarded verbatim to FCM (keys: `category`,
`route`/`entity_id`, `event_id`, `image`, `actions`).
