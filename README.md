# AppCreator CLI 🚀

> **AI-Ready Project Scaffolding CLI** voor moderne Fullstack, Backend, Embedded en CLI applicaties met ingebouwde **Google Antigravity** skills en regels.

AppCreator stelt je in staat om via een interactieve terminal wizard binnen enkele seconden een complete, werkende en modulaire mappenstructuur op te zetten. Elk gegenereerd project wordt direct uitgerust met `.agents/rules` en `.agents/skills`, inclusief een interactieve architect-workflow om datamodellen en Shadcn UI-componenten direct met AI te bouwen.

---

## ✨ Functionaliteiten

- **🎯 Categorie-gestuurde Wizard:** Kies uit 4 kernarchetypes met alleen de relevante vervolgvragen.
- **🧱 Volledig Modulaire Lagen:** Geen starre sjablonen, maar herbruikbare backend, frontend, database en AI-lagen samengesteld met Jinja2.
- **🤖 Geïntegreerde AI-Skills (`.agents/`):**
  - **`init-project`:** Universele startskill die de lokale omgeving controleert en de ontwikkelaar aan de hand neemt.
  - **`brainstorm-architect`:** Interactieve software architect & UI/UX designer die domeinen vastlegt en automatisch de juiste **Shadcn-Vue** componenten installeert via de terminal (`npx shadcn-vue add ...`).
  - **`test-engineer`:** Geautomatiseerde Pytest & Vitest testsuites en mocks.
  - **`code-reviewer`:** Kwaliteits- en securitychecks zonder compromissen of anti-patterns.
  - **`database-architect`:** Relationeel schema-ontwerp en Alembic async migraties.
  - **`docker-devops`:** Multi-stage Dockerfiles en Docker Compose orchestration.
- **⚡ Slimme Tooling & Snelheid:**
  - Automatische detectie van `uv` voor razendsnelle Python installaties.
  - Detectie van `npm`/`pnpm` voor frontend installaties.
  - Optionele automatische `git init` met initiële commit.
  - Gegenereerd `.appcreator.json` projectmanifest voor metadata en toekomstige CLI acties.

---

## 📁 Ondersteunde Project Categorieën

| Categorie | Tech Stack | Inbegrepen Componenten |
| :--- | :--- | :--- |
| **🌐 Fullstack Web & API** | Vue 3 + FastAPI | Vue 3 (Vite, TS, Tailwind, Shadcn-Vue, Pinia, Axios) + FastAPI (SQLAlchemy 2.0 async, Pydantic v2, CORS, Healthcheck) + PostgreSQL / SQLite + Docker Compose |
| **⚡ Backend API Only** | FastAPI | Async FastAPI service met routing, Pydantic schemas, database sessies en health endpoint |
| **📡 Embedded / IoT** | ESP32 PlatformIO | C++ firmware skelet met 115200 baud serial telemetrie, JSON status payloads, LED indicator en Arduino framework |
| **💻 Python CLI Tool** | Typer + Rich | Moderne command-line tool met Typer routing, Rich console formatting en Pytest testsuite |

---

## 🛠️ Installatie & Gebruik

### Installatie (Ontwikkelmodus)

```bash
git clone https://github.com/sybolt/AppcreatorCLI.git
cd AppcreatorCLI
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Een Nieuw Project Aanmaken

Start eenvoudig de interactieve wizard:
```bash
appcreator
```
Of geef direct de projectnaam mee:
```bash
appcreator create MijnApplicatie
```

### Beschikbare Categorieën & Skills Bekijken

```bash
appcreator list
```

### Extra AI-Skill Toevoegen aan een Bestaand Project

Ben je al aan het werk in een project en wil je bijvoorbeeld de `database-architect` of `docker-devops` skill toevoegen?
```bash
cd MijnApplicatie
appcreator add-skill
```
Of direct bij naam:
```bash
appcreator add-skill database-architect
```

### Project Info Bekijken

```bash
cd MijnApplicatie
appcreator info
```

---

## 🧠 Aan de Slag met Google Antigravity

Zodra je project is aangemaakt:

1. Navigeer naar de projectmap:
   ```bash
   cd MijnApplicatie
   ```
2. Open de map in **Google Antigravity**:
   ```bash
   antigravity .
   ```
3. Type in de Antigravity chat:
   ```text
   /init-project
   ```
   De AI assistent verifieert direct je omgeving (Python venv, Node dependencies, Git) en start automatisch de bijpassende vervolgstap:
   - Voor Web/Fullstack: De **`brainstorm-architect`** sessie start direct, vraagt naar je gewenste schermen en kleurstijl, en installeert zelfstandig de benodigde Shadcn-Vue componenten via `npx shadcn-vue@latest add [component]`!

---

## 🧪 Testen

Voer de geautomatiseerde integratietesten uit:
```bash
pytest -v tests/
```

---

## 📂 Codebase Structuur

```text
AppcreatorCLI/
├── appcreator/
│   ├── main.py                # Typer CLI commando's (create, list, add-skill, info)
│   ├── ui.py                  # Rich styling, banners, tabellen en voortgang
│   └── core/
│       ├── generator.py       # Modulaire Jinja2 rendering & lagen-assembler
│       ├── detector.py        # Systeemdetectie (uv, npm, pnpm, git, docker)
│       ├── manifest.py        # .appcreator.json beheer
│       └── installer.py       # Automatische dependency installatie & git init
├── templates/
│   ├── common/                # Universele bestanden (.gitignore, README, docker-compose)
│   ├── backends/fastapi/      # Werkende FastAPI backend boilerplate
│   ├── frontends/vue3/        # Werkende Vue 3 + Tailwind + Shadcn frontend
│   ├── embedded/esp32/        # Werkende PlatformIO ESP32 firmware
│   ├── cli/python-typer/      # Werkende Python CLI boilerplate
│   ├── rules/                 # Centrale .agents/rules regels
│   └── skills/                # Centrale .agents/skills catalogus (9 skills)
└── tests/
    └── test_generation.py     # End-to-end tests voor alle projecttypen
```
