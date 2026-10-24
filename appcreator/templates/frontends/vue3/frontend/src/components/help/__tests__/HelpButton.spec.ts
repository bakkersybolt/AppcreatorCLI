import { describe, expect, it } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { defineComponent, h } from 'vue'

import HelpButton from '../HelpButton.vue'

const Stub = defineComponent({ render: () => h('div') })

async function mountAt(path: string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/with-help', component: Stub, meta: { help: 'aan-de-slag/welkom' } },
      { path: '/without-help', component: Stub },
      { path: '/help/:category/:slug', name: 'help-article', component: Stub },
    ],
  })
  await router.push(path)
  const wrapper = mount(HelpButton, { global: { plugins: [router] } })
  await flushPromises()
  return wrapper
}

describe('HelpButton', () => {
  it('links to the help article of the current route', async () => {
    const wrapper = await mountAt('/with-help')
    const link = wrapper.get('[data-testid="help-button"]')
    expect(link.attributes('href')).toBe('/help/aan-de-slag/welkom')
    expect(link.attributes('aria-label')).toBe('Hulp bij dit scherm')
  })

  it('is hidden on a route without meta.help', async () => {
    const wrapper = await mountAt('/without-help')
    expect(wrapper.find('[data-testid="help-button"]').exists()).toBe(false)
  })
})
