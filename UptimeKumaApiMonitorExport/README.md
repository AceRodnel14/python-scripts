# Uptime Kuma – List Monitor Endpoints (v2.x)

This utility connects to an Uptime Kuma 2.x server via the official Socket.IO interface (using the [`uptime-kuma-api`](https://pypi.org/project/uptime-kuma-api/) Python client) and prints all monitor endpoints (URLs, hostnames/ports, etc.) found by `get_monitors()` / `get_monitor()`.

> Uptime Kuma’s programmatic API is Socket.IO-first; monitor CRUD is performed over websocket events and **not** a public REST CRUD API. This script uses the Python wrapper to simplify those calls.  
> References: [Kuma API wiki](https://github.com/louislam/uptime-kuma/wiki/API-Documentation/692198f84f3675a53a8ece7eb91a6a84566ee98e), [wrapper `get_monitors()` docs](https://uptime-kuma-api.readthedocs.io/en/latest/api.html).  

## Requirements
- Python 3.8+
- `pip install uptime-kuma-api`

## Usage

```bash
export KUMA_URL="https://uptime.example.com"
# EITHER username/password:
export KUMA_USERNAME="admin"
export KUMA_PASSWORD="******"
# OR a JWT from a prior “Remember me” login:
# export KUMA_JWT="eyJhbGciOi..."

# Optional for self-signed certs:
# export KUMA_SSL_VERIFY=false

python UptimeKumaApiMonitorExport.py