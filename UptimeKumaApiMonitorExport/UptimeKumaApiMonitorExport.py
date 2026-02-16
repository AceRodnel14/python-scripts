# ===============================================
# Uptime Kuma 2.x – List all monitor endpoints
# Uses the 'uptime-kuma-api' Socket.IO client
# ===============================================

import os
import sys
from typing import Any, Dict, List, Optional

try:
    from uptime_kuma_api import UptimeKumaApi  # pip install uptime-kuma-api
except ImportError as exc:
    print("Missing dependency 'uptime-kuma-api'. Install with: pip install uptime-kuma-api")
    raise

# -----------------------------
# Helpers
# -----------------------------

def _endpoint_from_monitor(m: Dict[str, Any]) -> str:
    """
    Derive an endpoint string from a monitor object returned by uptime-kuma-api.
    Covers common monitor types (HTTP/HTTPS, PING, TCP/PORT, KEYWORD, etc.).
    Unknown types fall back to a useful summary.

    Fields are based on Kuma's internal monitor structure (accessed via Socket.IO).
    Ref: Kuma API (Socket.IO) + wrapper methods. 
    """
    mtype = (m.get("type") or "").lower()

    # HTTP / HTTPS / JSON_QUERY / KEYWORD / REAL_BROWSER share 'url'
    if mtype in {"http", "json_query", "keyword", "real_browser"} and m.get("url"):
        return m["url"]

    # PING + DNS primarily carry hostname
    if mtype in {"ping", "dns", "tailscale_ping"} and m.get("hostname"):
        return str(m["hostname"])

    # TCP/PORT monitors have host + port
    if mtype in {"port"} and m.get("hostname") and m.get("port") is not None:
        return f"{m['hostname']}:{m['port']}"

    # gRPC keyword checks may use grpcUrl
    if mtype in {"grpc_keyword"} and m.get("grpcUrl"):
        return m["grpcUrl"]

    # DB / Redis / Kafka producers etc. often carry connection strings or host/port
    for key in ("databaseConnectionString", "redisConnectionString", "kafkaBrokers"):
        if key in m and m.get(key):
            return str(m[key])

    # Docker monitor: container + host
    if mtype == "docker":
        container = m.get("docker_container") or m.get("dockerContainer")
        host = m.get("docker_host") or m.get("dockerHost")
        if container and host:
            return f"docker://{host}/{container}"
        if container:
            return f"docker://{container}"

    # PUSH monitors use a pushToken
    if mtype == "push" and m.get("pushToken"):
        return f"push://{m['pushToken']}"

    # MQTT may have hostname + port + topic
    if mtype == "mqtt":
        host = m.get("hostname") or ""
        port = m.get("port")
        topic = m.get("mqttTopic")
        base = f"{host}:{port}" if host and port is not None else host or ""
        return f"mqtt://{base}{(' topic=' + topic) if topic else ''}".strip()

    # Game servers / Steam / Gamedig: hostname + port
    if mtype in {"steam", "gamedig"} and m.get("hostname"):
        port = m.get("port")
        return f"{m['hostname']}:{port}" if port is not None else m["hostname"]

    # SQL Server / Postgres / MySQL can also expose host/port
    if mtype in {"sqlserver", "postgres", "mysql"} and m.get("hostname"):
        port = m.get("port")
        return f"{m['hostname']}:{port}" if port is not None else m["hostname"]

    # Default fallback: name + (id), type
    return f"{m.get('name', 'Unknown')} (type={mtype}, id={m.get('id')})"


def _format_monitor_line(m: Dict[str, Any]) -> str:
    tags = m.get("tags") or []
    tag_str = ""
    if tags:
        tag_names = [t.get("name") if isinstance(t, dict) else str(t) for t in tags]
        tag_str = f" [tags: {', '.join(tag_names)}]"

    # Example line:
    # [#12] API – https://api.example.com/health  (type=http) [tags: prod, critical]
    endpoint = _endpoint_from_monitor(m)
    mid = m.get("id") or "?"
    name = m.get("name") or "(no-name)"
    mtype = (m.get("type") or "?").lower()
    return f"[#{mid}] {name} – {endpoint}  (type={mtype}){tag_str}"


def list_endpoints(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    jwt_token: Optional[str] = None,
    ssl_verify: bool = True,
) -> List[str]:
    """
    Connect to Kuma and return formatted lines of all monitors' endpoints.

    Authentication:
      - username/password via `login`
      - or JWT via `login_by_token` (if you saved 'Remember me' before in the UI)

    Notes:
      * Kuma’s programmatic API is Socket.IO-first; the python client maps calls like
        `get_monitors()`/`get_monitor()` to the underlying events. 
      * v2.x still follows this model (full CRUD is via Socket.IO). 
    """
    lines: List[str] = []
    with UptimeKumaApi(url=url, ssl_verify=ssl_verify) as api:
        if jwt_token:
            api.login_by_token(jwt_token)
        else:
            if not username or not password:
                raise ValueError("username/password or jwt_token is required")
            api.login(username, password)

        monitors = api.get_monitors()  # returns list[dict]
        for m in monitors:
            lines.append(_format_monitor_line(m))

    return lines


# -----------------------------
# CLI entry
# -----------------------------

def main() -> int:
    """
    Environment variables (or pass as args if you prefer to extend):
        KUMA_URL          e.g. https://uptime.example.com
        KUMA_USERNAME     admin username (omit if using KUMA_JWT)
        KUMA_PASSWORD     admin password (omit if using KUMA_JWT)
        KUMA_JWT          JWT from a prior 'Remember me' login (optional)
        KUMA_SSL_VERIFY   'true'/'false' (default true)
    """
    url = os.getenv("KUMA_URL")
    username = os.getenv("KUMA_USERNAME")
    password = os.getenv("KUMA_PASSWORD")
    jwt_token = os.getenv("KUMA_JWT")
    ssl_verify_env = os.getenv("KUMA_SSL_VERIFY", "true").lower()
    ssl_verify = ssl_verify_env not in {"0", "false", "no"}

    if not url:
        print("ERROR: KUMA_URL is required")
        return 2

    try:
        lines = list_endpoints(url, username, password, jwt_token, ssl_verify)
        if not lines:
            print("No monitors found.")
        else:
            print("\n".join(lines))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())