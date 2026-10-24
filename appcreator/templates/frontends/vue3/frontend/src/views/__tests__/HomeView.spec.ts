import { describe, expect, it, vi } from 'vitest'

import { mockedApi } from '@/test/api'
import { httpError, mountView, settle } from '@/test/helpers'
import HomeView from '@/views/HomeView.vue'

vi.mock('@/services/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))
const api = mockedApi()

describe('HomeView', () => {
  it('shows a connected backend', async () => {
    api.get.mockResolvedValue({
      data: { status: 'healthy', app_name: 'App', environment: 'test', version: '0.1.0' },
    })
    const { wrapper } = await mountView(HomeView, '/')
    await settle()
    expect(api.get).toHaveBeenCalledWith('/health')
    expect(wrapper.get('[data-testid=backend-status]').text()).toBe('Verbonden')
    wrapper.unmount()
  })

  it('shows an unreachable backend and checks again on the button', async () => {
    api.get.mockRejectedValue(httpError(503))
    const { wrapper } = await mountView(HomeView, '/')
    await settle()
    expect(wrapper.get('[data-testid=backend-status]').text()).toBe('Niet bereikbaar')

    await wrapper.get('button').trigger('click')
    await settle()
    expect(api.get).toHaveBeenCalledTimes(2)
    wrapper.unmount()
  })
})
