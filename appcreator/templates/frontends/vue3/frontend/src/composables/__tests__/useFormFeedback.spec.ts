import { describe, expect, it, vi } from 'vitest'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { httpError, settle } from '@/test/helpers'
import { issueMessage, issuePath, useFormFeedback, validationIssues } from '@/composables/useFormFeedback'

describe('validationIssues', () => {
  it('reads the Pydantic detail list of a 422', () => {
    const issues = validationIssues(httpError(422, [{ loc: ['body', 'name'], type: 'missing', msg: 'Field required' }]))
    expect(issues).toEqual([{ loc: ['body', 'name'], type: 'missing', msg: 'Field required' }])
  })

  it('is null for a business-rule 422 with a text, and for other statuses', () => {
    expect(validationIssues(httpError(422, 'Name is already taken'))).toBeNull()
    expect(validationIssues(httpError(409))).toBeNull()
    expect(validationIssues(new Error('x'))).toBeNull()
  })
})

describe('issuePath', () => {
  it('turns a body location into a vee-validate path', () => {
    expect(issuePath(['body', 'name'])).toBe('name')
    expect(issuePath(['body', 'items', 0, 'name'])).toBe('items[0].name')
    expect(issuePath(['body', 'dates', 2])).toBe('dates[2]')
  })

  it('ignores query and path parameters', () => {
    expect(issuePath(['query', 'limit'])).toBeNull()
    expect(issuePath(['path', 'item_id'])).toBeNull()
    expect(issuePath(['body'])).toBeNull()
  })
})

describe('issueMessage', () => {
  it.each([
    [{ type: 'missing' }, 'Vul dit veld in.'],
    [{ type: 'string_too_short', ctx: { min_length: 1 } }, 'Vul dit veld in.'],
    [{ type: 'string_too_short', ctx: { min_length: 8 } }, 'Gebruik minimaal 8 tekens.'],
    [{ type: 'string_too_long', ctx: { max_length: 100 } }, 'Gebruik maximaal 100 tekens.'],
    [{ type: 'too_long', ctx: { max_length: 10 } }, 'Je kunt er maximaal 10 toevoegen.'],
    [{ type: 'less_than_equal', ctx: { le: 5 } }, 'Vul maximaal 5 in.'],
    [{ type: 'int_parsing' }, 'Vul een getal in.'],
    [{ type: 'date_parsing' }, 'Vul een geldige datum in.'],
    [{ type: 'enum' }, 'Kies een van de opties.'],
    [{ type: 'value_error', msg: 'Value error, something English' }, 'Controleer dit veld.'],
  ])('%o → %s', (issue, text) => {
    expect(issueMessage({ loc: ['body', 'x'], ...issue })).toBe(text)
  })
})

describe('Dutch zod defaults (lib/zod-nl)', () => {
  function message(schema: z.ZodTypeAny, value: unknown): string | undefined {
    const result = schema.safeParse(value)
    return result.success ? undefined : result.error.issues[0]?.message
  }

  it('replaces the English defaults', () => {
    expect(message(z.string().max(100), 'x'.repeat(101))).toBe('Gebruik maximaal 100 tekens.')
    expect(message(z.string().min(3), 'ab')).toBe('Gebruik minimaal 3 tekens.')
    expect(message(z.string(), undefined)).toBe('Vul dit veld in.')
    expect(message(z.string().email(), 'nope')).toBe('Dit is geen geldig e-mailadres.')
    expect(message(z.number().int(), 1.5)).toBe('Vul een heel getal in.')
    expect(message(z.number().max(5), 6)).toBe('Vul maximaal 5 in.')
    expect(message(z.array(z.string()).max(2), ['a', 'b', 'c'])).toBe('Je kunt er maximaal 2 toevoegen.')
    expect(message(z.enum(['a', 'b']), 'c')).toBe('Kies een van de opties.')
  })

  it('keeps a message given by the schema', () => {
    expect(message(z.string().min(1, 'Vul je naam in.'), '')).toBe('Vul je naam in.')
  })
})

describe('useFormFeedback focus', () => {
  // A form whose input is disabled while submitting, as most forms do.
  function mountForm(save: () => Promise<void>) {
    const Comp = defineComponent({
      setup() {
        const form = useForm({
          validationSchema: toTypedSchema(z.object({ name: z.string().min(1, 'Vul je naam in.') })),
        })
        const [name] = form.defineField('name')
        const { submit, formError } = useFormFeedback(form, { fallback: 'Opslaan lukte niet.' })
        return { name, errors: form.errors, isSubmitting: form.isSubmitting, formError, onSubmit: submit(save) }
      },
      template: `<form @submit="onSubmit"><input v-model="name" :disabled="isSubmitting" :aria-invalid="!!errors.name" />
        <p v-if="formError" data-slot="form-alert">{{ formError }}</p><button type="submit">Opslaan</button></form>`,
    })
    return mount(Comp, { attachTo: document.body })
  }

  it('focuses an empty field even when it is disabled during the submit', async () => {
    const save = vi.fn().mockResolvedValue(undefined)
    const wrapper = mountForm(save)
    await wrapper.get('form').trigger('submit')
    await settle()
    expect(save).not.toHaveBeenCalled()
    expect(document.activeElement).toBe(wrapper.get('input').element)
    wrapper.unmount()
  })

  it('puts a backend 422 at the field and focuses it after the submit', async () => {
    const wrapper = mountForm(() =>
      Promise.reject(httpError(422, [{ loc: ['body', 'name'], type: 'string_too_long', ctx: { max_length: 100 } }])),
    )
    await wrapper.get('input').setValue('Anna')
    await wrapper.get('form').trigger('submit')
    await settle()
    expect(wrapper.get('input').attributes('aria-invalid')).toBe('true')
    expect(document.activeElement).toBe(wrapper.get('input').element)
    expect(wrapper.find('[data-slot=form-alert]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('keeps a backend error through revalidation until the field changes', async () => {
    const wrapper = mountForm(() =>
      Promise.reject(httpError(422, [{ loc: ['body', 'name'], type: 'string_too_long', ctx: { max_length: 100 } }])),
    )
    await wrapper.get('input').setValue('Anna')
    await wrapper.get('form').trigger('submit')
    await settle()
    await wrapper.get('input').trigger('blur') // vee-validate revalidates; the name is valid for zod
    await settle()
    expect(wrapper.get('input').attributes('aria-invalid')).toBe('true')
    await wrapper.get('input').setValue('Anna B')
    await settle()
    expect(wrapper.get('input').attributes('aria-invalid')).toBe('false')
    wrapper.unmount()
  })

  it('shows other errors above the form', async () => {
    const wrapper = mountForm(() => Promise.reject(httpError(422, 'Name is already taken')))
    await wrapper.get('input').setValue('Anna')
    await wrapper.get('form').trigger('submit')
    await settle()
    expect(wrapper.get('[data-slot=form-alert]').text()).toBe('Opslaan lukte niet. Controleer wat je hebt ingevuld.')
    wrapper.unmount()
  })
})
