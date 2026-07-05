# BAIT — Home Assistant Integration

Push notifications for the BAIT mobile app, delivered from Home Assistant via
Firebase Cloud Messaging. The integration registers BAIT devices over an
authenticated HA endpoint, stores their FCM tokens, and exposes `notify`
services for automations.

## Install via HACS

1. In Home Assistant, open **HACS**.
2. Top-right menu → **Custom repositories**.
3. Add `https://github.com/techmarkai/BAIT` with category **Integration**.
4. Install **BAIT**, then **restart Home Assistant**.

## Configure

1. **Settings → Devices & Services → Add Integration → BAIT.**
2. Paste your Firebase **service-account JSON** (Firebase console → Project
   settings → Service accounts → *Generate new private key*).

The BAIT app then registers automatically over `/api/bait/register` using its
existing Home Assistant login — no extra configuration.

## Notify services

- `notify.bait_<device>` — one device
- `notify.bait_<user>` — all of a user's devices

The `data` object in a notify call is forwarded verbatim to FCM. Recognised
keys: `category`, `route` / `entity_id`, `event_id`, `image`, `actions`.

Example automation action:

```yaml
service: notify.bait_pixel
data:
  title: Front door
  message: The front door was unlocked
  data:
    category: security
    entity_id: lock.front_door
```

## License

MIT — see [LICENSE](LICENSE).
