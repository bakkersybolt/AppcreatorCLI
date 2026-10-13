"""AppCreator CLI - AI-Ready Project Scaffolding Tool."""

import re
from pathlib import Path
from typing import List, Optional

import questionary
import typer
from rich.table import Table

from appcreator.core.detector import detect_system_tools
from appcreator.core.assistants import ASSISTANTS, normalize_assistants
from appcreator.core.generator import TEMPLATES_DIR, assemble_project, build_context, copy_skill
from appcreator.core.installer import init_git_repository, setup_node_environment, setup_python_environment
from appcreator.core.manifest import add_skill_to_manifest, load_manifest
from appcreator.core.naming import validate_app_name
from appcreator.core.skills import optionele_skills_voor, skill_past_bij_project
from appcreator.ui import (
    console,
    print_banner,
    print_error,
    print_info,
    print_step,
    print_success_card,
    print_summary_card,
    print_warning,
)

app = typer.Typer(
    name="appcreator",
    help="AppCreator: Genereer AI-ready startmappen voor je projecten met ingebouwde skills voor Google Antigravity en Claude Code.",
    no_args_is_help=False,
)

CATEGORIEEN = [
    {"key": "fullstack", "name": "Fullstack Web & API (Vue 3 + FastAPI + Database)"},
    {"key": "backend", "name": "Backend API Only (FastAPI + Database)"},
    {"key": "embedded", "name": "Embedded / IoT (ESP32 + PlatformIO C++)"},
    {"key": "cli", "name": "Python CLI Tool (Typer + Rich)"},
]

ASSISTENT_KEUZES = [
    {"name": "Google Antigravity (.agents/)", "value": ["antigravity"]},
    {"name": "Claude Code (CLAUDE.md + .claude/)", "value": ["claude"]},
    {"name": "Beide", "value": ["antigravity", "claude"]},
]


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Standaard entrypoint: start de interactieve wizard als er geen subcommando is opgegeven."""
    if ctx.invoked_subcommand is None:
        create(app_naam=None)


def parse_entity_names(raw: str) -> List[str]:
    """Parseert en valideert een vrije/komma-gescheiden string met entiteitsnamen."""
    if not raw or not raw.strip():
        return []
    # Verwijder mogelijke prefixen zoals 'custom:' of 'domeinen:'
    cleaned = re.sub(r"^(custom|entities|domeinen|entiteiten):\s*", "", raw.strip(), flags=re.IGNORECASE)
    # Splits op komma's of puntkomma's
    if "," in cleaned or ";" in cleaned:
        tokens = re.split(r"[,;]+", cleaned)
    else:
        tokens = cleaned.split()

    results: List[str] = []
    for token in tokens:
        sub = re.sub(r"[^a-zA-Z0-9_]", "", token.strip())
        if sub:
            parts = sub.split("_")
            pascal = "".join(p.capitalize() for p in parts if p)
            if pascal and pascal not in results:
                results.append(pascal)
    return results


def vraag_entiteiten() -> List[str]:
    """Laat de gebruiker via een interactieve checkbox multiselect entiteiten kiezen."""
    keuzes = questionary.checkbox(
        "Selecteer welke voorbeeld-entiteiten / domeinen je wilt genereren in de backend:",
        choices=[
            questionary.Choice("Item (Generiek / Standaard)", value="Item", checked=True),
            questionary.Choice("User (Gebruikersbeheer / Auth)", value="User", checked=False),
            questionary.Choice("Order (Bestellingen / E-commerce)", value="Order", checked=False),
            questionary.Choice("Device / Sensor (IoT & Hardware)", value="Device", checked=False),
            questionary.Choice("Todo (Taken / Task Manager)", value="Todo", checked=False),
            questionary.Choice("Custom (Zelf extra entiteiten opgeven...)", value="__custom__", checked=False),
        ],
    ).ask()

    if keuzes is None:
        return []

    resultaat: List[str] = [k for k in keuzes if k != "__custom__"]

    if "__custom__" in keuzes:
        invoer = questionary.text(
            "Voer je custom entiteiten in (bijv. 'Customer, Product, Ticket'):",
            default="",
        ).ask()
        if invoer:
            custom_items = parse_entity_names(invoer)
            for item in custom_items:
                if item not in resultaat:
                    resultaat.append(item)

    return resultaat


@app.command()
def create(
    app_naam: Optional[str] = typer.Argument(None, help="De naam van je nieuwe applicatie"),
):
    """Initialiseer een nieuw project via de interactieve categorie-wizard."""
    print_banner()

    # 1. Applicatienaam
    if not app_naam:
        print_step(1, 5, "Applicatienaam")
        app_naam = questionary.text(
            "Wat is de naam van je nieuwe applicatie?",
            default="MijnNieuweApp",
            validate=lambda tekst: validate_app_name(tekst) or True,
        ).ask()

    naam_fout = validate_app_name(app_naam or "")
    if naam_fout:
        print_error(f"{naam_fout} Setup afgebroken.")
        raise typer.Exit(1)

    app_naam = app_naam.strip()
    doel_pad = Path.cwd() / app_naam

    if doel_pad.exists() and any(doel_pad.iterdir()):
        print_warning(f"De doelmap './{app_naam}' bestaat al en is niet leeg.")
        overschrijven = questionary.confirm("Wil je toch doorgaan in deze map?").ask()
        if not overschrijven:
            print_info("Setup afgebroken.")
            raise typer.Exit()

    # 2. Categorie kiezen
    print_step(2, 5, "Project Categorie")
    categorie_keuze = questionary.select(
        "Kies een hoofdrichting voor je project:",
        choices=[c["name"] for c in CATEGORIEEN],
    ).ask()

    if not categorie_keuze:
        raise typer.Exit()

    geselecteerde_cat = next(c for c in CATEGORIEEN if c["name"] == categorie_keuze)["key"]

    # 3. Stack-specifieke vragen
    print_step(3, 5, "Stack Configuratie")
    stack_config = {}

    if geselecteerde_cat == "fullstack":
        stack_config["backend"] = "fastapi"
        stack_config["frontend"] = "vue3"

        db_keuze = questionary.select(
            "Welke database wil je gebruiken?",
            choices=["postgres", "sqlite", "none"],
            default="postgres",
        ).ask()
        stack_config["database"] = db_keuze
        entiteiten = vraag_entiteiten()
        stack_config["entiteiten"] = entiteiten
        stack_config["kern_domein"] = entiteiten[0] if entiteiten else None

    elif geselecteerde_cat == "backend":
        stack_config["backend"] = "fastapi"

        db_keuze = questionary.select(
            "Welke database wil je gebruiken?",
            choices=["postgres", "sqlite", "none"],
            default="postgres",
        ).ask()
        stack_config["database"] = db_keuze
        entiteiten = vraag_entiteiten()
        stack_config["entiteiten"] = entiteiten
        stack_config["kern_domein"] = entiteiten[0] if entiteiten else None

    elif geselecteerde_cat == "embedded":
        stack_config["hardware"] = "esp32"

    elif geselecteerde_cat == "cli":
        stack_config["cli"] = "python-typer"

    # 4. AI-assistent en optionele AI-skills selecteren
    print_step(4, 5, "AI-assistent & Skills")
    assistants = questionary.select(
        "Voor welke AI-assistent wil je regels en skills genereren?",
        choices=[questionary.Choice(title=k["name"], value=k["value"]) for k in ASSISTENT_KEUZES],
    ).ask()
    assistants = normalize_assistants(assistants)

    console.print("[dim]Basis-skills (init-project en stack-regels) worden altijd automatisch toegevoegd.[/dim]")

    passende_skills = optionele_skills_voor(geselecteerde_cat, stack_config.get("database"))
    skill_choices = [
        questionary.Choice(
            title=f"{s['name']}: {s['desc']}",
            value=s["name"],
            checked=s["checked"],
        )
        for s in passende_skills
    ]

    gekozen_skills = questionary.checkbox(
        "Selecteer welke extra AI-skills je wilt toevoegen:",
        choices=skill_choices,
    ).ask()

    if gekozen_skills is None:
        gekozen_skills = [s["name"] for s in passende_skills if s["checked"]]

    # 5. Installatie & Git opties
    print_step(5, 5, "Tooling & Installatie")
    tools = detect_system_tools()

    install_deps = False
    if geselecteerde_cat in ["fullstack", "backend", "cli"]:
        install_prompt = "Direct dependencies installeren? (venv / requirements"
        if geselecteerde_cat == "fullstack":
            install_prompt += " & npm install"
        if tools["uv"]:
            install_prompt += " - 'uv' gedetecteerd voor snelle setup"
        install_prompt += ")"
        install_deps = questionary.confirm(install_prompt, default=True).ask()

    init_git = questionary.confirm(
        "Git repository initialiseren en een eerste commit maken?",
        default=True,
    ).ask()

    # Samenvatting
    project_summary = {
        "app_naam": app_naam,
        "categorie_label": categorie_keuze,
        "backend": stack_config.get("backend"),
        "frontend": stack_config.get("frontend"),
        "hardware": stack_config.get("hardware"),
        "database": stack_config.get("database"),
        "entiteiten": stack_config.get("entiteiten"),
        "assistants": assistants,
        "skills": gekozen_skills,
        "install_deps": install_deps,
        "init_git": init_git,
    }

    print_summary_card(project_summary)

    akkoord = questionary.confirm("Wil je het project nu genereren?", default=True).ask()
    if not akkoord:
        print_info("Generatie geannuleerd.")
        raise typer.Exit()

    # Generatie uitvoeren
    with console.status(f"[bold cyan]Bezig met genereren van '{app_naam}'...", spinner="dots"):
        assemble_project(
            app_naam=app_naam,
            category=geselecteerde_cat,
            stack=stack_config,
            skills=gekozen_skills,
            target_dir=doel_pad,
            assistants=assistants,
        )

    console.print(f"[green]✓[/green] Bestanden en mappenstructuur gegenereerd in [cyan]{doel_pad}[/cyan]")

    # Optionele dependency installatie
    if install_deps:
        if stack_config.get("backend") or stack_config.get("cli"):
            with console.status("[bold cyan]Python omgeving inrichten en dependencies installeren...", spinner="dots"):
                req_path = doel_pad / "backend" / "requirements.txt"
                if not req_path.exists() and (doel_pad / "requirements.txt").exists():
                    req_path = doel_pad / "requirements.txt"
                python_dir = doel_pad / "backend" if (doel_pad / "backend").exists() else doel_pad
                python_ok = setup_python_environment(
                    target_dir=python_dir,
                    requirements_path=req_path if req_path.exists() else None,
                )
            if python_ok:
                console.print("[green]✓[/green] Python venv gereed.")
            else:
                install_cmd = "pip install -r requirements.txt" if req_path.exists() else 'pip install -e ".[dev]"'
                print_warning(
                    "Python dependencies zijn niet (volledig) geïnstalleerd. Voer dit later handmatig uit:\n"
                    f"cd {python_dir} && python3 -m venv .venv && .venv/bin/{install_cmd}"
                )

        if stack_config.get("frontend"):
            with console.status("[bold cyan]Frontend dependencies installeren via npm...", spinner="dots"):
                node_ok = setup_node_environment(doel_pad / "frontend")
            if node_ok:
                console.print("[green]✓[/green] Frontend dependencies gereed.")
            else:
                print_warning(
                    "Frontend dependencies zijn niet geïnstalleerd. Voer dit later handmatig uit:\n"
                    f"cd {doel_pad / 'frontend'} && npm install"
                )

    # Optionele Git init
    if init_git:
        with console.status("[bold cyan]Git repository initialiseren...", spinner="dots"):
            git_ok = init_git_repository(doel_pad, initial_commit=True)
        if git_ok:
            console.print("[green]✓[/green] Git repository geïnitialiseerd met eerste commit.")
        else:
            print_warning(
                "Git repository is niet (volledig) geïnitialiseerd. Voer dit later handmatig uit:\n"
                f"cd {doel_pad} && git init && git add . && git commit -m 'chore: initial commit'"
            )

    # Resultaat & instructies
    alle_skills = (load_manifest(doel_pad) or {}).get("skills", gekozen_skills)
    print_success_card(app_naam, str(doel_pad), alle_skills, assistants)


@app.command(name="list")
def list_resources():
    """Toon alle beschikbare categorieën, tech-stacks en AI-skills."""
    print_banner()

    # Categorieën tabel
    cat_table = Table(title="📁 Beschikbare Project Categorieën", border_style="cyan")
    cat_table.add_column("Key", style="bold green", width=12)
    cat_table.add_column("Omschrijving", style="white")

    for cat in CATEGORIEEN:
        cat_table.add_row(cat["key"], cat["name"])

    console.print(cat_table)
    console.print()

    # Skills tabel
    skills_dir = TEMPLATES_DIR / "skills"
    skill_table = Table(title="🤖 Beschikbare AI-Skills", border_style="cyan")
    skill_table.add_column("Skill Naam", style="bold yellow", width=22)
    skill_table.add_column("Doel & Functionaliteit", style="white")

    if skills_dir.exists():
        for skill_path in sorted(skills_dir.iterdir()):
            if skill_path.is_dir() and not skill_path.name.startswith("."):
                skill_file = skill_path / "SKILL.md"
                if not skill_file.exists():
                    skill_file = skill_path / "SKILL.md.jinja"
                desc = "Geen omschrijving"
                if skill_file.exists():
                    for line in skill_file.read_text(encoding="utf-8").splitlines():
                        if line.startswith("description:"):
                            desc = line.replace("description:", "").strip().strip('"').strip("'")
                            break
                        elif line.startswith("**Doel:**"):
                            desc = line.replace("**Doel:**", "").strip()
                            break
                skill_table.add_row(skill_path.name, desc)

    console.print(skill_table)
    console.print()


@app.command(name="add-skill")
def add_skill(
    skill_naam: Optional[str] = typer.Argument(None, help="De naam van de toe te voegen skill"),
):
    """Voeg een AI-skill toe aan het huidige project (voor de assistenten uit het manifest)."""
    manifest = load_manifest()
    project_dir = Path.cwd()

    assistants = normalize_assistants(manifest.get("assistants") if manifest else None)
    if not manifest:
        # Zonder manifest: gebruik de assistent(en) waarvan al een skills-map in het project staat
        aanwezig = [key for key, a in ASSISTANTS.items() if (project_dir / a.skills_dir).exists()]
        assistants = normalize_assistants(aanwezig)

    if not any((project_dir / ASSISTANTS[key].skills_dir).exists() for key in assistants):
        print_warning("Geen skills-map (.agents/ of .claude/) gevonden in de huidige directory. Weet je zeker dat dit een AI-project is?")
        doorgaan = questionary.confirm("Wil je toch doorgaan?").ask()
        if not doorgaan:
            raise typer.Exit()

    skills_dir = TEMPLATES_DIR / "skills"
    beschikbare_skills = sorted(
        d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
    )

    # Met een manifest bieden we alleen skills aan die bij het projecttype passen
    if manifest:
        category = manifest.get("category", "")
        stack = manifest.get("stack", {})
        passende_skills = [s for s in beschikbare_skills if skill_past_bij_project(s, category, stack)]
    else:
        category = "fullstack"
        stack = {"backend": "fastapi", "frontend": "vue3"}
        passende_skills = beschikbare_skills

    huidige_skills = manifest.get("skills", []) if manifest else []
    kandidaten = [s for s in passende_skills if s not in huidige_skills]

    if not skill_naam:
        if not kandidaten:
            print_info("Alle passende skills zijn al geïnstalleerd in dit project!")
            raise typer.Exit()

        skill_naam = questionary.select(
            "Welke skill wil je toevoegen?",
            choices=kandidaten,
        ).ask()

    if not skill_naam:
        raise typer.Exit()

    if skill_naam not in beschikbare_skills:
        print_error(f"Skill '{skill_naam}' niet gevonden. Beschikbaar: {', '.join(beschikbare_skills)}")
        raise typer.Exit(1)

    if skill_naam not in passende_skills:
        print_error(f"Skill '{skill_naam}' past niet bij dit projecttype ({category}). Passend: {', '.join(passende_skills)}")
        raise typer.Exit(1)

    app_naam = manifest.get("app_naam", project_dir.name) if manifest else project_dir.name
    context = build_context(app_naam, category, stack, assistants)

    succes = copy_skill(skill_naam, project_dir, context)
    if succes:
        add_skill_to_manifest(project_dir, skill_naam)
        doelen = ", ".join(f"{ASSISTANTS[key].skills_dir}/{skill_naam}" for key in assistants)
        console.print(f"[green]✓ Skill '{skill_naam}' succesvol toegevoegd aan {doelen}[/green]")
    else:
        print_error(f"Kon skill '{skill_naam}' niet kopiëren.")


@app.command(name="info")
def show_info():
    """Toon informatie over het project in de huidige directory."""
    manifest = load_manifest()
    if not manifest:
        print_error("Geen .appcreator.json manifest gevonden in de huidige map.")
        raise typer.Exit(1)

    print_banner()
    table = Table(title=f"📦 Project Info: {manifest.get('app_naam')}", border_style="cyan")
    table.add_column("Eigenschap", style="bold white", width=20)
    table.add_column("Waarde", style="cyan")

    table.add_row("Naam", manifest.get("app_naam", "-"))
    table.add_row("Categorie", manifest.get("category", "-"))
    table.add_row("Aangemaakt op", manifest.get("created_at", "-")[:19].replace("T", " "))

    stack = manifest.get("stack", {})
    if stack:
        for k, v in stack.items():
            table.add_row(f"Stack: {k}", str(v))

    assistants = normalize_assistants(manifest.get("assistants"))
    table.add_row("AI-assistent", ", ".join(ASSISTANTS[key].naam for key in assistants))

    skills = manifest.get("skills", [])
    table.add_row("Geïnstalleerde Skills", ", ".join(skills))

    console.print(table)


@app.command(name="dev")
def dev(
    project_dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Pad naar het project (standaard huidige map)",
    ),
):
    """Start lokale ontwikkelingsservices (database, backend, frontend) met realtime gecombineerde logs."""
    from appcreator.core.dev_runner import run_dev_server

    print_banner()
    run_dev_server(project_dir=project_dir)


@app.command(name="start")
def start(
    project_dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Pad naar het project (standaard huidige map)",
    ),
):
    """Alias voor 'appcreator dev'."""
    dev(project_dir=project_dir)


if __name__ == "__main__":
    app()
