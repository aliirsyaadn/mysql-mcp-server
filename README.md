# MySQL MCP Server Python Implementation

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

## 🚀 Development Setup

Follow these steps to get the MySQL MCP server running for development:

### 1. Install dependencies for local development

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the MCP SDK
pip install mcp
```

### 2. Configure database connection

Create a `.env` file in the project root directory. You can copy the provided example:

```bash
cp .env.example .env
```

Then edit the `.env` file with your database details:

```
# MySQL Connection Settings
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=your_database
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# Operation Controls (true/false)
MYSQL_ENABLE_SELECT=true
MYSQL_ENABLE_INSERT=false
MYSQL_ENABLE_UPDATE=false
MYSQL_ENABLE_DELETE=false
```

### 3. Run the MCP Inspector for development

```bash
# Run the server with the MCP Inspector
mcp dev server.py
```

This will start:
- The MySQL MCP server in development mode
- The MCP Inspector web interface (default: http://127.0.0.1:6274)
- A proxy server that connects the two

The MCP Inspector provides a web-based interface to test your MCP server. You can:
- Browse available tools and resources
- Execute tool calls and see their responses
- Test full conversations with simulated LLM responses
- Debug issues with your server implementation

### 4. Build the Docker image (for production deployment)

```bash
docker build -t mysql-mcp-server .
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
        "--env-file", "/path/to/your/.env",
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
    "--env-file", "/path/to/your/.env",
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
  
- **IN Operations**:
  > "Find all users with these email addresses: user1@example.com, user2@example.com, user3@example.com"

## 🔍 Working with IN Operations

The server provides special handling for SQL `IN` operations with lists. You can use either of these approaches:

### Approach 1: Expanded Placeholders (Traditional)

```sql
-- Each value needs its own placeholder
SELECT * FROM users WHERE email IN (%s, %s, %s)
```

With parameters: `["user1@example.com", "user2@example.com", "user3@example.com"]`

### Approach 2: List Parameter (Simplified)

```sql
-- Single placeholder for the entire list
SELECT * FROM users WHERE email IN (%s)
```

With parameters: `[["user1@example.com", "user2@example.com", "user3@example.com"]]` (nested list)

The server will automatically detect and expand the list parameter into the correct number of placeholders.

## 🧰 Available Tools

The MySQL MCP server provides several powerful tools for different SQL operations:

### 1. Query Execution Tools

#### mysql_execute_query
Execute any SQL query on the MySQL database with automatic operation type detection.

**Parameters**:
- `query` (required): The SQL query to execute
- `params` (optional): Array of parameters for parameterized queries

**Example**:
```sql
SELECT * FROM orders WHERE order_date > '2024-01-01' LIMIT 10
```

#### mysql_select
Execute SELECT queries only (for read-only operations).

**Parameters**:
- `query` (required): The SELECT query to execute
- `params` (optional): Array of parameters for parameterized queries

**Example**:
```sql
SELECT * FROM users WHERE age > 25
```

#### mysql_insert
Execute INSERT queries only (when explicitly enabled).

**Parameters**:
- `query` (required): The INSERT query to execute
- `params` (optional): Array of parameters for parameterized queries

**Example**:
```sql
INSERT INTO customers (name, email) VALUES (%s, %s)
```

#### mysql_update
Execute UPDATE queries only (when explicitly enabled).

**Parameters**:
- `query` (required): The UPDATE query to execute
- `params` (optional): Array of parameters for parameterized queries

**Example**:
```sql
UPDATE products SET price = price * 0.9 WHERE category = 'electronics'
```

#### mysql_delete
Execute DELETE queries only (when explicitly enabled).

**Parameters**:
- `query` (required): The DELETE query to execute
- `params` (optional): Array of parameters for parameterized queries

**Example**:
```sql
DELETE FROM orders WHERE status = 'cancelled' AND created_at < '2023-01-01'
```

### 2. Helper Tools

#### mysql_list_tables
List all tables in a database.

**Parameters**:
- `database` (optional): Database name (defaults to the current database)

#### mysql_describe_table
Get the structure of a specific table.

**Parameters**:
- `table_name` (required): Name of the table to describe
- `database` (optional): Database name (defaults to the current database)


## 📝 Implementation Notes

This server uses the `FastMCP` framework from the MCP Python SDK, which provides a simpler and more Pythonic way to create MCP servers compared to the lower-level MCP Server API. FastMCP:

- Uses decorators to define tools
- Handles serialization/deserialization automatically
- Provides built-in support for different transport methods (stdio, SSE)
- Simplifies parameter typing and validation

## 🔒 Security Considerations

- **Credentials Security**: The server uses environment variables for database credentials. For production environments, consider using more secure methods for credential management.
- **Operation Control**: By default, only SELECT operations are enabled. INSERT, UPDATE, and DELETE operations are disabled for safety and must be explicitly enabled via environment variables.
- **Data Privacy**: The Docker container does not persist any data from your database, but be mindful of what data you allow Claude to access.
- **Limited Permissions**: Use a database user with read-only access or only the permissions required for your use case.

### Controlling Operation Types

The server provides fine-grained control over which SQL operation types are allowed:

| Environment Variable | Default | Description |
|----------------------|---------|-------------|
| `MYSQL_ENABLE_SELECT` | `true` | Controls whether SELECT queries are allowed |
| `MYSQL_ENABLE_INSERT` | `false` | Controls whether INSERT queries are allowed |
| `MYSQL_ENABLE_UPDATE` | `false` | Controls whether UPDATE queries are allowed |
| `MYSQL_ENABLE_DELETE` | `false` | Controls whether DELETE queries are allowed |

Example of starting the Docker container with an .env file:

```bash
# Run with environment variables from .env file
docker run --rm -i --env-file .env mysql-mcp-server

# Alternatively, override specific variables
docker run --rm -i \
  -e MYSQL_HOST=localhost \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=password \
  -e MYSQL_ENABLE_INSERT=true \
  mysql-mcp-server
```

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
Made with ❤️ for the Ali + Claude Code
</div>