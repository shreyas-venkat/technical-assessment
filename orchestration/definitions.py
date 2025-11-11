"""Dagster definitions for the Dakota Analytics pipeline."""
import os
from pathlib import Path
from dagster import (
    Definitions,
    ScheduleDefinition,
    DefaultScheduleStatus,
    load_assets_from_modules,
    AssetSelection,
    define_asset_job,
)
# Temporarily comment out dbt integration to get Dagster working first
# from dagster_dbt import DbtCliResource, dbt_assets, DbtProject

from orchestration.assets import ingestion
from orchestration.resources import DuckDBWarehouse, FastAPIClient


# TODO: Add dbt integration back once basic Dagster is working
# # Load dbt project
# dbt_project_dir = Path(__file__).parent.parent / "dbt"
# dbt_project = DbtProject(
#     project_dir=dbt_project_dir,
#     packaged_project_dir=dbt_project_dir,
# )


# Load all assets
ingestion_assets = load_assets_from_modules([ingestion])

# Create a job that materializes the GL records asset
daily_ingestion_job = define_asset_job(
    name="daily_ingestion_job",
    selection=AssetSelection.assets(ingestion.raw_gl_records),
    description="Daily ingestion of GL records from FastAPI to DuckDB"
)

# Schedule for the job
daily_ingestion_schedule = ScheduleDefinition(
    job=daily_ingestion_job,
    cron_schedule="0 6 * * *",  # 6 AM daily
    default_status=DefaultScheduleStatus.STOPPED,
)

# Resources - FastAPI to DuckDB only
resources = {
    "duckdb_warehouse": DuckDBWarehouse(
        database_path=os.getenv("DUCKDB_PATH", "/app/data/analytics.duckdb")
    ),
    "fastapi_client": FastAPIClient(
        base_url=os.getenv("FASTAPI_URL", "http://fastapi:8000")
    ),
    # TODO: Add back dbt resource once dbt integration is working
    # "dbt": DbtCliResource(
    #     project_dir=dbt_project.project_dir,
    #     profiles_dir=dbt_project.project_dir,
    #     target="dev",
    # ),
}

# Main definitions (without dbt assets for now)
defs = Definitions(
    assets=[
        *ingestion_assets,
        # TODO: Add back dbt assets once working
        # dakota_dbt_assets,
    ],
    jobs=[
        daily_ingestion_job,
    ],
    schedules=[
        daily_ingestion_schedule,
    ],
    resources=resources,
)

# Export for Dagster to find
__all__ = ["defs"]