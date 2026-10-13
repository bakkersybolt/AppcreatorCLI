# Python CLI met Typer en Rich

## Structuur

- De broncode staat in `src/<package>/`, de tests in `tests/`. Commando's worden geregistreerd op de `app` in `main.py`.
- Elk commando is een eigen functie met een docstring: Typer toont die als helptekst.
- Splits commando's op in eigen modules met een eigen `typer.Typer()` zodra `main.py` onoverzichtelijk wordt, en voeg ze toe met `app.add_typer()`.
- Houd logica buiten de commandofuncties: een commando leest argumenten, roept een gewone functie aan en toont het resultaat. Zo is de logica te testen zonder de CLI.

## Invoer en uitvoer

- Geef alle argumenten en opties een type en een `help`-tekst.
- Toon uitvoer via de gedeelde Rich `console`, niet met `print()`.
- Vang verwachte fouten af, toon een duidelijke melding en stop met `raise typer.Exit(code=1)`. Laat geen traceback zien voor fouten die de gebruiker kan herstellen.

## Testen

- Test commando's met `typer.testing.CliRunner` en controleer `exit_code` en uitvoer.
- Draai de tests met `.venv/bin/pytest`.
