"""Generated Python code (FastAPI backend, Typer CLI) must pass ruff check + ruff format --check.

The generated projects ship their own strict ruff config (backend/pyproject.toml and the CLI's
pyproject.toml); this test runs ruff with exactly that config over every Python file the
backend/CLI templates produce, across the database x entities matrix.
"""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from appcreator.core.generator import assemble_project


def _ruff_cmd() -> list[str] | None:
    exe = shutil.which("ruff")
    if exe:
        return [exe]
    probe = subprocess.run([sys.executable, "-m", "ruff", "--version"], capture_output=True)
    if probe.returncode == 0:
        return [sys.executable, "-m", "ruff"]
    return None


RUFF = _ruff_cmd()

pytestmark = pytest.mark.skipif(RUFF is None, reason="ruff is not installed")


def _backend_cases():
    for category in ("fullstack", "backend"):
        for database in ("postgres", "sqlite", "none"):
            for entiteiten in ([], ["Product", "Order"]):
                stack = {"backend": "fastapi", "database": database, "entiteiten": entiteiten}
                if category == "fullstack":
                    stack["frontend"] = "vue3"
                case_id = f"{category}-{database}-{'entities' if entiteiten else 'empty'}"
                yield pytest.param("Mijn Tool", category, stack, case_id, id=case_id)
    # Long names push name-dependent lines (DB URL, decorators, imports) towards the line limit.
    stack = {
        "backend": "fastapi",
        "database": "postgres",
        "entiteiten": ["Klantafspraakherinnering", "Order"],
    }
    yield pytest.param("Een Behoorlijk Lange Applicatienaam Voor Testen", "backend", stack, "long", id="long-names")


def _lint(project_dir: Path, paths: list[str]):
    for args in (["check", "--no-cache"], ["format", "--check", "--diff", "--no-cache"]):
        result = subprocess.run(
            [*RUFF, *args, *paths],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"ruff {args[0]} failed in {project_dir}:\n{result.stdout}{result.stderr}"


def _compile_all(paths: list[Path]):
    assert paths, "expected generated Python files"
    for path in paths:
        py_compile.compile(str(path), doraise=True)


@pytest.fixture(autouse=True)
def _isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("APPCREATOR_HOME", str(tmp_path / "home"))


@pytest.mark.parametrize("app_naam,category,stack,case_id", list(_backend_cases()))
def test_backend_python_is_ruff_clean(tmp_path, app_naam, category, stack, case_id):
    target = tmp_path / case_id
    assemble_project(app_naam, category, stack, [], target, assistants=["claude"])
    backend = target / "backend"
    assert (backend / "pyproject.toml").is_file()
    _compile_all(list(backend.rglob("*.py")))
    _lint(backend, ["."])


def test_cli_python_is_ruff_clean(tmp_path):
    target = tmp_path / "cli"
    assemble_project("Mijn Tool", "cli", {"cli": "python-typer"}, [], target, assistants=["claude"])
    # Only the code from the python-typer template (src/, tests/); tooling such as
    # .claude/hooks comes from the shared common/ layer.
    _compile_all([*(target / "src").rglob("*.py"), *(target / "tests").rglob("*.py")])
    _lint(target, ["src", "tests"])

