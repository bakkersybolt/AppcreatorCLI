---
name: database-architect
description: "Ontwerpt het relationele schema, schrijft SQLAlchemy 2.0-modellen met relaties en indexen en beheert migraties met Alembic. Gebruik bij nieuwe of gewijzigde tabellen, relaties tussen entiteiten, trage queries of het opzetten van migraties."
---

# Database-architect

## Eenmalig: Alembic opzetten

Het gegenereerde project maakt tabellen aan met `create_all` bij het opstarten. Dat past bestaande tabellen niet aan. Zet Alembic op zodra het schema gaat veranderen. Controleer eerst of `backend/alembic/` al bestaat.

1. Initialiseer met het async-sjabloon:

   ```bash
   cd backend && .venv/bin/alembic init -t async alembic
   ```

2. Koppel de instellingen en de modellen in `backend/alembic/env.py`:

   ```python
   import app.models  # noqa: F401 - registreert alle tabellen op Base.metadata
   from app.core.config import settings
   from app.db.base import Base

   config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
   target_metadata = Base.metadata
   ```

3. Verwijder de `create_all`-aanroep uit de `lifespan` in `backend/app/main.py`, zodat alleen migraties het schema beheren.
4. Maak de eerste migratie en pas die toe (zie hieronder).

Bestaat de ontwikkeldatabase al met tabellen van `create_all`, dan botst de eerste migratie daarmee. Vraag de gebruiker of de ontwikkeldatabase leeg mag, of markeer de bestaande stand met `alembic stamp head`.

## Migraties

```bash
cd backend

# Migratie genereren uit de modelwijzigingen
.venv/bin/alembic revision --autogenerate -m "add orders table"

# Toepassen
.venv/bin/alembic upgrade head
```

Lees elke gegenereerde migratie na voordat je hem toepast. Autogenerate herkent een hernoemde kolom als verwijderen plus toevoegen, en dat kost de data in die kolom.

`alembic downgrade` verwijdert kolommen en tabellen, inclusief de data. Voer het alleen uit als de gebruiker daar om vraagt.

## Modellen

```python
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    user: Mapped["User"] = relationship(back_populates="orders")
```

- Gebruik `Mapped[T]` en `mapped_column()`.
- Gebruik `Numeric` met `Decimal` voor geldbedragen. `float` geeft afrondingsfouten.
- Leg bij elke foreign key vast wat er bij verwijderen gebeurt (`ondelete`), en zet er een index op.
- Zet `unique=True` op velden die uniek moeten zijn, zoals een e-mailadres. Controleren in de code alleen is niet genoeg bij gelijktijdige verzoeken.

## Relaties laden

In async code kan een relatie niet achteraf worden geladen: dat geeft een `MissingGreenlet`-fout. Laad wat je nodig hebt in de query:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

result = await db.execute(select(User).options(selectinload(User.orders)))
```

Kies het laden per query. Een relatie die standaard altijd wordt meegeladen, maakt ook de queries traag die hem niet nodig hebben.

## Trage queries

- Zet `echo=True` aan (dat is `DEBUG=True` in dit project) en tel de queries per verzoek. Eén query per rij in een lijst wijst op een ontbrekende `selectinload`.
- Voeg een index toe op kolommen waarop wordt gefilterd of gesorteerd, en een samengestelde index als ze steeds samen voorkomen.
- Pagineer lijsten met `limit` en `offset`.
