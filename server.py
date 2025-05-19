#!/usr/bin/env python
import os
import json
import re
import datetime
import mysql.connector
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from pathlib import Path
import config  # Import the config module

# Load environment variables from .env file if present
load_dotenv(override=True)  # override=True ensures .env variables take precedence

# Create an MCP server
mcp = FastMCP(
    name="MySQL MCP Server",
    host="0.0.0.0",  # only used for SSE transport
    port=8051,  # only used for SSE transport (set this to any port)
)

# Display configuration information
config.print_config()

# Add resource directly in server.py
@mcp.resource("examples://parameterized_query_examples")
def get_parameterized_query_examples():
    """Load parameterized query examples"""
    resource_path = Path(__file__).parent / "resources" / "parameterized_query_examples.json"
    try:
        with open(resource_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading resource: {e}")
        return {"error": str(e)}
    
print("Registered resource: examples://parameterized_query_examples")

class MySQLClient:
    def __init__(self, config):
        self.config = config
    
    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def _execute(self, query, params=None, operation_type=None):
        """Internal method to execute queries with permission checking"""
        # Check permission based on operation type
        if operation_type == "SELECT" and not config.ENABLE_SELECT:
            return {"error": True, "message": "SELECT operations are disabled", "code": 403}
        elif operation_type == "INSERT" and not config.ENABLE_INSERT:
            return {"error": True, "message": "INSERT operations are disabled", "code": 403}
        elif operation_type == "UPDATE" and not config.ENABLE_UPDATE:
            return {"error": True, "message": "UPDATE operations are disabled", "code": 403}
        elif operation_type == "DELETE" and not config.ENABLE_DELETE:
            return {"error": True, "message": "DELETE operations are disabled", "code": 403}
        
        # Process IN parameters if params contains lists
        try:
            if params is not None and isinstance(params, list) and any(isinstance(p, list) for p in params):
                # Expand any IN clauses with list parameters
                expanded_query, expanded_params = expand_in_params(query, params)
                query = expanded_query
                params = expanded_params
        except Exception as e:
            return {"error": True, "message": f"Error processing IN parameters: {str(e)}", "code": 400}
            
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # Ensure params is a list or tuple, even if None is provided
                params_list = params if params is not None else []
                
                cursor.execute(query, params_list)
                
                # Check if this is a SELECT query that returns data
                if cursor.description:
                    results = cursor.fetchall()
                    return results
                else:
                    # For non-SELECT queries, return affected row count
                    conn.commit()  # Ensure changes are committed
                    return {"affected_rows": cursor.rowcount}
            except mysql.connector.Error as err:
                # Return error information in a structured way
                return {"error": True, "message": str(err), "code": err.errno}
            finally:
                cursor.close()
    
    def execute_query(self, query, params=None):
        """Execute a query with auto-detection of operation type"""
        # Simple operation type detection (not foolproof but works for most cases)
        query_upper = query.strip().upper()
        
        if query_upper.startswith("SELECT") or query_upper.startswith("SHOW") or query_upper.startswith("DESCRIBE"):
            operation_type = "SELECT"
        elif query_upper.startswith("INSERT"):
            operation_type = "INSERT"
        elif query_upper.startswith("UPDATE"):
            operation_type = "UPDATE"
        elif query_upper.startswith("DELETE"):
            operation_type = "DELETE"
        else:
            # For other operations like CREATE, ALTER, etc. - allow execution without specific permission check
            operation_type = None
            
        return self._execute(query, params, operation_type)
    
    def execute_select(self, query, params=None):
        """Execute a SELECT query"""
        return self._execute(query, params, "SELECT")
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT query"""
        return self._execute(query, params, "INSERT")
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE query"""
        return self._execute(query, params, "UPDATE")
    
    def execute_delete(self, query, params=None):
        """Execute a DELETE query"""
        return self._execute(query, params, "DELETE")
    
    def list_tables(self, database=None):
        if database:
            query = f"SHOW TABLES FROM `{database}`"
            results = self.execute_select(query)
        else:
            query = "SHOW TABLES"
            results = self.execute_select(query)
            
        # Check if there was an error
        if isinstance(results, dict) and "error" in results:
            return results
            
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
            
        return self.execute_select(query)

# Helper function to handle IN parameters
def expand_in_params(query, params):
    """
    Helper function to dynamically expand IN clauses in SQL queries
    
    Args:
        query: SQL query string possibly containing IN (%s) patterns
        params: List of parameters that may include nested lists for IN clauses
        
    Returns:
        Tuple of (modified_query, flattened_params)
    """
    if params is None or not isinstance(params, list):
        return query, params
    
    # Create a copy of the parameters list to avoid modifying the original
    params_copy = list(params)
    modified_query = query
    flat_params = []
    
    # Look for potential IN clauses with a single placeholder
    in_clause_pattern = r'IN\s*\(\s*%s\s*\)'
    
    # Find all occurrences of IN (%s)
    in_clauses = list(re.finditer(in_clause_pattern, modified_query, re.IGNORECASE))
    
    # Process the IN clauses in reverse order to prevent position shifts
    for match in reversed(in_clauses):
        param_index = len(flat_params)
        param_value = params_copy[param_index] if param_index < len(params_copy) else None
        
        # Only process if the parameter is a list or tuple
        if isinstance(param_value, (list, tuple)) and param_value:
            # Create the expanded placeholders (%s, %s, %s, ...)
            placeholders = ', '.join(['%s'] * len(param_value))
            
            # Replace the IN (%s) with IN (expanded placeholders)
            start, end = match.span()
            modified_query = modified_query[:start] + f"IN ({placeholders})" + modified_query[end:]
            
            # Add the individual list items to the flattened params
            flat_params.extend(param_value)
            
            # Remove the processed parameter from the original list
            params_copy.pop(param_index)
        else:
            # Add the parameter to the flattened list
            flat_params.append(param_value)
            params_copy.pop(param_index)
    
    # Add any remaining parameters
    flat_params.extend(params_copy)
    
    return modified_query, flat_params

# Initialize the MySQL client with configuration from config module
mysql_client = MySQLClient(config.DB_CONFIG)

# Tool implementations
@mcp.tool()
def mysql_execute_query(query: str, params: list = None) -> str:
    """Execute a SQL query on the MySQL database
    
    Args:
        query: The SQL query to execute. Use %s as placeholders for parameters.
               For IN operations, you can use either approach:
               1. Expanded placeholders: "WHERE id IN (%s, %s, %s)" with params [1, 2, 3]
               2. List parameter: "WHERE id IN (%s)" with params [[1, 2, 3]]
               
        params: Query parameters (optional). A list of values that correspond to %s placeholders in the query.
               For example, if query is "SELECT * FROM users WHERE age > %s AND status = %s", 
               then params could be [25, "active"].
               
               For IN operations with lists, you can now pass the list directly:
               "SELECT * FROM users WHERE email IN (%s)" with params [["user1@example.com", "user2@example.com"]]
        
    Returns:
        The query results as a JSON string
        
    Notes:
        Refer to the 'parameterized_query_examples' resource for examples of using parameterized queries.
        Always use %s as the placeholder regardless of the parameter data type.
        
        This tool automatically detects the query type (SELECT, INSERT, UPDATE, DELETE) and
        checks if that operation type is enabled. For specific operation types, use the
        dedicated tools: mysql_select, mysql_insert, mysql_update, mysql_delete.
        
        For IN operations, both of these approaches now work:
        1. "SELECT * FROM users WHERE id IN (%s, %s, %s)" with params [1, 2, 3]
        2. "SELECT * FROM users WHERE id IN (%s)" with params [[1, 2, 3]]
    """
    # Ensure params is always a list, even if None is provided
    params_list = params if params is not None else []
            
    result = mysql_client.execute_query(query, params_list)
    return json.dumps(result, cls=config.DateTimeEncoder)

@mcp.tool()
def mysql_select(query: str, params: list = None) -> str:
    """Execute a SELECT query on the MySQL database
    
    Args:
        query: The SELECT query to execute. Use %s as placeholders for parameters.
               For IN operations, you can use either approach:
               1. Expanded placeholders: "WHERE id IN (%s, %s, %s)" with params [1, 2, 3]
               2. List parameter: "WHERE id IN (%s)" with params [[1, 2, 3]]
               
        params: Query parameters (optional). A list of values that correspond to %s placeholders in the query.
               For example, if query is "SELECT * FROM users WHERE age > %s AND status = %s", 
               then params could be [25, "active"].
               
               For IN operations with lists, you can now pass the list directly:
               "SELECT * FROM users WHERE email IN (%s)" with params [["user1@example.com", "user2@example.com"]]
        
    Returns:
        The query results as a JSON string
        
    Notes:
        This tool is specifically for SELECT operations. It will refuse to execute other SQL operations
        like INSERT, UPDATE, or DELETE.
        
        Refer to the 'parameterized_query_examples' resource for examples of using parameterized queries.
        Always use %s as the placeholder regardless of the parameter data type.
        
        For IN operations, both of these approaches now work:
        1. "SELECT * FROM users WHERE id IN (%s, %s, %s)" with params [1, 2, 3]
        2. "SELECT * FROM users WHERE id IN (%s)" with params [[1, 2, 3]]
    """
    # Validate that this is a SELECT query
    if not query.strip().upper().startswith("SELECT"):
        return json.dumps({"error": True, "message": "This tool only accepts SELECT queries", "code": 400})
    
    # Ensure params is always a list, even if None is provided
    params_list = params if params is not None else []
    
    result = mysql_client.execute_select(query, params_list)
    return json.dumps(result, cls=config.DateTimeEncoder)

@mcp.tool()
def mysql_insert(query: str, params: list = None) -> str:
    """Execute an INSERT query on the MySQL database
    
    Args:
        query: The INSERT query to execute. Use %s as placeholders for parameters.
        params: Query parameters (optional). A list of values that correspond to %s placeholders in the query.
               For example, if query is "INSERT INTO users (name, age) VALUES (%s, %s)", 
               then params could be ["John Doe", 30].
        
    Returns:
        The query results as a JSON string with affected row count
        
    Notes:
        This tool is specifically for INSERT operations. It will refuse to execute other SQL operations.
        INSERT operations can be disabled via the MYSQL_ENABLE_INSERT environment variable.
        
        Refer to the 'parameterized_query_examples' resource for examples of using parameterized queries.
        Always use %s as the placeholder regardless of the parameter data type.
    """
    # Validate that this is an INSERT query
    if not query.strip().upper().startswith("INSERT"):
        return json.dumps({"error": True, "message": "This tool only accepts INSERT queries", "code": 400})
    
    # Ensure params is always a list, even if None is provided
    params_list = params if params is not None else []
    result = mysql_client.execute_insert(query, params_list)
    return json.dumps(result, cls=config.DateTimeEncoder)

@mcp.tool()
def mysql_update(query: str, params: list = None) -> str:
    """Execute an UPDATE query on the MySQL database
    
    Args:
        query: The UPDATE query to execute. Use %s as placeholders for parameters.
        params: Query parameters (optional). A list of values that correspond to %s placeholders in the query.
               For example, if query is "UPDATE users SET name = %s WHERE id = %s", 
               then params could be ["Jane Smith", 123].
        
    Returns:
        The query results as a JSON string with affected row count
        
    Notes:
        This tool is specifically for UPDATE operations. It will refuse to execute other SQL operations.
        UPDATE operations can be disabled via the MYSQL_ENABLE_UPDATE environment variable.
        
        Refer to the 'parameterized_query_examples' resource for examples of using parameterized queries.
        Always use %s as the placeholder regardless of the parameter data type.
    """
    # Validate that this is an UPDATE query
    if not query.strip().upper().startswith("UPDATE"):
        return json.dumps({"error": True, "message": "This tool only accepts UPDATE queries", "code": 400})
    
    # Ensure params is always a list, even if None is provided
    params_list = params if params is not None else []
    result = mysql_client.execute_update(query, params_list)
    return json.dumps(result, cls=config.DateTimeEncoder)

@mcp.tool()
def mysql_delete(query: str, params: list = None) -> str:
    """Execute a DELETE query on the MySQL database
    
    Args:
        query: The DELETE query to execute. Use %s as placeholders for parameters.
        params: Query parameters (optional). A list of values that correspond to %s placeholders in the query.
               For example, if query is "DELETE FROM users WHERE id = %s", 
               then params could be [123].
        
    Returns:
        The query results as a JSON string with affected row count
        
    Notes:
        This tool is specifically for DELETE operations. It will refuse to execute other SQL operations.
        DELETE operations can be disabled via the MYSQL_ENABLE_DELETE environment variable.
        
        Refer to the 'parameterized_query_examples' resource for examples of using parameterized queries.
        Always use %s as the placeholder regardless of the parameter data type.
    """
    # Validate that this is a DELETE query
    if not query.strip().upper().startswith("DELETE"):
        return json.dumps({"error": True, "message": "This tool only accepts DELETE queries", "code": 400})
    
    # Ensure params is always a list, even if None is provided
    params_list = params if params is not None else []
    result = mysql_client.execute_delete(query, params_list)
    return json.dumps(result, cls=config.DateTimeEncoder)

@mcp.tool()
def mysql_list_tables(database: str = None) -> str:
    """List all tables in the MySQL database
    
    Args:
        database: Database name (optional, defaults to current database)
        
    Returns:
        List of tables as a JSON string
    """
    result = mysql_client.list_tables(database)
    return json.dumps(result, cls=config.DateTimeEncoder)

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
    return json.dumps(result, cls=config.DateTimeEncoder)



# Run the server
if __name__ == "__main__":
    print("Starting MySQL MCP Server...")
    # Run with stdio transport by default (for Docker compatibility)
    # Can be changed to "sse" for SSE transport
    mcp.run(transport="stdio")