---
name: python-fastapi
description: "Werkwijze voor endpoints, schema's, modellen en dependencies in de FastAPI-backend van dit project. Gebruik bij elk werk in backend/app: een entiteit of endpoint toevoegen, validatie, dependency injection of authenticatie."
---

# Python-fastapi

## Waar staat wat

| Onderdeel                   | Bestand                                                          |
| :-------------------------- | :--------------------------------------------------------------- |
| App en lifespan             | `backend/app/main.py`                                            |
| Instellingen                | `backend/app/core/config.py` (`settings`, namen in hoofdletters) |
| Database-engine en `get_db` | `backend/app/db/session.py`                                      |
| `Base` voor modellen        | `backend/app/db/base.py`                                         |
| Gedeelde dependencies       | `backend/app/api/deps.py` (`DbSession`)                          |
| Routerregistratie           | `backend/app/api/v1/router.py`                                   |
| Endpoints                   | `backend/app/api/v1/endpoints/<entiteit>.py`                     |
| Modellen en schema's        | `backend/app/models/`, `backend/app/schemas/`                    |

Alle routes staan onder `/api/v1`. Een nieuw project heeft alleen het health-endpoint; bouw nieuwe endpoints volgens het patroon hieronder. Het ontwerp van de applicatie staat in `.docs/ontwerp.md` zodra de ontwerpsessie is gedaan.

## Een entiteit toevoegen of uitwerken

1. **Model** in `backend/app/models/<entiteit>.py`, en importeer het in `models/__init__.py`.
2. **Schema's** in `backend/app/schemas/<entiteit>.py`: `Create`, `Update` met alle velden optioneel, en `Response` met `model_config = ConfigDict(from_attributes=True)`.
3. **Endpoints** volgens het voorbeeld.
4. **Router** registreren in `backend/app/api/v1/router.py`.
5. **Controleren** in http://localhost:8000/docs of met een test.

```python
# backend/app/api/v1/endpoints/todo.py
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate

router = APIRouter()


@router.get("/", response_model=list[TodoResponse])
async def list_todos(db: DbSession, skip: int = 0, limit: int = 50):
    result = await db.execute(select(Todo).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, db: DbSession):
    todo = await db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo niet gevonden")
    return todo


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate, db: DbSession):
    todo = Todo(**payload.model_dump())
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, payload: TodoUpdate, db: DbSession):
    todo = await db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo niet gevonden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: DbSession):
    todo = await db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo niet gevonden")
    await db.delete(todo)
    await db.commit()
```

Verplaats logica naar `backend/app/services/<entiteit>.py` zodra een endpoint meer doet dan één query.

## Valkuilen

- **Vergeten modelimport:** een model dat niet in `models/__init__.py` staat, krijgt geen tabel.
- **Gewijzigd model:** `create_all` maakt alleen ontbrekende tabellen aan en past bestaande niet aan. Gebruik migraties of maak de ontwikkeldatabase opnieuw aan.
- **Relaties in async code:** een relatie die niet vooraf is geladen geeft een `MissingGreenlet`-fout. Laad relaties in de query met `selectinload()`.
- **Blokkerende aanroepen:** `time.sleep` of `requests` in een `async` endpoint zet alle andere verzoeken stil.
- **Geen database gekozen:** `get_db` levert dan `None`. Voeg eerst een database toe voordat je queries schrijft.
- **Nieuwe instelling:** voeg die toe aan `Settings` in `core/config.py` en aan `backend/.env.example`.

## Verdieping

- [references/dependency-injection-patterns.md](references/dependency-injection-patterns.md): paginering, sorteren en filteren, servicelaag, request-context en caching als dependency. Lees dit bij lijsten met veel records of gedeelde logica tussen endpoints.
- [references/auth-jwt.md](references/auth-jwt.md): inloggen met JWT, wachtwoorden hashen en een `CurrentUser`-dependency. Lees dit zodra endpoints beveiligd moeten worden.
