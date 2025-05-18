#!/bin/bash
# setup.sh - Complete setup script for MySQL MCP Server

# Stop on any error
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Build the Docker image
echo "🔨 Building the Docker image..."
docker build -t mysql-mcp-server .

# Example configuration for claude_desktop_config.json
echo "
✅ Setup complete!

To add the MCP server to Claude Desktop, update your claude_desktop_config.json:

1. Find your claude_desktop_config.json at:
   - Windows: %APPDATA%\\Claude Desktop\\claude_desktop_config.json
   - macOS: ~/Library/Application Support/Claude Desktop/claude_desktop_config.json
   - Linux: ~/.config/Claude Desktop/claude_desktop_config.json

2. Add this to your configuration:
{
  \"mcpServers\": {
    \"mysql-mcp-server\": {
      \"name\": \"MySQL MCP Server\",
      \"command\": \"docker\",
      \"args\": [
        \"run\",
        \"--rm\",
        \"-i\",
        \"-e\", \"MYSQL_HOST=your_mysql_host\",
        \"-e\", \"MYSQL_PORT=your_mysql_port\",
        \"-e\", \"MYSQL_DB=your_database\",
        \"-e\", \"MYSQL_USER=your_username\",
        \"-e\", \"MYSQL_PASSWORD=your_password\",
        \"mysql-mcp-server\"
      ],
      \"enabled\": true
    }
  }
}

3. Don't forget to replace the placeholders with your actual database connection details.
4. Restart Claude Desktop to apply the changes.
"

# Finish
echo "📊 Use './run.sh' to test the server before adding to Claude Desktop"