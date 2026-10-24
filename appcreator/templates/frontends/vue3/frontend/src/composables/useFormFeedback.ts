import { nextTick, ref, watch } from 'vue'
import { isAxiosError } from 'axios'
import type { FormContext, GenericObject, Path, SubmissionHandler } from 'vee-validate'

import { apiErrorMessage, type ApiErrorMessages } from './useApiError'

/** One entry of FastAPI's 422 `detail` list (Pydantic v2). */
export interface ValidationIssue {
  loc: (string | number)[]
  type: string
  msg?: string
  ctx?: Record<string, unknown>
}

/** Backend field path (`name`, `items[0].name`) → form field path, or `null` for an error above the form. */
export type FieldMap = Readonly<Record<string, string | null>>

export interface FormFeedbackOptions {
  /** What failed, e.g. "Je gegevens konden niet worden opgeslagen." (see `apiErrorMessage`). */
  fallback: string
  /** Screen-specific texts per HTTP status, for errors shown above the form. */
  messages?: ApiErrorMessages
  /** Backend paths whose name differs from the form field, or that belong above the form (`null`). */
  fieldMap?: FieldMap
}

/** The validation issues of a 422 from Pydantic, or null (other status, or a business-rule 422 with a text). */
export function validationIssues(error: unknown): ValidationIssue[] | null {
  if (!isAxiosError(error) || error.response?.status !== 422) return null
  const detail: unknown = error.response.data?.detail
  if (!Array.isArray(detail)) return null
  return detail.filter(
    (item): item is ValidationIssue => !!item && Array.isArray(item.loc) && typeof item.type === 'string',
  )
}

/** Form path of a body issue: `["body", "steps", 0, "text"]` → `steps[0].text`; null outside the body. */
export function issuePath(loc: (string | number)[]): string | null {
  if (loc[0] !== 'body' || loc.length < 2) return null
  return loc
    .slice(1)
    .map((part, i) => (typeof part === 'number' ? `[${part}]` : i === 0 ? part : `.${part}`))
    .join('')
}

/** Dutch text for a Pydantic error type; the English `msg` is never shown to the user. */
export function issueMessage(issue: ValidationIssue): string {
  const ctx = issue.ctx ?? {}
  switch (issue.type) {
    case 'missing':
      return 'Vul dit veld in.'
    case 'string_too_short':
      return Number(ctx.min_length) <= 1 ? 'Vul dit veld in.' : `Gebruik minimaal ${ctx.min_length} tekens.`
    case 'string_too_long':
      return `Gebruik maximaal ${ctx.max_length} tekens.`
    case 'too_short':
      return `Voeg er minimaal ${ctx.min_length} toe.`
    case 'too_long':
      return `Je kunt er maximaal ${ctx.max_length} toevoegen.`
    case 'greater_than_equal':
      return `Vul minimaal ${ctx.ge} in.`
    case 'greater_than':
      return `Vul meer dan ${ctx.gt} in.`
    case 'less_than_equal':
      return `Vul maximaal ${ctx.le} in.`
    case 'less_than':
      return `Vul minder dan ${ctx.lt} in.`
    case 'int_parsing':
    case 'int_type':
    case 'int_from_float':
    case 'float_parsing':
    case 'float_type':
    case 'decimal_parsing':
    case 'decimal_type':
      return 'Vul een getal in.'
    case 'date_parsing':
    case 'date_type':
    case 'date_from_datetime_parsing':
    case 'datetime_parsing':
    case 'datetime_type':
    case 'datetime_from_date_parsing':
      return 'Vul een geldige datum in.'
    case 'enum':
    case 'literal_error':
      return 'Kies een van de opties.'
    case 'string_pattern_mismatch':
      return 'Dit heeft niet de juiste vorm.'
    default:
      return 'Controleer dit veld.'
  }
}

const FOCUSABLE =
  'input:not([type="hidden"]):not([disabled]), textarea:not([disabled]), select:not([disabled]), ' +
  'button:not([disabled]), [tabindex]:not([tabindex="-1"])'

/**
 * After the next render: focus the first field with an error (`aria-invalid="true"`, set by `FormControl`) and
 * scroll it to the middle of the screen. Without such a field, scroll the `FormAlert` into view instead.
 */
export async function focusFirstError(root: ParentNode | null = null): Promise<void> {
  await nextTick()
  const scope = root ?? document
  const invalid = scope.querySelector<HTMLElement>('[aria-invalid="true"]')
  const target = invalid ?? scope.querySelector<HTMLElement>('[data-slot="form-alert"]')
  if (!target) return
  target.scrollIntoView?.({ block: 'center' })
  if (!invalid) return
  const focusable = invalid.matches(FOCUSABLE) ? invalid : invalid.querySelector<HTMLElement>(FOCUSABLE)
  focusable?.focus({ preventScroll: true })
}

/** Value at a vee-validate path (`dates[1].date`), as JSON so it can be compared later. */
function snapshotAt(values: GenericObject, path: string): string {
  let current: unknown = values
  for (const key of path.split(/[.[\]]+/).filter(Boolean)) {
    if (current === null || typeof current !== 'object') return 'undefined'
    current = (current as Record<string, unknown>)[key]
  }
  return JSON.stringify(current) ?? 'undefined'
}

function formOf(evt: Event | undefined): HTMLElement | null {
  const target = evt?.target
  return target instanceof Element ? target.closest('form') : null
}

/**
 * Error and focus handling of one vee-validate form (the vaste regel for formulieren, see the skill `vue-shadcn`):
 * - `submit(fn)` replaces `handleSubmit(fn)`. Invalid input focuses the first field with an error; an API error
 *   thrown by `fn` goes to the field it belongs to (422 with Pydantic details), otherwise to `formError`.
 * - A backend field error stays until that field changes or the form is sent again; vee-validate's own
 *   revalidation (e.g. on blur when the focus moves) would otherwise wipe it.
 * - `formError` is the text for a `<FormAlert>` above the submit button; it stays until the next submit.
 * - `showApiError(error)` does the same for an error caught by the screen itself.
 *
 * A success toast and the "Opslaan…" button state stay with the screen.
 */
export function useFormFeedback<TValues extends GenericObject, TOutput extends GenericObject = TValues>(
  form: Pick<FormContext<TValues, TOutput>, 'handleSubmit' | 'setFieldError' | 'values' | 'errors'>,
  options: FormFeedbackOptions,
) {
  const formError = ref<string | null>(null)
  let lastForm: HTMLElement | null = null

  // Backend field errors with the field value they were about; put back when client validation clears them.
  const serverErrors = new Map<string, { message: string; value: string }>()
  watch(form.errors, (errors) => {
    for (const [path, { message, value }] of serverErrors) {
      if (snapshotAt(form.values, path) !== value) serverErrors.delete(path)
      else if (errors[path as Path<TValues>] !== message) form.setFieldError(path as Path<TValues>, message)
    }
  })

  function formPath(issue: ValidationIssue, fieldMap: FieldMap): string | null {
    const path = issuePath(issue.loc)
    if (path === null) return null
    if (path in fieldMap) return fieldMap[path] ?? null
    const top = path.split(/[.[]/)[0] ?? ''
    if (top in fieldMap) {
      const mapped = fieldMap[top]
      return mapped == null ? null : mapped + path.slice(top.length)
    }
    return top in form.values ? path : null
  }

  // Fields are often disabled while submitting; focus only after the submit has finished.
  let submitting = false
  let focusAfterSubmit = false

  async function focusNowOrAfterSubmit(): Promise<void> {
    if (submitting) focusAfterSubmit = true
    else await focusFirstError(lastForm)
  }

  async function showApiError(error: unknown, overrides: Partial<FormFeedbackOptions> = {}): Promise<void> {
    const { fallback, messages, fieldMap = {} } = { ...options, ...overrides }
    const issues = validationIssues(error)
    let aboveForm = issues === null || issues.length === 0
    for (const issue of issues ?? []) {
      const path = formPath(issue, fieldMap)
      if (path === null) aboveForm = true
      else {
        const message = issueMessage(issue)
        serverErrors.set(path, { message, value: snapshotAt(form.values, path) })
        form.setFieldError(path as Path<TValues>, message)
      }
    }
    formError.value = aboveForm ? apiErrorMessage(error, fallback, messages) : null
    await focusNowOrAfterSubmit()
  }

  function submit(fn: SubmissionHandler<TValues, TOutput>) {
    const handler = form.handleSubmit(
      async (values, ctx) => {
        lastForm = formOf(ctx.evt) ?? lastForm
        formError.value = null
        try {
          await fn(values, ctx)
        } catch (error) {
          await showApiError(error)
        }
      },
      (ctx) => {
        lastForm = formOf(ctx.evt) ?? lastForm
        formError.value = null
        void focusNowOrAfterSubmit()
      },
    )
    return async (evt?: Event): Promise<void> => {
      serverErrors.clear()
      submitting = true
      focusAfterSubmit = false
      try {
        await handler(evt)
      } finally {
        submitting = false
      }
      if (focusAfterSubmit) await focusFirstError(lastForm)
    }
  }

  /** Clear `formError` and the remembered backend field errors (e.g. next to `resetForm` when a dialog reopens). */
  function clearError(): void {
    formError.value = null
    serverErrors.clear()
  }

  /** Clear one field's error, also the remembered backend error (for fields the screen manages itself). */
  function clearFieldError(path: string): void {
    serverErrors.delete(path)
    form.setFieldError(path as Path<TValues>, undefined)
  }

  return { formError, submit, showApiError, clearError, clearFieldError }
}
