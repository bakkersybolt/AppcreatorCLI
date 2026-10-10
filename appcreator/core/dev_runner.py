"""Development environment runner for AppCreator CLI."""

import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

from rich.panel import Panel

from appcreator.core.manifest import load_manifest
from appcreator.ui import console, print_error, print_info, print_warning


def _stream_output(stream, prefix: str):
    """Reads lines from stream and outputs them to console with a styled prefix."""
    try:
        for line in iter(stream.readline, ""):
            if line:
                console.print(f"{prefix} {line.rstrip()}")
    except (ValueError, Exception):
        pass


def run_dev_server(project_dir: Optional[Path] = None):
    """Starts local development services (docker database, backend, frontend) with unified logs."""
    target_dir = (project_dir or Path.cwd()).resolve()

    manifest = load_manifest(target_dir)
    stack = manifest.get("stack", {}) if manifest else {}

    # Detecteer onderdelen
    has_backend = bool(stack.get("backend") == "fastapi" or (target_dir / "backend").is_dir())
    has_frontend = bool(stack.get("frontend") == "vue3" or (target_dir / "frontend").is_dir())
    has_postgres = bool(
        stack.get("database") == "postgres"
        or ((target_dir / "docker-compose.yml").is_file() and "postgres" in (target_dir / "docker-compose.yml").read_text())
    )

    if not has_backend and not has_frontend:
        print_error(
            f"Geen backend of frontend aangetroffen in '{target_dir}'. "
            "Zorg dat je in de hoofdmap van een AppCreator project staat."
        )
        return

    # 1. Database (PostgreSQL via Docker Compose)
    if has_postgres and (target_dir / "docker-compose.yml").is_file():
        if shutil.which("docker"):
            console.print("[dim yellow]📦 Database container opstarten via Docker Compose...[/dim yellow]")
            try:
                subprocess.run(
                    ["docker", "compose", "up", "-d", "postgres"],
                    cwd=str(target_dir),
                    check=False,
                    capture_output=True,
                )
                console.print("[bold yellow][database][/bold yellow] PostgreSQL container is actief op poort 5432.")
            except Exception as e:
                console.print(f"[dim red]Kon database niet starten via Docker: {e}[/dim red]")
        else:
            print_warning("Docker is niet geïnstalleerd of niet beschikbaar in PATH. PostgreSQL werd niet gestart.")

    # Bereid processen voor
    running_procs: List[subprocess.Popen] = []
    threads: List[threading.Thread] = []

    # 2. FastAPI Backend starten
    if has_backend:
        backend_dir = target_dir / "backend"
        backend_cmd: List[str] = []

        venv_uvicorn = backend_dir / ".venv" / "bin" / "uvicorn"
        venv_python = backend_dir / ".venv" / "bin" / "python"

        if venv_uvicorn.is_file():
            backend_cmd = [str(venv_uvicorn), "app.main:app", "--reload", "--port", "8000"]
        elif venv_python.is_file():
            backend_cmd = [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
        elif shutil.which("uvicorn"):
            backend_cmd = ["uvicorn", "app.main:app", "--reload", "--port", "8000"]
        else:
            backend_cmd = ["python3", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]

        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            b_proc = subprocess.Popen(
                backend_cmd,
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
            )
            running_procs.append(b_proc)

            b_thread = threading.Thread(
                target=_stream_output,
                args=(b_proc.stdout, "[bold cyan][backend ][/bold cyan]"),
                daemon=True,
            )
            b_thread.start()
            threads.append(b_thread)
        except Exception as e:
            console.print(f"[bold red]Fout bij starten backend:[/bold red] {e}")

    # 3. Vue 3 Frontend starten
    if has_frontend:
        frontend_dir = target_dir / "frontend"
        node_bin = "pnpm" if (frontend_dir / "pnpm-lock.yaml").is_file() and shutil.which("pnpm") else "npm"

        try:
            f_proc = subprocess.Popen(
                [node_bin, "run", "dev"],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            running_procs.append(f_proc)

            f_thread = threading.Thread(
                target=_stream_output,
                args=(f_proc.stdout, "[bold green][frontend][/bold green]"),
                daemon=True,
            )
            f_thread.start()
            threads.append(f_thread)
        except Exception as e:
            console.print(f"[bold red]Fout bij starten frontend:[/bold red] {e}")

    # Dashboard Banner tonen
    details = ["[bold white]AppCreator Local Dev Environment[/bold white]\n"]
    if has_frontend:
        details.append("• [bold green]Frontend UI:[/]   http://localhost:5173")
    if has_backend:
        details.append("• [bold cyan]Backend API:[/]   http://localhost:8000")
        details.append("• [bold cyan]API Docs:[/]      http://localhost:8000/docs")
    if has_postgres:
        details.append("• [bold yellow]Database:[/]      PostgreSQL op localhost:5432")
    details.append("\n[dim]Druk op Ctrl+C om alle services gelijktijdig te stoppen.[/dim]")

    console.print()
    console.print(
        Panel.fit(
            "\n".join(details),
            title="[bold cyan]🚀 Services Actief[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
        )
    )
    console.print()

    # Wacht op interrupt of einde van processen
    try:
        while True:
            # Controleer of er nog processen actief zijn
            alive = [p for p in running_procs if p.poll() is None]
            if not alive:
                break
            time.sleep(0.3)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]🛑 Ontvangen stop signaal, alle achtergrondservices afsluiten...[/bold yellow]")
    finally:
        for p in running_procs:
            if p.poll() is None:
                p.terminate()

        # Wacht maximaal 3 seconden op propere shutdown
        for p in running_procs:
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()

        console.print("[bold green]✓ Alle services zijn gestopt.[/bold green]\n")
