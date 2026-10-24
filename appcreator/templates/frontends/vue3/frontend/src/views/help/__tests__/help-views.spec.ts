import { describe, expect, it, vi } from 'vitest'

import { mountView, settle } from '@/test/helpers'

// Fixed test articles instead of the real ones, so a wording change in an article cannot break these view tests.
vi.mock('@/lib/help/articles', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/help/articles')>()
  const { helpArticleSources } = await import('@/test/fixtures/help')
  return {
    ...actual,
    allArticles: actual.loadArticles(
      helpArticleSources,
      actual.categories.map((category) => category.key),
    ),
  }
})

import HelpView from '../HelpView.vue'
import HelpArticleView from '../HelpArticleView.vue'

describe('HelpView', () => {
  it('shows the articles per category, drafts marked "Concept" in development', async () => {
    const { wrapper } = await mountView(HelpView, '/help')
    const category = wrapper.get('[data-testid="category-aan-de-slag"]').text()
    expect(category).toContain('Testartikel')
    expect(category).toContain('Verwant artikel')
    expect(category).toContain('Conceptartikel')
    expect(category).toContain('Concept')
    wrapper.unmount()
  })

  it('filters on title and keywords and says when nothing matches', async () => {
    const { wrapper } = await mountView(HelpView, '/help')
    await wrapper.get('input').setValue('proefwoord')
    expect(wrapper.get('[data-testid="category-aan-de-slag"]').text()).toContain('Testartikel')
    expect(wrapper.text()).not.toContain('Verwant artikel')

    await wrapper.get('input').setValue('qqqzzz')
    expect(wrapper.find('[data-testid="no-results"]').exists()).toBe(true)
    wrapper.unmount()
  })
})

describe('HelpArticleView', () => {
  it('renders the article without raw HTML and with a link back', async () => {
    const { wrapper } = await mountView(HelpArticleView, '/help/aan-de-slag/test-article')
    const article = wrapper.get('[data-testid="help-article"]')
    expect(article.get('h1').text()).toContain('Testartikel')
    expect(article.findAll('h2').map((h) => h.text())).toEqual(['Eerste sectie', 'Tweede sectie'])
    expect(article.findAll('ol > li')).toHaveLength(2)
    expect(article.find('b').exists()).toBe(false)
    expect(wrapper.text()).toContain('Terug naar Hulp')
    wrapper.unmount()
  })

  it('navigates internal links via the router', async () => {
    const { wrapper, router } = await mountView(HelpArticleView, '/help/aan-de-slag/test-article')
    await wrapper.get('[data-testid="help-article"] a[data-internal]').trigger('click', { button: 0 })
    await settle()
    expect(router.currentRoute.value.fullPath).toBe('/help/aan-de-slag/test-related')
    wrapper.unmount()
  })

  it('labels a draft "Concept"', async () => {
    const { wrapper } = await mountView(HelpArticleView, '/help/aan-de-slag/test-draft')
    expect(wrapper.get('[data-testid="draft-label"]').text()).toBe('Concept')
    wrapper.unmount()
  })

  it('shows a friendly message for an unknown article', async () => {
    const { wrapper } = await mountView(HelpArticleView, '/help/aan-de-slag/bestaat-niet')
    expect(wrapper.find('[data-testid="help-not-found"]').text()).toContain('Artikel niet gevonden')
    expect(wrapper.find('[data-testid="help-article"]').exists()).toBe(false)
    wrapper.unmount()
  })
})
