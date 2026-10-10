---
description: "Strikte architectuur- en componentenstandaarden voor de Vue 3 Frontend."
globs: "frontend/**/*"
---

# Vue 3 Frontend Regels

## UI Framework & Componenten (Shadcn-Vue)

- Wij gebruiken **shadcn-vue** voor alle herbruikbare UI componenten.
- Ga NIET zelf standaard knoppen, modals, of formulieren bouwen met losse Tailwind classes als daar een Shadcn component voor bestaat.
- Als je een component nodig hebt dat nog niet in `src/components/ui/` staat, installeer dit via de terminal met: `npx shadcn-vue@latest add [component-naam]`.
- Gebruik altijd de `cn()` utility uit `@/lib/utils` voor het samenvoegen van dynamische Tailwind classes.

## Reactivity & Composables (VueUse)

- Maak standaard gebruik van **@vueuse/core** voor veelvoorkomende logica (bijv. `useWindowSize`, `onClickOutside`, `useStorage`, `useDebounceFn`).
- Schrijf GEEN handmatige window listeners als er een VueUse alternatief is.

## TypeScript & Type Safety (STRIKT)

- Het gebruik van het type `any` is **STRIKT VERBODEN**. Gebruik bij onbekende data `unknown` en valideer dit, of definieer de exacte TypeScript interface.
- De frontend types sluiten aan op het OpenAPI schema via `src/types/schema.d.ts` (genereer via `npm run generate:types`).

## API Communicatie & State

- API communicatie verloopt via de centrale Axios instance in `src/services/api.ts`.
- Globale applicatiestate wordt beheerd in **Pinia** stores (`src/stores/`).

## Formulieren & Iconen

- Formulieren worden gebouwd met **vee-validate** in combinatie met **Zod** schema validatie.
- Iconen worden uitsluitend geïmporteerd uit **@lucide/vue** (bijv. `import { Check, AlertCircle } from 'lucide-vue-next'`).

# Kwaliteitsgarantie (No Lazy Workarounds)

1. Gebruik NOOIT quick hacks of linter suppressions (`// eslint-disable`, `/* @ts-ignore */`, `/* @vue-ignore */`).
2. Los fouten altijd structureel op met correcte types en idiomatische Vue 3 Composition API code.
