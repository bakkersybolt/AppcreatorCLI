---
trigger: glob
globs: "backend/**/*"
description: "Strikte architectuur- en codeerstandaarden voor de Python / FastAPI backend."
---

# Python & FastAPI Backend Regels

Houd je altijd aan PEP 8 en gebruik strikte type hints.

## Architectuur & Mappenstructuur

- **Routers (`backend/app/api/v1/endpoints/`):** FastAPI route handlers. Geen directe database queries of complexe business logica hier.
- **Services (`backend/app/services/`):** Domein en business logica. Schrijf herbruikbare functies en classes.
- **Models (`backend/app/models/`):** Uitsluitend SQLAlchemy 2.0 (async) modellen via `Mapped` en `mapped_column`.
- **Schemas (`backend/app/schemas/`):** Uitsluitend Pydantic v2 modellen (gebruik `model_config = ConfigDict(...)`). Splits ALTIJD input (`Create`, `Update`) en output (`Response`).
- **Dependencies (`backend/app/api/deps.py`):** Gebruik Python `Annotated` syntax voor Dependency Injection (bijv. `DbSession = Annotated[AsyncSession, Depends(get_db)]`).
- **Configuratie (`backend/app/core/config.py`):** Beheer alle instellingen en omgevingsvariabelen via `pydantic-settings`.

## Asynchrone Verwerking

- Gebruik altijd `async` endpoints voor database- of I/O-operaties.
- Gebruik NOOIT synchrone blocking calls (zoals `time.sleep`) binnen async routes; gebruik `asyncio.sleep` of `run_in_executor`.

## Foutafhandeling

- Gooi FastAPI `HTTPException` met heldere foutboodschappen en correcte HTTP status codes (400, 401, 403, 404, 422).
- Zorg dat interne serverfouten netjes gelogd worden.
