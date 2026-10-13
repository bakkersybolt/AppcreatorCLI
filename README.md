# AppCreator CLI 🚀

> **AI-Ready Project Scaffolding CLI** voor moderne Fullstack, Backend, Embedded en CLI applicaties met ingebouwde regels en skills voor **Google Antigravity** en **Claude Code**.

AppCreator stelt je in staat om via een interactieve terminal wizard binnen enkele seconden een complete, werkende en modulaire mappenstructuur op te zetten. Elk gegenereerd project krijgt regels en skills voor de AI-assistent die je in de wizard kiest: Google Antigravity (`.agents/`), Claude Code (`CLAUDE.md` + `.claude/`) of beide.

---

## ✨ Functionaliteiten

- **🎯 Categorie-gestuurde Wizard:** Kies uit 4 kernarchetypes met alleen de relevante vervolgvragen.
- **🧱 Volledig Modulaire Lagen:** Geen starre sjablonen, maar herbruikbare backend, frontend, database en AI-lagen samengesteld met Jinja2.
- **🤖 Geïntegreerde AI-Skills:** alleen de skills die bij het projecttype passen worden aangeboden.
  - **`init-project`:** startskill die de lokale omgeving controleert.
  - **`brainstorm-architect`:** ontwerpsessie in rondes (doel, gebruikers, datamodel, API, schermen) met als uitkomst `docs/ontwerp.md` en `docs/bouwplan.md`. Standaard bij web en backend.
  - **`feature-builder`:** bouwt de applicatie plak voor plak volgens het bouwplan. Standaard bij web en backend.
  - **`test-engineer`:** zet de testomgeving op en schrijft tests met Pytest en Vitest.
  - **`code-reviewer`:** beoordeelt wijzigingen op fouten, security, types en architectuur.
  - **`database-architect`:** schema-ontwerp en Alembic-migraties (bij een database).
  - **`docker-devops`:** Docker Compose, debuggen van containers en productie-images.
  - **Stack-skills** (`python-fastapi`, `vue-shadcn`, `esp32-development`) worden automatisch toegevoegd.
  - `test-engineer`, `code-reviewer`, `database-architect` en `docker-devops` zijn optioneel.
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

## 🧠 Aan de Slag met je AI-assistent

In de wizard kies je voor welke assistent de regels en skills worden gegenereerd:

| | Google Antigravity | Claude Code |
| :--- | :--- | :--- |
| Projectcontext (altijd actief) | `.agents/rules/project-context.md` | `CLAUDE.md` |
| Regels per map | `.agents/rules/*.md` (`trigger: glob`) | `.claude/rules/*.md` (`paths:`) |
| Skills | `.agents/skills/<naam>/SKILL.md` | `.claude/skills/<naam>/SKILL.md` |

Zodra je project is aangemaakt:

1. Navigeer naar de projectmap en open die in je assistent:
   ```bash
   cd MijnApplicatie
   antigravity .   # of: claude
   ```
2. Type in de chat:
   ```text
   /init-project
   ```
   De assistent controleert je omgeving. Bij een web- of backendproject gaat hij daarna direct door met de ontwerpsessie:

   | Stap | Skill | Uitkomst |
   | :--- | :--- | :--- |
   | 1 | `/init-project` | Werkende ontwikkelomgeving |
   | 2 | `/brainstorm-architect` | `docs/ontwerp.md` en `docs/bouwplan.md`: doel, gebruikers, datamodel, API en schermen |
   | 3 | `/feature-builder` | De applicatie, plak voor plak gebouwd en afgevinkt in het bouwplan |

   De ontwerpsessie begint bij het doel: wat is het idee, welk probleem lost het op en wanneer is de applicatie geslaagd. Een onderbroken sessie gaat verder waar hij was gebleven. Bij een ESP32- of CLI-project stelt `/init-project` zelf drie intakevragen.

De inhoud van regels en skills komt uit één bron in `appcreator/templates/rules/` en `appcreator/templates/skills/`. De frontmatter per assistent staat in `appcreator/core/assistants.py`.

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
│   ├── main.py                # Typer CLI commando's (create, list, add-skill, info, dev, start)
│   ├── ui.py                  # Rich styling, banners, tabellen en voortgang
│   ├── core/
│   │   ├── generator.py       # Modulaire Jinja2 rendering, lagen-assembler & docker-compose
│   │   ├── naming.py          # Slug, Python-packagenaam en validatie van de applicatienaam
│   │   ├── assistants.py      # AI-assistenten (Antigravity, Claude Code) en rule-frontmatter
│   │   ├── skills.py          # Skillcatalogus: welke skill past bij welk projecttype
│   │   ├── detector.py        # Systeemdetectie (uv, npm, pnpm, git, docker)
│   │   ├── manifest.py        # .appcreator.json beheer
│   │   ├── installer.py       # Automatische dependency installatie & git init
│   │   └── dev_runner.py      # Lokale dev-services met gecombineerde logs
│   └── templates/             # Wordt meegeleverd in het package (alleen *.jinja wordt gerenderd)
│       ├── common/            # Universele bestanden (.gitignore, README, dev.sh)
│       ├── backends/fastapi/  # Werkende FastAPI backend boilerplate
│       ├── frontends/vue3/    # Werkende Vue 3 + Tailwind + Shadcn frontend
│       ├── embedded/esp32/    # Werkende PlatformIO ESP32 firmware
│       ├── cli/python-typer/  # Werkende Python CLI boilerplate
│       ├── rules/             # Regelteksten (zonder frontmatter, die komt per assistent)
│       └── skills/            # Skillcatalogus (10 skills, SKILL.md of SKILL.md.jinja)
└── tests/
    ├── test_cli.py            # Tests voor de CLI commando's
    └── test_generation.py     # End-to-end tests voor alle projecttypen
```
