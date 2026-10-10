---
name: docker-devops
description: "DevOps en containerisatie skill voor multi-stage Dockerfiles, Docker Compose netwerken, volume management en CI/CD pipelines."
---

# Skill: docker-devops

**Doel:** Fungeren als DevOps Engineer. Zorgt voor betrouwbare containerisatie, Docker Compose orchestration en productieklare deployments.

## Docker Standaarden

### 1. Docker Compose Orchestration
- Zorg voor healthchecks op service-afhankelijkheden (bijv. Postgres `pg_isready` voordat de backend opstart).
- Gebruik named volumes voor persistente data (`postgres_data`).
- Gebruik `.env` bestanden voor gevoelige variabelen; commit nooit wachtwoorden of API keys in repository's.

Handige commando's:
```bash
# Services op de achtergrond starten
docker compose up -d

# Logs bekijken van een specifieke service
docker compose logs -f backend

# Status en containers controleren
docker compose ps

# Afsluiten inclusief volumes opruimen
docker compose down -v
```

### 2. Multi-Stage Docker Builds
Voor productie builds gebruik je altijd multi-stage containers om de image footprint minimaal te houden:
- **Frontend:** Build fase met Node 20 -> serveer via lichte Nginx Alpine image.
- **Backend:** Build fase voor wheels/dependencies -> minimale Python slim runtime.
