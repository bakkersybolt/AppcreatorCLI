---
onderwerp: Hulp in de app
categorie: onderdeel
trefwoorden: [hulp, help, hulpartikelen, markdown, frontmatter, zoeken, filteren, meta.help, vraagteken, documentatiecontrole, concept]
code:
  - frontend/src/content/help/
  - frontend/src/lib/help/
  - frontend/src/views/help/
  - frontend/src/components/help/HelpButton.vue
  - frontend/src/router/routes.ts
bijgewerkt: start
---

# Hulp in de app

Hulpartikelen zijn Markdown-bestanden in de frontend, getoond op `/help` en via de **?**-knop rechtsboven in elk scherm. Hoe je ze schrijft: skill `documentatie`.

## Hoe het werkt

1. Artikelen staan in `content/help/<categorie>/<slug>.md` met frontmatter (`title`, `category`, `keywords`, `status`, `updated`, en optioneel `roles`); de categorieën staan in `content/help/categories.json`.
2. `lib/help/articles.ts` laadt ze bij de build (Vite glob-import, `allArticles`) en `lib/help/frontmatter.ts` leest en controleert de frontmatter (`parseFrontmatter`, `validateFrontmatter`). Een artikel met ongeldige frontmatter wordt overgeslagen.
3. Elke route heeft `meta: { help: '<categorie>/<slug>' }` in `router/routes.ts`; `HelpButton` (in de kop van `App.vue`) maakt daar de **?**-link van en is verborgen als een route geen `meta.help` heeft.
4. `HelpView` (`/help`) toont de artikelen per categorie en filtert op titel en trefwoorden (`filterArticles`). `HelpArticleView` (`/help/<categorie>/<slug>`) toont één artikel; `lib/help/render.ts` zet de Markdown om met markdown-it, zonder HTML, en maakt van een link naar een ander `.md`-artikel een link binnen de app.
5. Artikelen met `status: draft` zijn alleen in ontwikkeling zichtbaar, met het label "Concept" (`visibleArticles`).

## Waar in de code

| Wat | Pad |
| :--- | :--- |
| Artikelen en categorieën | `frontend/src/content/help/` |
| Laden, filteren en omzetten | `frontend/src/lib/help/` |
| Schermen | `frontend/src/views/help/` |
| **?**-knop | `frontend/src/components/help/HelpButton.vue` |
| Koppeling route → artikel | `frontend/src/router/routes.ts` |
| Controles | `frontend/src/content/help/__tests__/docs.spec.ts` |
| Vaste testartikelen voor de schermtests | `frontend/src/test/fixtures/help.ts` |

## Beheer en valkuilen

- `npm run test` faalt als een route `meta.help` mist, een artikel ongeldige frontmatter heeft, langer is dan 250 woorden of een interne link breekt. De ontwikkelschermen (pad begint met `/_`, of `meta.devOnly`) en een route met de naam `not-found` tellen niet mee.
- Een nieuwe categorie komt in `categories.json` én krijgt een eigen map.
- De schermtests gebruiken de vaste artikelen uit `test/fixtures/help.ts`, zodat een tekstwijziging in een echt artikel ze niet breekt.

## Zie ook

- [Testen](../testen.md)
