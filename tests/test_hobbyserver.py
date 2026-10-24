"""Tests for the optional hobbyserver deploy (Docker + Traefik via GitHub Actions)."""

import json
import os
import subprocess

from appcreator.core.claude_settings import add_hobbyserver_guard
from appcreator.core.generator import assemble_project, build_context, copy_skill, render_feature
from appcreator.core.manifest import load_manifest
from appcreator.core.skills import hobbyserver_mogelijk, skill_past_bij_project

FULLSTACK = {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": []}
BACKEND = {"backend": "fastapi", "database": "postgres", "entiteiten": []}
HOBBY = {"hobbyserver": {"app_name": "mijn-shop", "domain": "mijnshop.nl", "ssh_host": "vps", "deploy_key": "~/.ssh/shop_deploy"}}


def test_hobbyserver_only_for_postgres_backends():
    assert hobbyserver_mogelijk("fullstack", FULLSTACK)
    assert not hobbyserver_mogelijk("backend", {**BACKEND, "database": "sqlite"})
    assert not hobbyserver_mogelijk("cli", {"cli": "python-typer"})
    assert skill_past_bij_project("hobbyserver-deploy", "backend", BACKEND)


def test_without_feature_there_are_no_deploy_files(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Mijn Shop", "fullstack", FULLSTACK, [], target, assistants=["claude"])
    for pad in ["deploy", ".github", "scripts", ".claude/hooks/hobbyserver-guard.sh", ".claude/skills/hobbyserver-deploy"]:
        assert not (target / pad).exists(), pad
    assert "hobbyserver" not in (target / ".claude" / "settings.json").read_text()


def test_fullstack_with_hobbyserver(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Mijn Shop", "fullstack", FULLSTACK, [], target, assistants=["claude"], features=HOBBY)

    app_env = (target / "deploy" / "app.env").read_text()
    assert "APP_NAME=mijn-shop" in app_env and "APP_DOMAIN=mijnshop.nl" in app_env
    assert "POSTGRES_DB=mijn_shop" in app_env and """CORS_ORIGINS='["https://mijnshop.nl"]'""" in app_env

    compose = (target / "deploy" / "compose.yml").read_text()
    assert "PathPrefix(`/api`)" in compose and "frontend:" in compose and "{%" not in compose

    workflow = (target / ".github" / "workflows" / "deploy.yml").read_text()
    assert "${{ secrets.DEPLOY_SSH_KEY }}" in workflow and "component: [backend, frontend]" in workflow
    assert "FRONTEND_IMAGE" in workflow and "{{ '{{' }}" not in workflow

    server = (target / "deploy" / "SERVER.md").read_text()
    assert 'ssh vps "uptime' in server and "{{.Names}}" in server

    guard = target / ".claude" / "hooks" / "hobbyserver-guard.sh"
    assert os.access(guard, os.X_OK) and "shop_deploy" in guard.read_text()
    assert os.access(target / "scripts" / "setup-github-secrets.sh", os.X_OK)
    assert "$HOME/.ssh/shop_deploy" in (target / "scripts" / "setup-github-secrets.sh").read_text()

    settings = (target / ".claude" / "settings.json").read_text()
    assert "hobbyserver-guard.sh" in settings
    json.loads(settings)

    assert "hobbyserver-deploy" in load_manifest(target)["skills"]
    assert load_manifest(target)["features"] == HOBBY
    context = (target / "CLAUDE.md").read_text()
    assert "@deploy/SERVER.md" in context and "https://mijnshop.nl" in context
    skill = (target / ".claude" / "skills" / "hobbyserver-deploy" / "SKILL.md").read_text()
    assert "ssh vps" in skill and "ServerManager" not in skill


def test_guard_blocks_destructive_server_commands(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Mijn Shop", "backend", BACKEND, [], target, assistants=["claude"], features=HOBBY)
    guard = target / ".claude" / "hooks" / "hobbyserver-guard.sh"

    def run(cmd):
        return subprocess.run(
            ["bash", str(guard)], input=json.dumps({"tool_input": {"command": cmd}}),
            capture_output=True, text=True, env={**os.environ, "GUARD_ONLY_SSH": "1"},
        ).returncode

    assert run('ssh vps "cd /opt/apps/x && docker compose down -v"') == 2
    assert run("cat ~/.ssh/shop_deploy") == 2
    assert run("docker compose down -v") == 0  # local development database stays free to reset


def test_backend_only_deploy_has_no_frontend(tmp_path):
    target = tmp_path / "Api"
    assemble_project("Mijn Shop", "backend", BACKEND, [], target, assistants=["antigravity"], features=HOBBY)
    compose = (target / "deploy" / "compose.yml").read_text()
    assert "frontend:" not in compose and "PathPrefix" not in compose
    workflow = (target / ".github" / "workflows" / "deploy.yml").read_text()
    assert "component: [backend]" in workflow and "FRONTEND_IMAGE" not in workflow
    assert not (target / ".claude").exists()
    assert "deploy/SERVER.md" in (target / ".agents" / "rules" / "project-context.md").read_text()


def test_feature_can_be_added_later(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Mijn Shop", "fullstack", FULLSTACK, [], target, assistants=["claude"])
    context = build_context("Mijn Shop", "fullstack", FULLSTACK, ["claude"], features=HOBBY)
    assert copy_skill("hobbyserver-deploy", target, context)
    render_feature(target, context, "hobbyserver")
    assert add_hobbyserver_guard(target)

    assert (target / "deploy" / "compose.yml").is_file()
    assert (target / ".claude" / "hooks" / "hobbyserver-guard.sh").is_file()
    settings = json.loads((target / ".claude" / "settings.json").read_text())
    bash_hooks = next(i for i in settings["hooks"]["PreToolUse"] if i["matcher"] == "Bash")["hooks"]
    assert sum("hobbyserver-guard" in h["command"] for h in bash_hooks) == 1
    add_hobbyserver_guard(target)  # idempotent
    bash_hooks = next(i for i in json.loads((target / ".claude" / "settings.json").read_text())["hooks"]["PreToolUse"] if i["matcher"] == "Bash")["hooks"]
    assert sum("hobbyserver-guard" in h["command"] for h in bash_hooks) == 1
    # Only feature files were rendered: the rest of the project is untouched
    assert not (target / "deploy" / "SERVER.md").read_text().startswith("{")
