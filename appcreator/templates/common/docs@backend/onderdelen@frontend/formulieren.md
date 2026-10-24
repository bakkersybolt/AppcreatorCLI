---
onderwerp: Formulieren
categorie: onderdeel
trefwoorden: [formulier, form, validatie, foutmelding, veldfout, 422, pydantic, zod, vee-validate, focus, aria-invalid, formalert, opgeslagen, toast, useFormFeedback, zod-nl]
code:
  - frontend/src/composables/useFormFeedback.ts
  - frontend/src/lib/zod-nl.ts
  - frontend/src/components/common/FormAlert.vue
bijgewerkt: start
---

# Formulieren

Alle formulieren gebruiken vee-validate met een zod-schema en dezelfde afhandeling van fouten en opslaan.

## Hoe het werkt

1. **Fout in de browser:** het zod-schema controleert de invoer vóór het versturen. Regels zonder eigen tekst
   krijgen een Nederlandse standaardtekst uit `lib/zod-nl.ts` (`.max(100)` → "Gebruik maximaal 100 tekens.").
   Houd de regels gelijk aan de backend-schema's.
2. **Focus:** bij een fout krijgt het eerste foute veld de focus en schuift het in beeld (`focusFirstError`). Een
   veld is "fout" als het `aria-invalid="true"` heeft; shadcn-`FormControl` zet dat zelf, eigen invoer
   (`defineField`, een eigen keuzelijst) moet het zelf zetten.
3. **Fout van de backend:** `useFormFeedback(form, { fallback, messages, fieldMap })` en `submit(fn)` in plaats van
   `handleSubmit(fn)`. Een 422 van Pydantic (`detail[].loc` + `type`) komt bij het veld, met een Nederlandse
   tekst per fouttype (`issueMessage`; de Engelse `msg` nooit tonen). Al het andere (409, 5xx, geen verbinding,
   een 422 met een tekst voor een bedrijfsregel, een veld dat niet in het formulier staat) komt in `formError`,
   getoond met `<FormAlert>` boven de knop. Die blijft staan tot de volgende poging.
   - `messages`: eigen tekst per HTTP-status, bijvoorbeeld voor de bekende 422-bedrijfsregels van dat endpoint.
   - `fieldMap`: backendpad → formulierveld als de namen verschillen, of `null` voor een fout boven het formulier.
   - `showApiError(error)` voor een fout die het scherm zelf afvangt.
   - Een veldfout van de backend blijft staan tot dat veld verandert of het formulier opnieuw wordt verstuurd;
     anders zou vee-validate hem wissen bij het hercontroleren (bijv. als de focus naar het veld springt).
     Beheert een scherm een veld zelf (geen vee-validate-waarde), wis de fout dan met `clearFieldError(path)`,
     niet met `setFieldError(path, undefined)`.
4. **Opslaan:** tijdens het opslaan is de knop uitgeschakeld met "Opslaan…" (of "Bezig…"); na een geslaagde opslag
   toont het scherm `toast.success(...)` ("Profiel opgeslagen.").

Toasts blijven voor fouten buiten een formulier, zoals laden of een losse knop.

## Testen

Per formulier in de spec: een mislukte opslag toont de `FormAlert`, een leeg verplicht veld krijgt de focus
(`document.activeElement`), en een Pydantic-422 (`httpError(422, [{ loc, type, ctx }])`) staat bij het veld.
Voorbeeld: `composables/__tests__/useFormFeedback.spec.ts`.

`settle()` uit `test/helpers.ts` wacht langer dan de 5 ms waarmee vee-validate zijn controle uitstelt (ook bij
versturen). Wacht in een formuliertest dus altijd met `settle()`, niet met alleen `flushPromises()`.
