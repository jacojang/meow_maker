#!/usr/bin/env bash
# One-time setup script for the Meow Maker EC2 instance.
#
# Run LOCALLY. It SSHes into the instance and runs the setup remotely
# (nothing here needs to be copied over first). Safe to re-run — every step
# is idempotent.
#
# Instance facts (Amazon Linux 2023, dnf-based):
#   - user: ec2-user (not ubuntu)
#   - Node.js is intentionally never installed here: the instance has only
#     913MB RAM / no swap (too tight for npm install/vite build), and its
#     dnf-provided nodejs (18.20.8) is older than what this project's Vite
#     requires (^20.19.0 || >=22.12.0). web/ is built locally instead — see
#     deploy/deploy.sh and docs/deployment/README.md.
set -euo pipefail

HOST="54.116.51.0"
HOST_DNS="ec2-54-116-51-0.ap-northeast-2.compute.amazonaws.com"
USER="ec2-user"
KEY="$HOME/.ssh/jacojang_new_key.pem"
REMOTE_DIR="/home/ec2-user/meow-maker"
REPO_URL="https://github.com/jacojang/meow_maker.git"

ssh -i "$KEY" "$USER@$HOST" bash -s <<EOF
set -euo pipefail

# 1. 1GB swap file (instance has 913MB RAM / no swap)
if ! sudo swapon --show | grep -q '/swapfile'; then
  sudo fallocate -l 1G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
fi
if ! grep -q '^/swapfile' /etc/fstab; then
  echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
fi

# 2. uv for ec2-user (installs to ~/.local/bin, no root/dnf needed)
if [ ! -x "\$HOME/.local/bin/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 3. Clone the repo if not already present
if [ ! -d "$REMOTE_DIR/.git" ]; then
  git clone "$REPO_URL" "$REMOTE_DIR"
fi

# 4. Install and enable the systemd unit (not started yet — nothing's
#    built/synced until the first deploy.sh run)
sudo cp "$REMOTE_DIR/deploy/meow-maker.service" /etc/systemd/system/meow-maker.service
sudo systemctl daemon-reload
sudo systemctl enable meow-maker
EOF

echo "Setup complete on $HOST ($HOST_DNS)."
