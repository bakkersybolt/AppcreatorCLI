"""Small edits to an existing .claude/settings.json (keeping what the user changed)."""

import json
from pathlib import Path

HOBBYSERVER_GUARD = 'GUARD_ONLY_SSH=1 bash "$CLAUDE_PROJECT_DIR/.claude/hooks/hobbyserver-guard.sh"'


def add_hobbyserver_guard(project_dir: Path) -> bool:
    """Adds the hobbyserver guard to the Bash PreToolUse hooks; returns False if settings.json is missing."""
    path = project_dir / ".claude" / "settings.json"
    if not path.is_file():
        return False
    settings = json.loads(path.read_text(encoding="utf-8"))
    pre = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
    bash = next((item for item in pre if item.get("matcher") == "Bash"), None)
    if bash is None:
        bash = {"matcher": "Bash", "hooks": []}
        pre.append(bash)
    if not any(h.get("command") == HOBBYSERVER_GUARD for h in bash["hooks"]):
        bash["hooks"].insert(0, {"type": "command", "command": HOBBYSERVER_GUARD})
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True
