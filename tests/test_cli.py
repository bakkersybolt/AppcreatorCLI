"""CLI command tests for AppCreator."""

import tempfile
from pathlib import Path
from typer.testing import CliRunner

from appcreator.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "appcreator" in result.output.lower()
    assert "dev" in result.output
    assert "start" in result.output


def test_cli_dev_help():
    result = runner.invoke(app, ["dev", "--help"])
    assert result.exit_code == 0
    assert "ontwikkelingsservices" in result.output


def test_cli_dev_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["dev", "--dir", tmpdir])
        assert result.exit_code == 0
        assert "Geen backend of frontend aangetroffen" in result.output


def test_cli_create_rejects_invalid_name():
    result = runner.invoke(app, ["create", "../kwaadaardig"])
    assert result.exit_code == 1
    assert "Ongeldige applicatienaam" in result.output


def _maak_project(tmp_path, monkeypatch, category, stack, assistants=None):
    from appcreator.core.generator import assemble_project

    assemble_project("AddSkillApp", category, stack, [], tmp_path, assistants=assistants)
    monkeypatch.chdir(tmp_path)


def test_add_skill_writes_to_assistants_from_manifest(tmp_path, monkeypatch):
    _maak_project(tmp_path, monkeypatch, "backend", {"backend": "fastapi", "database": "sqlite"}, ["claude", "antigravity"])

    result = runner.invoke(app, ["add-skill", "docker-devops"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "skills" / "docker-devops" / "SKILL.md").is_file()
    assert (tmp_path / ".agents" / "skills" / "docker-devops" / "SKILL.md").is_file()


def test_add_skill_with_manifest_without_assistants_defaults_to_antigravity(tmp_path, monkeypatch):
    import json

    _maak_project(tmp_path, monkeypatch, "backend", {"backend": "fastapi", "database": "sqlite"})
    manifest_path = tmp_path / ".appcreator.json"
    manifest = json.loads(manifest_path.read_text())
    del manifest["assistants"]
    manifest_path.write_text(json.dumps(manifest))

    result = runner.invoke(app, ["add-skill", "code-reviewer"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".agents" / "skills" / "code-reviewer" / "SKILL.md").is_file()
    assert not (tmp_path / ".claude").exists()


def test_add_skill_rejects_skill_that_does_not_fit(tmp_path, monkeypatch):
    _maak_project(tmp_path, monkeypatch, "embedded", {"hardware": "esp32"}, ["claude"])

    result = runner.invoke(app, ["add-skill", "vue-shadcn"])

    assert result.exit_code == 1
    assert "past niet bij dit projecttype" in result.output
    assert not (tmp_path / ".claude" / "skills" / "vue-shadcn").exists()


def test_list_shows_descriptions_for_templated_skills():
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "init-project" in result.output
    assert "Geen omschrijving" not in result.output


class _Antwoord:
    def __init__(self, waarde):
        self.waarde = waarde

    def ask(self):
        return self.waarde


def test_create_wizard_generates_claude_cli_project(tmp_path, monkeypatch):
    """Doorloopt de wizard met vaste antwoorden: CLI-project voor Claude Code, zonder installatie of git."""
    import appcreator.main as main_module

    aangeboden_skills = []

    def fake_select(message, choices, **kwargs):
        if "hoofdrichting" in message:
            return _Antwoord(next(c for c in choices if "CLI" in c))
        if "AI-assistent" in message:
            return _Antwoord(next(c.value for c in choices if "Claude" in c.title))
        raise AssertionError(f"Onverwachte vraag: {message}")

    def fake_checkbox(message, choices, **kwargs):
        aangeboden_skills.extend(c.value for c in choices)
        return _Antwoord([c.value for c in choices])

    def fake_confirm(message, **kwargs):
        return _Antwoord("genereren" in message)

    monkeypatch.setattr(main_module.questionary, "select", fake_select)
    monkeypatch.setattr(main_module.questionary, "checkbox", fake_checkbox)
    monkeypatch.setattr(main_module.questionary, "confirm", fake_confirm)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["create", "Mijn Tool"])

    assert result.exit_code == 0, result.output
    assert aangeboden_skills == ["test-engineer", "code-reviewer"]

    project = tmp_path / "Mijn Tool"
    assert (project / "CLAUDE.md").is_file()
    assert (project / ".claude" / "skills" / "test-engineer" / "SKILL.md").is_file()
    assert (project / ".claude" / "rules" / "cli-rules.md").is_file()
    assert not (project / ".agents").exists()
    assert not (project / ".git").exists()
    assert "Claude Code" in result.output
    assert "antigravity ." not in result.output

