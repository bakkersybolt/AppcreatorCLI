# Vue 3 frontend

Schrijf componenten met de Composition API en `<script setup lang="ts">`.

## Componenten (Shadcn-Vue)

- Gebruik Shadcn-Vue-componenten uit `@/components/ui/` voor knoppen, dialogs, formulieren en tabellen. Bouw die niet zelf met losse Tailwind-classes: dan lopen stijl en toegankelijkheid uiteen.
- Staat een component nog niet in `frontend/src/components/ui/`, installeer het dan eerst. De skill `vue-shadcn` beschrijft hoe.
- Voeg dynamische classes samen met `cn()` uit `@/lib/utils`.
- Importeer iconen uit `@lucide/vue`, bijvoorbeeld `import { Check } from '@lucide/vue'`.

## TypeScript

- Gebruik geen `any`; de linter keurt het af. Gebruik bij onbekende data `unknown` en valideer die, of definieer een interface.
- API-types komen uit `frontend/src/types/schema.d.ts`. Dat bestand wordt gegenereerd met `npm run generate:types`; bewerk het niet met de hand. Exporteer domeintypes via `frontend/src/types/index.ts`.

## Data en state

- Roep de API aan via de Axios-instance in `frontend/src/services/api.ts`, zodat basis-URL en authenticatie op één plek staan.
- Gedeelde state hoort in Pinia-stores in `frontend/src/stores/`. State van één component blijft in die component.
- Gebruik `@vueuse/core` voor browserlogica zoals `useStorage`, `useDebounceFn` en `onClickOutside` in plaats van eigen event listeners.

## Formulieren

- Bouw formulieren met vee-validate en een Zod-schema.

## Suppressies

- Gebruik `eslint-disable`, `@ts-ignore` of `@vue-ignore` alleen met een toelichting op dezelfde regel waarom het nodig is. Los de oorzaak op waar dat kan.
