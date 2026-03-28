#!/bin/bash
# MADA God's Eye Deployment Script — DigitalOcean GPU Droplet
set -e

echo "=== MADA GOD'S EYE DEPLOYMENT ==="

# Install dependencies
apt update && apt install -y python3-pip nodejs npm nginx git
npm install -g pm2 ts-node typescript

# Install Python dependencies
pip3 install requests h3 torch --index-url https://download.pytorch.org/whl/cu124

# Clone repo
git clone https://github.com/Acuterium-Technologies/mada-godseye.git /opt/mada-godseye
cd /opt/mada-godseye

# Start data ingest services
pm2 start scripts/data-sources/opensky-adsb.py --name mada-adsb --interpreter python3
pm2 start scripts/data-sources/ais-maritime.py --name mada-ais --interpreter python3
pm2 start services/czml-stream-server.ts --name czml-stream --interpreter ts-node

# Start AlDhil + UkhmaOS
pm2 start aldhil.ts --name aldhil --interpreter ts-node
pm2 start ukhmaos.ts --name ukhmaos --interpreter ts-node

pm2 save
pm2 startup

# Nginx reverse proxy for WebSocket
cat > /etc/nginx/sites-available/mada << 'NGINX'
server {
    listen 443 ssl;
    server_name api.majd.chat;
    ssl_certificate /etc/letsencrypt/live/api.majd.chat/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.majd.chat/privkey.pem;

    location /czml-stream {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
NGINX
ln -sf /etc/nginx/sites-available/mada /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

echo "=== MADA GOD'S EYE DEPLOYED ==="
pm2 list
