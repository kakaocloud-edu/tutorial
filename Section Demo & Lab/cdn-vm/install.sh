#!/usr/bin/env bash
set -euo pipefail

REPO_ARCHIVE="${CDN_LAB_REPO_ARCHIVE:-https://github.com/kakaocloud-edu/tutorial/archive/refs/heads/main.tar.gz}"
INSTALL_DIR="/opt/cdn-lab"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root. Try: sudo bash install.sh" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nginx python3 curl ca-certificates tar

mkdir -p "$INSTALL_DIR" /etc/cdn-lab /var/cache/nginx/cdn-lab

if [ -f "./app/cdn_admin.py" ] && [ -d "./app/static" ]; then
  cp ./app/cdn_admin.py "$INSTALL_DIR/cdn_admin.py"
  rm -rf "$INSTALL_DIR/static"
  cp -r ./app/static "$INSTALL_DIR/static"
  cp ./systemd/cdn-lab-admin.service /etc/systemd/system/cdn-lab-admin.service
else
  curl -fsSL "$REPO_ARCHIVE" -o "$TMP_DIR/source.tar.gz"
  tar -xzf "$TMP_DIR/source.tar.gz" -C "$TMP_DIR"
  SOURCE_DIR="$(find "$TMP_DIR" -type f -path '*/Section Demo & Lab/cdn-vm/app/cdn_admin.py' -printf '%h\n' | sed 's#/app$##' | head -n 1)"
  if [ -z "$SOURCE_DIR" ]; then
    echo "Could not find CDN Lab source files in archive: $REPO_ARCHIVE" >&2
    exit 1
  fi
  cp "$SOURCE_DIR/app/cdn_admin.py" "$INSTALL_DIR/cdn_admin.py"
  rm -rf "$INSTALL_DIR/static"
  cp -r "$SOURCE_DIR/app/static" "$INSTALL_DIR/static"
  cp "$SOURCE_DIR/systemd/cdn-lab-admin.service" /etc/systemd/system/cdn-lab-admin.service
fi

chmod +x "$INSTALL_DIR/cdn_admin.py"

if [ ! -f /etc/cdn-lab/config.json ]; then
  cat >/etc/cdn-lab/config.json <<'JSON'
{
  "origin_url": "",
  "ttl_seconds": 60,
  "cache_size": "100m",
  "inactive": "60m",
  "admin_port": 8080
}
JSON
fi

rm -f /etc/nginx/sites-enabled/default

if [ ! -f /etc/nginx/conf.d/cdn-lab.conf ]; then
  cat >/etc/nginx/conf.d/cdn-lab.conf <<'NGINX'
server {
    listen 80 default_server;
    server_name _;

    location = /__cdn_lab_health {
        access_log off;
        add_header Content-Type text/plain;
        return 200 "ok\n";
    }

    location / {
        add_header Content-Type text/plain;
        return 200 "CDN Lab is installed. Open http://THIS_VM_PUBLIC_IP:8080 and configure the Origin URL.\n";
    }
}
NGINX
fi

nginx -t
systemctl enable --now nginx
systemctl daemon-reload
systemctl enable --now cdn-lab-admin

PUBLIC_IP="$(curl -fsS --max-time 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || hostname -I | awk '{print $1}')"

echo
echo "CDN Lab installation complete."
echo "Admin console: http://${PUBLIC_IP}:8080"
echo "CDN endpoint:  http://${PUBLIC_IP}"
echo
