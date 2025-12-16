# OmniPrice System Architecture

Based on the codebase analysis (specifically `omniprice/main.py` and `infra/docker/docker-compose.yml`), OmniPrice is architected as a **Modular Monolith**.

## System Design Diagram

```mermaid
graph TD
    %% Styles
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef module fill:#ffffff,stroke:#2e7d32,stroke-width:1px,stroke-dasharray: 5 5;
    classDef infra fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef external fill:#eeeeee,stroke:#616161,stroke-width:2px;

    %% Users
    User((User))

    %% Frontend
    subgraph Frontend [Frontend Container :3000]
        ReactApp[React SPA]:::frontend
    end

    %% Backend Monolith
    subgraph Backend [Backend Container :8000]
        FastAPI[FastAPI App]:::backend
        
        subgraph Modules [Business Logic Modules]
            Auth[Auth Module]:::module
            Product[Product Module]:::module
            Pricing[Pricing Module]:::module
            Scraper[Scraper Module]:::module
            LLM[LLM Module]:::module
        end
        
        subgraph Core [Core Layer]
            Config[Settings]:::module
            DBConn[DB Connections]:::module
        end
        
        FastAPI --> Auth
        FastAPI --> Product
        FastAPI --> Pricing
        FastAPI --> Scraper
        FastAPI --> LLM
        Modules --> Core
    end

    %% Infrastructure
    subgraph Infra [Infrastructure]
        MongoDB[(MongoDB)]:::infra
        Redis[(Redis)]:::infra
        Celery[Celery Workers]:::infra
    end

    %% External
    subgraph External [External Services]
        Gemini[Gemini AI]:::external
        Websites[Competitor Sites]:::external
    end

    %% Flows
    User -->|Browser| ReactApp
    ReactApp -->|REST API| FastAPI
    
    %% Data Access
    Core -->|Motor/Beanie| MongoDB
    Core -->|Caching| Redis
    
    %% Async Tasks
    Scraper -.->|Tasks| Celery
    Celery -->|Store Results| MongoDB
    Celery -->|Fetch Data| Websites
    
    %% AI
    LLM -->|API Call| Gemini
```

## Component Breakdown

### 1. Frontend (Port 3000)
- **Tech**: React
- **Role**: Single Page Application (SPA) for the dashboard.
- **Communication**: Consumes the REST API exposed by the backend.

### 2. Backend Monolith (Port 8000)
- **Tech**: Python, FastAPI, Uvicorn.
- **Role**: Hosts all business logic in a single process.
- **Structure**:
    - **API Layer**: `api/v1/` handles routing and request validation.
    - **Modules**: `modules/` contains domain logic (Product, Pricing, etc.).
    - **Core**: `core/` handles shared concerns like DB connections and Settings.

### 3. Infrastructure
- **MongoDB**: Primary database. Accessed asynchronously via `motor`.
- **Redis**: Used for caching pricing data and as a message broker for Celery.
- **Celery**: Handles background tasks (e.g., scraping competitor prices) to keep the API responsive.

## Data Flow Example: "Get Optimized Price"
1. **User** requests price on Dashboard.
2. **FastAPI** receives `GET /api/v1/pricing/{id}`.
3. **Pricing Module** is called directly (function call).
4. **Pricing Module** checks **Redis** cache.
5. If miss, queries **MongoDB** via `core.database`.
6. Returns data to Frontend.
