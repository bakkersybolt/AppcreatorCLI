---
description: "Standaarden voor moderne Python CLI tools met Typer en Rich."
globs: "{src,tests}/**/*.py"
---

# Python CLI Richtlijnen

## Typer & Rich

- Gebruik **Typer** voor commando-parsing en opties, en **Rich** voor visuele consoles, panels, tabellen en voortgangsbalken.
- Houd commando's modulair en declareer subcommando's via duidelijke functies.
- Vang verwachte fouten netjes op en print vriendelijke foutmeldingen via `console.print("[bold red]Fout:[/bold red] ...")` met `raise typer.Exit(code=1)`.

## Type Hints & Testbaarheid

- Typeer alle argumenten en opties expliciet.
- Schrijf unit tests voor commando's met behulp van `typer.testing.CliRunner`.
