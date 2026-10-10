---
name: brainstorm-architect
description: "Fungeert als Software Architect en UI/UX Designer om backend domeinen, styling en Shadcn-Vue UI componenten vast te stellen en automatisch te installeren."
---

# Skill: brainstorm-architect

**Doel:** Samen met de ontwikkelaar het project van boilerplate naar een functionele, prachtig gestylede MVP brengen. Je doorloopt de fases stap voor stap en installeert benodigde componenten via de terminal.

## Werkwijze voor de AI Assistent

Doorloop de volgende 4 fases sequentieel. Vraag na elke fase om feedback en bevestiging van de ontwikkelaar voordat je verdergaat.

---

### Fase 1: Intake & Domein Modellen (Backend)

1. Vraag de gebruiker naar:
   - Het hoofddoel van de applicatie.
   - Wie de eindgebruikers zijn.
2. Doe op basis van het antwoord een concreet voorstel van de eerste 2 tot 4 domeinen/entiteiten (bijv. `Users`, `SensorReadings`, `Invoices`).
3. Zodra de gebruiker akkoord is, genereer je direct voor het belangrijkste domein:
   - Het SQLAlchemy model in `backend/app/models/`
   - Het Pydantic v2 schema in `backend/app/schemas/`
   - De FastAPI router in `backend/app/api/v1/endpoints/` en koppel deze aan de hoofdrouter.

---

### Fase 2: Styling & Huisstijl (Frontend)

1. Vraag de gebruiker naar de gewenste visuele sfeer en stijl:
   - Kleurenthema (bijv. "Modern slate met emerald accenten", "Donker cyber met paarse neon tinten", "Warm zand en navy").
   - Vormgeving (strak & zakelijk met scherpe hoeken, of modern & speels met grote radius).
2. Pas direct de CSS-variabelen aan in `frontend/src/assets/index.css`:
   - `--primary`, `--primary-foreground`, `--radius`, `--background`, etc.

---

### Fase 3: Shadcn UI Componenten Bepalen & Automatisch Installeren

1. Analyseer samen met de gebruiker welke eerste pagina's en layouts er nodig zijn (bijv. `DashboardLayout.vue`, `OverviewView.vue`, `CreateItemModal.vue`).
2. Stel een gerichte lijst samen van de benodigde **Shadcn-Vue** componenten (bijv. `button`, `card`, `input`, `dialog`, `table`, `dropdown-menu`, `badge`, `tabs`).
3. **Voer de installatie direct uit:**
   - Voer in de map `frontend/` het commando uit via de terminal:
     ```bash
     npx -y shadcn-vue@latest add button card input dialog table badge tabs --yes
     ```
   - Controleer of de componenten netjes in `frontend/src/components/ui/` zijn geplaatst.

---

### Fase 4: Premium UI Pagina's Bouwen

1. Bouw de daadwerkelijke Vue componenten voor de overeengekomen pagina's.
2. Gebruik uitsluitend:
   - De zojuist geïnstalleerde Shadcn componenten.
   - Tailwind CSS utility classes met `cn()`.
   - Lucide iconen uit `@lucide/vue`.
   - Veilige TypeScript types en VueUse composables.
3. Sluit de views aan op de Axios API service (`@/services/api`) en koppel ze aan `frontend/src/router/index.ts`.
