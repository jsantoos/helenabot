#!/bin/sh

echo "🟡 Iniciando túnel Cloudflare..."

# Gera túnel e salva saída no log + extrai a URL
cloudflared tunnel --url http://helena-bot:5001 2>&1 | tee /shared-data/cloudflared.log &

# Aguarda o log conter a URL do túnel
for i in $(seq 1 30); do
    URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' /shared-data/cloudflared.log | head -n 1)
    if [ -n "$URL" ]; then
        echo "$URL" > /shared-data/tunnel_url.txt
        echo "✅ Tunnel iniciado: $URL"
        break
    fi
    sleep 2
done

# Mantém o container ativo
tail -f /dev/null
