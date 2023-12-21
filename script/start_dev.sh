#! /bin/bash

# shellcheck source=/dev/null
source dfi-api.env

# shellcheck source=/dev/null
source tests.env

python3 -m pip install --upgrade pip --user
python3 -m venv .venv

# shellcheck source=/dev/null
source .venv/bin/activate
python3 -m pip install poetry
python3 -m poetry install

exec /bin/bash 