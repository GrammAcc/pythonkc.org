import secrets
from pathlib import Path

print("generating prod env vars...")

if not (local_env := Path("env")).exists():
    local_env.mkdir()


port = "443"
hostname = "pythonkc.org"

# This script needs to be updated based on the server environment we are deploying to and our production ssl setup.
envlines = [
    f"JWT_SECRET={secrets.token_hex(32)}",
    f"QUART_SECRET={secrets.token_hex(32)}",
    f"SITE_ROOT=https://www.{hostname}",
    "DB_URI=sqlite+aiosqlite:////home/pykcuser/dbs/pykc/pykc.db",
    "MEMBERS_DB_URI=sqlite+aiosqlite:////home/pykcuser/dbs/pykc/members.db",
    "EVENTS_DB_URI=sqlite+aiosqlite:////home/pykcuser/dbs/pykc/events.db",
    "BASE_URL=/pykc",
    "GRAMMLOG_DIR=/home/pykcuser/logs/pykc",
    "DEFAULT_GRAMMLOG_LEVEL=ERROR",
]

with open("env/prod.env", "w") as file:
    file.write("\n".join(envlines))

ssl_fullchain_path = "/home/pykcuser/.acme.sh/pythonkc.org_ecc/fullchain.cer"
ssl_cert_path = "/home/pykcuser/.acme.sh/pythonkc.org_ecc/pythonkc.org.cer"
ssl_key_path = "/home/pykcuser/.acme.sh/pythonkc.org_ecc/pythonkc.org.key"

serverlines = [
    'bind = "127.0.0.1:8002"',
    # Comment above line and uncomment following lines to serve standalone.
    # f'certfile = "{ssl_cert_path}"',
    # f'keyfile = "{ssl_key_path}"',
    # f'ca-certs = "{ssl_fullchain_path}"',
]

with open("env/prod.server.toml", "w") as file:
    file.write("\n".join(serverlines))

with open("deploy/nginx.conf.template", "r") as nginx_template:
    parsed = str(nginx_template.read())
    parsed = parsed.replace("[[ssl_cert_path]]", ssl_fullchain_path)
    parsed = parsed.replace("[[ssl_key_path]]", ssl_key_path)
    parsed = parsed.replace("[[port]]", port)
    parsed = parsed.replace("[[server_name]]", hostname)
    with open("env/nginx.conf", "w") as nginx_conf:
        nginx_conf.write(parsed)
