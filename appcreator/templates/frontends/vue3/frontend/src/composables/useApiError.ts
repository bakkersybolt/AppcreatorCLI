import { isAxiosError } from 'axios'
import { toast } from 'vue-sonner'

/**
 * Dutch explanation per HTTP status. The backend `detail` is English and never shown to the user;
 * screens pass their own text per status via `messages` where the generic one is too vague.
 */
export const STATUS_MESSAGES: Readonly<Record<number, string>> = {
  401: 'Je bent niet (meer) ingelogd. Log opnieuw in.',
  403: 'Je hebt hier geen rechten voor.',
  404: 'Dit bestaat niet (meer) of je hebt er geen toegang toe.',
  409: 'Dit kan nu niet. Vernieuw de pagina en probeer het opnieuw.',
  413: 'Het bestand is te groot. Kies een kleiner bestand.',
  415: 'Dit bestandstype wordt niet ondersteund.',
  422: 'Controleer wat je hebt ingevuld.',
}

export const SERVER_ERROR_MESSAGE = 'Er ging iets mis op de server. Probeer het later opnieuw.'
export const NETWORK_ERROR_MESSAGE = 'Geen verbinding met de server. Probeer het later opnieuw.'

/** Per-screen texts by HTTP status; they replace the whole message. */
export type ApiErrorMessages = Partial<Record<number, string>>

/** HTTP status of an API error, or null. */
export function apiErrorStatus(error: unknown): number | null {
  return isAxiosError(error) ? (error.response?.status ?? null) : null
}

/**
 * Dutch message for an API error, never the backend `detail`:
 * 1. a screen-specific text from `messages` for this status;
 * 2. no response: the network message;
 * 3. `fallback` (what failed) plus the standard explanation for the status (`STATUS_MESSAGES`, or the
 *    server message for 5xx); unknown statuses get only `fallback`.
 */
export function apiErrorMessage(error: unknown, fallback: string, messages: ApiErrorMessages = {}): string {
  const status = apiErrorStatus(error)
  if (status !== null && messages[status]) return messages[status]
  if (isAxiosError(error) && !error.response) return NETWORK_ERROR_MESSAGE
  const reason = status === null ? undefined : status >= 500 ? SERVER_ERROR_MESSAGE : STATUS_MESSAGES[status]
  return reason ? `${fallback} ${reason}` : fallback
}

/** Show an API error as a toast (outside forms; in a form use `useFormFeedback`). */
export function useApiError() {
  function showError(error: unknown, fallback: string, messages: ApiErrorMessages = {}): void {
    toast.error(apiErrorMessage(error, fallback, messages))
  }
  return { showError }
}
