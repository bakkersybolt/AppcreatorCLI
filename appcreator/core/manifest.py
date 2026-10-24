"""Project manifest manager (.appcreator.json) for AppCreator."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

MANIFEST_FILENAME = ".appcreator.json"
MANIFEST_VERSION = "0.2.0"


def create_manifest(
    project_dir: Path,
    app_naam: str,
    category: str,
    stack: Dict[str, Any],
    skills: List[str],
    assistants: Optional[List[str]] = None,
    ports: Optional[Dict[str, int]] = None,
    features: Optional[Dict[str, Any]] = None,
) -> Path:
    """Creates a new .appcreator.json manifest file in the project directory."""
    manifest_path = project_dir / MANIFEST_FILENAME
    data = {
        "generator": "AppCreator CLI",
        "version": MANIFEST_VERSION,
        "app_naam": app_naam,
        "category": category,
        "stack": stack,
        "skills": skills,
        "assistants": assistants or ["antigravity"],
        "ports": ports,
        "features": features or {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return manifest_path


def load_manifest(project_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Loads .appcreator.json from the current or specified directory."""
    target_dir = project_dir or Path.cwd()
    manifest_path = target_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return None
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def add_skill_to_manifest(project_dir: Path, skill_name: str) -> bool:
    """Adds a skill to .appcreator.json if not already present."""
    manifest_path = project_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return False
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = data.setdefault("skills", [])
        if skill_name not in skills:
            skills.append(skill_name)
            data["updated_at"] = datetime.now().isoformat()
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def update_manifest(project_dir: Path, **fields: Any) -> bool:
    """Overwrites top-level fields in .appcreator.json (e.g. ports, features)."""
    manifest_path = project_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return False
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError:
        return False
    data.update(fields)
    data["updated_at"] = datetime.now().isoformat()
    manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return True
