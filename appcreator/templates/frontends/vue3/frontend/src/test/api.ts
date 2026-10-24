import type { AxiosRequestConfig } from 'axios'
import type { Mock } from 'vitest'

import { api } from '@/services/api'

/** What a mocked call resolves to: an axios-like response, of which tests only fill `data`. */
type ApiResult = Promise<{ data?: unknown }>
type ReadCall = (url: string, config?: AxiosRequestConfig) => ApiResult
type WriteCall = (url: string, data?: unknown, config?: AxiosRequestConfig) => ApiResult

export interface MockedApi {
  get: Mock<ReadCall>
  post: Mock<WriteCall>
  put: Mock<WriteCall>
  patch: Mock<WriteCall>
  delete: Mock<ReadCall>
}

/**
 * The mocked axios instance, typed as mocks. `vi.mocked(api)` cannot type axios' generic methods as mocks,
 * so `api.get.mockResolvedValue(...)` would not typecheck. Use it together with the module mock:
 *
 * ```ts
 * vi.mock('@/services/api', () => ({
 *   api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() },
 * }))
 * const api = mockedApi()
 * ```
 */
export function mockedApi(): MockedApi {
  // Cast: under `vi.mock` the methods are `vi.fn()` mocks; the real axios types do not say so.
  return api as unknown as MockedApi
}
