import { describe, expect, it } from 'vitest'

import { helpArticleSources } from '@/test/fixtures/help'
import { filterArticles, loadArticles, pathToId, visibleArticles } from '../articles'
import { countWords, parseFrontmatter, validateFrontmatter } from '../frontmatter'
import { renderArticle, resolveArticleLink } from '../render'

const CATEGORIES = ['aan-de-slag']

describe('frontmatter', () => {
  it('parses values and inline lists', () => {
    const { data, body } = parseFrontmatter('---\ntitle: Titel\nkeywords: [a, b]\n---\n\nTekst')
    expect(data).toEqual({ title: 'Titel', keywords: ['a', 'b'] })
    expect(body.trim()).toBe('Tekst')
  })

  it('validates category, keywords, status and the optional roles', () => {
    const valid = { title: 'T', category: 'aan-de-slag', keywords: ['k'], status: 'draft', updated: 'start' }
    expect(validateFrontmatter(valid, CATEGORIES)).toEqual([])
    expect(validateFrontmatter({ ...valid, roles: [] }, CATEGORIES)).toEqual([])
    expect(validateFrontmatter({ ...valid, roles: 'iedereen' }, CATEGORIES)).toHaveLength(1)
    expect(
      validateFrontmatter({ ...valid, category: 'onbekend', keywords: [], status: 'af' }, CATEGORIES),
    ).toHaveLength(3)
  })

  it('counts words without tables and code blocks', () => {
    expect(countWords('## Kop\n\nEen twee drie.\n\n| a | b |\n\n```\ncode hier\n```')).toBe(4)
  })
})

describe('articles', () => {
  const articles = loadArticles(helpArticleSources, CATEGORIES)

  it('turns glob paths into ids', () => {
    expect(pathToId('../../content/help/aan-de-slag/welkom.md')).toBe('aan-de-slag/welkom')
  })

  it('hides drafts unless drafts are included', () => {
    expect(visibleArticles(articles, false).map((a) => a.id)).not.toContain('aan-de-slag/test-draft')
    expect(visibleArticles(articles, true).map((a) => a.id)).toContain('aan-de-slag/test-draft')
  })

  it('filters on title and keywords, every word must match', () => {
    expect(filterArticles(articles, 'PROEFWOORD').map((a) => a.title)).toEqual(['Testartikel'])
    expect(filterArticles(articles, 'verwant artikel').map((a) => a.title)).toEqual(['Verwant artikel'])
    expect(filterArticles(articles, '  ')).toHaveLength(articles.length)
  })
})

describe('render', () => {
  it('resolves relative article links to help routes', () => {
    expect(resolveArticleLink('andere.md#stap', 'aan-de-slag/welkom')).toBe('/help/aan-de-slag/andere#stap')
    expect(resolveArticleLink('https://example.com', 'aan-de-slag/welkom')).toBeNull()
  })

  it('never passes raw HTML and marks internal links', () => {
    const html = renderArticle('<script>x</script> [Ander](ander.md)', 'aan-de-slag/welkom')
    expect(html).not.toContain('<script>')
    expect(html).toContain('href="/help/aan-de-slag/ander" data-internal=""')
  })
})
