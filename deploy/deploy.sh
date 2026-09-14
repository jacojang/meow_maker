#!/usr/bin/env bash
# Deploy script for Meow Maker, intended to run ON an EC2 instance (Ubuntu)
# that already has the repo cloned and uv/node/npm/python3.12 installed.
#
# Placeholder path — adjust to match the real deployment location.
set -euo pipefail

REPO_DIR="/opt/meow-maker"

cd "$REPO_DIR"

git pull

npm --prefix web ci
npm --prefix web run build

uv sync --project server

sudo systemctl restart meow-maker
