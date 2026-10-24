/**
 * Fixed help articles for the help view tests, so those tests check the rendering and not the wording of the
 * real articles in `src/content/help/` (those are checked by `content/help/__tests__/docs.spec.ts`).
 *
 * Keys mimic the `import.meta.glob` paths, so `loadArticles` turns them into the ids `aan-de-slag/test-article`,
 * `aan-de-slag/test-related` and `aan-de-slag/test-draft`. Categories are real keys from `categories.json`.
 */
const PREFIX = '../../content/help/'

const testArticle = `---
title: Testartikel
category: aan-de-slag
keywords: [proefwoord, fixture]
status: published
updated: test
---

## Eerste sectie

Een inleiding met <b>geen HTML</b>.

## Tweede sectie

1. Stap een.
2. Stap twee.

Zie ook: [Verwant artikel](test-related.md)
`

const relatedArticle = `---
title: Verwant artikel
category: aan-de-slag
keywords: [verwant]
roles: []
status: published
updated: test
---

## Eerste sectie

Een verwant artikel.
`

const draftArticle = `---
title: Conceptartikel
category: aan-de-slag
keywords: [concept]
status: draft
updated: test
---

## Eerste sectie

Nog niet af.
`

export const helpArticleSources: Record<string, string> = {
  [`${PREFIX}aan-de-slag/test-article.md`]: testArticle,
  [`${PREFIX}aan-de-slag/test-related.md`]: relatedArticle,
  [`${PREFIX}aan-de-slag/test-draft.md`]: draftArticle,
}
