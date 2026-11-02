#!/bin/bash

# 1. Detectar o ID do contêiner do MongoDB usando grep (ou a opção que funcionou para você)
MONGO_CONTAINER_ID=$(sudo docker ps | grep "mongo" | awk '{print $1}')

# Verificar se o contêiner do MongoDB foi encontrado
if [ -z "$MONGO_CONTAINER_ID" ]; then
  echo "Contêiner do MongoDB não encontrado na lista de processos."
  exit 1
fi

echo "ID do contêiner MongoDB encontrado: $MONGO_CONTAINER_ID"

# 2. Executar o comando 'use helena_db' dentro do mongosh (sem manter o shell aberto)
echo "Executando o comando 'use helena_db'..."
sudo docker exec "$MONGO_CONTAINER_ID" mongosh --eval "use helena_db"

# 3. Abrir o shell interativo do mongosh
echo "Abrindo o shell interativo do mongosh..."
sudo docker exec -it "$MONGO_CONTAINER_ID" mongosh

echo "Você agora está no shell interativo do mongosh (o banco de dados 'helena_db' já foi selecionado)."

exit 0