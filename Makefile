# Caminhos dos diretórios
BIO_DIR=clients/bio
INSTITUTO_DIR=clients/instituto

# Comandos
UP_MONGO=docker compose -f docker-compose.mongo.yml up -d
UP_BIO=docker compose -f $(BIO_DIR)/docker-compose.yml up -d --build
UP_INSTITUTO=docker compose -f $(INSTITUTO_DIR)/docker-compose.yml up -d --build

# Targets
all: up-mongo up-bio wait up-instituto

up-mongo:
	@echo "🚀 Subindo MongoDB..."
	@$(UP_MONGO)

up-bio:
	@echo "📦 Subindo bot do cliente BIO..."
	@$(UP_BIO)

up-instituto:
	@echo "📦 Subindo bot do cliente INSTITUTO..."
	@$(UP_INSTITUTO)

wait:
	@echo "⏳ Aguardando 20 segundos antes de subir o próximo bot para evitar conflitos no túnel Cloudflare..."
	@sleep 20

down:
	@echo "🛑 Parando todos os containers..."
	@docker compose -f docker-compose.mongo.yml down
	@docker compose -f $(BIO_DIR)/docker-compose.yml down
	@docker compose -f $(INSTITUTO_DIR)/docker-compose.yml down

logs-bio:
	@docker logs -f helena-bot-bio

logs-instituto:
	@docker logs -f helena-bot-instituto

logs-mongo:
	@docker logs -f mongodb

tunnel-url:
	@echo "🔗 URL do túnel BIO:"
	@cat shared-data/tunnel_url_bio.txt || echo "❌ Tunnel não encontrado!"
	@echo "\n🔗 URL do túnel INSTITUTO:"
	@cat shared-data/tunnel_url_instituto.txt || echo "❌ Tunnel não encontrado!"

