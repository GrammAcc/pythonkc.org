import secrets
from pathlib import Path

print("generating test env vars...")

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
    "EVENTS_DB_URI=sqlite+aiosqlite:///env/dbs/test.events.db",
    "MEMBERS_DB_URI=sqlite+aiosqlite:///env/dbs/test.members.db",
    "BASE_URL=/",
    "GRAMMLOG_DIR=env/logs",
    "DEFAULT_GRAMMLOG_LEVEL=WARNING",
    "DISCORD_CLIENT_ID=test",
    "DISCORD_CLIENT_SECRET=test",
]

with open("env/test.env", "w") as file:
    file.write("\n".join(envlines))


ssl_cert_path = str(Path("env/certs/localhost.pem").absolute())
ssl_key_path = str(Path("env/certs/localhost-key.pem").absolute())
ssl_fullchain_path = str(Path("env/certs/root-ca.pem").absolute())

serverlines = [
    f'bind = "127.0.0.1:{port}"',
    f'certfile = "{ssl_cert_path}"',
    f'keyfile = "{ssl_key_path}"',
    f'ca-certs = "{ssl_fullchain_path}"',
]

with open("env/test.server.toml", "w") as file:
    file.write("\n".join(serverlines))
