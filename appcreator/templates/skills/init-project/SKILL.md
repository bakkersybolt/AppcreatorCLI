---
name: init-project
description: "Universele opstart- en intake-skill voor nieuw gegenereerde projecten. Controleert dependencies, definieert het applicatiedoel via een intake, werkt README.md en project-context.md bij, en start de brainstorm-sessie."
---

# Skill: init-project

**Doel:** Fungeren als onboardingsgids voor de ontwikkelaar. Deze skill controleert de lokale ontwikkelomgeving, stelt gerichte intake-vragen om het doel en de scope van de applicatie vast te leggen, actualiseert direct de `README.md` en `.agents/rules/project-context.md`, en schakelt daarna naadloos door naar de interactieve architectuursessie.

---

## Werkwijze voor de AI Assistent

Wanneer de gebruiker deze skill start (via `/init-project` of bij de start van een nieuw project), doorloop je de volgende vier stappen:

### Stap 1: Omgevingscontrole (Environment Verification)

1. **Lees de bestaande context:**
   - Inspecteer `.agents/rules/project-context.md` en `.appcreator.json` om de gekozen categorie, backend, frontend, database en eventuele domein-entiteiten te begrijpen.
2. **Controleer de repository status:**
   - **Backend:** Controleer of `backend/.venv` bestaat. Zo niet, meld dat dependencies geïnstalleerd kunnen worden via `cd backend && pip install -r requirements.txt`.
   - **Frontend:** Controleer of `frontend/node_modules` bestaat. Zo niet, meld dat `npm install` benodigd is.
   - **Git:** Controleer of een git repository geïnitialiseerd is.
3. **Meld de status kort en bondig aan de gebruiker.** Herinner de gebruiker eraan dat de applicatie lokaal gestart kan worden met `appcreator dev` (of `./dev.sh`).

---

### Stap 2: Intake - Doel en Doelgroep Definiëren

Stel de gebruiker 2 tot 3 scherpe, concrete intake-vragen om de visie en scope van de applicatie helder te krijgen:

1. **Wat is het hoofddoel van deze applicatie?**
   - *Welk specifiek probleem lost het op voor de gebruiker?*
2. **Wie zijn de primaire eindgebruikers en wat is de kern MVP-flow?**
   - *Wat zijn de 2 à 3 belangrijkste acties die een gebruiker direct moet kunnen uitvoeren?*
3. **Zijn er specifieke vereisten of wensen?**
   - *Bijvoorbeeld: authenticatie/rollen, externe API integraties, specifieke dashboard grafieken of realtime updates?*

> *Wacht op de antwoorden van de gebruiker voordat je doorgaat naar Stap 3.*

---

### Stap 3: Documentatie & Project Context Bijwerken

Zodra de gebruiker antwoord heeft gegeven op de intake-vragen, voer je direct de volgende updates uit in de codebase:

1. **`README.md` actualiseren:**
   - Herschrijf de root `README.md` naar een volwaardige projectdocumentatie met:
     - Een pakkende titel en samenvatting van het zojuist gedefinieerde doel.
     - **Kernfunctionaliteiten (MVP Scope):** Opsomming van de overeengekomen features.
     - **Tech Stack & Architectuur:** Toelichting van de backend, frontend en database.
     - **Lokale Ontwikkeling:** Instructies om het project te draaien met `appcreator dev` (of `./dev.sh`).
2. **`.agents/rules/project-context.md` aanvullen:**
   - Voeg onderaan het bestand de nieuwe context toe zodat elke toekomstige AI-sessie direct op de hoogte is:
     ```markdown
     ## Doel & Scope van de Applicatie

     - **Hoofddoel:** <Korte samenvatting van het probleem en de oplossing>
     - **Doelgroep:** <Primaire gebruikers>
     - **Kernfunctionaliteiten (MVP):**
       - <Feature 1>
       - <Feature 2>
       - <Feature 3>
     - **Aanvullende Wensen:** <Eventuele extra vereisten>
     ```

---

### Stap 4: Doorstart naar de Brainstorm & Architectuursessie

Meld de gebruiker dat het fundament, de documentatie en de AI-context nu succesvol zijn vastgelegd.

Schakel direct door naar de **Brainstorm & Architectuur fase**:
- Omdat het hoofddoel en de doelgroep nu al bekend zijn in `project-context.md`, hoeven deze vragen **niet** opnieuw gesteld te worden.
- Adviseer de gebruiker om over te gaan naar `/brainstorm-architect` en beveel het slash-commando **/grill-me** aan:
  > *"De basis en doelstellingen zijn nu vastgelegd in `README.md` en `project-context.md`. We kunnen nu direct door met `/brainstorm-architect`. Tip: typ `/grill-me` om in een interactief interview de datamodellen, relaties en benodigde Shadcn UI-componenten direct scherp te stellen en te implementeren!"*
