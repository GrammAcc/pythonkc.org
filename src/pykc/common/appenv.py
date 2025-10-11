import os
from pathlib import Path


def _parse_env(env_str: str) -> dict[str, str]:
    return dict([line.split("=", maxsplit=1) for line in env_str.splitlines(keepends=False)])


def _set_env(env_dict: dict[str, str]) -> None:
    for k, v in env_dict.items():
        os.environ[k] = v


def load_from_str(env_str: str) -> None:
    _set_env(_parse_env(env_str))


def load(override: str = ""):
    env_name = override.lower() if override != "" else os.environ.get("APPENV", "").lower()
    assert env_name != "", "APPENV or explicit override must be provided"
    env_str = Path(f"env/{env_name.lower()}.env").read_text()
    load_from_str(env_str)
    top_env_path = Path(".env")
    if top_env_path.exists():
        top_env_str = top_env_path.read_text()
        load_from_str(top_env_str)


# Ensure env vars are loaded as soon as possible.
load()
