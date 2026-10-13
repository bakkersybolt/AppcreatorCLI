# Python & FastAPI backend

Volg PEP 8 en geef alle functies type hints.

## Structuur

- **Routers (`backend/app/api/v1/endpoints/`):** alleen HTTP-afhandeling: invoer valideren, een service of query aanroepen en het antwoord teruggeven. Registreer elke nieuwe router in `backend/app/api/v1/router.py`.
- **Services (`backend/app/services/`):** maak deze map aan zodra een endpoint meer doet dan één query. Businesslogica hoort hier, zodat routers dun en los testbaar blijven.
- **Models (`backend/app/models/`):** SQLAlchemy 2.0 met `Mapped` en `mapped_column`. Importeer elk nieuw model in `models/__init__.py`, anders kent `Base.metadata` de tabel niet.
- **Schemas (`backend/app/schemas/`):** Pydantic v2 met `ConfigDict`. Gebruik aparte schema's voor invoer (`Create`, `Update`) en uitvoer (`Response`), zodat interne velden niet in de API lekken.
- **Dependencies (`backend/app/api/deps.py`):** `Annotated`-aliassen zoals `DbSession`. Voeg nieuwe gedeelde dependencies hier toe.
- **Configuratie (`backend/app/core/config.py`):** lees instellingen via `settings`, niet via `os.environ` elders in de code.

## Async

- Endpoints die de database of het netwerk raken zijn `async`.
- Gebruik geen blokkerende aanroepen (`time.sleep`, `requests`, synchrone databasedrivers) in async code: die zetten de hele event loop stil. Gebruik `asyncio.sleep`, `httpx.AsyncClient` of `asyncio.to_thread`.

## Fouten

- Gebruik `HTTPException` met een passende statuscode en een duidelijke melding.
- Log onverwachte fouten en geef geen stack traces of interne details terug aan de client.

## Suppressies

- Gebruik `# noqa` of `# type: ignore` alleen met een toelichting op dezelfde regel waarom het nodig is.
