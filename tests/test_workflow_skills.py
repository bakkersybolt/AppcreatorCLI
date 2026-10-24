"""Tests for the sprint workflow (sprint-plan, open-vragen) and the project context around it."""

import re

import pytest

from appcreator.core.generator import assemble_project
from appcreator.core.manifest import load_manifest
from appcreator.core.ports import ProjectPorts

FULLSTACK = {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": []}
BACKEND = {"backend": "fastapi", "database": "none", "entiteiten": []}

# Words that only belong to the app these skills were taken from
DD_TERMEN = re.compile(r"dwaze|druiven|wijn|avond|evening|kok\b|bordeaux|hobbyserver|mdh_postgres|V0\b", re.I)


def _tekst(target):
    return "\n".join(
        p.read_text(encoding="utf-8")
        for p in target.rglob("*")
        if p.is_file() and p.suffix in {".md", ".py", ".ts", ".vue", ".json", ".yml", ".sh"} and "node_modules" not in p.parts
    )


@pytest.mark.parametrize("assistants", [["claude"], ["antigravity"], ["antigravity", "claude"]])
@pytest.mark.parametrize("category, stack", [("fullstack", FULLSTACK), ("backend", BACKEND)])
def test_no_source_app_terms_leak_into_generated_projects(tmp_path, category, stack, assistants):
    target = tmp_path / "Schoon"
    assemble_project("Schoon", category, stack, [], target, assistants=assistants)
    for regel in _tekst(target).splitlines():
        assert not DD_TERMEN.search(regel), regel


def test_sprint_workflow_skills_are_installed_for_backends_only(tmp_path):
    web = tmp_path / "Web"
    assemble_project("Web", "fullstack", FULLSTACK, [], web, assistants=["claude"])
    skills = web / ".claude" / "skills"
    for naam in ["sprint-plan", "open-vragen"]:
        assert (skills / naam / "SKILL.md").is_file()
        assert naam in load_manifest(web)["skills"]
    for bestand in ["bouwplan-template.md", "verslag-fase-template.md", "verslag-sprint-template.md", "check_ownership.py"]:
        assert (skills / "sprint-plan" / bestand).is_file()

    cli = tmp_path / "Cli"
    assemble_project("Cli", "cli", {"cli": "python-typer"}, [], cli, assistants=["claude"])
    assert not (cli / ".claude" / "skills" / "sprint-plan").exists()


def test_sprint_plan_uses_the_project_ports_and_names(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Demo Shop", "fullstack", FULLSTACK, [], target, assistants=["claude"], ports=ProjectPorts.for_slot(2))
    skill = (target / ".claude" / "skills" / "sprint-plan" / "SKILL.md").read_text()
    bouwplan = (target / ".claude" / "skills" / "sprint-plan" / "bouwplan-template.md").read_text()

    assert "track A 8201, B 8202" in skill
    assert "demo_shop_<track>_test" in skill
    assert ".claude/skills/sprint-plan/check_ownership.py" in skill
    assert "`AskUserQuestion`" in skill
    assert "Postgres **5434**, backend **8200**, frontend **5300**" in bouwplan
    assert "docker exec demo-shop-postgres createdb" in bouwplan
    assert ".docs/ontwerp/02-gebruikers-en-stromen.md" in bouwplan


def test_sprint_plan_for_antigravity_backend_has_no_claude_tools_or_frontend(tmp_path):
    target = tmp_path / "Api"
    assemble_project("Api", "backend", BACKEND, [], target, assistants=["antigravity"])
    skill = (target / ".agents" / "skills" / "sprint-plan" / "SKILL.md").read_text()
    bouwplan = (target / ".agents" / "skills" / "sprint-plan" / "bouwplan-template.md").read_text()
    for term in ["AskUserQuestion", "SendMessage", "isolation", ".claude/", "npm run", "frontend/"]:
        assert term not in skill, term
        assert term not in bouwplan, term
    assert ".agents/skills/sprint-plan/check_ownership.py" in skill


def test_project_context_describes_where_everything_lives(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Web", "fullstack", FULLSTACK, [], target, assistants=["claude"])
    context = (target / "CLAUDE.md").read_text()
    for kop in ["## Waar staat wat", "## Taalconventie", "## Werken in sprints", "## Parallelle sessies", "## Leerdoel"]:
        assert kop in context
    for pad in [".docs/ontwerp/", ".docs/sprints/", ".docs/open-vragen/", ".todos/", "docs/", "frontend/src/content/help/"]:
        assert f"`{pad}`" in context

    cli = tmp_path / "Cli"
    assemble_project("Cli", "cli", {"cli": "python-typer"}, [], cli, assistants=["claude"])
    cli_context = (cli / "CLAUDE.md").read_text()
    assert ".docs/sprints" not in cli_context and "## Werken in sprints" not in cli_context
    assert "## Leerdoel" in cli_context
