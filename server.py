#!/usr/bin/env python
# mysql_mcp_server.py
import os
import json
import mysql.connector
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Create an MCP server
mcp = FastMCP(
    name="MySQL MCP Server",
    host="0.0.0.0",  # only used for SSE transport
    port=8051,  # only used for SSE transport (set this to any port)
)

class MySQLClient:
    def __init__(self, config):
        self.config = config
    
    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def execute_query(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or [])
                
                # Check if this is a SELECT query that returns data
                if cursor.description:
                    results = cursor.fetchall()
                    return results
                else:
                    # For non-SELECT queries, return affected row count
                    return {"affected_rows": cursor.rowcount}
            finally:
                cursor.close()
    
    def list_tables(self, database=None):
        if database:
            query = f"SHOW TABLES FROM `{database}`"
            results = self.execute_query(query)
        else:
            query = "SHOW TABLES"
            results = self.execute_query(query)
            
        # Reformat results to match the expected output format
        tables = []
        for row in results:
            # Get first value (table name) from each row
            tables.append({
                "table_name": list(row.values())[0]
            })
        return tables
    
    def describe_table(self, table_name, database=None):
        if database:
            query = f"DESCRIBE `{database}`.`{table_name}`"
        else:
            query = f"DESCRIBE `{table_name}`"
            
        return self.execute_query(query)
    
    def get_table_data(self, table_name, limit=100, database=None, where_clause=None, order_by=None):
        # Build the query safely with params
        if database:
            query = f"SELECT * FROM `{database}`.`{table_name}`"
        else:
            query = f"SELECT * FROM `{table_name}`"
            
        params = []
        
        if where_clause:
            query += " WHERE " + where_clause
        
        if order_by:
            query += " ORDER BY " + order_by
        
        query += " LIMIT %s"
        params.append(limit)
        
        return self.execute_query(query, params)

# Get connection details from environment variables
db_host = os.environ.get("MYSQL_HOST", "localhost")
db_port = os.environ.get("MYSQL_PORT", "3306")
db_name = os.environ.get("MYSQL_DB", "mysql")
db_user = os.environ.get("MYSQL_USER", "root")
db_password = os.environ.get("MYSQL_PASSWORD", "")

# Construct the connection config
db_config = {
    "host": db_host,
    "port": int(db_port),
    "database": db_name,
    "user": db_user,
    "password": db_password
}

# Initialize the MySQL client
mysql_client = MySQLClient(db_config)

# Tool implementations
@mcp.tool()
def mysql_execute_query(query: str, params: list = None) -> str:
    """Execute a SQL query on the MySQL database
    
    Args:
        query: The SQL query to execute
        params: Query parameters (optional)
        
    Returns:
        The query results as a JSON string
    """
    result = mysql_client.execute_query(query, params or [])
    return json.dumps(result)

@mcp.tool()
def mysql_list_tables(database: str = None) -> str:
    """List all tables in the MySQL database
    
    Args:
        database: Database name (optional, defaults to current database)
        
    Returns:
        List of tables as a JSON string
    """
    result = mysql_client.list_tables(database)
    return json.dumps(result)

@mcp.tool()
def mysql_describe_table(table_name: str, database: str = None) -> str:
    """Get the structure of a specific table
    
    Args:
        table_name: Name of the table to describe
        database: Database name (optional, defaults to current database)
        
    Returns:
        Table structure as a JSON string
    """
    result = mysql_client.describe_table(table_name, database)
    return json.dumps(result)

@mcp.tool()
def mysql_get_table_data(
    table_name: str, 
    limit: int = 100, 
    database: str = None, 
    where_clause: str = None, 
    order_by: str = None
) -> str:
    """Get data from a specific table with optional limit
    
    Args:
        table_name: Name of the table to query
        limit: Maximum number of rows to return (default: 100)
        database: Database name (optional, defaults to current database)
        where_clause: WHERE clause for filtering (without the 'WHERE' keyword)
        order_by: ORDER BY clause for sorting (without the 'ORDER BY' keywords)
        
    Returns:
        Table data as a JSON string
    """
    result = mysql_client.get_table_data(table_name, limit, database, where_clause, order_by)
    return json.dumps(result)

# Run the server
if __name__ == "__main__":
    print("Starting MySQL MCP Server...")
    # Run with stdio transport by default (for Docker compatibility)
    # Can be changed to "sse" for SSE transport
    mcp.run(transport="stdio")