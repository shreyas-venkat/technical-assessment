# FastAPI Fake Data Service

Build a FastAPI service that generates synthetic enrichment data for the pipeline.

## Requirements

- Create a FastAPI application that serves synthetic data
- Use `uv` for dependency management
- Containerize within Docker
- Include health check endpoint
- Generate data types relevant to your analysis (your choice for what makes sense)

## Local Development with Docker

```bash
# Build the container
docker compose build fastapi

# Run the service (and the optional postgres dependency)
docker compose up fastapi
```

The API will be exposed on `http://localhost:8000`. Interactive documentation is available at `http://localhost:8000/docs`, and the streaming endpoint example lives at `http://localhost:8000/get-gl`.

## What We're Looking For

- Clean API design
- Proper data models
- Reasonable synthetic data generation
- Good error handling
- API documentation (FastAPI auto-docs?)
- Containerization

The data you generate should enrich the source data in meaningful ways.
