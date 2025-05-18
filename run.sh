#!/bin/bash
# run.sh - Script to build and run the MySQL MCP Server

# Stop on any error
set -e

echo "🔨 Building the Docker image..."
docker build -t mysql-mcp-server .

echo "🚀 Running the MySQL MCP Server container..."
echo "📝 Using connection: MYSQL_HOST=$MYSQL_HOST, MYSQL_DB=$MYSQL_DB"

docker run -it --rm \
  -e MYSQL_HOST="${MYSQL_HOST:-localhost}" \
  -e MYSQL_PORT="${MYSQL_PORT:-3306}" \
  -e MYSQL_DB="${MYSQL_DB:-mysql}" \
  -e MYSQL_USER="${MYSQL_USER:-root}" \
  -e MYSQL_PASSWORD="${MYSQL_PASSWORD}" \
  mysql-mcp-server