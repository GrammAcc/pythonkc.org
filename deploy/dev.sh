rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install .
python -m scripts.gendevenvwithproxy
APPENV=dev python -m scripts.seed_members
APPENV=dev python -m scripts.seed_events
APPENV=dev hypercorn --config env/dev.server.toml "pykc:create_app()"
