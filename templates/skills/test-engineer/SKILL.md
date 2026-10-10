---
name: test-engineer
description: "Test automation en quality assurance skill voor Pytest en Vitest testsuites, mocks en integratietesten."
---

# Skill: test-engineer

**Doel:** Fungeren als Senior QA / Test Automation Engineer. Helpt bij het opzetten, schrijven en uitvoeren van robuuste unit- en integratietesten voor backend (Pytest) en frontend (Vitest).

## Richtlijnen voor Test Creatie

### 1. Backend Testing (Pytest + FastAPI + Async SQLAlchemy)

- Gebruik `httpx.AsyncClient` met `ASGITransport` voor het testen van FastAPI endpoints.
- Gebruik een isolated database fixture (in-memory SQLite of Docker testcontainer) zodat testen elkaar niet beïnvloeden.
- Test altijd de "Happy Path", randgevallen (edge cases), en foutcondities (400, 404, 422).

Voorbeeld Pytest structuur (`backend/tests/test_endpoints.py`):
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
```

### 2. Frontend Testing (Vitest + Vue Test Utils)

- Test component rendering, interactie (klikken, invoer), en form validatie met Vee-Validate / Zod.
- Mock Axios API calls zodat frontend tests onafhankelijk van een live backend kunnen slagen.

### 3. Test Executie

Voer tests altijd uit via de terminal:
```bash
# Backend testen
cd backend && pytest -v

# Frontend testen (indien vitest geconfigureerd)
cd frontend && npm run test
```
