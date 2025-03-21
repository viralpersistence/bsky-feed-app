#!/usr/bin/env bash

set -e

if [ ! -d "app_venv" ]; then
  virtualenv app_venv || exit
fi

. app_venv/bin/activate

pip install -r requirements.txt