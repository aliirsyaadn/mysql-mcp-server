FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server script and resources
COPY server.py /app/
COPY resources/ /app/resources/

# Set default configuration (can be overridden at runtime)
ENV MYSQL_HOST=localhost
ENV MYSQL_PORT=3306
ENV MYSQL_DB=mysql
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=

# Set operation permissions (can be overridden at runtime)
ENV MYSQL_ENABLE_SELECT=true
ENV MYSQL_ENABLE_INSERT=false
ENV MYSQL_ENABLE_UPDATE=false
ENV MYSQL_ENABLE_DELETE=false

# Make it executable
RUN chmod +x /app/server.py

# The server will run on stdio
ENTRYPOINT ["python", "/app/server.py"]