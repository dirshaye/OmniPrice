# OmniPrice Implementation Roadmap

This document outlines the strategic plan to build the OmniPrice Modular Monolith, moving from a "Walking Skeleton" to a full MVP.

## Phase 1: The Foundation (Core & Auth)
**Goal:** A running server with secure user access.
1.  **Database Setup**: Finalize `core/database.py` (MongoDB/Motor/Beanie).
2.  **Authentication Module**:
    *   User Models (Beanie Documents).
    *   Registration & Login Logic.
    *   JWT Token Generation & Validation.
3.  **Frontend Auth**: Connect React Login/Register pages to the backend.

## Phase 2: The "Noun" (Product Module)
**Goal:** Users can manage the core entities (Products).
1.  **Backend**:
    *   Product Models (Name, SKU, Cost, Price).
    *   CRUD API Endpoints.
2.  **Frontend**:
    *   Connect `Products` page to list, add, and edit real products.

## Phase 3: The "Input" (Scraper & Competitors)
**Goal:** Ingest external data for dynamic pricing.
1.  **Competitor Module**: Define "Competitor" entities linked to Products.
2.  **Scraper Engine**:
    *   Setup **Celery** (Task Queue) + **Redis**.
    *   Implement **Playwright** tasks to visit URLs and extract prices.
3.  **Frontend**: Display competitor data on the dashboard.

## Phase 4: The "Brain" (Pricing & LLM)
**Goal:** Intelligent analysis and price optimization.
1.  **Pricing Engine**: Implement rule-based logic (e.g., "5% below average").
2.  **LLM Integration**: Connect Google Gemini API for context/sentiment analysis.
3.  **Frontend**: Pricing Dashboard with AI suggestions.

## DevOps & Infrastructure Strategy
*   **Containerization**: Keep `docker-compose` active for local development (Mongo, Redis) immediately.
*   **Deployment**: Configure CI/CD pipelines after **Phase 2** is stable.
*   **Monitoring**: Configure Prometheus/Grafana dashboards during **Phase 3** (when we have background tasks to monitor).
