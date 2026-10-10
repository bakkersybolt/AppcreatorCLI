---
name: database-architect
description: "Database specialist voor relationeel schema-ontwerp, SQLAlchemy 2.0 modellen, Alembic async migraties en query-optimalisatie."
---

# Skill: database-architect

**Doel:** Fungeren als Database Architect. Begeleidt schema-ontwerp, relationele koppelingen (one-to-many, many-to-many), indexeringsstrategieën en databasemigraties met Alembic.

## Werkwijze & Standaarden

### 1. SQLAlchemy 2.0 Async Modellen
- Gebruik altijd `Mapped[T]` en `mapped_column()` voor typeveiligheid.
- Definieer foreign keys en relaties expliciet met `relationship(..., lazy="selectin")` om N+1 query problemen in async code te voorkomen.

Voorbeeld:
```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    total_amount: Mapped[float] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="orders", lazy="selectin")
```

### 2. Alembic Migraties
Voer databasewijzigingen altijd gecontroleerd door via migratiescripts:
```bash
# Nieuwe migratie genereren
alembic revision --autogenerate -m "add orders table"

# Migratie toepassen
alembic upgrade head

# Rollback indien nodig
alembic downgrade -1
```

### 3. Query Optimalisatie
- Maak samengestelde indexen aan op kolommen die frequent gecombineerd gefilterd of gesorteerd worden.
- Gebruik `select(Model).options(selectinload(Model.relation))` voor eager loading.
