# BAIT — Home Assistant Integration

Push notifications for the BAIT mobile app, delivered from Home Assistant via
Firebase Cloud Messaging. Notifications are relayed through the hosted BAIT push
service, so **you don't need your own Firebase project or any keys** — install,
add the integration, and it works.

## Install via HACS

1. In Home Assistant, open **HACS**.
2. Top-right menu → **Custom repositories**.
3. Add `https://github.com/techmarkai/BAIT` with category **Integration**.
4. Install **BAIT**, then **restart Home Assistant**.

## Configure

1. **Settings → Devices & Services → Add Integration → BAIT.**
2. There is nothing to fill in — just submit. The integration registers this
   Home Assistant with the BAIT push service automatically.

The BAIT app then registers your devices over `/api/bait/register` using their
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

## Upgrading from 0.1.x

0.2.0 replaces the "bring your own Firebase service-account JSON" setup with the
hosted relay. There is no automatic migration: **remove the old BAIT integration
and add it again** (Settings → Devices & Services). No Firebase key is needed
anymore.

## License

MIT — see [LICENSE](LICENSE).
