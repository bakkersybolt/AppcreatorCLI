"""System tools and environment detector for AppCreator."""

import shutil
import subprocess
from typing import Dict, Optional


def is_command_available(command: str) -> bool:
    """Checks whether an executable command is available on the system PATH."""
    return shutil.which(command) is not None


def detect_system_tools() -> Dict[str, bool]:
    """Detects available developer tools on the system."""
    return {
        "uv": is_command_available("uv"),
        "python3": is_command_available("python3") or is_command_available("python"),
        "npm": is_command_available("npm"),
        "pnpm": is_command_available("pnpm"),
        "yarn": is_command_available("yarn"),
        "git": is_command_available("git"),
        "docker": is_command_available("docker"),
    }


def get_preferred_python_installer() -> str:
    """Returns 'uv' if available for high-speed installs, otherwise 'pip'."""
    if is_command_available("uv"):
        return "uv"
    return "pip"


def get_preferred_node_installer() -> str:
    """Returns 'pnpm' if available, otherwise 'npm'."""
    if is_command_available("pnpm"):
        return "pnpm"
    return "npm"
