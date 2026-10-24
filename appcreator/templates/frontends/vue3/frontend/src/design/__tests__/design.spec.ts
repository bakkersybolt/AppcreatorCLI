import { describe, expect, it, vi } from 'vitest'

import { routes } from '@/router/routes'
import { mountView, settle } from '@/test/helpers'
import DesignIndex from '../DesignIndex.vue'
import DesignScreen from '../DesignScreen.vue'
import { designScreens } from '../screens'

describe('design sandbox', () => {
  it('registers its routes as development-only', () => {
    const sandbox = routes.filter((route) => route.path.startsWith('/_ontwerp'))
    expect(sandbox.map((route) => route.name)).toEqual(['design', 'design-screen'])
    expect(sandbox.every((route) => route.meta?.devOnly === true)).toBe(true)
  })

  it('lists every sandbox screen', async () => {
    const { wrapper } = await mountView(DesignIndex, '/_ontwerp')
    const list = wrapper.get('[data-testid="design-screens"]').text()
    for (const screen of designScreens) expect(list).toContain(screen.title)
    wrapper.unmount()
  })

  it('shows a sandbox screen and switches the frame width', async () => {
    const { wrapper } = await mountView(DesignScreen, '/_ontwerp/voorbeeld')
    // The screen is a lazy component: wait until its import has loaded.
    await vi.waitFor(async () => {
      await settle()
      expect(wrapper.find('[data-testid="voorbeeld-scherm"]').exists()).toBe(true)
    })
    await wrapper
      .findAll('button')
      .find((b) => b.text() === '390 px')!
      .trigger('click')
    expect(wrapper.get('[data-testid="design-frame"]').attributes('style')).toContain('max-width: 390px')
    wrapper.unmount()
  })

  it('says so for an unknown screen', async () => {
    const { wrapper } = await mountView(DesignScreen, '/_ontwerp/bestaat-niet')
    expect(wrapper.find('[data-testid="design-not-found"]').exists()).toBe(true)
    wrapper.unmount()
  })
})
