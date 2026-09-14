# Deployment (배포)

Deploying and running the game on AWS EC2.

## What goes here

- The deployment runbook (step-by-step, kept current)
- Environment/instance setup notes (OS, installed dependencies, ports)
- Release notes per deployment

## Status

No real EC2 instance has been provisioned yet — provisioning is explicitly
out of scope until it's confirmed separately (see
`docs/planning/initial-release.md` and `AGENTS.md` Boundaries). What follows
is the prepared runbook for when that happens; it should be updated with the
actual steps taken once a real deployment occurs.

## Prerequisites

- An Ubuntu EC2 instance with `python3.12`, `uv`, and `node`/`npm` installed
- Port 8000 open in the instance's security group (v1 serves plain HTTP,
  no reverse proxy/HTTPS)

## One-time setup

1. Clone the repo to the instance, e.g. `/opt/meow-maker` (placeholder path
   used throughout `deploy/`; adjust if the real path differs):
   ```
   sudo git clone <repo-url> /opt/meow-maker
   ```
2. Install the systemd unit:
   ```
   sudo cp /opt/meow-maker/deploy/meow-maker.service /etc/systemd/system/
   sudo systemctl enable meow-maker
   ```

## Routine deploys

```
ssh <user>@<ec2-host>
/opt/meow-maker/deploy/deploy.sh
```

`deploy/deploy.sh` pulls the latest code, builds the frontend
(`web/dist`), syncs backend dependencies with `uv`, and restarts the
`meow-maker` systemd service.

## Next stage

This is the last stage in the loop; the next task typically returns to
[`../planning/`](../planning/README.md) for the next feature.
