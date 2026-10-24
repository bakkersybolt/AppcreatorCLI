"""`appcreator ports`: show, reassign or adopt the port block of a project."""

from pathlib import Path
from typing import List

from rich.table import Table

from appcreator.core.manifest import load_manifest, update_manifest
from appcreator.core.naming import make_slug
from appcreator.core.ports import (
    ProjectPorts,
    allocate_ports,
    port_is_free,
    register_ports,
    replace_port_numbers,
    resolve_ports,
    write_root_env,
)
from appcreator.ui import console, print_error, print_info

# Files that contain the app's port numbers (relative to the project root)
PORT_FILES = [
    ".env",
    ".env.example",
    "backend/.env",
    "backend/.env.example",
    "backend/app/core/config.py",
    "frontend/.env",
    "frontend/.env.example",
    "frontend/vite.config.ts",
    "frontend/package.json",
    "docker-compose.yml",
    "dev.sh",
    "README.md",
    "CLAUDE.md",
]
PORT_GLOBS = [".agents/**/*.md", ".claude/**/*.md", "docs/**/*.md", "frontend/playwright*.ts"]


def _port_files(project_dir: Path) -> List[Path]:
    files = [project_dir / rel for rel in PORT_FILES if (project_dir / rel).is_file()]
    for pattern in PORT_GLOBS:
        files.extend(p for p in project_dir.glob(pattern) if p.is_file())
    return list(dict.fromkeys(files))


def _slug(project_dir: Path) -> str:
    manifest = load_manifest(project_dir) or {}
    return make_slug(manifest.get("app_naam") or project_dir.name)


def _has_postgres(project_dir: Path) -> bool:
    manifest = load_manifest(project_dir) or {}
    if manifest.get("stack", {}).get("database") == "postgres":
        return True
    compose = project_dir / "docker-compose.yml"
    return compose.is_file() and "postgres" in compose.read_text(encoding="utf-8")


def show_ports(project_dir: Path) -> None:
    ports, sources = resolve_ports(project_dir)
    table = Table(title=f"🔌 Poorten van {project_dir.name}", border_style="cyan")
    table.add_column("Onderdeel", style="bold white")
    table.add_column("Poort", style="cyan")
    table.add_column("Bron", style="dim")
    table.add_column("Status")

    rows = [
        ("Backend (FastAPI)", ports.backend, sources["backend"]),
        ("Frontend (Vite)", ports.frontend, sources["frontend"]),
        ("PostgreSQL", ports.postgres, sources["postgres"]),
    ]
    for naam, port, bron in rows:
        status = "[green]vrij[/green]" if port_is_free(port) else "[yellow]in gebruik[/yellow]"
        table.add_row(naam, str(port), bron, status)
    table.add_row("Agent-backends", f"{ports.agent_start}–{ports.agent_end}", "afgeleid", "")
    table.add_row("E2E (backend / frontend)", f"{ports.e2e_backend} / {ports.e2e_frontend}", "afgeleid", "")
    console.print(table)
    if "standaard" in sources.values():
        print_info("Dit project gebruikt (deels) de standaardpoorten. Neem eigen poorten over met 'appcreator ports --adopt' of kies een nieuw blok met 'appcreator ports --reassign'.")


def reassign_ports(project_dir: Path) -> ProjectPorts:
    """Moves the project to a new free port block and rewrites every file that mentions the old ports."""
    old, _ = resolve_ports(project_dir)
    new = allocate_ports(project_dir, _slug(project_dir), exclude_current=True)

    gewijzigd = []
    for path in _port_files(project_dir):
        tekst = path.read_text(encoding="utf-8")
        nieuw = replace_port_numbers(tekst, old, new)
        if nieuw != tekst:
            path.write_text(nieuw, encoding="utf-8")
            gewijzigd.append(path.relative_to(project_dir))

    write_root_env(project_dir, new, include_postgres=_has_postgres(project_dir))
    update_manifest(project_dir, ports=new.as_manifest())

    console.print(f"[green]✓[/green] Nieuw poortblok: backend {new.backend}, frontend {new.frontend}, postgres {new.postgres}")
    if gewijzigd:
        console.print("[dim]Bijgewerkt: " + ", ".join(str(p) for p in gewijzigd) + "[/dim]")
    if _has_postgres(project_dir):
        print_info("Herstart de database met 'docker compose up -d postgres' zodat hij op de nieuwe poort luistert.")
    return new


def adopt_ports(project_dir: Path) -> ProjectPorts:
    """Records the ports a project already uses (env/.env) in its manifest and the registry."""
    ports, sources = resolve_ports(project_dir)
    if not (load_manifest(project_dir)):
        print_error("Geen .appcreator.json gevonden; alleen AppCreator-projecten kunnen poorten overnemen.")
        return ports

    # Reserve the slot whose block the backend port falls in, so new apps skip it
    slot = (ports.backend - 8000) // 100 if ports.backend > 8000 and ports.backend % 100 == 0 else 0
    adopted = ProjectPorts(slot=slot, backend=ports.backend, frontend=ports.frontend, postgres=ports.postgres)

    write_root_env(project_dir, adopted, include_postgres=_has_postgres(project_dir))
    update_manifest(project_dir, ports=adopted.as_manifest())
    if slot:
        register_ports(project_dir, _slug(project_dir), adopted)

    console.print(f"[green]✓[/green] Poorten overgenomen: backend {adopted.backend}, frontend {adopted.frontend}, postgres {adopted.postgres}")
    if "standaard" in sources.values():
        print_info("Niet elke poort stond in .env; ontbrekende poorten zijn op de standaardwaarde gezet. Controleer .env.")
    return adopted
