"""UI and styling helpers using Rich for AppCreator CLI."""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from appcreator.core.assistants import ASSISTANTS, join_namen, normalize_assistants

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
            "[dim]Snel modulaire projecten opzetten met ingebouwde AI-skills & regels voor Google Antigravity en Claude Code.[/dim]",
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

    assistants = normalize_assistants(project_data.get("assistants"))
    table.add_row("AI-assistent", join_namen([ASSISTANTS[key].naam for key in assistants]))

    skills = project_data.get("skills", [])
    if skills:
        skills_formatted = ", ".join(f"[green]{s}[/green]" for s in skills)
        table.add_row("Extra AI-skills", skills_formatted)

    ports = project_data.get("ports")
    if ports:
        table.add_row("Poorten", f"backend {ports.backend}, frontend {ports.frontend}, postgres {ports.postgres}")

    hobby = (project_data.get("features") or {}).get("hobbyserver")
    if hobby:
        table.add_row("Hobbyserver", f"https://{hobby['domain']} (ssh {hobby['ssh_host']})")

    table.add_row("Installatie", "Direct uitvoeren" if project_data.get("install_deps") else "Overslaan (later)")
    table.add_row("Git Initialisatie", "Ja + Initial commit" if project_data.get("init_git") else "Nee")

    console.print(table)
    console.print()


def print_success_card(app_naam: str, doel_pad: str, installed_skills: list, assistants: Optional[List[str]] = None, ports=None):
    """Prints the completion card with next steps instructions."""
    console.print()
    skills_text = "\n".join(f"  • [green]✓[/green] [bold]{s}[/bold]" for s in installed_skills)
    gekozen = [ASSISTANTS[key] for key in normalize_assistants(assistants)]
    skills_dirs = ", ".join(f"{a.skills_dir}/" for a in gekozen)
    open_text = "\n".join(f"     [cyan]{a.open_cmd}[/cyan]  ({a.naam})" for a in gekozen)

    body = (
        f"[bold green]✨ Project '{app_naam}' is succesvol gegenereerd![/bold green]\n\n"
        f"[bold white]Locatie:[/bold white] [cyan]{doel_pad}[/cyan]\n\n"
        f"[bold white]Geïnstalleerde AI-Skills ({skills_dirs}):[/bold white]\n{skills_text}\n\n"
        f"[bold yellow]👉 Volgende stappen:[/bold yellow]\n"
        f"  1. Ga naar je projectmap:\n"
        f"     [cyan]cd {app_naam}[/cyan]\n\n"
        f"  2. Start de ontwikkelomgeving met gecombineerde logs:\n"
        f"     [bold cyan]appcreator dev[/bold cyan]  (of [cyan]./dev.sh[/cyan])\n"
        + (f"     Frontend op [cyan]http://localhost:{ports.frontend}[/cyan], API op [cyan]http://localhost:{ports.backend}/docs[/cyan]\n" if ports else "")
        + "\n"
        f"  3. Open het project in je AI-assistent:\n"
        f"{open_text}\n\n"
        f"  4. Voer in de chat de startskill uit; bij een web- of backendproject volgt daarna de ontwerpsessie:\n"
        f"     [bold yellow]/init-project[/bold yellow]\n"
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
