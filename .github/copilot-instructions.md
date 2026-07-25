# SecureWealth AI - GitHub Copilot Instructions

You are the primary software engineer working on SecureWealth AI.

This repository already contains a complete architecture specification located at:

docs/PROJECT_SPEC.md

Before making ANY code changes:

- Read docs/PROJECT_SPEC.md completely.
- Follow the architecture exactly.
- Do not invent new folders.
- Do not change technologies.
- Do not simplify features.
- Do not replace libraries without explicit instructions.

---

# Project Goal

Build an enterprise-grade AI Financial Safety and Decision Intelligence Platform.

The application must feel like a production fintech product rather than a hackathon prototype.

---

# Tech Stack

Frontend

- Next.js 15
- TypeScript
- TailwindCSS
- shadcn/ui
- Recharts
- Framer Motion

Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT Authentication

Machine Learning

- Pandas
- NumPy
- Scikit-learn
- Isolation Forest
- XGBoost
- SHAP

AI

- LangGraph
- LangChain
- Groq API

Database

- PostgreSQL

Memory

- ChromaDB

Deployment

- Docker
- Railway
- Vercel

---

# Coding Standards

Always write production-quality code.

Use:

- Type hints
- Docstrings
- Logging
- Exception handling
- Validation
- Modular architecture
- SOLID principles

Never write placeholder code unless explicitly requested.

Never leave TODO comments.

Implement complete functionality.

---

# API Standards

Every endpoint must include:

Proper request validation

Proper response models

Status codes

Error handling

Logging

Authentication where required

---

# Frontend Standards

Modern fintech UI.

Responsive.

Accessible.

Dark mode ready.

Beautiful animations.

Reusable components.

No inline styling.

---

# AI Standards

Every AI decision must be explainable.

Every prediction returns:

- confidence
- explanation
- contributing features

---

# Security

Never hardcode secrets.

Use environment variables.

Use JWT.

Hash passwords.

Validate every request.

---

# Development Rules

Always prefer maintainability over shortcuts.

Always keep files organized.

Never duplicate logic.

Always reuse utilities.

Always keep naming consistent.

Always update documentation if architecture changes.

---

The objective is to build a production-ready application suitable for enterprise deployment.