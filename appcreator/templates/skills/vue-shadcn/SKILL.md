---
name: vue-shadcn
description: "Werkwijze voor de Vue 3-frontend met Shadcn-Vue: componenten installeren en gebruiken, formulieren met validatie en foutafhandeling, en het thema aanpassen. Gebruik bij elk werk aan schermen of componenten in frontend/src."
---

# Vue-shadcn

De frontend draait op Vue 3, Tailwind CSS v4 (via `@tailwindcss/vite`, zonder `tailwind.config.js`), Shadcn-Vue op `reka-ui`, `vue-sonner` voor meldingen en vee-validate met zod voor formulieren.

## Componenten installeren

Shadcn-Vue-componenten worden als broncode in het project gezet, in `frontend/src/components/ui/`. Kijk eerst of het component daar al staat. Bij de start staan er `alert`, `button`, `form`, `input`, `label` en `sonner`.

Gebruik altijd het script, nooit `npx shadcn-vue add` direct:

```bash
# Eén of meer componenten (vanuit de projectroot of frontend/)
frontend/scripts/shadcn-add.sh tooltip
frontend/scripts/shadcn-add.sh card dialog table
```

Het script draait `shadcn-vue add` (vaste versie, te overschrijven met `SHADCN_VUE_VERSION=`) en ruimt daarna de bekende bijwerkingen op:

- bestaande componenten worden nooit overschreven (`yes n`); wil je dat bewust, overschrijf dan met de hand;
- `package.json`, `package-lock.json` en `src/assets/index.css` worden teruggezet (geen pakket `cn`, geen Google-font, geen extra `@layer base`); bij een gewijzigde lockfile draait het `npm ci`; het begin van de css-diff wordt getoond voor als je er iets uit nodig hebt;
- `from 'cn'` wordt `from '@/lib/utils'`;
- de nieuwe bestanden worden met Prettier opgemaakt, zodat `npm run lint` slaagt;
- het meldt de nieuwe bestanden, nieuwe bestanden buiten `src/components/ui/` en gewijzigde bestaande bestanden.

**Exitcode 2:** een nieuw component importeert een pakket dat niet in `package.json` staat (bijv. `calendar` → `@internationalized/date`). Het script noemt de naam; voeg het pakket bewust toe met `npm install <naam>`, of verwijder de nieuwe componentbestanden weer.

**Korte controle achteraf:** `git status` toont alleen nieuwe bestanden onder `src/components/ui/`, daarna `npm run lint && npm run build`.

De instellingen staan in `frontend/components.json`. De geïnstalleerde bestanden zijn van het project: pas ze aan als het ontwerp daarom vraagt.

## Een component gebruiken

```vue
<script setup lang="ts">
import { Plus } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const emit = defineEmits<{
  create: []
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Overzicht</CardTitle>
      <CardDescription>Beheer je actieve records</CardDescription>
    </CardHeader>
    <CardContent>
      <Button class="gap-2" @click="emit('create')">
        <Plus class="h-4 w-4" />
        Nieuw toevoegen
      </Button>
    </CardContent>
  </Card>
</template>
```

- Importeer componenten uit `@/components/ui/<component>` en iconen uit `@lucide/vue`.
- Voeg voorwaardelijke classes samen met `cn()` uit `@/lib/utils`: `:class="cn('rounded-lg border', isActive && 'border-primary')"`.
- Meldingen gaan via `toast` uit `vue-sonner`; de enige `<Toaster>` staat in `App.vue`. Een API-fout buiten een formulier toon je met `useApiError().showError(error, 'Laden lukte niet.')` uit `@/composables/useApiError`: die geeft per HTTP-status een Nederlandse tekst en toont nooit de Engelse `detail` van de backend.

## Formulieren

Leg de validatie vast in een Zod-schema en koppel het formulier aan `useFormFeedback`:

```vue
<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { toast } from 'vue-sonner'
import { z } from 'zod'

import FormAlert from '@/components/common/FormAlert.vue'
import { Button } from '@/components/ui/button'
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { useFormFeedback } from '@/composables/useFormFeedback'
import { api } from '@/services/api'

const form = useForm({
  validationSchema: toTypedSchema(
    z.object({
      name: z.string().min(1, 'Vul een naam in.').max(100),
    }),
  ),
})
const { formError, submit } = useFormFeedback(form, { fallback: 'Opslaan lukte niet.' })

const onSubmit = submit(async (values) => {
  await api.post('/items', values)
  toast.success('Opgeslagen.')
})
</script>

<template>
  <form class="space-y-4" @submit="onSubmit">
    <FormField v-slot="{ componentField }" name="name">
      <FormItem>
        <FormLabel>Naam</FormLabel>
        <FormControl><Input v-bind="componentField" :disabled="form.isSubmitting.value" /></FormControl>
        <FormMessage />
      </FormItem>
    </FormField>
    <FormAlert v-if="formError"><span v-text="formError" /></FormAlert>
    <Button type="submit" :disabled="form.isSubmitting.value">
      <span v-text="form.isSubmitting.value ? 'Opslaan…' : 'Opslaan'" />
    </Button>
  </form>
</template>
```

### Vaste regel voor formulieren

Elk formulier doet deze vier dingen (uitleg in `frontend/src/composables/useFormFeedback.ts`, voorbeeldtests in `frontend/src/composables/__tests__/useFormFeedback.spec.ts`):

1. **`useFormFeedback(form, { fallback, messages, fieldMap })` en `submit(fn)`** in plaats van `handleSubmit(fn)` met
   een eigen try/catch. Een 422 van Pydantic komt dan bij het veld in het Nederlands; al het andere in `formError`.
2. **`<FormAlert v-if="formError">` boven de verstuurknop**, niet alleen een toast. Bekende 422-bedrijfsregels van
   het endpoint (een tekst als `detail`) krijgen een eigen Nederlandse tekst via `messages: { 422: '…' }`.
3. **Focus op het eerste foute veld** gaat vanzelf via `submit`, mits elk veld bij een fout `aria-invalid="true"`
   heeft. `FormControl` doet dat; bij `defineField` of een eigen invoer zet je `:aria-invalid="!!errors.x"` zelf.
4. **Na opslaan `toast.success('… opgeslagen.')`** en tijdens het opslaan een uitgeschakelde knop met "Opslaan…".

Gebruik in zod-regels liefst een eigen tekst; zonder tekst geeft `lib/zod-nl.ts` een Nederlandse standaardtekst.
Houd de limieten gelijk aan het backend-schema. Test per formulier: mislukte opslag toont de `FormAlert`, een leeg
verplicht veld krijgt de focus, en een Pydantic-422 staat bij het veld.

## Thema

De huisstijl staat in `frontend/src/assets/brand/tokens.css` (`--brand-primary`, `--brand-bg`, `--brand-radius`, `--brand-font-sans`, ...). `frontend/src/assets/index.css` koppelt die aan de shadcn-variabelen (`--primary`, `--background`, `--radius`) en via `@theme inline` aan Tailwind. Pas kleuren aan in `tokens.css` (de skill `design-system` vult ze), niet in de componenten. Gebruik in componenten de bijbehorende classes zoals `bg-primary`, `text-muted-foreground`, `bg-success/10` en `text-destructive`. Vaste kleuren zoals `bg-blue-500` volgen het thema niet.

Er is geen donkere modus: `dark:`-classes werken alleen onder een `.dark`-class, die standaard nergens staat.

## Data ophalen

Haal data op via `api` uit `@/services/api` (basis-URL `/api/v1`, in development via de Vite-proxy naar de backend) en gebruik de gegenereerde types uit `frontend/src/types/`. Toon bij elke aanroep een laadstatus en een foutmelding.

## Valkuilen

- De shadcn-CLI zet `from 'cn'`-imports, een npm-pakket `cn` en soms een Google-font met `@layer base` in `src/assets/index.css` (het lettertype staat lokaal via `@fontsource-variable/inter`). `scripts/shadcn-add.sh` draait dat allemaal terug; daarom nooit de CLI direct gebruiken.
- reka-ui zet de staat in `data-state="open|closed|checked|..."`; de shadcn-componenten gebruiken korte varianten (`data-open:`, `data-checked:`). Die worden in `src/assets/index.css` met `@custom-variant` op reka's attributen gezet. Verwijder die regels niet.
- `vue-sonner` v2 heeft zijn css apart (`import 'vue-sonner/style.css'` in `components/ui/sonner/Sonner.vue`); zonder die import duwt de toaster de pagina weg.
- Een file-upload: zet geen eigen `Content-Type`; axios kiest bij `FormData` zelf `multipart/form-data`.

## Controleren

```bash
cd frontend && npm run lint && npm run test && npm run build
```
