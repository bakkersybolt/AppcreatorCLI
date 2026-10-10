"""Integration tests for AppCreator project generation."""

import json
import shutil
import tempfile
from pathlib import Path
import pytest

from appcreator.core.generator import assemble_project
from appcreator.core.manifest import load_manifest, add_skill_to_manifest


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp(prefix="appcreator_test_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def test_generate_fullstack_project(tmp_dir):
    app_naam = "MijnFullstackApp"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="fullstack",
        stack={
            "backend": "fastapi",
            "frontend": "vue3",
            "database": "postgres",
            "kern_domein": "Product",
        },
        skills=["brainstorm-architect", "test-engineer"],
        target_dir=target,
    )

    # Verifieer mappen en bestanden
    assert (target / "backend").is_dir()
    assert (target / "frontend").is_dir()
    assert (target / "docker-compose.yml").is_file()
    assert (target / ".gitignore").is_file()
    assert (target / "README.md").is_file()
    assert (target / "dev.sh").is_file()
    assert (target / ".appcreator.json").is_file()

    # Verifieer dev.sh opstartscript
    dev_sh_content = (target / "dev.sh").read_text()
    assert "uvicorn" in dev_sh_content
    assert "npm run dev" in dev_sh_content
    assert "postgres" in dev_sh_content

    # Verifieer backend inhoud
    backend_main = (target / "backend" / "app" / "main.py").read_text()
    assert len(backend_main) > 100
    assert "FastAPI" in backend_main
    assert "CORSMiddleware" in backend_main

    # Verifieer frontend inhoud
    assert (target / "frontend" / "package.json").is_file()
    assert (target / "frontend" / "tailwind.config.js").is_file()
    assert (target / "frontend" / "postcss.config.js").is_file()
    assert (target / "frontend" / "src" / "views" / "HomeView.vue").is_file()
    assert (target / "frontend" / "src" / "services" / "api.ts").is_file()

    # Verifieer .agents structuur
    assert (target / ".agents" / "rules" / "project-context.md").is_file()
    assert (target / ".agents" / "rules" / "backend-rules.md").is_file()
    assert (target / ".agents" / "rules" / "frontend-rules.md").is_file()
    assert (target / ".agents" / "skills" / "init-project" / "SKILL.md").is_file()
    assert (target / ".agents" / "skills" / "brainstorm-architect" / "SKILL.md").is_file()
    assert (target / ".agents" / "skills" / "python-fastapi" / "SKILL.md").is_file()
    assert (target / ".agents" / "skills" / "vue-shadcn" / "SKILL.md").is_file()

    # Verifieer manifest inhoud
    manifest = load_manifest(target)
    assert manifest is not None
    assert manifest["app_naam"] == app_naam
    assert manifest["category"] == "fullstack"
    assert "brainstorm-architect" in manifest["skills"]


def test_generate_backend_only_project(tmp_dir):
    app_naam = "MijnApi"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="backend",
        stack={
            "backend": "fastapi",
            "database": "sqlite",
            "kern_domein": "Sensor",
        },
        skills=["database-architect"],
        target_dir=target,
    )

    assert (target / "backend").is_dir()
    assert not (target / "frontend").exists()
    assert (target / ".agents" / "rules" / "backend-rules.md").is_file()
    assert not (target / ".agents" / "rules" / "frontend-rules.md").exists()
    assert (target / ".agents" / "skills" / "database-architect" / "SKILL.md").is_file()


def test_generate_embedded_project(tmp_dir):
    app_naam = "SmartSensorESP"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="embedded",
        stack={
            "hardware": "esp32",
        },
        skills=["code-reviewer"],
        target_dir=target,
    )

    assert (target / "platformio.ini").is_file()
    assert (target / "src" / "main.cpp").is_file()
    main_cpp = (target / "src" / "main.cpp").read_text()
    assert "SmartSensorESP" in main_cpp

    assert (target / ".agents" / "rules" / "esp32-rules.md").is_file()
    assert (target / ".agents" / "skills" / "esp32-development" / "SKILL.md").is_file()


def test_generate_cli_project(tmp_dir):
    app_naam = "DataSyncTool"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="cli",
        stack={
            "cli": "python-typer",
        },
        skills=["test-engineer"],
        target_dir=target,
    )

    assert (target / "pyproject.toml").is_file()
    assert (target / "src" / "datasynctool" / "main.py").is_file()
    assert (target / "tests" / "test_cli.py").is_file()
    assert (target / ".agents" / "rules" / "cli-rules.md").is_file()


def test_add_skill_manifest_flow(tmp_dir):
    app_naam = "TestProject"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="backend",
        stack={"backend": "fastapi"},
        skills=[],
        target_dir=target,
    )

    manifest_before = load_manifest(target)
    assert "docker-devops" not in manifest_before["skills"]

    # Voeg skill toe
    success = add_skill_to_manifest(target, "docker-devops")
    assert success is True

    manifest_after = load_manifest(target)
    assert "docker-devops" in manifest_after["skills"]


def test_generate_backend_without_entity(tmp_dir):
    app_naam = "CleanBackend"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="backend",
        stack={
            "backend": "fastapi",
            "database": "sqlite",
            "kern_domein": None,
        },
        skills=[],
        target_dir=target,
    )

    # Verifieer dat router.py geen foutieve imports of routers bevat
    router_code = (target / "backend" / "app" / "api" / "v1" / "router.py").read_text()
    assert "health" in router_code
    assert "include_router(health.router" in router_code
    assert "None" not in router_code

    # Verifieer dat er geen none.py of lege domein bestanden zijn aangemaakt
    endpoints_files = list((target / "backend" / "app" / "api" / "v1" / "endpoints").glob("*.py"))
    endpoint_names = [f.name for f in endpoints_files]
    assert "health.py" in endpoint_names
    assert len(endpoint_names) == 1

    # Verifieer dat models en schemas mappen __init__.py hebben
    assert (target / "backend" / "app" / "models" / "__init__.py").is_file()
    assert (target / "backend" / "app" / "schemas" / "__init__.py").is_file()


def test_parse_entity_names():
    from appcreator.main import parse_entity_names

    assert parse_entity_names("custom: item, user, todo") == ["Item", "User", "Todo"]
    assert parse_entity_names("Item, User, Todo") == ["Item", "User", "Todo"]
    assert parse_entity_names("customer; order; ticket") == ["Customer", "Order", "Ticket"]
    assert parse_entity_names("user_profile, order_item") == ["UserProfile", "OrderItem"]
    assert parse_entity_names("") == []


def test_generate_backend_with_multiple_entities(tmp_dir):
    app_naam = "MultiEntityBackend"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="backend",
        stack={
            "backend": "fastapi",
            "database": "postgres",
            "entiteiten": ["Item", "User", "Todo"],
        },
        skills=[],
        target_dir=target,
    )

    # Verifieer individuele models
    assert (target / "backend" / "app" / "models" / "item.py").is_file()
    assert (target / "backend" / "app" / "models" / "user.py").is_file()
    assert (target / "backend" / "app" / "models" / "todo.py").is_file()

    # Verifieer individuele schemas
    assert (target / "backend" / "app" / "schemas" / "item.py").is_file()
    assert (target / "backend" / "app" / "schemas" / "user.py").is_file()
    assert (target / "backend" / "app" / "schemas" / "todo.py").is_file()

    # Verifieer endpoints
    assert (target / "backend" / "app" / "api" / "v1" / "endpoints" / "item.py").is_file()
    assert (target / "backend" / "app" / "api" / "v1" / "endpoints" / "user.py").is_file()
    assert (target / "backend" / "app" / "api" / "v1" / "endpoints" / "todo.py").is_file()

    # Verifieer models/__init__.py
    models_init = (target / "backend" / "app" / "models" / "__init__.py").read_text()
    assert "from app.models.item import Item" in models_init
    assert "from app.models.user import User" in models_init
    assert "from app.models.todo import Todo" in models_init

    # Verifieer router.py imports en routes
    router_code = (target / "backend" / "app" / "api" / "v1" / "router.py").read_text()
    assert "health, item, user, todo" in router_code
    assert 'api_router.include_router(item.router, prefix="/items", tags=["Items"])' in router_code
    assert 'api_router.include_router(user.router, prefix="/users", tags=["Users"])' in router_code
    assert 'api_router.include_router(todo.router, prefix="/todos", tags=["Todos"])' in router_code


