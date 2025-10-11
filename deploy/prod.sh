source .venv/bin/activate
pip install .
APPENV=prod hypercorn --config env/prod.server.toml "pykc:create_app()"
