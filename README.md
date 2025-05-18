# MySQL MCP Server for Claude Desktop

<div align="center">

*Connect Claude directly to your MySQL databases*

</div>

## 📋 Overview

This project provides a Message Connectivity Protocol (MCP) server that connects Claude AI to your remote MySQL databases. With this integration, Claude can directly interact with your databases through natural language, enabling you to:

- Query data using natural language instead of SQL
- Get insights and analysis from your database information
- Automate database exploration and documentation

## ✨ Features

- 🔍 **Execute custom SQL queries** - Run any SQL query and get formatted results
- 📊 **List all tables** - Quickly view all tables in your database
- 📝 **Describe table structures** - Understand column definitions and relationships
- 📑 **Fetch and filter data** - Get specific data with custom filtering and sorting

## 📦 Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your system
- MySQL database credentials (host, port, database name, username, password)
- [Claude Desktop](https://www.anthropic.com/claude/download) or any Claude interface supporting MCP

## 🚀 Quick Setup (Recommended)

The easiest way to set up is using our provided setup script:

```bash
# Make scripts executable
chmod +x setup.sh run.sh

# Run the setup script
./setup.sh
```

This script will:
1. Build the Docker image
2. Provide detailed instructions for configuring Claude Desktop

## 🛠️ Manual Setup

### 1. Save all project files

Make sure you have all these files in your directory:
- `server.py` - The main MCP server using FastMCP
- `Dockerfile` - For building the Docker image 
- `requirements.txt` - Python dependencies
- `run.sh` - Helper script to run the server
- `setup.sh` - Complete setup script

### 2. Install dependencies (optional for local development)

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Build the Docker image

```bash
docker build -t mysql-mcp-server .
```

### 4. Test the server

Set your database connection details as environment variables:

```bash
export MYSQL_HOST="your_mysql_host"
export MYSQL_PORT="3306"  # Default MySQL port
export MYSQL_DB="your_database"
export MYSQL_USER="your_username"
export MYSQL_PASSWORD="your_password"

# Run the server
./run.sh
```

### 5. Configure Claude Desktop

Edit your `claude_desktop_config.json` file, located at:
- **Windows**: `%APPDATA%\Claude Desktop\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude Desktop/claude_desktop_config.json`
- **Linux**: `~/.config/Claude Desktop/claude_desktop_config.json`

Add the MCP server configuration:

```json
{
  "mcpServers": {
    "mysql-mcp-server": {
      "name": "MySQL MCP Server",
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "MYSQL_HOST=localhost",
        "-e", "MYSQL_PORT=3306",
        "-e", "MYSQL_DB=mysql",
        "-e", "MYSQL_USER=root",
        "-e", "MYSQL_PASSWORD=password",
        "mysql-mcp-server"
      ],
      "enabled": true
    }
  }
}
```

Restart Claude Desktop for the changes to take effect.

### 6. Configure Claude Code

Edit your `~/.claude.json` and configure mcpServers tag on scope global, local, or project. or simply run this command:
```bash
claude mcp add-json mysql-mcp-server '{
  "name": "MySQL MCP Server",
  "command": "docker",
  "args": [
    "run",
    "--rm",
    "-i",
    "-e", "MYSQL_HOST=localhost",
    "-e", "MYSQL_PORT=3306",
    "-e", "MYSQL_DB=mysql",
    "-e", "MYSQL_USER=root",
    "-e", "MYSQL_PASSWORD=password",
    "mysql-mcp-server"
  ]
}'
```

## 💬 Using with Claude

Once connected, you can interact with your MySQL database using natural language. Here are some examples:

- **List tables**:
  > "Show me all tables in my MySQL database"

- **Table structure**:
  > "What's the structure of the users table?"
  
- **Query data**:
  > "Get the first 10 orders placed in the last month, sorted by total amount"
  
- **Complex analysis**:
  > "Show me the top 5 customers by revenue in Q1 2024, including their contact information"

- **Execute custom SQL**:
  > "Run this SQL query: SELECT department, AVG(salary) FROM employees GROUP BY department"

## 🧰 Available Tools

The MySQL MCP server provides four powerful tools:

### 1. mysql_execute_query
Execute any SQL query on the MySQL database.

**Parameters**:
- `query` (required): The SQL query to execute
- `params` (optional): Array of parameters for parameterized queries

**Example**:
```sql
SELECT * FROM orders WHERE order_date > '2024-01-01' LIMIT 10
```

### 2. mysql_list_tables
List all tables in a database.

**Parameters**:
- `database` (optional): Database name (defaults to the current database)

### 3. mysql_describe_table
Get the structure of a specific table.

**Parameters**:
- `table_name` (required): Name of the table to describe
- `database` (optional): Database name (defaults to the current database)

### 4. mysql_get_table_data
Get data from a specific table with filtering and sorting options.

**Parameters**:
- `table_name` (required): Name of the table to query
- `limit` (optional, default: 100): Maximum number of rows to return
- `database` (optional): Database name (defaults to the current database)
- `where_clause` (optional): Filtering condition (without the 'WHERE' keyword)
- `order_by` (optional): Sorting specification (without the 'ORDER BY' keywords)

## 📝 Implementation Notes

This server uses the `FastMCP` framework from the MCP Python SDK, which provides a simpler and more Pythonic way to create MCP servers compared to the lower-level MCP Server API. FastMCP:

- Uses decorators to define tools
- Handles serialization/deserialization automatically
- Provides built-in support for different transport methods (stdio, SSE)
- Simplifies parameter typing and validation

## 🔒 Security Considerations

- **Credentials Security**: The server uses environment variables for database credentials. For production environments, consider using more secure methods for credential management.
- **Query Access**: By default, this server allows execution of any SQL query. Consider adding constraints or validation to prevent risky operations.
- **Data Privacy**: The Docker container does not persist any data from your database, but be mindful of what data you allow Claude to access.
- **Limited Permissions**: Use a database user with read-only access or only the permissions required for your use case.

## 🔍 Troubleshooting

If you encounter issues:

1. **Connection Problems**
   - Check that your MySQL connection details are correct
   - Ensure your MySQL server allows remote connections
   - Verify network/firewall settings for remote databases

2. **Docker Issues**
   - Ensure Docker is running (`docker info`)
   - Check Docker logs (`docker logs CONTAINER_ID`)
   - Verify the image was built correctly (`docker images`)

3. **MCP Server Issues**
   - Check for errors in the Claude Desktop MCP server logs
   - Verify the command in `claude_desktop_config.json` is correct
   - Make sure environment variables are properly escaped

4. **Python Dependencies**
   - If developing locally, ensure all requirements are installed
   - Check for version conflicts in Python packages

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
Made with ❤️ for the Claude community
</div>