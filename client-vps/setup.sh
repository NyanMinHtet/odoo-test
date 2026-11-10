#!/usr/bin/env bash
set -Eeuo pipefail

# Require environment variables
: "${IMAGE:?Set IMAGE}"
PORT="${PORT:-8069}"

# Update package lists and install required utilities
apt update -y

# Install required packages
apt install -y ca-certificates curl gnupg jq gettext-base ufw

# Add Docker's official apt repository
. /etc/os-release
install -m 0755 -d /etc/apt/keyrings
curl -fsSL "https://download.docker.com/linux/ubuntu/gpg" | gpg --dearmor -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list

# Update and install Docker and related components
apt update -y
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker
systemctl enable --now docker

# Configure UFW to allow only necessary ports (22 and PORT)
ufw --force enable
ufw allow 22/tcp
ufw allow "${PORT}"/tcp

# Create Odoo directory structure
mkdir -p /opt/odoo/{runtime,data,backups}
chmod 750 /opt/odoo

# Generate database and admin passwords
DB_PASSWORD=$(openssl rand -hex 24)
ADMIN_PASSWD=$(openssl rand -hex 24)

# Write .env file with sensitive information
ENV_FILE="/opt/odoo/.env"
cat > "$ENV_FILE" <<EOF
IMAGE=${IMAGE}
PORT=${PORT}
DB_PASSWORD=${DB_PASSWORD}
ADMIN_PASSWD=${ADMIN_PASSWD}
EOF
chmod 600 "$ENV_FILE"

# Write docker-compose.yml
COMPOSE_FILE="/opt/odoo/docker-compose.yml"
cat > "$COMPOSE_FILE" <<EOF
version: "3.8"

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - odoo-net

  odoo:
    image: ${IMAGE}
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      USER: odoo
      PASSWORD: ${DB_PASSWORD}
    volumes:
      - odoo-data:/var/lib/odoo
      - ./runtime/odoo.conf:/etc/odoo/odoo.conf:ro
    ports:
      - "${PORT}:8069"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8069/web/login"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - odoo-net

networks:
  odoo-net:
    driver: bridge

volumes:
  pgdata:
  odoo-data:
EOF

# Write odoo.conf template (with escaped variables for envsubst)
ODOO_CONF_TEMPLATE="/opt/odoo/odoo.conf.template"
cat > "$ODOO_CONF_TEMPLATE" <<EOF
admin_passwd = \${ADMIN_PASSWD}
db_host = db
db_port = 5432
db_name = odoo
dbfilter = ^odoo$
list_db = False
# Set to True only if you later put nginx/Caddy in front of Odoo.
proxy_mode = False
workers = 4
max_cron_threads = 1
limit_time_cpu = 600
limit_time_real = 1200
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
EOF

# Render the odoo.conf file
RENDERED_CONF="/opt/odoo/runtime/odoo.conf"
envsubst < "$ODOO_CONF_TEMPLATE" > "$RENDERED_CONF"
chmod 600 "$RENDERED_CONF"

# If registry token is set, log in and persist credentials
if [ -n "${REGISTRY_TOKEN:-}" ]; then
  echo "Logging into GHCR..."
  echo "$REGISTRY_TOKEN" | docker login ghcr.io -u "$REGISTRY_USER" --password-stdin
  if [ -f "/opt/odoo/.registry" ]; then
    chmod 600 "/opt/odoo/.registry"
  fi
fi

# Pull and start Odoo
echo "Pulling Odoo image and starting..."
cd /opt/odoo
docker compose pull odoo
docker compose up -d

# Wait for Odoo to be ready (max ~200s)
echo "Waiting for Odoo to start..."
for i in $(seq 1 200); do
  if docker compose exec -T odoo curl -sf http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    break
  fi
  sleep 1
  if [ $i -eq 200 ]; then
    echo "Timeout waiting for Odoo to start"
    docker compose logs --tail=50 odoo
    exit 1
  fi
done

# Create auto-update script
AUTO_UPDATE_SCRIPT="/opt/odoo/auto-update.sh"
cat > "$AUTO_UPDATE_SCRIPT" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail

# Source environment variables
source /opt/odoo/.env

# Log into GHCR if needed
if [ -n "${REGISTRY_TOKEN:-}" ]; then
  echo "$REGISTRY_TOKEN" | docker login ghcr.io -u "$REGISTRY_USER" --password-stdin
fi

# Pull and restart Odoo
echo "Pulling Odoo image..."
docker compose pull odoo

echo "Starting Odoo..."
docker compose up -d --remove-orphans

# Wait for Odoo to be ready
for i in $(seq 1 30); do
  if docker compose exec -T odoo curl -sf http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    echo "Auto-update completed successfully!"
    break
  fi
  sleep 5
  if [ $i -eq 30 ]; then
    echo "Auto-update timed out"
    exit 1
  fi
done
EOF
chmod 755 "$AUTO_UPDATE_SCRIPT"

# Create cron job for auto-updates
CRON_FILE="/etc/cron.d/odoo-auto-update"
cat > "$CRON_FILE" <<EOF
*/5 * * * * root /opt/odoo/auto-update.sh >> /var/log/odoo-auto-update.log 2>&1
EOF
chmod 644 "$CRON_FILE"

# Get public IP for final message
PUBLIC_IP=$(curl -fsS https://api.ipify.org 2>/dev/null || hostname -I | awk '{print $1}')

echo "Setup complete! Odoo is live at http://${PUBLIC_IP}:${PORT}"
echo "Auto-update is enabled (runs every 5 minutes via cron)"
