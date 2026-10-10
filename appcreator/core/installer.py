"""Dependency installation and Git setup manager for AppCreator."""

import subprocess
import sys
from pathlib import Path
from typing import Optional
from appcreator.core.detector import detect_system_tools, get_preferred_python_installer, get_preferred_node_installer
from appcreator.ui import console


def setup_python_environment(target_dir: Path, requirements_path: Optional[Path] = None) -> bool:
    """Sets up Python virtual environment and installs dependencies using uv if available, else venv+pip."""
    tools = detect_system_tools()
    python_cmd = "python3" if tools["python3"] else sys.executable
    venv_dir = target_dir / ".venv"

    try:
        if tools["uv"]:
            # uv venv is near-instantaneous
            subprocess.run(["uv", "venv", str(venv_dir)], check=True, cwd=str(target_dir), capture_output=True)
            if requirements_path and requirements_path.exists():
                subprocess.run(
                    ["uv", "pip", "install", "-r", str(requirements_path), "--python", str(venv_dir / "bin" / "python")],
                    check=True,
                    cwd=str(target_dir),
                    capture_output=True,
                )
            return True
        else:
            # Fallback to standard python3 -m venv
            subprocess.run([python_cmd, "-m", "venv", str(venv_dir)], check=True, cwd=str(target_dir), capture_output=True)
            pip_bin = venv_dir / "bin" / "pip"
            if pip_bin.exists() and requirements_path and requirements_path.exists():
                subprocess.run(
                    [str(pip_bin), "install", "-r", str(requirements_path)],
                    check=True,
                    cwd=str(target_dir),
                    capture_output=True,
                )
            return True
    except subprocess.CalledProcessError as e:
        console.print(f"[dim red]Waarschuwing bij Python installatie: {e}[/dim red]")
        return False
    except Exception as e:
        console.print(f"[dim red]Onverwachte fout bij Python setup: {e}[/dim red]")
        return False


def setup_node_environment(target_dir: Path) -> bool:
    """Installs Node dependencies using pnpm or npm in target_dir."""
    tools = detect_system_tools()
    installer = get_preferred_node_installer()
    if not (tools["npm"] or tools["pnpm"]):
        return False

    try:
        subprocess.run([installer, "install"], check=True, cwd=str(target_dir), capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[dim red]Waarschuwing bij {installer} installatie: {e}[/dim red]")
        return False
    except Exception as e:
        console.print(f"[dim red]Onverwachte fout bij Node setup: {e}[/dim red]")
        return False


def init_git_repository(target_dir: Path, initial_commit: bool = True) -> bool:
    """Initializes a git repository and optionally creates the initial commit."""
    tools = detect_system_tools()
    if not tools["git"]:
        return False

    try:
        subprocess.run(["git", "init"], check=True, cwd=str(target_dir), capture_output=True)
        if initial_commit:
            subprocess.run(["git", "add", "."], check=True, cwd=str(target_dir), capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "chore: initial commit from AppCreator CLI"],
                check=True,
                cwd=str(target_dir),
                capture_output=True,
            )
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[dim red]Waarschuwing bij Git initialisatie: {e}[/dim red]")
        return False
    except Exception as e:
        console.print(f"[dim red]Onverwachte fout bij Git setup: {e}[/dim red]")
        return False
