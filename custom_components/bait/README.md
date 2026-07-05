# BAIT Home Assistant Integration

Registers BAIT mobile devices and sends push notifications via Firebase Cloud
Messaging.

## Install
Copy `custom_components/bait/` into your Home Assistant `config/custom_components/`
directory and restart HA.

## Configure
Settings → Devices & Services → Add Integration → **BAIT**. Paste your Firebase
service-account JSON (from the Firebase console → Project settings → Service
accounts → Generate new private key).

## Endpoints (authenticated with a normal HA token)
- `POST /api/bait/register` — `{device_id, device_name, push_token, platform, app_version}`
- `POST /api/bait/unregister` — `{device_id}`

## Notify services
- `notify.bait_<device>` — one device
- `notify.bait_<user>` — all of a user's devices

`data` in the notify call is forwarded verbatim to FCM (keys: `category`,
`route`/`entity_id`, `event_id`, `image`, `actions`).
