# SecureWealth AI

SecureWealth AI is an AI-powered financial safety and decision intelligence platform. This repository currently contains the production-grade foundation scaffold for the backend, frontend, database connectivity, Dockerization, and application structure required for the later intelligence phases.

## Project Overview

The platform is designed to evolve into a secure fintech product that can ingest customer transactions, maintain digital financial profiles, surface risk signals, and support explainable recommendations. The current build stops at foundation only and deliberately excludes machine learning, LangGraph orchestration, fraud detection, Digital Wealth Twin logic, recommendation logic, and report generation.

## Architecture

The repository is organized as a modular monorepo with clear separation between presentation, API, service, repository, and infrastructure layers.

- `frontend/` contains the Next.js 15 application with the landing page, auth pages, dashboard shell, theme handling, and reusable UI primitives.
- `backend/` contains the FastAPI application with configuration, logging, security helpers, routing, database session management, and structured error handling.
- `ml/` is reserved for future model training, inference, preprocessing, and explainability modules.
- `data/` stores the source transaction dataset.
- `scripts/` is reserved for repeatable automation tasks.

## Tech Stack

Frontend

- Next.js 15
- TypeScript
- TailwindCSS
- shadcn/ui-style component structure
- Framer Motion
- Axios
- Recharts
- Lucide React

Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT utilities
- Uvicorn

Infrastructure

- Docker
- Docker Compose
- Alembic scaffold

## Local Setup

### Backend

1. Create and activate a Python environment.
2. Install backend dependencies from `backend/requirements.txt`.
3. Copy `backend/.env.example` to `backend/.env` and adjust values for your environment.
4. Start the API from the `backend/` directory with Uvicorn.

Example:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. Install Node.js dependencies in `frontend/`.
2. Copy `frontend/.env.example` to `frontend/.env.local` if you want to override the backend URL.
3. Start the Next.js development server.

Example:

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

The root `docker-compose.yml` file starts PostgreSQL, the backend API, and the frontend application together.

```bash
docker compose up --build
```

## Folder Structure

```text
AI-Financial-Guardian/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── config/
│   │   ├── core/
│   │   ├── database/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tests/
│   │   └── utils/
│   ├── alembic/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── public/
│   ├── services/
│   ├── styles/
│   ├── types/
│   └── utils/
├── data/
├── docs/
├── ml/
├── scripts/
├── docker-compose.yml
└── README.md
```

## Foundation Status

This build includes:

- Backend configuration loading
- Structured logging and exception handling
- Request ID middleware
- PostgreSQL engine and session setup
- JWT and password hashing utilities
- Health and version endpoints
- Next.js app shell and responsive pages
- Dark mode toggle
- Docker and Compose scaffolding
- Alembic structure only

The following are intentionally deferred to later builds:

- Machine learning pipelines
- Fraud detection models
- Financial health scoring logic
- Digital Wealth Twin persistence
- LangGraph agents and AI orchestration
- Report generation
