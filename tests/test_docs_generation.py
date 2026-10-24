"""The generated docs/ pass the same checks as backend/tests/test_docs.py in the project itself."""

import importlib.util
import re
import sys
import types

import pytest

from appcreator.core.generator import TEMPLATES_DIR, assemble_project

STACKS = {
    "fullstack-postgres": ("fullstack", {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": []}),
    "backend-sqlite": ("backend", {"backend": "fastapi", "database": "sqlite", "entiteiten": []}),
    "backend-none": ("backend", {"backend": "fastapi", "database": "none", "entiteiten": []}),
}


def _load_docs_checks(docs_dir):
    """Imports the project's test_docs.py with a stub for `app.core.config` and DOCS_DIR pointed at docs_dir."""
    stub = types.ModuleType("app.core.config")
    stub.Settings = type("Settings", (), {"model_fields": {}})
    sys.modules.setdefault("app", types.ModuleType("app"))
    sys.modules.setdefault("app.core", types.ModuleType("app.core"))
    sys.modules["app.core.config"] = stub
    spec = importlib.util.spec_from_file_location("project_test_docs", TEMPLATES_DIR / "backends/fastapi/backend/tests/test_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DOCS_DIR = docs_dir
    module.INDEX = docs_dir / "README.md"
    return module


@pytest.fixture(params=list(STACKS), ids=list(STACKS))
def project(request, tmp_path):
    category, stack = STACKS[request.param]
    target = tmp_path / "DocsApp"
    assemble_project("DocsApp", category, stack, [], target, assistants=["claude"])
    return target


def test_generated_docs_pass_the_project_checks(project):
    docs = project / "docs"
    checks = _load_docs_checks(docs)
    files = sorted(docs.rglob("*.md"))
    assert docs / "README.md" in files

    for path in files:
        tekst = path.read_text(encoding="utf-8")
        assert "{{" not in tekst and "{%" not in tekst, path
        woorden = checks.count_words(tekst)
        assert woorden <= checks.MAX_WORDS, f"{path.name}: {woorden} woorden"
        checks.test_doc_links_work(path)
        if path != docs / "README.md":
            checks.test_doc_is_in_index(path)


def test_every_generated_setting_is_documented(project):
    config = (project / "backend" / "app" / "core" / "config.py").read_text()
    velden = re.findall(r"^    ([A-Z][A-Z0-9_]+)\s*:", config, re.M)
    assert {"APP_NAME", "DATABASE_URL", "CORS_ORIGINS"} <= set(velden)
    configuratie = (project / "docs" / "configuratie.md").read_text()
    assert [v for v in velden if f"`{v}`" not in configuratie] == []


def test_docs_test_and_skill_are_generated(project):
    assert (project / "backend" / "tests" / "test_docs.py").is_file()
    skill = project / ".claude" / "skills" / "documentatie"
    assert (skill / "SKILL.md").is_file() and (skill / "docs-onderwerp-template.md").is_file()
    has_frontend = (project / "frontend").is_dir()
    assert (skill / "help-artikel-template.md").is_file() == has_frontend
    assert (project / "docs" / "onderdelen" / "hulp.md").is_file() == has_frontend
    tekst = (skill / "SKILL.md").read_text()
    assert ("frontend/src/content/help" in tekst) == has_frontend


def test_no_docs_for_cli_and_embedded(tmp_path):
    for category, stack in [("cli", {"cli": "python-typer"}), ("embedded", {"hardware": "esp32"})]:
        target = tmp_path / category
        assemble_project(category, category, stack, [], target, assistants=["claude"])
        assert not (target / "docs").exists()
        assert not (target / ".claude" / "skills" / "documentatie").exists()
