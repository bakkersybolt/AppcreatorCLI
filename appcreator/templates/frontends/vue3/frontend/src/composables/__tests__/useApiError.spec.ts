import { describe, expect, it, vi } from 'vitest'
import { AxiosError } from 'axios'

import { httpError } from '@/test/helpers'
import {
  apiErrorMessage,
  apiErrorStatus,
  NETWORK_ERROR_MESSAGE,
  SERVER_ERROR_MESSAGE,
  STATUS_MESSAGES,
  useApiError,
} from '@/composables/useApiError'

const toastError = vi.hoisted(() => vi.fn())
vi.mock('vue-sonner', () => ({ toast: { error: toastError } }))

describe('apiErrorMessage', () => {
  it('never shows the English backend detail', () => {
    const message = apiErrorMessage(httpError(409, 'Item is locked'), 'Opslaan lukte niet.')
    expect(message).not.toContain('locked')
    expect(message).toBe(`Opslaan lukte niet. ${STATUS_MESSAGES[409]}`)
  })

  it.each([401, 403, 404, 409, 413, 415, 422])('has a Dutch text for %i', (status) => {
    expect(apiErrorMessage(httpError(status), 'Mislukt.')).toBe(`Mislukt. ${STATUS_MESSAGES[status]}`)
  })

  it('uses the server message for 5xx', () => {
    expect(apiErrorMessage(httpError(503), 'Mislukt.')).toBe(`Mislukt. ${SERVER_ERROR_MESSAGE}`)
  })

  it('prefers a screen-specific text', () => {
    expect(apiErrorMessage(httpError(404), 'Mislukt.', { 404: 'Dit item bestaat niet.' })).toBe(
      'Dit item bestaat niet.',
    )
  })

  it('shows the network message without a response', () => {
    expect(apiErrorMessage(new AxiosError('Network Error'), 'Mislukt.')).toBe(NETWORK_ERROR_MESSAGE)
  })

  it('falls back for unknown statuses and non-axios errors', () => {
    expect(apiErrorMessage(httpError(418), 'Mislukt.')).toBe('Mislukt.')
    expect(apiErrorMessage(new Error('boom'), 'Mislukt.')).toBe('Mislukt.')
  })
})

describe('apiErrorStatus', () => {
  it('returns the status or null', () => {
    expect(apiErrorStatus(httpError(403))).toBe(403)
    expect(apiErrorStatus(new Error('x'))).toBeNull()
  })
})

describe('useApiError', () => {
  it('shows the message as a toast', () => {
    useApiError().showError(httpError(403), 'Mislukt.', { 403: 'Alleen voor beheerders.' })
    expect(toastError).toHaveBeenCalledWith('Alleen voor beheerders.')
  })
})
