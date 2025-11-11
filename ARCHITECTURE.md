# Data Pipeline Architecture

## Overview

This project implements a comprehensive data engineering pipeline for oil & gas analytics, centered around a FastAPI service that generates synthetic GL (General Ledger) data.

## Architecture Components

### 1. **API Layer** (`api/`)
- **FastAPI Service**: Core data generation and streaming service
- **Clean Design**: RESTful endpoints with comprehensive documentation
- **Data Models**: Strongly typed models using dataclasses and Pydantic
- **Error Handling**: Custom exception classes with global handlers
- **Health Monitoring**: Built-in health check endpoints

### 2. **Database Layer** (`database/`)
- **PostgreSQL**: Primary data store for raw and transformed data
- **Schema Design**: Time-series optimized for GL transactions
- **Initialization**: Automated schema setup via init scripts

### 3. **Transformation Layer** (`dbt/`)
- **dbt Models**: Layered transformation architecture
- **Data Quality**: Built-in tests and documentation
- **Incremental Processing**: Efficient handling of large datasets

### 4. **Ingestion Layer** (`ingestion/`)
- **Multi-Source**: EIA API + FastAPI streaming data
- **Batch & Streaming**: Handles both batch and real-time ingestion
- **Error Recovery**: Robust retry mechanisms

### 5. **Orchestration Layer** (`orchestration/`)
- **Workflow Management**: Dagster-based pipeline orchestration
- **Scheduling**: Automated daily/hourly job execution
- **Monitoring**: Pipeline health and performance tracking

### 6. **Analytics Layer** (`reports/`)
- **Jupyter Notebooks**: Interactive analysis environment
- **Visualization**: Charts and dashboards for insights
- **Export Capabilities**: PDF/Excel report generation

## Container Architecture

### Current Setup (`docker-compose.yml`)
```yaml
services:
  postgres:     # Database
  fastapi:      # API Service
```

### Full Pipeline (`docker-compose.full-pipeline.yml`)
```yaml
services:
  postgres:     # Database
  redis:        # Caching & Queuing
  fastapi:      # API Service
  ingestion:    # Data Ingestion
  dbt:          # Transformations
  dagster:      # Orchestration
  jupyter:      # Analytics (Optional)
  prometheus:   # Monitoring (Optional)
  grafana:      # Dashboards (Optional)
```

## Data Flow

1. **Historical Data**: Generated deterministically at startup (365 days)
2. **Streaming Data**: Continuous generation (30-second intervals)
3. **Ingestion**: Raw data stored in PostgreSQL staging tables
4. **Transformation**: dbt models create analytics-ready tables
5. **Analytics**: Jupyter notebooks for exploration and reporting

## Key Features

### ✅ **Clean API Design**
- RESTful endpoints with clear naming
- Comprehensive OpenAPI documentation
- Proper HTTP status codes and error responses
- Streaming and batch endpoints

### ✅ **Proper Data Models**
- Strongly typed dataclasses for GL records
- Pydantic models for configuration
- Clear separation of concerns
- Domain-specific oil & gas fields

### ✅ **Reasonable Synthetic Data Generation**
- Deterministic generation with seeded randomness
- Realistic oil & gas accounting scenarios
- Proper GL double-entry bookkeeping
- Time-series data with proper fiscal periods

### ✅ **Good Error Handling**
- Custom exception hierarchy
- Global exception handlers
- Structured error responses
- Comprehensive logging

### ✅ **API Documentation**
- FastAPI auto-generated docs
- Detailed endpoint descriptions
- Example requests/responses
- Interactive testing interface

### ✅ **Containerization**
- Multi-stage Docker builds
- Health checks for all services
- Environment-based configuration
- Production-ready setup

## Scaling Considerations

### Current State: **Development Ready**
- Single FastAPI container
- Basic PostgreSQL setup
- Suitable for development and testing

### Next Phase: **Production Ready**
- Multi-container architecture
- Redis for caching and queuing
- Monitoring and observability
- Horizontal scaling capabilities

### Future Enhancements
- Kubernetes deployment
- Auto-scaling based on load
- Multi-region deployment
- Advanced monitoring and alerting

## Getting Started

### Development (Current)
```bash
docker compose up fastapi
```

### Full Pipeline (Future)
```bash
docker compose -f docker-compose.full-pipeline.yml up
```

## Configuration

Environment variables are managed through:
- `.env` files for local development
- Docker environment variables for containers
- Pydantic Settings for type-safe configuration

Key configuration options:
- `HISTORICAL_DAYS`: Number of historical records to generate
- `STREAMING_INTERVAL_SECONDS`: Real-time generation frequency
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `EIA_API_KEY`: External API access

This architecture provides a solid foundation for a production-grade data engineering pipeline while maintaining simplicity for development and testing.
