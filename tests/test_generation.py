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


ALLE_OPTIONELE_SKILLS = ["brainstorm-architect", "test-engineer", "code-reviewer", "database-architect", "docker-devops"]
FULLSTACK = {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": ["Item", "User"]}


def _alle_tekst(target: Path) -> str:
    """Alle gegenereerde tekst buiten de meegeleverde naslag, voor controles op verboden termen."""
    delen = []
    for pad in target.rglob("*"):
        if pad.is_file() and pad.suffix in {".md", ".vue", ".json", ".py", ".sh", ".ts", ".cpp", ".toml", ".yml"}:
            delen.append(pad.read_text(encoding="utf-8"))
    return "\n".join(delen)


def _frontmatter(skill_file: Path) -> dict:
    regels = skill_file.read_text(encoding="utf-8").splitlines()
    assert regels[0] == "---", f"{skill_file} mist frontmatter"
    einde = regels.index("---", 1)
    velden = {}
    for regel in regels[1:einde]:
        sleutel, _, waarde = regel.partition(":")
        velden[sleutel.strip()] = waarde.strip().strip('"')
    return velden


def test_generate_for_claude_only(tmp_dir):
    target = tmp_dir / "ClaudeApp"
    assemble_project("ClaudeApp", "fullstack", FULLSTACK, ALLE_OPTIONELE_SKILLS, target, assistants=["claude"])

    assert (target / "CLAUDE.md").is_file()
    assert not (target / "CLAUDE.md").read_text().startswith("---")
    assert (target / ".claude" / "skills" / "init-project" / "SKILL.md").is_file()
    assert (target / ".claude" / "skills" / "python-fastapi" / "references" / "auth-jwt.md").is_file()
    assert not (target / ".agents").exists()

    backend_rule = (target / ".claude" / "rules" / "backend-rules.md").read_text()
    assert backend_rule.startswith('---\npaths:\n  - "backend/**/*"\n---\n')
    assert "trigger:" not in backend_rule

    tekst = _alle_tekst(target)
    for verboden in ["Antigravity", ".agents/", "/grill-me"]:
        assert verboden not in tekst, f"'{verboden}' hoort niet in een Claude-project"

    assert load_manifest(target)["assistants"] == ["claude"]


def test_generate_for_antigravity_only_is_default(tmp_dir):
    target = tmp_dir / "AntiApp"
    assemble_project("AntiApp", "fullstack", FULLSTACK, ALLE_OPTIONELE_SKILLS, target)

    assert not (target / "CLAUDE.md").exists()
    assert not (target / ".claude").exists()

    context = (target / ".agents" / "rules" / "project-context.md").read_text()
    assert context.startswith("---\ntrigger: always_on\n")
    frontend_rule = (target / ".agents" / "rules" / "frontend-rules.md").read_text()
    assert frontend_rule.startswith('---\ntrigger: glob\nglobs: "frontend/**/*"\n')

    brainstorm_skill = (target / ".agents" / "skills" / "brainstorm-architect" / "SKILL.md").read_text()
    assert "/grill-me" in brainstorm_skill
    assert "Claude" not in _alle_tekst(target)
    assert load_manifest(target)["assistants"] == ["antigravity"]


def test_generate_for_both_assistants(tmp_dir):
    target = tmp_dir / "BeideApp"
    assemble_project("BeideApp", "fullstack", FULLSTACK, ["brainstorm-architect"], target, assistants=["claude", "antigravity"])

    assert (target / "CLAUDE.md").is_file()
    assert (target / ".agents" / "rules" / "project-context.md").is_file()

    for skills_dir in [".agents/skills", ".claude/skills"]:
        brainstorm_skill = (target / skills_dir / "brainstorm-architect" / "SKILL.md").read_text()
        # Het doel moet in beide contextbestanden terechtkomen, anders lopen ze uiteen
        assert "`.agents/rules/project-context.md` en `CLAUDE.md`" in brainstorm_skill

    assert "/grill-me" in (target / ".agents" / "skills" / "brainstorm-architect" / "SKILL.md").read_text()
    assert "/grill-me" not in (target / ".claude" / "skills" / "brainstorm-architect" / "SKILL.md").read_text()
    assert load_manifest(target)["assistants"] == ["antigravity", "claude"]


@pytest.mark.parametrize(
    "category, stack, skills",
    [
        ("fullstack", FULLSTACK, ALLE_OPTIONELE_SKILLS),
        ("backend", {"backend": "fastapi", "database": "none", "entiteiten": []}, ["brainstorm-architect", "test-engineer", "code-reviewer", "docker-devops"]),
        ("embedded", {"hardware": "esp32"}, ["code-reviewer"]),
        ("cli", {"cli": "python-typer"}, ["test-engineer", "code-reviewer"]),
    ],
)
def test_generated_skills_are_wellformed(tmp_dir, category, stack, skills):
    import re

    target = tmp_dir / "SkillApp"
    assemble_project("SkillApp", category, stack, skills, target, assistants=["antigravity", "claude"])

    skill_files = list(target.glob(".agents/skills/*/SKILL.md")) + list(target.glob(".claude/skills/*/SKILL.md"))
    assert len(skill_files) >= 2 * (1 + len(skills))

    for skill_file in skill_files:
        velden = _frontmatter(skill_file)
        assert velden["name"] == skill_file.parent.name
        assert "Gebruik" in velden["description"], f"{skill_file}: description zegt niet wanneer de skill geldt"

        tekst = skill_file.read_text(encoding="utf-8")
        assert "{%" not in tekst and "{{" not in tekst
        for link in re.findall(r"\]\(([^)#]+)\)", tekst):
            if not link.startswith("http"):
                assert (skill_file.parent / link).is_file(), f"{skill_file}: dode link naar {link}"

    # Het manifest bevat alle geïnstalleerde skills, ook de stack-skills
    geinstalleerd = sorted(p.parent.name for p in target.glob(".claude/skills/*/SKILL.md"))
    assert sorted(load_manifest(target)["skills"]) == geinstalleerd


@pytest.mark.parametrize(
    "category, stack, verwacht_pad",
    [
        ("fullstack", FULLSTACK, ".todos/frontend/src/composables/"),
        ("backend", {"backend": "fastapi", "database": "none", "entiteiten": []}, ".todos/backend/app/api/v1/endpoints/"),
        ("embedded", {"hardware": "esp32"}, ".todos/src/"),
        ("cli", {"cli": "python-typer"}, ".todos/src/todoapp/"),
    ],
)
def test_todo_skill_is_always_installed(tmp_dir, category, stack, verwacht_pad):
    target = tmp_dir / "TodoApp"
    assemble_project("TodoApp", category, stack, [], target, assistants=["antigravity", "claude"])

    for skills_dir in [".agents/skills", ".claude/skills"]:
        skill = (target / skills_dir / "todo-beheer" / "SKILL.md").read_text()
        assert verwacht_pad in skill

    # De aanwijzing staat in de altijd geladen context, zodat de agent todo's ook ongevraagd vastlegt
    assert "todo-beheer" in (target / "CLAUDE.md").read_text()
    assert "todo-beheer" in (target / ".agents" / "rules" / "project-context.md").read_text()
    assert "todo-beheer" in load_manifest(target)["skills"]


def test_embedded_project_has_no_web_content_in_skills(tmp_dir):
    target = tmp_dir / "EspApp"
    assemble_project("EspApp", "embedded", {"hardware": "esp32"}, ["code-reviewer"], target, assistants=["claude"])

    skills_tekst = "\n".join(p.read_text() for p in (target / ".claude").rglob("*.md")) + (target / "CLAUDE.md").read_text()
    for web_term in ["Shadcn", "FastAPI", "frontend", "backend/"]:
        assert web_term not in skills_tekst, f"'{web_term}' hoort niet in een ESP32-project"
    assert "delay(" not in (target / "src" / "main.cpp").read_text().split("void loop()")[1]


def test_optional_skills_are_filtered_per_category():
    from appcreator.core.skills import optionele_skills_voor, skill_past_bij_project

    def namen(category, database=None):
        return [s["name"] for s in optionele_skills_voor(category, database)]

    assert namen("embedded") == ["code-reviewer"]
    assert namen("cli") == ["test-engineer", "code-reviewer"]
    assert "database-architect" in namen("fullstack", "postgres")
    assert "database-architect" not in namen("backend", "none")
    # De ontwerpsessie is geen keuze meer: web en backend krijgen hem altijd
    assert "brainstorm-architect" not in namen("fullstack", "postgres")
    assert skill_past_bij_project("brainstorm-architect", "backend", {"backend": "fastapi"})
    assert skill_past_bij_project("feature-builder", "fullstack", {"backend": "fastapi", "frontend": "vue3"})

    assert skill_past_bij_project("init-project", "embedded", {"hardware": "esp32"})
    assert skill_past_bij_project("esp32-development", "embedded", {"hardware": "esp32"})
    assert not skill_past_bij_project("vue-shadcn", "backend", {"backend": "fastapi"})
    assert not skill_past_bij_project("brainstorm-architect", "cli", {"cli": "python-typer"})


def test_templates_follow_their_own_rules(tmp_dir):
    target = tmp_dir / "RegelApp"
    assemble_project("RegelApp", "fullstack", FULLSTACK, [], target, assistants=["claude"])

    assert "any" not in (target / "frontend" / "src" / "views" / "HomeView.vue").read_text().split("</script>")[0].replace("company", "")
    assert (target / "frontend" / "src" / "lib" / "utils.ts").is_file()
    assert "lucide-vue-next" not in _alle_tekst(target)

    gitignore = (target / ".gitignore").read_text().splitlines()
    assert "lib/" not in gitignore
    assert "include/secrets.h" in gitignore


RONDES_FULLSTACK = [
    "## Ronde 1: Doel",
    "## Ronde 2: Gebruikers en stromen",
    "## Ronde 3: Datamodel",
    "## Ronde 4: API en toegang",
    "## Ronde 5: Schermen",
    "## Ronde 6: Navigatie en uitstraling",
    "## Ronde 7: Randvoorwaarden en scope",
    "## Ronde 8: Bouwvolgorde",
]


def test_design_session_is_always_installed_for_web_and_backend(tmp_dir):
    web = tmp_dir / "Web"
    assemble_project("Web", "fullstack", {"backend": "fastapi", "frontend": "vue3", "database": "postgres"}, [], web, assistants=["claude"])
    api = tmp_dir / "Api"
    assemble_project("Api", "backend", {"backend": "fastapi", "database": "sqlite"}, [], api, assistants=["claude"])

    for project in (web, api):
        skills = project / ".claude" / "skills"
        assert (skills / "brainstorm-architect" / "SKILL.md").is_file()
        assert (skills / "brainstorm-architect" / "references" / "ontwerp" / "README.md").is_file()
        assert (skills / "brainstorm-architect" / "references" / "sprints-overzicht.md").is_file()
        assert (skills / "feature-builder" / "SKILL.md").is_file()
        assert {"brainstorm-architect", "feature-builder"} <= set(load_manifest(project)["skills"])

    for category, stack in [("embedded", {"hardware": "esp32"}), ("cli", {"cli": "python-typer"})]:
        target = tmp_dir / category
        assemble_project(category, category, stack, [], target, assistants=["claude"])
        assert not (target / ".claude" / "skills" / "brainstorm-architect").exists()
        assert not (target / ".claude" / "skills" / "feature-builder").exists()


def test_brainstorm_rounds_start_with_goal_and_follow_the_stack(tmp_dir):
    web = tmp_dir / "Web"
    assemble_project("Web", "fullstack", {"backend": "fastapi", "frontend": "vue3", "database": "postgres"}, [], web, assistants=["claude"])
    skill = (web / ".claude" / "skills" / "brainstorm-architect" / "SKILL.md").read_text()

    posities = [skill.index(kop) for kop in RONDES_FULLSTACK]
    assert posities == sorted(posities)
    eerste_ronde = skill[posities[0]:posities[1]]
    for onderwerp in ["Het idee", "Het probleem", "Succes"]:
        assert onderwerp in eerste_ronde
    assert ".docs/ontwerp/" in skill and ".docs/sprints/overzicht.md" in skill and "/sprint-plan" in skill
    assert ".docs/ontwerp.md" not in skill and ".docs/bouwplan.md" not in skill

    ontwerp = web / ".claude" / "skills" / "brainstorm-architect" / "references" / "ontwerp"
    assert sorted(p.name for p in ontwerp.iterdir()) == [
        "01-doel.md", "02-gebruikers-en-stromen.md", "03-datamodel.md", "04-api-en-toegang.md",
        "05-schermen.md", "06-navigatie-en-uitstraling.md", "07-randvoorwaarden-en-scope.md", "README.md",
    ]
    index = (ontwerp / "README.md").read_text()
    assert "# Ontwerp: Web" in index
    assert "[05-schermen.md](05-schermen.md)" in index and "- [ ] 8. Bouwvolgorde" in index
    assert "# Schermen" in (ontwerp / "05-schermen.md").read_text()

    api = tmp_dir / "Api"
    assemble_project("Api", "backend", {"backend": "fastapi", "database": "sqlite"}, [], api, assistants=["claude"])
    api_skill = (api / ".claude" / "skills" / "brainstorm-architect" / "SKILL.md").read_text()
    assert "## Ronde 5: Randvoorwaarden en scope" in api_skill
    assert "## Ronde 6: Bouwvolgorde" in api_skill
    assert "Schermen" not in api_skill and "Navigatie" not in api_skill

    api_ontwerp = api / ".claude" / "skills" / "brainstorm-architect" / "references" / "ontwerp"
    assert sorted(p.name for p in api_ontwerp.iterdir()) == [
        "01-doel.md", "02-gebruikers-en-stromen.md", "03-datamodel.md", "04-api-en-toegang.md",
        "05-randvoorwaarden-en-scope.md", "README.md",
    ]
    api_index = (api_ontwerp / "README.md").read_text()
    assert "Schermen" not in api_index and "Navigatie" not in api_index
    assert "- [ ] 6. Bouwvolgorde" in api_index and "- [ ] 7." not in api_index
    assert "Schermen" not in (api / ".claude" / "skills" / "brainstorm-architect" / "references" / "sprints-overzicht.md").read_text()

    api_builder = (api / ".claude" / "skills" / "feature-builder" / "SKILL.md").read_text()
    assert "## Stap 3: Afronden" in api_builder and "Frontend" not in api_builder


def test_init_project_hands_over_to_design_session_for_web_only(tmp_dir):
    web = tmp_dir / "Web"
    assemble_project("Web", "fullstack", {"backend": "fastapi", "frontend": "vue3", "database": "sqlite"}, [], web, assistants=["claude"])
    web_init = (web / ".claude" / "skills" / "init-project" / "SKILL.md").read_text()
    assert ".claude/skills/brainstorm-architect/SKILL.md" in web_init
    assert "Intake" not in web_init and "hoofddoel" not in web_init.lower()

    cli = tmp_dir / "Cli"
    assemble_project("Cli", "cli", {"cli": "python-typer"}, [], cli, assistants=["claude"])
    cli_init = (cli / ".claude" / "skills" / "init-project" / "SKILL.md").read_text()
    assert "## Stap 2: Intake" in cli_init
    assert "brainstorm-architect" not in cli_init


def test_new_backend_without_entities_has_only_health_endpoint(tmp_dir):
    target = tmp_dir / "Leeg"
    assemble_project("Leeg", "backend", {"backend": "fastapi", "database": "postgres"}, [], target, assistants=["claude"])

    endpoints = sorted(p.name for p in (target / "backend" / "app" / "api" / "v1" / "endpoints").glob("*.py"))
    assert endpoints == ["health.py"]
    assert "voorbeelden met een lijst in het geheugen" not in (target / "CLAUDE.md").read_text()
    claude_md = (target / "CLAUDE.md").read_text()
    assert ".docs/ontwerp/" in claude_md and ".docs/sprints/" in claude_md and ".docs/ontwerp.md" not in claude_md

