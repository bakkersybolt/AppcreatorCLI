import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { defineComponent, h, type Component } from 'vue'
import { AxiosError, AxiosHeaders } from 'axios'

import { routes } from '@/router/routes'

// Shared test data builders (`makeItem(overrides)` etc.) go here too, next to these helpers.

/** An axios-style error with an HTTP status, as the mocked `api` would reject with. */
export function httpError(status: number, detail?: unknown): AxiosError {
  const headers = new AxiosHeaders()
  return new AxiosError('Request failed', String(status), { headers }, null, {
    status,
    statusText: '',
    headers,
    config: { headers },
    data: detail !== undefined ? { detail } : {},
  })
}

/**
 * Let pending promises, timers and vee-validate's async validation finish. vee-validate debounces schema
 * validation by 5 ms (also on submit), so wait past that twice (typing, then submitting) before the short rounds.
 */
export async function settle(): Promise<void> {
  for (let i = 0; i < 2; i++) {
    await new Promise((resolve) => setTimeout(resolve, 6))
    await flushPromises()
  }
  for (let i = 0; i < 5; i++) {
    await new Promise((resolve) => setTimeout(resolve, 0))
    await flushPromises()
  }
}

const Stub = defineComponent({ render: () => h('div') })

/** Mount a view at `path` with a memory router (other routes stubbed) and a fresh pinia. */
export async function mountView(view: Component, path: string, setup?: () => void) {
  const pinia = createPinia()
  setActivePinia(pinia)
  setup?.()
  const router = createRouter({
    history: createMemoryHistory(),
    routes: routes.map((r) => ({ ...r, component: Stub }) as typeof r),
  })
  await router.push(path)
  await router.isReady()
  const wrapper = mount(view, { global: { plugins: [pinia, router] }, attachTo: document.body })
  await flushPromises()
  return { wrapper, router }
}
