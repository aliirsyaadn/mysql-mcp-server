FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server script
COPY server.py /app/

# Make it executable
RUN chmod +x /app/server.py

# The server will run on stdio
ENTRYPOINT ["python", "/app/server.py"]