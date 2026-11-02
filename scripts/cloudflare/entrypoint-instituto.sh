#!/bin/sh
echo "🟡 Iniciando túnel Cloudflare..."

cloudflared tunnel --url http://helena-bot-instituto:5002 > /shared-data/cloudflared-instituto.log 2>&1 &

for i in $(seq 1 30); do
    URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' /shared-data/cloudflared-instituto.log | head -n 1)
    if [ -n "$URL" ]; then
        echo "$URL" > /shared-data/tunnel_url_instituto.txt
        echo "✅ Tunnel iniciado: $URL"
        break
    fi
    sleep 2
done

tail -f /dev/null
