"""Dagster resources for the Dakota Analytics pipeline."""
import os
import sys
from pathlib import Path

import duckdb
import requests
from dagster import ConfigurableResource

# Add the app directory to Python path for imports
sys.path.insert(0, '/app')

try:
    from database.connection_manager import get_connection_manager
except ImportError:
    # Fallback if running outside container
    get_connection_manager = None


class DuckDBWarehouse(ConfigurableResource):
    """DuckDB warehouse resource for direct database access."""

    database_path: str = os.getenv("DUCKDB_PATH", "/app/data/analytics.duckdb")

    def get_connection(self):
        """Get DuckDB connection directly to the database file."""
        # In the unified container, connect directly to the database file
        # This avoids API key authentication issues since we're in the same container
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(db_path))


class FastAPIClient(ConfigurableResource):
    """FastAPI client resource for ingesting GL data."""

    base_url: str = os.getenv("FASTAPI_URL", "http://fastapi:8000")

    def get_health(self) -> dict:
        """Get FastAPI service health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_gl_records(self, start_date: str = None, end_date: str = None, limit: int = 1000) -> list:
        """Get GL records from FastAPI batch endpoint (non-streaming)."""

        params = {"limit": limit}
        if start_date and end_date:
            params.update({"start_date": start_date, "end_date": end_date})

        # Use the new batch endpoint for predictable, finite data
        response = requests.get(f"{self.base_url}/get-gl-batch", params=params)
        response.raise_for_status()
        return response.json().get("data", [])


