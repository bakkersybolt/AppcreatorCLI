---
name: init-project
description: "Universele opstart- en intake-skill voor nieuw gegenereerde projecten. Controleert dependencies en start de initiële architectuursessie."
---

# Skill: init-project

**Doel:** Fungeren als onboardingsgids voor de ontwikkelaar. Deze skill controleert de lokale ontwikkelomgeving, bevestigt dat alle benodigdheden aanwezig zijn, en start direct de interactieve architect- of implementatiesessie.

## Instructies voor de AI Assistent

Wanneer de gebruiker deze skill start, voer je direct de volgende stappen uit:

### Stap 1: Omgevingscontrole (Environment Verification)
Controleer de status van de repository:
1. **Projectcontext lezen:** Lees `.agents/rules/project-context.md` en `.appcreator.json` om direct te begrijpen welke stack en tools zijn gekozen.
2. **Backend controle (indien van toepassing):**
   - Controleer of `backend/.venv` bestaat. Zo niet, bied aan om de virtuele omgeving aan te maken en `requirements.txt` te installeren via de terminal.
3. **Frontend controle (indien van toepassing):**
   - Controleer of `frontend/node_modules` bestaat. Zo niet, bied aan om `npm install` (of `pnpm install`) uit te voeren.
4. **Git controle:**
   - Controleer of er een git repository is geïnitialiseerd.

Rapporteer kort en overzichtelijk de gezondheidsstatus van het project aan de gebruiker.

### Stap 2: Starten van de Volgende Fase

Afhankelijk van het projecttype activeer je direct de juiste interactieve workflow:

- **Bij Fullstack Web & API of Frontend (Vue + FastAPI):**
  - Informeer de gebruiker dat de basis gereed is.
  - Vraag toestemming om direct over te gaan naar `/brainstorm-architect` om samen:
    1. De eerste domeinmodellen en backend-endpoints vast te stellen.
    2. De visuele huisstijl/kleuren in te stellen.
    3. De benodigde **Shadcn-Vue** componenten te selecteren en automatisch te installeren via `npx shadcn-vue@latest add ...`.
    4. De eerste pagina's te bouwen.

- **Bij Backend API Only:**
  - Vraag naar de specifieke domein-entiteiten (bijv. Users, Orders, Sensors) en genereer de SQLAlchemy modellen, Pydantic schema's en router endpoints.

- **Bij Embedded / IoT (ESP32):**
  - Vraag naar de aangesloten sensoren/actuatoren, WiFi configuratie (SSID/Wachtwoord placeholder) en eventueel MQTT/HTTP broker details.

- **Bij Python CLI:**
  - Vraag welke commando's en flags de tool nodig heeft en werk de argumentenstructuur direct uit.
