import secrets
from pathlib import Path

print("generating dev env vars...")

if not (local_env := Path("env")).exists():
    local_env.mkdir()
if not (db_env := local_env / "dbs").exists():
    db_env.mkdir()

jwt_secret = secrets.token_hex(32)
quart_secret = secrets.token_hex(32)

port = "8000"
hostname = "localhost"

envlines = [
    f"JWT_SECRET={jwt_secret}",
    f"QUART_SECRET={quart_secret}",
    f"SITE_ROOT=https://{hostname}:{port}",
    "EVENTS_DB_URI=sqlite+aiosqlite:///env/dbs/dev.events.db",
    "MEMBERS_DB_URI=sqlite+aiosqlite:///env/dbs/dev.members.db",
    "BASE_URL=/pykc",
    "GRAMMLOG_DIR=env/logs",
    "DEFAULT_GRAMMLOG_LEVEL=DEBUG",
]

with open("env/dev.env", "w") as file:
    file.write("\n".join(envlines))

serverlines = [
    'bind = "127.0.0.1:8002"',
]

with open("env/dev.server.toml", "w") as file:
    file.write("\n".join(serverlines))

ssl_cert_path = str(Path("env/certs/localhost.pem").absolute())
ssl_key_path = str(Path("env/certs/localhost-key.pem").absolute())
ssl_fullchain_path = str(Path("env/certs/root-ca.pem").absolute())


with open("deploy/nginx.conf.template", "r") as nginx_template:
    parsed = str(nginx_template.read())
    parsed = parsed.replace("[[ssl_cert_path]]", ssl_cert_path)
    parsed = parsed.replace("[[ssl_key_path]]", ssl_key_path)
    parsed = parsed.replace("[[port]]", port)
    parsed = parsed.replace("[[server_name]]", hostname)
    with open("env/nginx.conf", "w") as nginx_conf:
        nginx_conf.write(parsed)
