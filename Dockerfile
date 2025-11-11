FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Ensure duckdb is installed
RUN uv pip install duckdb>=1.2.1

# Copy all application code
COPY database/ /app/database/
COPY orchestration/ /app/orchestration/
COPY dbt/ /app/dbt/

# Set Python path
ENV PYTHONPATH=/app

# Generate dbt manifest
WORKDIR /app/dbt
RUN uv run dbt deps || echo "No dependencies to install"
RUN uv run dbt parse

# Back to app directory
WORKDIR /app

# Create data and dagster directories with proper permissions
RUN mkdir -p /app/data /app/dagster_home && \
    chmod 755 /app/data /app/dagster_home && \
    chown -R root:root /app/data /app/dagster_home

# Copy dagster configuration
COPY orchestration/dagster.yml /app/dagster_home/dagster.yaml

# Expose ports
EXPOSE 3000 8080

# Health check for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/server_info && curl -f http://localhost:8080/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Ensure data directory has proper permissions\n\
chmod 755 /app/data\n\
touch /app/data/analytics.duckdb\n\
chmod 644 /app/data/analytics.duckdb\n\
\n\
# Initialize database in background\n\
echo "Starting database initialization..."\n\
uv run python database/init_database.py &\n\
DB_PID=$!\n\
\n\
# Wait a moment for database to start\n\
sleep 5\n\
\n\
# Start Dagster orchestrator\n\
echo "Starting Dagster orchestrator..."\n\
uv run dagster dev --host 0.0.0.0 --port 3000 --workspace orchestration/workspace.yaml &\n\
DAGSTER_PID=$!\n\
\n\
# Wait for both processes\n\
wait $DB_PID\n\
wait $DAGSTER_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
