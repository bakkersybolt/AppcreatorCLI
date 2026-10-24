"""Tests for the Claude Code hooks, settings and git hooks in generated projects."""

import json
import os
import subprocess

import pytest

from appcreator.core.generator import assemble_project

FULLSTACK = {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": []}


def _guard(target, command, cwd=None):
    return subprocess.run(
        ["python3", str(target / ".claude" / "hooks" / "worktree-shell-guard.py")],
        input=json.dumps({"cwd": str(cwd or target), "tool_input": {"command": command}}),
        capture_output=True,
        text=True,
        env={**os.environ, "WORKTREE_GUARD_FORCE": "1"},
    )


def test_claude_project_gets_settings_and_executable_hooks(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Web", "fullstack", FULLSTACK, [], target, assistants=["claude"])

    settings = json.loads((target / ".claude" / "settings.json").read_text())
    commands = [h["command"] for groep in settings["hooks"].values() for item in groep for h in item["hooks"]]
    assert any("lint-changed-file.sh" in c for c in commands)
    assert any("worktree-shell-guard.py" in c for c in commands)
    assert not any("hobbyserver" in c for c in commands)
    assert "Bash(npm run lint)" in settings["permissions"]["allow"]
    assert "Bash(.venv/bin/pytest)" in settings["permissions"]["allow"]

    for hook in ["lint-changed-file.sh", "worktree-shell-guard.py"]:
        assert os.access(target / ".claude" / "hooks" / hook, os.X_OK), hook
    assert os.access(target / ".githooks" / "pre-commit", os.X_OK)
    subprocess.run(["bash", "-n", str(target / ".claude" / "hooks" / "lint-changed-file.sh")], check=True)
    subprocess.run(["bash", "-n", str(target / ".githooks" / "pre-commit")], check=True)
    assert ".claude/worktrees/" in (target / ".gitignore").read_text()


def test_settings_follow_the_stack(tmp_path):
    target = tmp_path / "Cli"
    assemble_project("Cli", "cli", {"cli": "python-typer"}, [], target, assistants=["claude"])
    allow = json.loads((target / ".claude" / "settings.json").read_text())["permissions"]["allow"]
    assert "Bash(.venv/bin/pytest)" in allow
    assert not any("npm" in a for a in allow)
    assert not (target / ".githooks").exists()


def test_antigravity_only_project_has_no_claude_folder(tmp_path):
    target = tmp_path / "Ag"
    assemble_project("Ag", "fullstack", FULLSTACK, [], target, assistants=["antigravity"])
    assert not (target / ".claude").exists()


@pytest.mark.parametrize(
    "command, geweigerd",
    [
        ("cd frontend && npm test", True),
        ("git -C backend status", True),
        ("for f in a b; do echo $f; done", True),
        ("cat <<EOF\nx\nEOF", True),
        ("npm --prefix frontend run test", False),
        ("git status", False),
    ],
)
def test_worktree_guard_blocks_shell_constructs(tmp_path, command, geweigerd):
    target = tmp_path / "Web"
    assemble_project("Web", "fullstack", FULLSTACK, [], target, assistants=["claude"])
    result = _guard(target, command)
    assert (result.returncode == 2) == geweigerd, result.stderr


def test_worktree_guard_names_the_apps_postgres_container(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Mijn Shop", "fullstack", FULLSTACK, [], target, assistants=["claude"])
    result = _guard(target, "psql -c 'select 1'", cwd=target / "backend")
    assert result.returncode == 2
    assert "docker exec mijn-shop-postgres psql" in result.stderr
