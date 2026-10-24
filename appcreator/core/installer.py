"""Dependency installation and Git setup manager for AppCreator."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from appcreator.core.detector import detect_system_tools, get_preferred_node_installer
from appcreator.ui import console


def _format_process_error(error: subprocess.CalledProcessError) -> str:
    """Returns the command and the last lines of its stderr/stdout for a failed subprocess."""
    output = error.stderr or error.stdout or b""
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    tail = "\n".join(output.strip().splitlines()[-8:])
    command = " ".join(str(part) for part in error.cmd)
    return f"'{command}' eindigde met exit code {error.returncode}\n{tail}".rstrip()


def setup_python_environment(target_dir: Path, requirements_path: Optional[Path] = None) -> bool:
    """Sets up Python virtual environment and installs dependencies using uv if available, else venv+pip.

    Installs from requirements_path when given; otherwise installs the project itself in
    editable mode (with its 'dev' extra) when target_dir contains a pyproject.toml.
    """
    tools = detect_system_tools()
    python_cmd = "python3" if tools["python3"] else sys.executable
    venv_dir = target_dir / ".venv"

    install_args: List[str] = []
    if requirements_path and requirements_path.exists():
        install_args = ["-r", str(requirements_path)]
    elif (target_dir / "pyproject.toml").exists():
        install_args = ["-e", ".[dev]"]

    try:
        if tools["uv"]:
            # uv venv is near-instantaneous
            subprocess.run(["uv", "venv", str(venv_dir)], check=True, cwd=str(target_dir), capture_output=True)
            if install_args:
                subprocess.run(
                    ["uv", "pip", "install", *install_args, "--python", str(venv_dir / "bin" / "python")],
                    check=True,
                    cwd=str(target_dir),
                    capture_output=True,
                )
            return True
        else:
            # Fallback to standard python3 -m venv
            subprocess.run([python_cmd, "-m", "venv", str(venv_dir)], check=True, cwd=str(target_dir), capture_output=True)
            pip_bin = venv_dir / "bin" / "pip"
            if install_args:
                subprocess.run(
                    [str(pip_bin), "install", *install_args],
                    check=True,
                    cwd=str(target_dir),
                    capture_output=True,
                )
            return True
    except subprocess.CalledProcessError as e:
        console.print(f"Waarschuwing bij Python installatie: {_format_process_error(e)}", style="dim red", markup=False)
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
        console.print(f"Waarschuwing bij {installer} installatie: {_format_process_error(e)}", style="dim red", markup=False)
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
        # Versioned git hooks (.githooks/pre-commit); enabled after the initial commit,
        # because dependencies may not be installed yet.
        if (target_dir / ".githooks").is_dir():
            subprocess.run(["git", "config", "core.hooksPath", ".githooks"], check=True, cwd=str(target_dir), capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"Waarschuwing bij Git initialisatie: {_format_process_error(e)}", style="dim red", markup=False)
        return False
    except Exception as e:
        console.print(f"[dim red]Onverwachte fout bij Git setup: {e}[/dim red]")
        return False
