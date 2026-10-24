# Stijlregels

Deze regels houden elk scherm in dezelfde stijl. De skill `design-system` legt de uitstraling vast en neemt ontwerpen over; werk dit bestand daarbij bij. Staat hieronder nog "nog niet vastgelegd", vraag dan eerst om de uitstraling vast te leggen of houd het neutraal.

## Karakter

Nog niet vastgelegd. Na de ontwerpronde "Navigatie en uitstraling" staat hier in een paar woorden de sfeer (bijv. "rustig en zakelijk", "speels en warm") en voor welk apparaat de app vooral is.

## Kleur en typografie

- Kleuren, hoekradius en lettertype staan alleen in `frontend/src/assets/brand/tokens.css`. `frontend/src/assets/index.css` koppelt ze aan de thema-klassen.
- Gebruik in componenten alleen thema-klassen: `bg-primary`, `text-primary-foreground`, `bg-card`, `text-muted-foreground`, `bg-success/10`, `text-destructive`, `border-border`.
- Nooit een vaste kleur in een component: geen hex, geen `bg-[#…]`, geen Tailwind-paletkleur zoals `bg-blue-500`. Mist er een kleur, voeg dan een token toe in `tokens.css` en koppel hem in `index.css`.
- Groen (`success`) voor gelukt, `warning` voor iets waar de gebruiker nog iets mee moet, `destructive` voor fouten.
- Eén lettertype (`--brand-font-sans`). Koppen `font-bold` of `font-semibold`, lopende tekst in de standaardgrootte.

## Bouwstenen

Bouw schermen uit deze bouwstenen; maak geen eigen variant van iets dat hier al staat. Mist er iets, breid dan de bouwsteen uit of voeg er een toe in `frontend/src/components/common/` en zet hem in deze tabel.

| Bouwsteen | Wanneer |
| :--- | :--- |
| `FormAlert` (`components/common/`) | Algemene fout van een formulier, boven de verzendknop (`formError` van `useFormFeedback`) |
| `Button` (`components/ui/button`) | Elke knop; `default` voor de hoofdactie, `outline` of `ghost` voor de rest, `destructive` voor verwijderen |
| `Input`, `Label`, `Form*` (`components/ui/`) | Formuliervelden, met vee-validate (skill `vue-shadcn`) |
| `Alert` (`components/ui/alert`) | Melding in een scherm die geen formulierfout is |
| `Toaster` (`components/ui/sonner`) | Korte bevestiging na een actie (`toast.success(...)`), en fouten buiten een formulier |

Andere shadcn-vue-componenten installeer je met `frontend/scripts/shadcn-add.sh <naam>` (skill `vue-shadcn`).

## Verboden

Deze regels worden automatisch bewaakt door `frontend/design-guard.json` (test `src/test/__tests__/design-guard.spec.ts` en, als het project die heeft, de lint-hook na elke bewerking). Ze gelden niet in `src/components/ui/`, `src/assets/` en tests.

- Losse hex-kleuren (`color: #fff`, `{ color: '#fff' }`).
- Willekeurige Tailwind-kleuren (`bg-[#…]`, `text-[oklch(…)]`).
- `dark:`-varianten: er is (nog) geen donker thema.

Verandert een regel bewust, pas dan dit bestand én `design-guard.json` aan.

## Controle

- Bekijk elk nieuw of gewijzigd scherm op 390 px (telefoon) en 1280 px (desktop) breed: niets valt buiten beeld, niets overlapt, knoppen zijn te raken.
- Probeer een nieuwe uitstraling eerst in de ontwerpomgeving (`/_ontwerp`, alleen in `npm run dev`, map `frontend/src/design/`).
- `cd frontend && npm run lint && npm run build && npm run test` slaagt, inclusief de stijlbewaking.
