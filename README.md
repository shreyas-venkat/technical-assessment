# Dakota Analytics - Data Engineering Technical Assessment

## Overview

Build an end-to-end data pipeline that ingests source data, enriches it with synthetic data, transforms it using dbt, and produces analytical reports. Using AI tooling is fine, just be professional.

## The Challenge

![Architecture Diagram](data-engineer-applicant.png)

Implement a production-ready data pipeline with these components:

### 1. FastAPI Data Service (20 points) **COMPLETED**
Create a FastAPI application that generates synthetic enrichment data relevant to energy analytics.
- Use `uv` for dependency management
- Design and implement useful enrichment data schemas
- Containerize the service
- See [api/README.md](api/README.md)

**Implementation Details:**
- **QByte GL Data Service**: Generates synthetic General Ledger records for oil & gas operations
- **Deterministic Data**: Fixed seed ensures consistent data across runs
- **Streaming & Batch**: Real-time streaming (30s intervals) + historical batch data (365 days)
- **Production Ready**: Custom error handling, health checks, comprehensive logging
- **Oil & Gas Domain**: Wells, basins, AFE numbers, JIB numbers, proper GL accounting

**Quick Start:**
```bash
# Build and run the FastAPI service
docker compose up --build fastapi

# Access the service
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
# Stream: http://localhost:8000/get-gl

# Test streaming with Python client
python view_stream.py
```

### 2. Data Ingestion (20 points)
Build clients to fetch data from:
- A source of your choice
- OR (not and) EIA API (https://www.eia.gov/opendata/) - register for free API key
- Your FastAPI enrichment service

Implement error handling, retries, and logging.
See [ingestion/README.md](ingestion/README.md)

### 3. Orchestration (20 points)
Choose and implement a workflow orchestrator (Dagster, Airflow, Prefect, etc.)
- Daily batch ingestion from EIA
- Frequent ingestion from FastAPI service
- dbt transformation execution
- Data quality checks
- Report generation
- Error handling and monitoring

See [orchestration/README.md](orchestration/README.md)

### 4. Database Design (15 points)
Design a Database schema for:
- Raw data storage
- Transformed analytics tables
- Time-series considerations if any

Include initialization scripts and ER diagram.
See [database/README.md](database/README.md)

### 5. dbt Transformations (20 points)
Implement layered dbt models:
- Organize in chosen architecture pattern
- Include data quality tests
- Document models
- Use incremental models where appropriate

See [dbt/README.md](dbt/README.md)

### 6. Reporting (10 points)
Generate automated reports of your choice:
- Excel dashboard with metrics and charts
- Jupyter notebook with exploratory analysis
- PDF executive summary
- Doesn't have to be all, just relevant

See [reports/README.md](reports/README.md)

## Deliverables

### Required Structure

```
your-fork/
├── README.md              # Update with setup instructions
├── docker-compose.yml     # All services defined
├── run.sh / run.bat       # Startup script (see below)
├── .env.example          # Environment variables template
│
├── api/                  # FastAPI service
├── ingestion/            # Data ingestion clients
├── orchestration/        # Your orchestrator implementation
├── database/             # Schema and init scripts
├── dbt/                  # dbt project
├── reports/              # Report generation
│
├── docs/                 # YOUR DOCUMENTATION
│   ├── architecture.md   # System architecture and design
│   ├── decisions.md      # Technical decisions and rationale
│   └── er_diagram.png    # Database schema diagram
│
└── tests/                # Your tests

```

### Documentation (in `/docs/`)

Create these files explaining your work:

**`docs/architecture.md`**
- System design overview
- Technology choices and why
- Data flow
- Scalability considerations

**`docs/decisions.md`**
- Key technical decisions
- Trade-offs considered
- Alternative approaches
- Rationale for choices

### Startup Script Requirements

**Create a script (e.g., `run.sh` for Unix/Mac or `run.bat` for Windows) that:**

1. Sets up the environment (dependencies, `.env` file, builds containers)
2. Starts all services via docker-compose
3. Runs the pipeline end-to-end
4. Generates reports
5. Provides clear output/logging of what's happening

The script should be idempotent and handle:
- First-time setup
- Subsequent runs
- Basic error handling

We will evaluate your solution by running this script in a clean environment. Include usage instructions in your README.

## Evaluation Criteria

- **Technical Excellence (40%)** - Code quality, error handling, testing, performance
- **Architecture & Design (30%)** - Tool choices, database design, scalability, separation of concerns
- **Documentation (20%)** - Clarity, completeness, decision rationale
- **Innovation (10%)** - Creative solutions, best practices, additional value

## Time Expectation

Approximately 4-6 hours. Focus on quality and demonstrating best practices.

## Submission

1. Fork this repository
2. Implement your solution
3. Test that your startup script works in a clean environment
4. Email your repository URL to: **technical-assessment@dakotaanalytics.com**

Include in your email:
- Your name
- Repository link (should be public)
- Brief summary of your approach

## Questions?

For clarification on requirements only: **technical-assessment@dakotaanalytics.com**

We can clarify requirements but won't help with implementation decisions - that's what we're evaluating!

---
