"""UI and styling helpers using Rich for AppCreator CLI."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

console = Console()

BANNER_ART = r"""
   ___                 ____                _             
  / _ \ _ __  _ __    / ___|_ __ ___  __ _| |_ ___  _ __ 
 / /_\ \ '_ \| '_ \  | |   | '__/ _ \/ _` | __/ _ \| '__|
|  _  | |_) | |_) | | |___| | |  __/ (_| | || (_) | |   
\_| |_/ .__/| .__/   \____|_|  \___|\__,_|\__\___/|_|   
      |_|   |_|                                          
"""


def print_banner():
    """Prints the stylish AppCreator welcome banner."""
    console.print(BANNER_ART, style="bold cyan")
    console.print(
        Panel.fit(
            "[bold white]🚀 AppCreator[/bold white] [dim]v0.1.0[/dim] — [italic green]AI-Ready Project Scaffolding CLI[/italic green]\n"
            "[dim]Snel modulaire projecten opzetten met ingebouwde Google Antigravity AI-skills & regels.[/dim]",
            border_style="cyan",
            padding=(0, 2),
        )
    )
    console.print()


def print_step(step_num: int, total_steps: int, title: str):
    """Prints a styled step divider."""
    console.print(f"\n[bold cyan]─── Stap {step_num}/{total_steps}: {title} ───[/bold cyan]\n")


def print_summary_card(project_data: dict):
    """Renders a rich table summarizing all choices before generation."""
    table = Table(title="📋 Project Configuratie Samenvatting", border_style="cyan")
    table.add_column("Instelling", style="bold white", width=22)
    table.add_column("Gekozen Waarde", style="cyan")

    table.add_row("Projectnaam", project_data.get("app_naam", "-"))
    table.add_row("Categorie", project_data.get("categorie_label", "-"))

    if "backend" in project_data and project_data["backend"]:
        table.add_row("Backend Stack", project_data["backend"])
    if "frontend" in project_data and project_data["frontend"]:
        table.add_row("Frontend Stack", project_data["frontend"])
    if "hardware" in project_data and project_data["hardware"]:
        table.add_row("Hardware / Embedded", project_data["hardware"])
    if "database" in project_data and project_data["database"]:
        table.add_row("Database", project_data["database"])
    if "entiteiten" in project_data and project_data["entiteiten"]:
        table.add_row("Entiteiten", ", ".join(project_data["entiteiten"]))
    elif "kern_domein" in project_data and project_data["kern_domein"]:
        table.add_row("Entiteit", project_data["kern_domein"])

    skills = project_data.get("skills", [])
    if skills:
        skills_formatted = ", ".join(f"[green]{s}[/green]" for s in skills)
        table.add_row("AI Skills (.agents/)", skills_formatted)

    table.add_row("Installatie", "Direct uitvoeren" if project_data.get("install_deps") else "Overslaan (later)")
    table.add_row("Git Initialisatie", "Ja + Initial commit" if project_data.get("init_git") else "Nee")

    console.print(table)
    console.print()


def print_success_card(app_naam: str, doel_pad: str, installed_skills: list):
    """Prints the completion card with next steps instructions."""
    console.print()
    skills_text = "\n".join(f"  • [green]✓[/green] [bold]{s}[/bold]" for s in installed_skills)
    
    body = (
        f"[bold green]✨ Project '{app_naam}' is succesvol gegenereerd![/bold green]\n\n"
        f"[bold white]Locatie:[/bold white] [cyan]{doel_pad}[/cyan]\n\n"
        f"[bold white]Geïnstalleerde AI-Skills (.agents/skills/):[/bold white]\n{skills_text}\n\n"
        f"[bold yellow]👉 Volgende stappen:[/bold yellow]\n"
        f"  1. Ga naar je projectmap:\n"
        f"     [cyan]cd {app_naam}[/cyan]\n\n"
        f"  2. Start de ontwikkelomgeving met gecombineerde logs:\n"
        f"     [bold cyan]appcreator dev[/bold cyan]  (of [cyan]./dev.sh[/cyan])\n\n"
        f"  3. Open het project in Google Antigravity of VS Code:\n"
        f"     [cyan]antigravity .[/cyan]  (of code .)\n\n"
        f"  4. Voer in de chat de startskill uit om direct de architect-intake te starten:\n"
        f"     [bold yellow]/init-project[/bold yellow] (of open [dim].agents/skills/init-project/SKILL.md[/dim])\n"
    )

    console.print(Panel(body, title="🎉 Setup Voltooid", border_style="green", padding=(1, 2)))
    console.print()


def print_error(message: str):
    """Prints a styled error message."""
    console.print(f"[bold red]❌ Fout:[/bold red] {message}")


def print_warning(message: str):
    """Prints a styled warning message."""
    console.print(f"[bold yellow]⚠️  Waarschuwing:[/bold yellow] {message}")


def print_info(message: str):
    """Prints a styled info message."""
    console.print(f"[cyan]ℹ️  {message}[/cyan]")
