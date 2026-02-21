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
    f"SITE_ROOT=http://{hostname}:{port}",
    "EVENTS_DB_URI=sqlite+aiosqlite:///env/dbs/dev.events.db",
    "MEMBERS_DB_URI=sqlite+aiosqlite:///env/dbs/dev.members.db",
    "BASE_URL=/",
    "GRAMMLOG_DIR=env/logs",
    "DEFAULT_GRAMMLOG_LEVEL=DEBUG",
]

with open("env/dev.env", "w") as file:
    file.write("\n".join(envlines))

serverlines = [
    f'bind = "127.0.0.1:{port}"',
]

with open("env/dev.server.toml", "w") as file:
    file.write("\n".join(serverlines))
