"""Project manifest manager (.appcreator.json) for AppCreator."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

MANIFEST_FILENAME = ".appcreator.json"


def create_manifest(
    project_dir: Path,
    app_naam: str,
    category: str,
    stack: Dict[str, Any],
    skills: List[str],
    assistants: Optional[List[str]] = None,
) -> Path:
    """Creates a new .appcreator.json manifest file in the project directory."""
    manifest_path = project_dir / MANIFEST_FILENAME
    data = {
        "generator": "AppCreator CLI",
        "version": "0.1.0",
        "app_naam": app_naam,
        "category": category,
        "stack": stack,
        "skills": skills,
        "assistants": assistants or ["antigravity"],
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
