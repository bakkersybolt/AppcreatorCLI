# Vue 3 frontend

Schrijf componenten met de Composition API en `<script setup lang="ts">`.

## Componenten (Shadcn-Vue)

- Gebruik Shadcn-Vue-componenten uit `@/components/ui/` voor knoppen, dialogs, formulieren en tabellen. Bouw die niet zelf met losse Tailwind-classes: dan lopen stijl en toegankelijkheid uiteen.
- Staat een component nog niet in `frontend/src/components/ui/`, installeer het dan met `frontend/scripts/shadcn-add.sh <component>`, nooit met `npx shadcn-vue add` direct (de CLI wijzigt anders `package.json` en `index.css`). De skill `vue-shadcn` beschrijft hoe.
- Kleuren, lettertype en afronding komen uit de design tokens in `frontend/src/assets/brand/tokens.css` (Tailwind v4, `@theme` in `src/assets/index.css`). Geen losse hexkleuren of `bg-[#…]` in componenten; de regels staan in `design-rules.md`.
- Voeg dynamische classes samen met `cn()` uit `@/lib/utils`.
- Importeer iconen uit `@lucide/vue`, bijvoorbeeld `import { Check } from '@lucide/vue'`.

## TypeScript

- Gebruik geen `any`; de linter keurt het af. Gebruik bij onbekende data `unknown` en valideer die, of definieer een interface.
- API-types komen uit `frontend/src/types/schema.d.ts`. Dat bestand wordt gegenereerd met `npm run generate:types`; bewerk het niet met de hand. Exporteer domeintypes via `frontend/src/types/index.ts`.

## Data en state

- Roep de API aan via de Axios-instance in `frontend/src/services/api.ts`, zodat basis-URL en authenticatie op één plek staan. De basis-URL is relatief (`/api/v1`); in ontwikkeling stuurt de Vite-proxy dat door naar de backend.
- Gedeelde state hoort in Pinia-stores in `frontend/src/stores/`. State van één component blijft in die component.
- Gebruik `@vueuse/core` voor browserlogica zoals `useStorage`, `useDebounceFn` en `onClickOutside` in plaats van eigen event listeners.

## Formulieren

- Bouw formulieren met vee-validate en een Zod-schema, en gebruik `useFormFeedback` met `<FormAlert>` voor fouten van de API (zie de skill `vue-shadcn`, "Vaste regel voor formulieren").
- Toon het resultaat van een actie met een toast (`vue-sonner`, al gekoppeld in `App.vue`).

## Suppressies

- Gebruik `eslint-disable`, `@ts-ignore` of `@vue-ignore` alleen met een toelichting op dezelfde regel waarom het nodig is. Los de oorzaak op waar dat kan.

## Routes en hulp

- Elke nieuwe route krijgt `meta: { help: '<categorie>/<slug>' }` in `frontend/src/router/routes.ts` en een hulpartikel in `frontend/src/content/help/` (skill `documentatie`). De test `content/help/__tests__/docs.spec.ts` controleert dat.
