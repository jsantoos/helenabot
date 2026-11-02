#!/bin/bash

echo "🚨 Warning: This will delete all current data from MongoDB!"
read -p "Do you wish to continue? (y/n): " confirm

if [[ "$confirm" != "y" ]]; then
    echo "❌ Operation canceled."
    exit 1
fi

echo "🔻 Stopping containers and removing volumes..."
docker compose down -v

echo "🧹 Removing mongo-data volume..."
rm -rf ./mongo-data

echo "🧹 Removing chroma_db directory..."
rm -rf ./chroma_db

echo "🚀 Starting MongoDB with a unique index..."
docker compose up -d --remove-orphans --build


echo "⏳ Waiting for MongoDB to start..."
sleep 5

echo "✅ MongoDB restarted, and the index will be created via init-index.js (if it's in the correct path)."

echo "🚀 Starting the application..."

# List running containers
echo "📋 Listing running containers..."

container_id=$(docker ps -q --filter "name=helena-bot")
# Display logs of the specified container
echo "📖 Displaying logs for container: $container_id"
docker logs -f "$container_id"
