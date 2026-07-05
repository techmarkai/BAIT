"""Constants for the BAIT integration."""

DOMAIN = "bait"

STORAGE_KEY = "bait_devices"
STORAGE_VERSION = 1

# Config entry data
CONF_SERVICE_ACCOUNT = "service_account"

# HTTP endpoints
REGISTER_URL = "/api/bait/register"
UNREGISTER_URL = "/api/bait/unregister"

# hass.data[DOMAIN] sub-keys
DATA_ENTRIES = "entries"
DATA_VIEWS_REGISTERED = "views_registered"
