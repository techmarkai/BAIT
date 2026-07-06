"""Constants for the BAIT integration."""

DOMAIN = "bait"

STORAGE_KEY = "bait_devices"
STORAGE_VERSION = 1

# Config entry data (per-install relay credentials)
CONF_INSTANCE_ID = "instance_id"
CONF_INSTANCE_KEY = "instance_key"

# Central BAIT push relay (Firebase Cloud Functions in project bait-632d4).
# Update if the deployed region/URL differs.
RELAY_URL = "https://us-central1-bait-632d4.cloudfunctions.net"

# HTTP endpoints (phone -> HA)
REGISTER_URL = "/api/bait/register"
UNREGISTER_URL = "/api/bait/unregister"

# hass.data[DOMAIN] sub-keys
DATA_ENTRIES = "entries"
DATA_VIEWS_REGISTERED = "views_registered"
