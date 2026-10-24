# AppCreator CLI 🚀

> **AI-Ready Project Scaffolding CLI** voor moderne Fullstack, Backend, Embedded en CLI applicaties met ingebouwde regels en skills voor **Google Antigravity** en **Claude Code**.

AppCreator stelt je in staat om via een interactieve terminal wizard binnen enkele seconden een complete, werkende en modulaire mappenstructuur op te zetten. Elk gegenereerd project krijgt regels en skills voor de AI-assistent die je in de wizard kiest: Google Antigravity (`.agents/`), Claude Code (`CLAUDE.md` + `.claude/`) of beide.

---

## ✨ Functionaliteiten

- **🎯 Categorie-gestuurde Wizard:** Kies uit 4 kernarchetypes met alleen de relevante vervolgvragen.
- **🧱 Volledig Modulaire Lagen:** Geen starre sjablonen, maar herbruikbare backend, frontend, database en AI-lagen samengesteld met Jinja2.
- **🤖 Geïntegreerde AI-Skills:** alleen de skills die bij het projecttype passen worden aangeboden.
  - **`init-project`:** startskill die de lokale omgeving controleert.
  - **`todo-beheer`:** legt werk buiten de scope van de chat (of op verzoek) vast als `.md`-todo in `.todos/`, in dezelfde mappenstructuur als de code. Toont en pakt open todo's ook op. Altijd aanwezig.
  - **`brainstorm-architect`:** ontwerpsessie in rondes (doel, gebruikers, datamodel, API, schermen). Elke ronde komt in een eigen bestand in `.docs/ontwerp/`, de bouwvolgorde in `.docs/sprints/overzicht.md`. Standaard bij web en backend.
  - **`sprint-plan`:** bereidt per sprint een bouwplan in fases voor en voert de sprint uit als leider-agent met (parallelle) subagents in git-worktrees, met fase- en sprintverslagen. Standaard bij web en backend.
  - **`open-vragen`:** legt beslissingen die nog genomen moeten worden vast in `.docs/open-vragen/`. Standaard bij web en backend.
  - **`documentatie`:** houdt `docs/` (technisch) en bij een frontend de hulpartikelen in de app bij; tests in het project dwingen af dat ze compleet blijven. Standaard bij web en backend.
  - **`design-system`:** legt de uitstraling vast in design tokens en `design-rules.md`, en neemt een ontwerp over uit elke bron (screenshot, URL, Figma, gegenereerde React-code, beschrijving). Standaard bij een Vue-frontend.
  - **`feature-builder`:** bouwt één losse plak buiten een sprint.
  - **`hobbyserver-deploy`:** uitrollen naar je eigen server (Docker + Traefik via GitHub Actions). Optioneel in de wizard bij PostgreSQL.
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
- **🔌 Eigen poorten per app:** elke web-app krijgt bij het aanmaken een vrij poortblok (bijv. backend 8100, frontend 5200, PostgreSQL 5433), zodat meerdere apps en worktrees naast elkaar draaien. De poorten staan in `.env` in de projectroot; alles leest ze daaruit.
- **🪝 Hooks voor Claude Code:** lint na elke wijziging, een guard voor shellcommando's in worktrees, een permissie-allowlist en een git pre-commit-hook voor de documentatie.

---

## 📁 Ondersteunde Project Categorieën

| Categorie                  | Tech Stack       | Inbegrepen Componenten                                                                                                                                       |
| :------------------------- | :--------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🌐 Fullstack Web & API** | Vue 3 + FastAPI  | Vue 3 (Vite, TS, Tailwind v4, shadcn-vue/reka-ui, Pinia, Axios) + FastAPI (SQLAlchemy 2.0 async, Pydantic v2, CORS, Healthcheck) + PostgreSQL / SQLite + Docker Compose |
| **⚡ Backend API Only**    | FastAPI          | Async FastAPI service met routing, Pydantic schemas, database sessies en health endpoint                                                                     |
| **📡 Embedded / IoT**      | ESP32 PlatformIO | C++ firmware skelet met 115200 baud serial telemetrie, JSON status payloads, LED indicator en Arduino framework                                              |
| **💻 Python CLI Tool**     | Typer + Rich     | Moderne command-line tool met Typer routing, Rich console formatting en Pytest testsuite                                                                     |

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

### Lokaal Starten

```bash
cd MijnApplicatie
appcreator dev        # database, backend en frontend met gecombineerde logs
```

`appcreator dev` gebruikt de poorten van het project en stopt met een duidelijke melding als een poort al bezet is.

### Poorten Bekijken of Wijzigen

```bash
appcreator ports              # tabel met de poorten, waar ze vandaan komen en of ze vrij zijn
appcreator ports --reassign   # nieuw vrij poortblok; .env, backend/.env, CLAUDE.md en docs worden bijgewerkt
appcreator ports --adopt      # een bestaand project: neem de poorten uit .env over in manifest en register
```

Het register van uitgedeelde poortblokken staat in `~/.appcreator/ports.json` (te verplaatsen met `APPCREATOR_HOME`).

### Project Info Bekijken

```bash
cd MijnApplicatie
appcreator info
```

---

## 🧠 Aan de Slag met je AI-assistent

In de wizard kies je voor welke assistent de regels en skills worden gegenereerd:

|                                | Google Antigravity                     | Claude Code                      |
| :----------------------------- | :------------------------------------- | :------------------------------- |
| Projectcontext (altijd actief) | `.agents/rules/project-context.md`     | `CLAUDE.md`                      |
| Regels per map                 | `.agents/rules/*.md` (`trigger: glob`) | `.claude/rules/*.md` (`paths:`)  |
| Skills                         | `.agents/skills/<naam>/SKILL.md`       | `.claude/skills/<naam>/SKILL.md` |

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

   | Stap | Skill                   | Uitkomst                                                                                         |
   | :--- | :---------------------- | :----------------------------------------------------------------------------------------------- |
   | 1    | `/init-project`         | Werkende ontwikkelomgeving                                                                       |
   | 2    | `/brainstorm-architect` | `.docs/ontwerp/` (één bestand per onderdeel) en `.docs/sprints/overzicht.md` met de sprints      |
   | 3    | `/sprint-plan`          | Per sprint een bouwplan, uitgevoerd door subagents, met verslagen en bijgewerkte documentatie    |

   De ontwerpsessie begint bij het doel: wat is het idee, welk probleem lost het op en wanneer is de applicatie geslaagd. Een onderbroken sessie gaat verder waar hij was gebleven. Bij een ESP32- of CLI-project stelt `/init-project` zelf drie intakevragen.

### Waar staat wat in een gegenereerd project

| Map | Inhoud |
| :--- | :--- |
| `CLAUDE.md` / `.agents/rules/project-context.md` | Projectcontext: stack, commando's, poorten, afspraken |
| `.claude/` / `.agents/` | Rules, skills (en bij Claude Code: hooks en `settings.json`) |
| `.docs/ontwerp/` | Het ontwerp, één bestand per onderdeel |
| `.docs/sprints/` | Bouwvolgorde en per sprint het bouwplan en de verslagen |
| `.docs/open-vragen/` | Beslissingen die nog genomen moeten worden |
| `.todos/` | Werk voor later, in dezelfde mappenstructuur als de code |
| `docs/` | Technische documentatie: hoe de app nu werkt |
| `frontend/src/content/help/` | Hulpartikelen voor gebruikers, getoond in de app |

De inhoud van regels en skills komt uit één bron in `appcreator/templates/rules/` en `appcreator/templates/skills/`. De frontmatter per assistent staat in `appcreator/core/assistants.py`.

---

## 🧪 Testen

Voer de geautomatiseerde integratietesten uit:

```bash
.venv/bin/pytest -q          # alle tests (ruff-controles van gegenereerde code worden overgeslagen zonder ruff)
```

---

## 📂 Codebase Structuur

```text
AppcreatorCLI/
├── appcreator/
│   ├── main.py                # Typer CLI commando's (create, list, add-skill, info, dev, start, ports)
│   ├── ui.py                  # Rich styling, banners, tabellen en voortgang
│   ├── core/
│   │   ├── generator.py       # Modulaire Jinja2 rendering, lagen-assembler, @flag-bestanden
│   │   ├── ports.py           # Poortblok per app: toewijzen, register, oplossen
│   │   ├── port_commands.py   # `appcreator ports` (tonen, --reassign, --adopt)
│   │   ├── design.py          # Onderdelen van het ontwerp (.docs/ontwerp/) per stack
│   │   ├── claude_settings.py # Kleine wijzigingen in een bestaand .claude/settings.json
│   │   ├── naming.py          # Slug, Python-packagenaam en validatie van de applicatienaam
│   │   ├── assistants.py      # AI-assistenten (Antigravity, Claude Code) en rule-frontmatter
│   │   ├── skills.py          # Skillcatalogus: welke skill past bij welk projecttype
│   │   ├── detector.py        # Systeemdetectie (uv, npm, pnpm, git, docker)
│   │   ├── manifest.py        # .appcreator.json beheer
│   │   ├── installer.py       # Automatische dependency installatie & git init
│   │   └── dev_runner.py      # Lokale dev-services met gecombineerde logs
│   └── templates/             # Wordt meegeleverd in het package (alleen *.jinja wordt gerenderd)
│       │                      # Een @flag in een bestands- of mapnaam (bijv. docs@backend/) maakt het conditioneel
│       ├── common/            # Universele bestanden (.gitignore, README, dev.sh, docker-compose, docs/, hooks, deploy)
│       ├── backends/fastapi/  # Werkende FastAPI backend boilerplate
│       ├── frontends/vue3/    # Werkende Vue 3 + Tailwind + Shadcn frontend
│       ├── embedded/esp32/    # Werkende PlatformIO ESP32 firmware
│       ├── cli/python-typer/  # Werkende Python CLI boilerplate
│       ├── rules/             # Regelteksten (zonder frontmatter, die komt per assistent)
│       └── skills/            # Skillcatalogus (SKILL.md of SKILL.md.jinja)
└── tests/                     # Tests per onderwerp: generatie, poorten, hooks, docs, skills, lint, frontend
```
