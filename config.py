#!/usr/bin/env python
"""
Configuration module for MySQL MCP Server
Contains configuration settings, environment variable handling,
and utility classes like the DateTimeEncoder
"""
import os
import json
import datetime
from pathlib import Path

# Operation permissions (can be enabled/disabled via environment variables)
ENABLE_SELECT = os.environ.get("MYSQL_ENABLE_SELECT", "true").lower() == "true"
ENABLE_INSERT = os.environ.get("MYSQL_ENABLE_INSERT", "false").lower() == "true"
ENABLE_UPDATE = os.environ.get("MYSQL_ENABLE_UPDATE", "false").lower() == "true"
ENABLE_DELETE = os.environ.get("MYSQL_ENABLE_DELETE", "false").lower() == "true"

# Database connection settings
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "database": os.environ.get("MYSQL_DB", "mysql"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "")
}

# Resource loading
RESOURCES_DIR = Path(__file__).parent / "resources"

# Custom JSON encoder to handle datetime objects and bytes
class DateTimeEncoder(json.JSONEncoder):
    """JSON Encoder that properly serializes datetime objects to ISO format strings and bytes to strings"""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')  # Convert bytes to string
        return super().default(obj)

# Print configuration information on startup
def print_config():
    """Print the current configuration settings"""
    print(f"MySQL MCP Server Configuration:")
    print(f"- Database: {DB_CONFIG['database']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"- SELECT operations: {'Enabled' if ENABLE_SELECT else 'Disabled'}")
    print(f"- INSERT operations: {'Enabled' if ENABLE_INSERT else 'Disabled'}")
    print(f"- UPDATE operations: {'Enabled' if ENABLE_UPDATE else 'Disabled'}")
    print(f"- DELETE operations: {'Enabled' if ENABLE_DELETE else 'Disabled'}")

# Function to load resources from the resources directory
def load_resources(mcp):
    """Load all JSON resources from the resources directory"""
    print("Resource loading has been disabled temporarily")
    
    # Don't try to load any resources for now - let's get the server working first
    # Once we have a working server, we can add resources one by one
    pass