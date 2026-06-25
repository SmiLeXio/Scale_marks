#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

APP_DIR="/opt/linji"
HOST_IP="123.57.134.105"
API_PORT="8010"
TARBALL="/tmp/linji-deploy.tar"
RELEASE_ID="$(date +%Y%m%d%H%M%S)"
RELEASE_DIR="${APP_DIR}/releases/${RELEASE_ID}"
ENV_FILE="${APP_DIR}/shared/backend.env"

if [ ! -f "${TARBALL}" ]; then
  echo "Missing deploy tarball: ${TARBALL}" >&2
  exit 1
fi

echo "[deploy] installing system packages"
apt-get update
apt-get install -y python3-venv python3-pip nginx curl nodejs npm

echo "[deploy] unpacking release ${RELEASE_ID}"
mkdir -p "${APP_DIR}/releases" "${APP_DIR}/data" "${APP_DIR}/shared" "${RELEASE_DIR}"
tar -xf "${TARBALL}" -C "${RELEASE_DIR}"

if [ ! -f "${ENV_FILE}" ]; then
  if [ -f "${RELEASE_DIR}/backend/.env" ]; then
    cp "${RELEASE_DIR}/backend/.env" "${ENV_FILE}"
  else
    cp "${RELEASE_DIR}/backend/.env.example" "${ENV_FILE}"
  fi
fi

upsert_env() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" "${ENV_FILE}"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "${ENV_FILE}"
  else
    printf "%s=%s\n" "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

current_secret="$(grep '^SECRET_KEY=' "${ENV_FILE}" | cut -d= -f2- || true)"
if [ -z "${current_secret}" ] || [ "${current_secret}" = "change-me-in-development" ]; then
  upsert_env "SECRET_KEY" "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
fi
upsert_env "DATABASE_URL" "sqlite:////opt/linji/data/reptilecare.db"
upsert_env "BACKEND_CORS_ORIGINS" "http://${HOST_IP},http://${HOST_IP}:80"
cp "${ENV_FILE}" "${RELEASE_DIR}/backend/.env"

echo "[deploy] installing backend dependencies"
cd "${RELEASE_DIR}/backend"
python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip wheel
./venv/bin/pip install -r requirements.txt

echo "[deploy] building frontend"
cd "${RELEASE_DIR}/frontend"
npm ci --no-audit --no-fund
npm run build

echo "[deploy] switching current release"
ln -sfn "${RELEASE_DIR}" "${APP_DIR}/current"

echo "[deploy] writing systemd services"
cat > /etc/systemd/system/linji-api.service <<EOF
[Unit]
Description=Linji FastAPI service
After=network.target

[Service]
Type=simple
WorkingDirectory=${APP_DIR}/current/backend
ExecStart=${APP_DIR}/current/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port ${API_PORT}
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/linji-qq-bot.service <<EOF
[Unit]
Description=Linji QQ group bot worker
After=network.target linji-api.service

[Service]
Type=simple
WorkingDirectory=${APP_DIR}/current/backend
ExecStart=${APP_DIR}/current/backend/venv/bin/python -m app.workers.qq_group_bot
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/linji-reminder-worker.service <<EOF
[Unit]
Description=Linji reminder worker
After=network.target linji-api.service

[Service]
Type=simple
WorkingDirectory=${APP_DIR}/current/backend
ExecStart=${APP_DIR}/current/backend/venv/bin/python -m app.workers.reminder_summary_worker
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "[deploy] writing nginx config"
cat > /etc/nginx/sites-available/linji <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _ ${HOST_IP};

    root ${APP_DIR}/current/frontend/dist;
    index index.html;
    client_max_body_size 20m;

    location /api/ {
        proxy_pass http://127.0.0.1:${API_PORT}/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sfn /etc/nginx/sites-available/linji /etc/nginx/sites-enabled/linji
nginx -t

if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
  ufw allow 80/tcp
fi

echo "[deploy] starting services"
systemctl daemon-reload
systemctl enable --now nginx
systemctl enable --now linji-api linji-qq-bot linji-reminder-worker
systemctl restart linji-api linji-qq-bot linji-reminder-worker nginx

sleep 3
echo "[deploy] local health check"
curl -fsS http://127.0.0.1:${API_PORT}/api/health
echo
curl -fsSI http://127.0.0.1/ | head -n 1

echo "[deploy] service state"
systemctl --no-pager --full status linji-api linji-qq-bot linji-reminder-worker nginx | sed -n '1,160p'

echo "[deploy] done"
