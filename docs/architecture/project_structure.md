# OmniPrice Project Structure

This document outlines the complete directory structure for the OmniPrice Modular Monolith system, including Backend, Frontend, and Infrastructure.

```text
OmniPrice/
│
├── omniprice/                      # BACKEND (FastAPI Monolith)
│   ├── __init__.py
│   ├── main.py                     # App entry point
│   │
│   ├── api/                        # API Gateway Layer
│   │   └── v1/                     # Version 1 Routes
│   │       ├── __init__.py
│   │       ├── products.py         # Product endpoints
│   │       ├── pricing.py          # Pricing endpoints
│   │       ├── competitors.py      # Competitor endpoints
│   │       ├── auth.py             # Auth endpoints
│   │       └── llm.py              # AI endpoints
│   │
│   ├── modules/                    # Business Logic Layer (Service-Oriented)
│   │   ├── product/                # Product Domain
│   │   │   ├── models.py           # DB Models
│   │   │   ├── schemas.py          # Pydantic Schemas
│   │   │   ├── repository.py       # DB Access
│   │   │   └── service.py          # Business Logic
│   │   ├── pricing/                # Pricing Domain
│   │   ├── competitor/             # Competitor Domain
│   │   ├── scraper/                # Scraper Domain
│   │   ├── auth/                   # Auth Domain
│   │   ├── llm/                    # AI Domain
│   │   └── notifications/          # Notification Domain
│   │
│   └── core/                       # Shared Infrastructure
│       ├── config.py               # Settings
│       ├── database.py             # MongoDB Connection
│       ├── redis.py                # Redis Connection
│       ├── security.py             # JWT Utils
│       ├── exceptions.py           # Custom Errors
│       └── dependencies.py         # FastAPI Dependencies
│
├── frontend/                       # FRONTEND (React)
│   ├── public/
│   ├── src/
│   │   ├── components/             # Reusable UI Components
│   │   │   ├── common/             # Buttons, Inputs, etc.
│   │   │   ├── layout/             # Header, Sidebar, Footer
│   │   │   └── features/           # Domain-specific components
│   │   ├── pages/                  # Page Views
│   │   │   ├── dashboard/
│   │   │   ├── products/
│   │   │   ├── pricing/
│   │   │   ├── competitors/
│   │   │   └── auth/
│   │   ├── services/               # API Clients (Axios)
│   │   ├── contexts/               # React Context (Auth, Theme)
│   │   ├── hooks/                  # Custom Hooks
│   │   ├── utils/                  # Helpers
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── Dockerfile
│
├── infra/                          # INFRASTRUCTURE
│   ├── docker/                     # Docker Compose files
│   ├── terraform/                  # IaC (AWS/Azure)
│   └── monitoring/                 # Prometheus/Grafana configs
│
├── docs/                           # DOCUMENTATION
│   ├── api/
│   └── architecture/
│
├── tests/                          # TESTING
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env                            # Environment Variables
├── .gitignore
├── Makefile                        # Command shortcuts
├── requirements.txt                # Python dependencies
└── README.md
```
