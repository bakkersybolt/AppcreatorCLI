"""Per-project port allocation for AppCreator.

Every generated app gets its own block of ports (a "slot"), so several apps
and git worktrees can run side by side. Slot 0 holds the framework defaults
(8000/5173/5432) and is never handed out: other tools on the machine use them.

The root .env of a project is the single source of truth at runtime; the
registry in ~/.appcreator/ports.json only prevents two apps getting the same slot.
"""

import json
import os
import re
import socket
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from appcreator.core.manifest import load_manifest

MAX_SLOT = 50
REGISTRY_FILENAME = "ports.json"

# Offsets from the main ports for agent backends, e2e and screenshot servers
AGENT_OFFSET = 1  # agent backends: backend+1 … backend+9
AGENT_COUNT = 9
E2E_OFFSET = 10
SCREENSHOT_OFFSET = 11


@dataclass(frozen=True)
class ProjectPorts:
    slot: int
    backend: int
    frontend: int
    postgres: int

    @classmethod
    def for_slot(cls, slot: int) -> "ProjectPorts":
        return cls(slot=slot, backend=8000 + 100 * slot, frontend=5100 + 100 * slot, postgres=5432 + slot)

    @property
    def agent_start(self) -> int:
        return self.backend + AGENT_OFFSET

    @property
    def agent_end(self) -> int:
        return self.backend + AGENT_COUNT

    @property
    def e2e_backend(self) -> int:
        return self.backend + E2E_OFFSET

    @property
    def e2e_frontend(self) -> int:
        return self.frontend + E2E_OFFSET

    @property
    def screenshot_backend(self) -> int:
        return self.backend + SCREENSHOT_OFFSET

    @property
    def screenshot_frontend(self) -> int:
        return self.frontend + SCREENSHOT_OFFSET

    def main_ports(self) -> Tuple[int, ...]:
        """Ports that must be free when the slot is handed out."""
        return (self.backend, self.frontend, self.postgres, self.e2e_backend, self.e2e_frontend)

    def as_env(self) -> Dict[str, str]:
        return {
            "BACKEND_PORT": str(self.backend),
            "FRONTEND_PORT": str(self.frontend),
            "POSTGRES_PORT": str(self.postgres),
            "AGENT_PORT_START": str(self.agent_start),
            "E2E_BACKEND_PORT": str(self.e2e_backend),
            "E2E_FRONTEND_PORT": str(self.e2e_frontend),
        }

    def as_manifest(self) -> Dict[str, int]:
        return {"slot": self.slot, "backend": self.backend, "frontend": self.frontend, "postgres": self.postgres}

    def as_context(self) -> Dict[str, int]:
        return {
            **self.as_manifest(),
            "agent_start": self.agent_start,
            "agent_end": self.agent_end,
            "e2e_backend": self.e2e_backend,
            "e2e_frontend": self.e2e_frontend,
            "screenshot_backend": self.screenshot_backend,
            "screenshot_frontend": self.screenshot_frontend,
        }


# Framework defaults; used for projects generated before ports were allocated
LEGACY_PORTS = ProjectPorts(slot=0, backend=8000, frontend=5173, postgres=5432)


def default_ports() -> ProjectPorts:
    """Deterministic ports for rendering without an allocation (tests, add-skill on old projects)."""
    return ProjectPorts.for_slot(1)


# --- Registry -------------------------------------------------------------------------------


def appcreator_home() -> Path:
    return Path(os.environ.get("APPCREATOR_HOME") or (Path.home() / ".appcreator"))


def _registry_path() -> Path:
    return appcreator_home() / REGISTRY_FILENAME


def load_registry() -> Dict[str, Any]:
    path = _registry_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data.get("projects"), dict):
                return data
        except (ValueError, OSError):
            pass
    return {"version": 1, "projects": {}}


def save_registry(data: Dict[str, Any]) -> None:
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def _prune(data: Dict[str, Any], keep: Optional[str] = None) -> None:
    """Drops registry entries whose project folder no longer exists."""
    for pad in list(data["projects"]):
        if pad != keep and not Path(pad).exists():
            del data["projects"][pad]


def port_is_free(port: int) -> bool:
    """True when nothing listens on the port: no answer on localhost and binding succeeds."""
    for family, host in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
        try:
            with socket.socket(family, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.2)
                if sock.connect_ex((host, port)) == 0:
                    return False
        except OSError:
            pass  # e.g. no IPv6 on this machine
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("", port))
    except OSError:
        return False
    return True


def _register(data: Dict[str, Any], project_dir: Path, app_slug: str, ports: ProjectPorts) -> None:
    data["projects"][str(project_dir)] = {
        "app_slug": app_slug,
        "slot": ports.slot,
        "allocated_at": datetime.now().isoformat(timespec="seconds"),
    }


def allocate_ports(project_dir: Path, app_slug: str, exclude_current: bool = False) -> ProjectPorts:
    """Hands out the first slot that is neither registered nor in use, and registers it.

    The same project folder gets its existing slot back, unless exclude_current is set
    (used by `appcreator ports --reassign`).
    """
    project_dir = project_dir.resolve()
    data = load_registry()
    _prune(data, keep=str(project_dir))

    current = data["projects"].get(str(project_dir))
    if current and not exclude_current:
        return ProjectPorts.for_slot(int(current["slot"]))

    taken = {int(entry["slot"]) for pad, entry in data["projects"].items() if pad != str(project_dir)}
    if current:
        taken.add(int(current["slot"]))

    for slot in range(1, MAX_SLOT + 1):
        if slot in taken:
            continue
        ports = ProjectPorts.for_slot(slot)
        if all(port_is_free(p) for p in ports.main_ports()):
            _register(data, project_dir, app_slug, ports)
            save_registry(data)
            return ports

    raise RuntimeError(f"Geen vrij poortblok gevonden (slot 1-{MAX_SLOT} zijn bezet).")


def register_ports(project_dir: Path, app_slug: str, ports: ProjectPorts) -> None:
    """Records ports chosen elsewhere (e.g. `appcreator ports --adopt`) in the registry."""
    data = load_registry()
    _register(data, project_dir.resolve(), app_slug, ports)
    save_registry(data)


def release_ports(project_dir: Path) -> None:
    data = load_registry()
    if data["projects"].pop(str(project_dir.resolve()), None) is not None:
        save_registry(data)


# --- Runtime resolution ---------------------------------------------------------------------


def read_env_file(path: Path) -> Dict[str, str]:
    """Parses KEY=value lines of a .env file (comments and blank lines ignored)."""
    values: Dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep and key.strip():
            values[key.strip()] = value.strip().strip("'\"")
    return values


def _as_int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value) if value else None
    except ValueError:
        return None


def resolve_ports(project_dir: Path) -> Tuple[ProjectPorts, Dict[str, str]]:
    """Returns the ports of a project and where each one came from.

    Order per port: environment variable, root .env, manifest, legacy default.
    """
    env_file = read_env_file(project_dir / ".env")
    manifest_ports = ((load_manifest(project_dir) or {}).get("ports")) or {}

    resolved: Dict[str, int] = {}
    sources: Dict[str, str] = {}
    for name, env_key in (("backend", "BACKEND_PORT"), ("frontend", "FRONTEND_PORT"), ("postgres", "POSTGRES_PORT")):
        for source, value in (
            ("omgeving", _as_int(os.environ.get(env_key))),
            (".env", _as_int(env_file.get(env_key))),
            ("manifest", manifest_ports.get(name)),
            ("standaard", getattr(LEGACY_PORTS, name)),
        ):
            if value:
                resolved[name] = int(value)
                sources[name] = source
                break

    slot = int(manifest_ports.get("slot", 0)) if manifest_ports else 0
    return ProjectPorts(slot=slot, **resolved), sources


# --- Writing ports into a project -----------------------------------------------------------

ENV_HEADER = "# Poorten van deze app (toegewezen door appcreator; wijzigen met `appcreator ports --reassign`)"


def root_env_text(ports: ProjectPorts, include_postgres: bool) -> str:
    lines = [ENV_HEADER]
    for key, value in ports.as_env().items():
        if key == "POSTGRES_PORT" and not include_postgres:
            continue
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def write_root_env(project_dir: Path, ports: ProjectPorts, include_postgres: bool) -> None:
    """Writes the port keys into .env and .env.example, keeping any other lines intact."""
    for name in (".env", ".env.example"):
        path = project_dir / name
        nieuw = root_env_text(ports, include_postgres)
        if path.is_file():
            port_keys = set(ports.as_env())
            overig = [
                line
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() != ENV_HEADER and line.partition("=")[0].strip() not in port_keys
                and not line.startswith("# Host-poort waarop de PostgreSQL")
            ]
            rest = "\n".join(overig).strip()
            nieuw = nieuw + ("\n" + rest + "\n" if rest else "")
        path.write_text(nieuw, encoding="utf-8")


def ports_from_manifest(manifest: Optional[Dict[str, Any]]) -> Optional[ProjectPorts]:
    """The ports recorded in a manifest, or None for projects generated before allocation."""
    data = (manifest or {}).get("ports")
    if not data:
        return None
    try:
        return ProjectPorts(**{k: int(data[k]) for k in ("slot", "backend", "frontend", "postgres")})
    except (KeyError, TypeError, ValueError):
        return None


PORTS_BLOCK = re.compile(r"(<!-- appcreator:ports:start -->\n)(.*?)(<!-- appcreator:ports:end -->)", re.S)


def replace_port_numbers(text: str, old: ProjectPorts, new: ProjectPorts) -> str:
    """Swaps every derived port number of `old` for the one of `new` (longest numbers first)."""
    mapping = {str(old.as_context()[k]): str(new.as_context()[k]) for k in new.as_context() if k != "slot"}
    pattern = re.compile(r"(?<!\d)(" + "|".join(sorted(map(re.escape, mapping), key=len, reverse=True)) + r")(?!\d)")
    return pattern.sub(lambda m: mapping[m.group(1)], text)
