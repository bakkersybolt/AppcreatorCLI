---
onderwerp: Hulp in de app
categorie: onderdeel
trefwoorden: [hulp, help, hulpartikelen, markdown, frontmatter, zoeken, meta.help, vraagteken, documentatiecontrole, concept]
code:
  - frontend/src/content/help/
  - frontend/src/lib/help/
  - frontend/src/views/help/
  - frontend/src/components/help/HelpButton.vue
bijgewerkt: start
---

# Hulp in de app

Hulpartikelen zijn Markdown-bestanden in de frontend, getoond op `/help` en via de **?**-knop per scherm. Hoe je ze schrijft: skill `documentatie`.

## Hoe het werkt

1. Artikelen staan in `content/help/<categorie>/<slug>.md` met frontmatter (`title`, `category`, `keywords`, `status`, `updated`); de categorieën staan in `categories.json`.
2. `lib/help/articles.ts` laadt ze bij de build (Vite glob-import) en `lib/help/frontmatter.ts` leest de frontmatter.
3. Elke route heeft `meta.help: '<categorie>/<slug>'` in `router/index.ts`; `HelpButton` maakt daar de **?**-link van.
4. `HelpView` toont de categorieën en zoekt op titel en trefwoorden; `HelpArticleView` toont één artikel, met Markdown omgezet door `lib/help/render.ts`.
5. Artikelen met `status: draft` zijn alleen in ontwikkeling zichtbaar (label "Concept").

## Waar in de code

| Wat | Pad |
| :--- | :--- |
| Artikelen | `frontend/src/content/help/` |
| Laden en omzetten | `frontend/src/lib/help/` |
| Schermen | `frontend/src/views/help/` |
| Controles | `frontend/src/content/help/__tests__/docs.spec.ts` |

## Beheer en valkuilen

- `npm run test` faalt als een route `meta.help` mist, een artikel ongeldige frontmatter heeft, langer is dan 250 woorden of een interne link breekt.
- Een nieuwe categorie komt in `categories.json` én krijgt een eigen map.

## Zie ook

- [Testen](../testen.md)
