#!/usr/bin/env bash
# Routine deploy script for Meow Maker. Run LOCALLY, after the one-time
# deploy/setup-instance.sh has already been run once.
#
# web/ is built here on the local machine, and only the built web/dist/ is
# synced to the instance — Node is never installed there (see
# deploy/setup-instance.sh and docs/deployment/README.md for why). server/
# is updated via `git pull` + `uv sync` run directly on the instance, since
# it's plain Python source with no build step.
set -euo pipefail

HOST="54.116.51.0"
USER="ec2-user"
KEY="$HOME/.ssh/jacojang_new_key.pem"
REMOTE_DIR="/home/ec2-user/meow-maker"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Building web/ locally"
npm --prefix "$REPO_ROOT/web" ci
npm --prefix "$REPO_ROOT/web" run build

echo "==> Syncing web/dist/ to $HOST:$REMOTE_DIR/web/dist/"
rsync -avz --delete \
  -e "ssh -i $KEY" \
  "$REPO_ROOT/web/dist/" "$USER@$HOST:$REMOTE_DIR/web/dist/"

echo "==> Updating server/ on instance and restarting service"
ssh -i "$KEY" "$USER@$HOST" bash -s <<EOF
set -euo pipefail
git -C "$REMOTE_DIR" pull
~/.local/bin/uv sync --project "$REMOTE_DIR/server"
sudo systemctl restart meow-maker
EOF

echo "==> Checking health endpoint"
for attempt in 1 2 3 4 5; do
  if curl -fsS "http://$HOST:8000/health"; then
    echo
    exit 0
  fi
  sleep 2
done
echo "Health check failed after restart" >&2
exit 1
