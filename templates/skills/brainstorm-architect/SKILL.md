---
name: brainstorm-architect
description: "Fungeert als Software Architect en UI/UX Designer om backend datamodellen, styling en Shadcn-Vue UI componenten vast te stellen en automatisch te installeren via een interactieve grill-me sessie."
---

# Skill: brainstorm-architect

**Doel:** Samen met de ontwikkelaar het project van boilerplate naar een functionele, prachtig gestylede MVP brengen. Deze skill bouwt direct voort op de context die is vastgelegd via `/init-project` en doorloopt de fases stap voor stap.

---

## Werkwijze voor de AI Assistent

### Voorbereiding: Context Ophalen
Lees **eerst** `.agents/rules/project-context.md` en `README.md`.
- Het hoofddoel, de doelgroep en de globale features zijn hierin al gedefinieerd door de `/init-project` intake.
- Vraag de gebruiker **niet** opnieuw naar wat de app globaal doet, maar verwijs ernaar en ga direct de diepte in.

Doorloop de volgende 4 fases sequentieel. Gebruik een actieve, onderzoekende houding (in de stijl van `/grill-me`) om aannames te valideren en ontwerpbeslissingen scherp te krijgen:

---

### Fase 1: Datamodellen & Relaties (Backend)

1. **Grill de architectuur:**
   - Bekijk de eventueel al gegenereerde entiteiten in `backend/app/models/`.
   - Vraag naar de specifieke attributen, datatypes en onderlinge relaties (bijv: *"Moet een `Todo` gekoppeld zijn aan een `User` via een ForeignKey?", "Zijn er statusvelden zoals `pending`/`completed`?"*).
2. **Implementatie uitvoeren:**
   - Werk de SQLAlchemy modellen bij of voeg nieuwe toe in `backend/app/models/`.
   - Schrijf de bijbehorende Pydantic schema's in `backend/app/schemas/`.
   - Koppel de endpoints in `backend/app/api/v1/endpoints/` en monteer ze in `router.py`.

---

### Fase 2: Styling & Huisstijl (Frontend)

1. **Visuele sfeer bepalen:**
   - Vraag de gebruiker naar het gewenste kleurenpalet en uitstraling (bijv: *Modern slate met emerald accenten*, *Dark cyber met neon paars*, of *Clean minimalistisch neutraal*).
2. **Thema toepassen:**
   - Pas direct de CSS variabelen aan in `frontend/src/assets/index.css` (`--primary`, `--radius`, `--background`, `--card`, etc.).

---

### Fase 3: Shadcn-Vue Componenten Bepalen & Automatisch Installeren

1. Analyseer samen met de gebruiker welke pagina's en layouts er nodig zijn voor de MVP (bijv. `DashboardLayout.vue`, `ItemOverview.vue`, `CreateModal.vue`).
2. Bepaal welke **Shadcn-Vue** componenten hiervoor nodig zijn (bijv. `button`, `card`, `input`, `dialog`, `table`, `badge`, `tabs`, `dropdown-menu`).
3. **Voer de installatie direct uit via de terminal:**
   ```bash
   cd frontend && npx -y shadcn-vue@latest add button card input dialog table badge tabs --yes
   ```
4. Controleer of de componenten netjes zijn toegevoegd in `frontend/src/components/ui/`.

---

### Fase 4: Premium MVP Pagina's & Integratie Bouwen

1. Bouw de daadwerkelijke Vue views in `frontend/src/views/` en componenten in `frontend/src/components/`.
2. Zorg voor:
   - Gebruik van de geïnstalleerde Shadcn componenten.
   - Koppeling met de API via `@/services/api`.
   - Volledige TypeScript types (geen `any`).
   - Hot-reload testen (via `appcreator dev`).
