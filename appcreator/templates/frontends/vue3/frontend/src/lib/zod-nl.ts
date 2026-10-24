import { z } from 'zod'

/**
 * Dutch default texts for zod. A rule with its own message (`.min(1, 'Vul je naam in.')`) keeps that message;
 * this map only replaces zod's English defaults, so a rule like `.max(100)` never shows English to the user.
 * Installed once in `main.ts` (and in the test setup).
 */
export const dutchErrorMap: z.ZodErrorMap = (issue) => {
  switch (issue.code) {
    case z.ZodIssueCode.invalid_type:
      if (issue.received === 'undefined' || issue.received === 'null') return { message: 'Vul dit veld in.' }
      if (issue.expected === 'integer') return { message: 'Vul een heel getal in.' }
      if (issue.expected === 'number' || issue.expected === 'bigint') return { message: 'Vul een getal in.' }
      if (issue.expected === 'date') return { message: 'Vul een geldige datum in.' }
      return { message: 'Controleer dit veld.' }
    case z.ZodIssueCode.too_small: {
      const min = Number(issue.minimum)
      if (issue.type === 'string') {
        return { message: min <= 1 ? 'Vul dit veld in.' : `Gebruik minimaal ${min} tekens.` }
      }
      if (issue.type === 'array' || issue.type === 'set') return { message: `Voeg er minimaal ${min} toe.` }
      if (issue.type === 'date') return { message: 'Deze datum is te vroeg.' }
      return { message: issue.inclusive ? `Vul minimaal ${min} in.` : `Vul meer dan ${min} in.` }
    }
    case z.ZodIssueCode.too_big: {
      const max = Number(issue.maximum)
      if (issue.type === 'string') return { message: `Gebruik maximaal ${max} tekens.` }
      if (issue.type === 'array' || issue.type === 'set') return { message: `Je kunt er maximaal ${max} toevoegen.` }
      if (issue.type === 'date') return { message: 'Deze datum is te laat.' }
      return { message: issue.inclusive ? `Vul maximaal ${max} in.` : `Vul minder dan ${max} in.` }
    }
    case z.ZodIssueCode.invalid_string:
      if (issue.validation === 'email') return { message: 'Dit is geen geldig e-mailadres.' }
      if (issue.validation === 'url') return { message: 'Dit is geen geldige link.' }
      return { message: 'Dit heeft niet de juiste vorm.' }
    case z.ZodIssueCode.invalid_enum_value:
    case z.ZodIssueCode.invalid_literal:
    case z.ZodIssueCode.invalid_union:
    case z.ZodIssueCode.invalid_union_discriminator:
      return { message: 'Kies een van de opties.' }
    case z.ZodIssueCode.invalid_date:
      return { message: 'Vul een geldige datum in.' }
    case z.ZodIssueCode.not_multiple_of:
      return {
        message: Number(issue.multipleOf) === 1 ? 'Vul een heel getal in.' : 'Dit getal kan niet.',
      }
    default:
      return { message: 'Controleer dit veld.' }
  }
}

z.setErrorMap(dutchErrorMap)
