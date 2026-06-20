# ML Arena

A web platform that lets a user upload a dataset, select a target column, and start an automated machine-learning training job.

## Why it matters

The project turns model experimentation into a repeatable workflow. Instead of manually comparing algorithms, the service runs training in the background and makes the resulting model available for download.

## What it does

- Accepts CSV datasets
- Detects classification or regression tasks
- Compares models with PyCaret
- Runs training asynchronously with Celery and Redis
- Tracks jobs and downloadable model files

## Technology

FastAPI, PyCaret, Pandas, Celery, Redis, SQLite, JWT, HTML, CSS, and JavaScript.

## Run

Install `requirements.txt`, start Redis and a Celery worker, then run:

```bash
uvicorn main:app --reload
```

The current login is a prototype and should be replaced before production use.
