"""AppCreator CLI - AI-Ready Project Scaffolding Tool."""

import os
import sys
from pathlib import Path
from typing import List, Optional

import questionary
import typer
from rich.table import Table

from appcreator.core.detector import detect_system_tools
from appcreator.core.generator import TEMPLATES_DIR, assemble_project, copy_skill
from appcreator.core.installer import init_git_repository, setup_node_environment, setup_python_environment
from appcreator.core.manifest import add_skill_to_manifest, load_manifest
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
    help="AppCreator: Genereer AI-ready startmappen voor je projecten met ingebouwde Antigravity skills.",
    no_args_is_help=False,
)

CATEGORIEEN = [
    {"key": "fullstack", "name": "🌐 Fullstack Web & API (Vue 3 + FastAPI + Database)"},
    {"key": "backend", "name": "⚡ Backend API Only (FastAPI + Database)"},
    {"key": "embedded", "name": "📡 Embedded / IoT (ESP32 + PlatformIO C++)"},
    {"key": "cli", "name": "💻 Python CLI Tool (Typer + Rich)"},
]

OPTIONELE_SKILLS = [
    {"name": "brainstorm-architect", "desc": "Domeinen, models & UI brainstorming (Aanbevolen)", "checked": True},
    {"name": "test-engineer", "desc": "Pytest / Vitest testautomatisering (Aanbevolen)", "checked": True},
    {"name": "code-reviewer", "desc": "Clean code, security & type review (Aanbevolen)", "checked": True},
    {"name": "database-architect", "desc": "Alembic migraties & query optimalisatie", "checked": False},
    {"name": "docker-devops", "desc": "Dockerfiles & compose netwerken", "checked": False},
]


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Standaard entrypoint: start de interactieve wizard als er geen subcommando is opgegeven."""
    if ctx.invoked_subcommand is None:
        create(app_naam=None)


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
        ).ask()

    if not app_naam:
        print_error("Geen applicatienaam opgegeven. Setup afgebroken.")
        raise typer.Exit(1)

    app_slug = app_naam.lower().replace(" ", "-").replace("_", "-")
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

        domein = questionary.text(
            "Wat is de primaire entiteit / kern domein? (bijv. 'Item', 'User', 'Sensor')",
            default="Item",
        ).ask()
        stack_config["kern_domein"] = domein.capitalize() if domein else "Item"

    elif geselecteerde_cat == "backend":
        stack_config["backend"] = "fastapi"

        db_keuze = questionary.select(
            "Welke database wil je gebruiken?",
            choices=["postgres", "sqlite", "none"],
            default="postgres",
        ).ask()
        stack_config["database"] = db_keuze

        domein = questionary.text(
            "Wat is de primaire entiteit / kern domein? (bijv. 'Item', 'User', 'Sensor')",
            default="Item",
        ).ask()
        stack_config["kern_domein"] = domein.capitalize() if domein else "Item"

    elif geselecteerde_cat == "embedded":
        stack_config["hardware"] = "esp32"

    elif geselecteerde_cat == "cli":
        stack_config["cli"] = "python-typer"

    # 4. Optionele AI-skills selecteren
    print_step(4, 5, "Google Antigravity AI-Skills (.agents/)")
    console.print("[dim]Basis-skills (init-project en stack-regels) worden altijd automatisch toegevoegd.[/dim]")

    skill_choices = [
        questionary.Choice(
            title=f"{s['name']}: {s['desc']}",
            value=s["name"],
            checked=s["checked"],
        )
        for s in OPTIONELE_SKILLS
    ]

    gekozen_skills = questionary.checkbox(
        "Selecteer welke extra AI-rollen je wilt toevoegen:",
        choices=skill_choices,
    ).ask()

    if gekozen_skills is None:
        gekozen_skills = ["brainstorm-architect", "test-engineer", "code-reviewer"]

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
        )

    console.print(f"[green]✓[/green] Bestanden en mappenstructuur gegenereerd in [cyan]{doel_pad}[/cyan]")

    # Optionele dependency installatie
    if install_deps:
        if stack_config.get("backend") or stack_config.get("cli"):
            with console.status("[bold cyan]Python omgeving inrichten en dependencies installeren...", spinner="dots"):
                req_path = doel_pad / "backend" / "requirements.txt"
                if not req_path.exists() and (doel_pad / "requirements.txt").exists():
                    req_path = doel_pad / "requirements.txt"
                setup_python_environment(
                    target_dir=doel_pad / "backend" if (doel_pad / "backend").exists() else doel_pad,
                    requirements_path=req_path if req_path.exists() else None,
                )
            console.print("[green]✓[/green] Python venv gereed.")

        if stack_config.get("frontend"):
            with console.status("[bold cyan]Frontend dependencies installeren via npm...", spinner="dots"):
                setup_node_environment(doel_pad / "frontend")
            console.print("[green]✓[/green] Frontend dependencies gereed.")

    # Optionele Git init
    if init_git:
        with console.status("[bold cyan]Git repository initialiseren...", spinner="dots"):
            init_git_repository(doel_pad, initial_commit=True)
        console.print("[green]✓[/green] Git repository geïnitialiseerd met eerste commit.")

    # Resultaat & instructies
    alle_skills = sorted(list(set(["init-project"] + gekozen_skills)))
    print_success_card(app_naam, str(doel_pad), alle_skills)


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
    skill_table = Table(title="🤖 Beschikbare AI-Skills (.agents/skills/)", border_style="cyan")
    skill_table.add_column("Skill Naam", style="bold yellow", width=22)
    skill_table.add_column("Doel & Functionaliteit", style="white")

    if skills_dir.exists():
        for skill_path in sorted(skills_dir.iterdir()):
            if skill_path.is_dir() and not skill_path.name.startswith("."):
                skill_file = skill_path / "SKILL.md"
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
    """Voeg een AI-skill toe aan het huidige project (.agents/skills/)."""
    manifest = load_manifest()
    project_dir = Path.cwd()

    if not (project_dir / ".agents").exists():
        print_warning("Geen '.agents' map gevonden in de huidige directory. Weet je zeker dat dit een AI-project is?")
        doorgaan = questionary.confirm("Wil je toch doorgaan?").ask()
        if not doorgaan:
            raise typer.Exit()

    skills_dir = TEMPLATES_DIR / "skills"
    beschikbare_skills = [
        d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
    ]

    huidige_skills = manifest.get("skills", []) if manifest else []
    kandidaten = [s for s in beschikbare_skills if s not in huidige_skills]

    if not skill_naam:
        if not kandidaten:
            print_info("Alle beschikbare skills zijn al geïnstalleerd in dit project!")
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

    context = manifest or {
        "app_naam": project_dir.name,
        "app_slug": project_dir.name.lower(),
        "backend": "fastapi",
        "frontend": "vue3",
    }

    succes = copy_skill(skill_naam, project_dir, context)
    if succes:
        add_skill_to_manifest(project_dir, skill_naam)
        console.print(f"[green]✓ Skill '{skill_naam}' succesvol toegevoegd aan .agents/skills/{skill_naam}[/green]")
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

    skills = manifest.get("skills", [])
    table.add_row("Geïnstalleerde Skills", ", ".join(skills))

    console.print(table)


if __name__ == "__main__":
    app()
