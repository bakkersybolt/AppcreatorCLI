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


def test_cli_project_name_with_space_gives_valid_package(tmp_dir):
    app_naam = "Mijn App"
    target = tmp_dir / app_naam

    assemble_project(
        app_naam=app_naam,
        category="cli",
        stack={"cli": "python-typer"},
        skills=[],
        target_dir=target,
    )

    assert (target / "src" / "mijn_app" / "main.py").is_file()
    assert not (target / "src" / "mijn-app").exists()

    pyproject = (target / "pyproject.toml").read_text()
    assert 'name = "mijn-app"' in pyproject
    assert 'mijn-app = "mijn_app.main:app"' in pyproject
    assert "pytest" in pyproject

    test_code = (target / "tests" / "test_cli.py").read_text()
    assert "from mijn_app.main import app" in test_code


@pytest.mark.parametrize(
    "category, stack",
    [
        ("fullstack", {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": ["Item", "User"]}),
        ("backend", {"backend": "fastapi", "database": "sqlite", "entiteiten": ["Sensor"]}),
        ("backend", {"backend": "fastapi", "database": "none", "entiteiten": []}),
        ("embedded", {"hardware": "esp32"}),
        ("cli", {"cli": "python-typer"}),
    ],
)
def test_generated_python_compiles_and_has_no_template_leftovers(tmp_dir, category, stack):
    target = tmp_dir / "Mijn Test App"

    assemble_project(
        app_naam="Mijn Test App",
        category=category,
        stack=stack,
        skills=["brainstorm-architect", "test-engineer", "code-reviewer", "database-architect", "docker-devops"],
        target_dir=target,
    )

    for py_file in target.rglob("*.py"):
        compile(py_file.read_text(encoding="utf-8"), str(py_file), "exec")

    assert not list(target.rglob("*.jinja"))
    assert "Mijn Test App" in (target / "README.md").read_text()


def test_frontend_files_rendered_with_slug(tmp_dir):
    target = tmp_dir / "Mijn Web_App"

    assemble_project(
        app_naam="Mijn Web_App",
        category="fullstack",
        stack={"backend": "fastapi", "frontend": "vue3", "database": "sqlite", "entiteiten": []},
        skills=[],
        target_dir=target,
    )

    package = json.loads((target / "frontend" / "package.json").read_text())
    assert package["name"] == "mijn-web-app-frontend"
    assert "vitest" in package["devDependencies"]
    assert (target / "frontend" / "eslint.config.ts").is_file()
    assert not (target / "frontend" / ".eslintrc.config.ts").exists()
    assert "Mijn Web_App" in (target / "frontend" / "README.md").read_text()
    assert "Mijn Web_App" in (target / "backend" / "app" / "__init__.py").read_text()


def test_root_env_with_postgres_port_only_for_postgres(tmp_dir):
    pg_target = tmp_dir / "PgApp"
    assemble_project(
        app_naam="PgApp",
        category="backend",
        stack={"backend": "fastapi", "database": "postgres", "entiteiten": []},
        skills=[],
        target_dir=pg_target,
    )
    assert "POSTGRES_PORT=5432" in (pg_target / ".env").read_text()
    assert "POSTGRES_PORT=5432" in (pg_target / ".env.example").read_text()
    assert "${POSTGRES_PORT:-5432}:5432" in (pg_target / "docker-compose.yml").read_text()
    assert "POSTGRES_PORT=" not in (pg_target / "backend" / ".env").read_text()

    sqlite_target = tmp_dir / "SqliteApp"
    assemble_project(
        app_naam="SqliteApp",
        category="backend",
        stack={"backend": "fastapi", "database": "sqlite", "entiteiten": []},
        skills=[],
        target_dir=sqlite_target,
    )
    assert not (sqlite_target / ".env").exists()


def test_dev_runner_reads_postgres_port(tmp_dir, monkeypatch):
    from appcreator.core.dev_runner import _get_postgres_port

    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    assert _get_postgres_port(tmp_dir) == "5432"

    (tmp_dir / ".env").write_text("# commentaar\nPOSTGRES_PORT=5433\n")
    assert _get_postgres_port(tmp_dir) == "5433"

    monkeypatch.setenv("POSTGRES_PORT", "6000")
    assert _get_postgres_port(tmp_dir) == "6000"


def test_non_jinja_file_is_copied_unchanged(tmp_dir):
    from appcreator.core.generator import render_file

    src = tmp_dir / "Component.vue"
    src.write_text("<template>{{ teller }}</template>\n")
    dst = tmp_dir / "out" / "Component.vue"

    render_file(src, dst, {})

    assert dst.read_text() == "<template>{{ teller }}</template>\n"


def test_unknown_template_variable_raises(tmp_dir):
    import jinja2
    from appcreator.core.generator import render_file

    src = tmp_dir / "kapot.txt.jinja"
    src.write_text("Hallo {{ bestaat_niet }}\n")

    with pytest.raises(jinja2.UndefinedError):
        render_file(src, tmp_dir / "kapot.txt", {"app_naam": "X"})


def test_validate_app_name():
    from appcreator.core.naming import make_package_name, make_slug, validate_app_name

    for geldig in ["MijnApp", "Mijn App", "mijn-app_2"]:
        assert validate_app_name(geldig) is None
    for ongeldig in ["", "   ", "../x", "a/b", "1app", "app!", ".."]:
        assert validate_app_name(ongeldig) is not None

    assert make_slug("Mijn Web_App") == "mijn-web-app"
    assert make_package_name("Mijn Web_App") == "mijn_web_app"


def test_python_setup_installs_pyproject_project_editable(tmp_dir, monkeypatch):
    from appcreator.core import installer

    (tmp_dir / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    calls = []
    monkeypatch.setattr(installer.subprocess, "run", lambda cmd, **kwargs: calls.append(cmd))

    assert installer.setup_python_environment(target_dir=tmp_dir, requirements_path=None) is True

    install_calls = [c for c in calls if "install" in c]
    assert len(install_calls) == 1
    assert install_calls[0][install_calls[0].index("-e") + 1] == ".[dev]"

