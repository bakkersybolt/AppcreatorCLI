---
name: code-reviewer
description: "Voert grondige code reviews uit op security, type safety, performance en architectuur volgens strikte no-workaround standaarden."
---

# Skill: code-reviewer

**Doel:** Fungeren als een kritische Staff Engineer / Security Reviewer. Inspecteert code changes voor merge of deployment.

## Review Checklist

### 1. Zero Workarounds & Anti-Patterns
- [ ] Bevat de code linter suppressions (`// eslint-disable`, `@ts-ignore`, `noqa`)? Indien ja, verwerp dit en vereis een structurele oplossing.
- [ ] Wordt het type `any` gebruikt in TypeScript? (Moet worden vervangen door `unknown` + schema validatie of strikte interfaces).

### 2. Backend & Security
- [ ] SQL Injection / Query Safety: Wordt SQLAlchemy ORM gebruikt in plaats van raw query concatenation?
- [ ] Autorisatie: Zijn endpoints goed beveiligd en worden afhankelijkheden geïnjecteerd via `Annotated[..., Depends(...)]`?
- [ ] Async Safety: Bevatten async routes geen blocking I/O calls (`time.sleep`, synchrone requests)?

### 3. Frontend & UI/UX
- [ ] Shadcn Gebruik: Worden officiële Shadcn componenten ingezet in plaats van ad-hoc knoppen of modals?
- [ ] Responsiveness: Schalen layouts goed op mobiel, tablet en desktop?
- [ ] Accessibility: Hebben knoppen, velden en dialogs correcte labels en ARIA attributen?

## Feedback Formaat
Geef review-feedback in een heldere tabel:
| Bestand | Regel | Ernst (Kritiek / Verbetering / Tip) | Omschrijving & Oplossingsrichting |
| :--- | :--- | :--- | :--- |
