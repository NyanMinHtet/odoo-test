# Odoo Client Deployment

## Workflow

1. Push code to the repository.
2. GitHub Actions builds a Docker image containing Odoo 17+ and custom addons.
3. The image is pushed to GitHub Container Registry (GHCR).
4. The client VPS pulls the image and runs a single command to deploy Odoo.

## Deployment Command

bash
sudo PORT=8069 \
     IMAGE=ghcr.io/<user>/<repo>/odoo:latest \
     bash <(curl -fsSL https://raw.githubusercontent.com/<user>/<repo>/main/client-vps/setup.sh)


Required environment variables:
- `IMAGE` — GHCR image URL (e.g., `ghcr.io/org/repo/odoo:latest`)
- `PORT` — Host port to publish Odoo on (default: 8069)

## Reverse Proxy / TLS

This kit serves plain HTTP on the chosen `PORT`. If the client wants HTTPS, they must put their own nginx/Caddy/Traefik in front, point it at `http://127.0.0.1:<PORT>`, and set `proxy_mode = True` in `/opt/odoo/runtime/odoo.conf` afterward (then run `docker compose restart odoo`).

**Important:** WebSocket/longpolling (port 8072) requires reverse-proxy handling and is **NOT exposed** by this kit. If the client needs live chat / longpolling, the reverse proxy must forward `/websocket*` and `/longpolling*` to the Odoo container's internal port 8072.

## Firewall

Only SSH (22) and the chosen `PORT` are opened by the setup script. If the client adds a reverse proxy on 80/443, they must open those ports themselves with:

bash
ufw allow 80,443/tcp


## Manual Module Upgrade

bash
docker compose exec odoo odoo -d odoo -u <module> --stop-after-init

# odoo-test
