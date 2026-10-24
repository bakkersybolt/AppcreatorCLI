"""Tests for per-project port allocation, resolution and their use in generated projects."""

import json
import re
import socket
import subprocess
from pathlib import Path

import pytest

from appcreator.core.generator import assemble_project
from appcreator.core.manifest import load_manifest
from appcreator.core.ports import (
    LEGACY_PORTS,
    ProjectPorts,
    allocate_ports,
    load_registry,
    replace_port_numbers,
    resolve_ports,
)

FULLSTACK = {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": []}


def test_slots_derive_a_full_port_block():
    ports = ProjectPorts.for_slot(2)
    assert (ports.backend, ports.frontend, ports.postgres) == (8200, 5300, 5434)
    assert (ports.agent_start, ports.agent_end) == (8201, 8209)
    assert (ports.e2e_backend, ports.e2e_frontend) == (8210, 5310)


def test_allocate_skips_registered_slots_and_is_idempotent(tmp_path):
    a = allocate_ports(tmp_path / "a", "a")
    (tmp_path / "a").mkdir()
    b = allocate_ports(tmp_path / "b", "b")
    (tmp_path / "b").mkdir()

    assert a.slot != b.slot and 0 not in (a.slot, b.slot)
    assert allocate_ports(tmp_path / "a", "a") == a
    assert set(load_registry()["projects"]) == {str((tmp_path / "a").resolve()), str((tmp_path / "b").resolve())}


def test_allocate_prunes_projects_that_no_longer_exist(tmp_path):
    weg = allocate_ports(tmp_path / "weg", "weg")  # folder never created
    nieuw = allocate_ports(tmp_path / "nieuw", "nieuw")
    assert nieuw.slot == weg.slot
    assert str((tmp_path / "weg").resolve()) not in load_registry()["projects"]


def test_allocate_skips_a_slot_whose_port_is_in_use(tmp_path):
    eerste_vrije = allocate_ports(tmp_path / "probe", "probe")
    (tmp_path / "probe").rmdir() if (tmp_path / "probe").exists() else None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bezet:
        bezet.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            bezet.bind(("127.0.0.1", eerste_vrije.backend))
        except OSError:
            pytest.skip("poort al in gebruik op deze machine")
        bezet.listen(1)
        ports = allocate_ports(tmp_path / "app", "app")
    assert ports.slot != eerste_vrije.slot


def test_resolve_order_env_then_dotenv_then_manifest_then_legacy(tmp_path, monkeypatch):
    assert resolve_ports(tmp_path)[0] == LEGACY_PORTS

    (tmp_path / ".appcreator.json").write_text(json.dumps({"ports": ProjectPorts.for_slot(3).as_manifest()}))
    ports, bronnen = resolve_ports(tmp_path)
    assert ports.backend == 8300 and bronnen["backend"] == "manifest"

    (tmp_path / ".env").write_text("# poorten\nBACKEND_PORT=8400\n")
    ports, bronnen = resolve_ports(tmp_path)
    assert ports.backend == 8400 and bronnen["backend"] == ".env"
    assert ports.frontend == 5400 and bronnen["frontend"] == "manifest"

    monkeypatch.setenv("BACKEND_PORT", "9000")
    assert resolve_ports(tmp_path)[0].backend == 9000


def test_legacy_project_without_ports_keeps_postgres_port_from_env(tmp_path):
    (tmp_path / ".env").write_text("POSTGRES_PORT=5433\n")
    ports, _ = resolve_ports(tmp_path)
    assert (ports.backend, ports.frontend, ports.postgres) == (8000, 5173, 5433)


def test_generated_project_stores_its_ports(tmp_path):
    target = tmp_path / "PoortApp"
    ports = ProjectPorts.for_slot(4)
    assemble_project("PoortApp", "fullstack", FULLSTACK, [], target, assistants=["claude"], ports=ports)

    env = (target / ".env").read_text()
    for regel in ["BACKEND_PORT=8400", "FRONTEND_PORT=5500", "POSTGRES_PORT=5436", "AGENT_PORT_START=8401", "E2E_BACKEND_PORT=8410"]:
        assert regel in env
    assert (target / ".env.example").read_text() == env
    assert load_manifest(target)["ports"] == ports.as_manifest()

    compose = (target / "docker-compose.yml").read_text()
    assert "name: poortapp" in compose
    assert "${BACKEND_PORT:-8400}:8000" in compose
    assert "${FRONTEND_PORT:-5500}:${FRONTEND_PORT:-5500}" in compose
    assert "${POSTGRES_PORT:-5436}:5432" in compose
    assert "VITE_PROXY_TARGET=http://backend:8000" in compose

    vite = (target / "frontend" / "vite.config.ts").read_text()
    assert "Number(env.FRONTEND_PORT) || 5500" in vite and "strictPort: true" in vite
    assert "env.BACKEND_PORT || 8400" in vite
    assert "'/api/v1'" in (target / "frontend" / "src" / "services" / "api.ts").read_text()
    assert "${BACKEND_PORT:-8400}/openapi.json" in (target / "frontend" / "package.json").read_text()
    assert "localhost:5436/poortapp_db" in (target / "backend" / ".env").read_text()
    assert '"http://localhost:5500"' in (target / "backend" / "app" / "core" / "config.py").read_text()
    assert "settings.CORS_ORIGINS" in (target / "backend" / "app" / "main.py").read_text()
    assert "| Backend (FastAPI) | 8400 |" in (target / "CLAUDE.md").read_text()


def test_no_hardcoded_default_ports_in_generated_project(tmp_path):
    target = tmp_path / "Vrij"
    assemble_project("Vrij", "fullstack", FULLSTACK, [], target, assistants=["antigravity", "claude"], ports=ProjectPorts.for_slot(3))

    toegestaan = re.compile(r"@postgres:5432|:5432'|backend:8000|}:8000'|--port\", \"8000\"|EXPOSE 8000")
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix in {".png", ".ico", ".svg"}:
            continue
        for nr, regel in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            schoon = toegestaan.sub("", regel)
            assert not re.search(r"(?<!\d)(8000|5173|5432)(?!\d)", schoon), f"{path.relative_to(target)}:{nr}: {regel}"


def test_backend_only_project_has_no_frontend_ports_in_compose(tmp_path):
    target = tmp_path / "Api"
    assemble_project("Api", "backend", {"backend": "fastapi", "database": "sqlite", "entiteiten": []}, [], target)
    compose = (target / "docker-compose.yml").read_text()
    assert "frontend" not in compose and "postgres" not in compose
    env = (target / ".env").read_text()
    assert "BACKEND_PORT=" in env and "POSTGRES_PORT" not in env


def test_cli_and_embedded_projects_get_no_ports(tmp_path):
    for category, stack in [("cli", {"cli": "python-typer"}), ("embedded", {"hardware": "esp32"})]:
        target = tmp_path / category
        assemble_project(category, category, stack, [], target)
        assert not (target / ".env").exists()
        assert not (target / "docker-compose.yml").exists()
        assert not (target / "dev.sh").exists()
        assert load_manifest(target)["ports"] is None


def test_dev_script_reads_ports_from_env(tmp_path):
    target = tmp_path / "Sh"
    assemble_project("Sh", "fullstack", FULLSTACK, [], target, ports=ProjectPorts.for_slot(2))
    dev_sh = (target / "dev.sh").read_text()
    assert ". ./.env" in dev_sh
    assert 'BACKEND_PORT="${BACKEND_PORT:-8200}"' in dev_sh
    assert '--port "$BACKEND_PORT"' in dev_sh
    subprocess.run(["bash", "-n", str(target / "dev.sh")], check=True)


def test_dev_runner_starts_services_on_project_ports(tmp_path, monkeypatch):
    from appcreator.core import dev_runner

    target = tmp_path / "Run"
    assemble_project("Run", "fullstack", {**FULLSTACK, "database": "sqlite"}, [], target, ports=ProjectPorts.for_slot(5))

    gestart = []

    class FakeProc:
        stdout = None

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

    def fake_popen(cmd, cwd=None, env=None, **kwargs):
        gestart.append((cmd, Path(cwd).name, env or {}))
        return FakeProc()

    monkeypatch.setattr(dev_runner.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(dev_runner.threading, "Thread", lambda *a, **k: type("T", (), {"start": lambda self: None})())
    monkeypatch.setattr(dev_runner, "port_is_free", lambda port: True)
    dev_runner.run_dev_server(target)

    backend_cmd, _, _ = next(g for g in gestart if g[1] == "backend")
    assert backend_cmd[-2:] == ["--port", "8500"]
    _, _, frontend_env = next(g for g in gestart if g[1] == "frontend")
    assert frontend_env["FRONTEND_PORT"] == "5600"
    assert frontend_env["VITE_PROXY_TARGET"] == "http://localhost:8500"


def test_dev_runner_stops_when_port_is_taken(tmp_path, monkeypatch, capsys):
    from appcreator.core import dev_runner

    target = tmp_path / "Bezet"
    assemble_project("Bezet", "backend", {"backend": "fastapi", "database": "sqlite", "entiteiten": []}, [], target)
    monkeypatch.setattr(dev_runner, "port_is_free", lambda port: False)
    monkeypatch.setattr(dev_runner.subprocess, "Popen", lambda *a, **k: pytest.fail("mag niet starten"))
    dev_runner.run_dev_server(target)


def test_replace_port_numbers_swaps_derived_ports_only():
    old, new = ProjectPorts.for_slot(1), ProjectPorts.for_slot(2)
    tekst = "backend 8100, agent 8101-8109, e2e 8110/5210, frontend 5200, db 5433, versie 81000"
    assert replace_port_numbers(tekst, old, new) == "backend 8200, agent 8201-8209, e2e 8210/5310, frontend 5300, db 5434, versie 81000"


def test_reassign_rewrites_project_files(tmp_path):
    from appcreator.core.port_commands import reassign_ports

    target = tmp_path / "Verhuis"
    old = allocate_ports(target, "verhuis")
    assemble_project("Verhuis", "fullstack", FULLSTACK, [], target, assistants=["claude"], ports=old)

    new = reassign_ports(target)
    assert new.slot != old.slot
    assert f"BACKEND_PORT={new.backend}" in (target / ".env").read_text()
    assert f"localhost:{new.postgres}/" in (target / "backend" / ".env").read_text()
    assert f"| Backend (FastAPI) | {new.backend} |" in (target / "CLAUDE.md").read_text()
    assert str(old.backend) not in (target / "frontend" / "vite.config.ts").read_text()
    assert load_manifest(target)["ports"] == new.as_manifest()
    assert load_registry()["projects"][str(target.resolve())]["slot"] == new.slot


def test_adopt_records_existing_ports(tmp_path):
    from appcreator.core.port_commands import adopt_ports

    target = tmp_path / "Oud"
    target.mkdir()
    (target / ".appcreator.json").write_text(json.dumps({"app_naam": "Oud", "stack": {"database": "postgres"}}))
    (target / ".env").write_text("POSTGRES_PORT=5433\nBACKEND_PORT=8100\nFRONTEND_PORT=5180\n")

    adopted = adopt_ports(target)
    assert (adopted.slot, adopted.backend, adopted.frontend) == (1, 8100, 5180)
    assert load_manifest(target)["ports"]["frontend"] == 5180
    assert load_registry()["projects"][str(target.resolve())]["slot"] == 1
    assert allocate_ports(tmp_path / "Nieuw", "nieuw").slot != 1
