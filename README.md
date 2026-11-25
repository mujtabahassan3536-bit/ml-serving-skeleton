# ML House Price Serving Skeleton

A production-oriented FastAPI inference and data-serving skeleton demonstrating strict API input contracts, automated messy-data ETL, multi-stage non-root Docker containerization, and multi-job GitHub Actions CI/CD.

## Architecture & Request Flow

```text
Client Request (JSON)
       │
       ▼
Pydantic v2 Schema (app/schema.py) ──► Normalizes & validates inputs (422 on invalid data)
       │
       ▼
Pandas ETL & Estimator (app/predictor.py) ──► Cleans noisy CSV rows & computes city stats/estimates
       │
       ▼
FastAPI Endpoints (app/main.py) ──► /health | /stats | /predict
       │
       ▼
Multi-Stage Docker Runtime (appuser) ──► Verified via GitHub Actions CI/CD