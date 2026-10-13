"""Modular template assembly and Jinja2 rendering engine for AppCreator."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import jinja2

from appcreator.core.assistants import (
    ASSISTANTS,
    PROJECT_CONTEXT_DESCRIPTION,
    PROJECT_CONTEXT_SOURCE,
    RULES,
    assistant_context,
    project_assistant_context,
    rule_frontmatter,
)
from appcreator.core.manifest import create_manifest
from appcreator.core.skills import BASIS_SKILLS, stack_skills
from appcreator.core.naming import make_package_name, make_slug

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def get_jinja_env() -> jinja2.Environment:
    """Configures a strict Jinja2 environment: unknown variables raise instead of rendering empty."""
    return jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )


def render_string(template_str: str, context: Dict[str, Any]) -> str:
    """Renders an in-memory string with Jinja2."""
    env = get_jinja_env()
    template = env.from_string(template_str)
    return template.render(**context)


def render_file(src_path: Path, dst_path: Path, context: Dict[str, Any]):
    """Renders a .jinja file with Jinja2; any other file is copied unchanged."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if src_path.name.endswith(".jinja"):
        content = src_path.read_text(encoding="utf-8")
        dst_path.write_text(render_string(content, context), encoding="utf-8")
    else:
        shutil.copy2(src_path, dst_path)

    if dst_path.name.endswith(".sh"):
        dst_path.chmod(dst_path.stat().st_mode | 0o111)


def copy_and_render_tree(src_dir: Path, dst_dir: Path, context: Dict[str, Any]):
    """Recursively copies and renders a template directory into dst_dir."""
    if not src_dir.exists():
        return

    for root, dirs, files in os.walk(src_dir):
        rel_root = Path(root).relative_to(src_dir)

        # Skip pycache, entity templates and hidden system dirs
        if any(part.startswith("__pycache__") or part.startswith("_") for part in rel_root.parts):
            continue

        for file_name in files:
            # Sla entiteit-specifieke sjablonen over als er geen kern_domein is gekozen
            if not context.get("kern_domein") and "kern_domein" in file_name:
                continue

            src_file = Path(root) / file_name

            # Resolve template variables in target file path (e.g. {{ app_slug }})
            rel_file_path_str = str(rel_root / file_name)
            rendered_rel_path = render_string(rel_file_path_str, context)

            # Strip .jinja suffix if present
            if rendered_rel_path.endswith(".jinja"):
                rendered_rel_path = rendered_rel_path[:-6]

            target_file = dst_dir / rendered_rel_path
            render_file(src_file, target_file, context)


def generate_docker_compose(dst_dir: Path, context: Dict[str, Any]):
    """Generates a tailored docker-compose.yml based on chosen components."""
    backend = context.get("backend")
    frontend = context.get("frontend")
    database = context.get("database")

    if not backend and not frontend and database != "postgres":
        return

    lines = [
        "services:",
    ]

    # Database service
    if database == "postgres":
        lines.extend([
            "  postgres:",
            "    image: postgres:16-alpine",
            f"    container_name: {context.get('app_slug', 'app')}-postgres",
            "    restart: unless-stopped",
            "    environment:",
            "      POSTGRES_USER: postgres",
            "      POSTGRES_PASSWORD: postgrespassword",
            f"      POSTGRES_DB: {context.get('app_slug', 'app')}_db",
            "    ports:",
            "      - '${POSTGRES_PORT:-5432}:5432'",
            "    volumes:",
            "      - postgres_data:/var/lib/postgresql/data",
            "    healthcheck:",
            "      test: ['CMD-SHELL', 'pg_isready -U postgres']",
            "      interval: 5s",
            "      timeout: 5s",
            "      retries: 5",
            "",
        ])

    # Backend service
    if backend == "fastapi":
        lines.extend([
            "  backend:",
            "    build:",
            "      context: ./backend",
            "      dockerfile: Dockerfile",
            f"    container_name: {context.get('app_slug', 'app')}-backend",
            "    restart: unless-stopped",
            "    ports:",
            "      - '8000:8000'",
            "    environment:",
        ])
        if database == "postgres":
            lines.extend([
                f"      - DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@postgres:5432/{context.get('app_slug', 'app')}_db",
            ])
        else:
            lines.extend([
                "      - DATABASE_URL=sqlite+aiosqlite:///./app.db",
            ])
        lines.extend([
            "      - ENVIRONMENT=development",
            "    volumes:",
            "      - ./backend:/app",
        ])
        if database == "postgres":
            lines.extend([
                "    depends_on:",
                "      postgres:",
                "        condition: service_healthy",
            ])
        lines.append("")

    # Frontend service
    if frontend == "vue3":
        lines.extend([
            "  frontend:",
            "    build:",
            "      context: ./frontend",
            "      dockerfile: Dockerfile",
            f"    container_name: {context.get('app_slug', 'app')}-frontend",
            "    restart: unless-stopped",
            "    ports:",
            "      - '5173:5173'",
            "    volumes:",
            "      - ./frontend:/app",
            "      - /app/node_modules",
            "    environment:",
            "      - VITE_API_URL=http://localhost:8000/api/v1",
            "",
        ])

    if database == "postgres":
        lines.extend([
            "volumes:",
            "  postgres_data:",
            "",
        ])

    compose_file = dst_dir / "docker-compose.yml"
    compose_file.write_text("\n".join(lines), encoding="utf-8")

    # Docker Compose leest variabelen uit de .env naast docker-compose.yml (niet uit backend/.env)
    if database == "postgres":
        root_env = "# Host-poort waarop de PostgreSQL container bereikbaar is\nPOSTGRES_PORT=5432\n"
        (dst_dir / ".env").write_text(root_env, encoding="utf-8")
        (dst_dir / ".env.example").write_text(root_env, encoding="utf-8")


def write_rules(dst_dir: Path, context: Dict[str, Any]):
    """Writes the project context and stack rules for every chosen assistant."""
    rules_source_dir = TEMPLATES_DIR / "rules"

    for key in context["assistants"]:
        assistant = ASSISTANTS[key]
        rule_context = {**context, **assistant_context(key)}

        # Universal project context (CLAUDE.md voor Claude Code, always_on rule voor Antigravity)
        body = render_string((rules_source_dir / PROJECT_CONTEXT_SOURCE).read_text(encoding="utf-8"), rule_context)
        context_path = dst_dir / assistant.context_file
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(rule_frontmatter(key, PROJECT_CONTEXT_DESCRIPTION) + body, encoding="utf-8")

        # Stack specific rules
        for rule in RULES:
            if context.get(rule.stack_key) != rule.stack_value:
                continue
            body = (rules_source_dir / f"{rule.name}.md").read_text(encoding="utf-8")
            rule_path = dst_dir / assistant.rules_dir / f"{rule.name}.md"
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            rule_path.write_text(rule_frontmatter(key, rule.description, rule.globs) + body, encoding="utf-8")


def copy_skill(skill_name: str, dst_dir: Path, context: Dict[str, Any]) -> bool:
    """Copies and renders a single skill from templates/skills for every chosen assistant."""
    src_skill_dir = TEMPLATES_DIR / "skills" / skill_name
    if not src_skill_dir.exists():
        return False
    for key in context["assistants"]:
        skill_context = {**context, **assistant_context(key)}
        target_skill_dir = dst_dir / ASSISTANTS[key].skills_dir / skill_name
        copy_and_render_tree(src_skill_dir, target_skill_dir, skill_context)
    return True


def build_context(
    app_naam: str,
    category: str,
    stack: Dict[str, Any],
    assistants: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Builds the template context for a project from its name, category and stack."""
    entiteiten = stack.get("entiteiten")
    if entiteiten is None:
        if stack.get("kern_domein"):
            entiteiten = [stack["kern_domein"]]
        else:
            entiteiten = []

    return {
        "app_naam": app_naam,
        "app_slug": make_slug(app_naam),
        "package_name": make_package_name(app_naam),
        "category": category,
        "backend": stack.get("backend"),
        "frontend": stack.get("frontend"),
        "hardware": stack.get("hardware"),
        "cli": stack.get("cli"),
        "database": stack.get("database", "none"),
        "entiteiten": entiteiten,
        "kern_domein": entiteiten[0] if entiteiten else None,
        **project_assistant_context(assistants),
    }


def assemble_project(
    app_naam: str,
    category: str,
    stack: Dict[str, Any],
    skills: List[str],
    target_dir: Path,
    assistants: Optional[List[str]] = None,
) -> Path:
    """Assembles all layers and renders the project into target_dir."""
    context = build_context(app_naam, category, stack, assistants)
    entiteiten = context["entiteiten"]

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Base / Common layer
    common_dir = TEMPLATES_DIR / "common"
    if common_dir.exists():
        copy_and_render_tree(common_dir, target_dir, context)

    # 2. Stack Layers
    if stack.get("backend") == "fastapi":
        backend_dir = TEMPLATES_DIR / "backends" / "fastapi"
        copy_and_render_tree(backend_dir, target_dir, context)

        # Render entity-templates voor elke geselecteerde entiteit
        if entiteiten:
            entity_tpl_dir = TEMPLATES_DIR / "backends" / "fastapi" / "_entity_templates"
            model_tpl = entity_tpl_dir / "model.py.jinja"
            schema_tpl = entity_tpl_dir / "schema.py.jinja"
            endpoint_tpl = entity_tpl_dir / "endpoint.py.jinja"

            for entiteit in entiteiten:
                slug = entiteit.lower()
                ent_context = dict(context)
                ent_context["kern_domein"] = entiteit
                ent_context["entiteit"] = entiteit

                if model_tpl.exists():
                    render_file(model_tpl, target_dir / "backend" / "app" / "models" / f"{slug}.py", ent_context)
                if schema_tpl.exists():
                    render_file(schema_tpl, target_dir / "backend" / "app" / "schemas" / f"{slug}.py", ent_context)
                if endpoint_tpl.exists():
                    render_file(endpoint_tpl, target_dir / "backend" / "app" / "api" / "v1" / "endpoints" / f"{slug}.py", ent_context)

    if stack.get("frontend") == "vue3":
        frontend_dir = TEMPLATES_DIR / "frontends" / "vue3"
        copy_and_render_tree(frontend_dir, target_dir, context)

    if stack.get("hardware") == "esp32":
        embedded_dir = TEMPLATES_DIR / "embedded" / "esp32"
        copy_and_render_tree(embedded_dir, target_dir, context)

    if stack.get("cli") == "python-typer":
        cli_dir = TEMPLATES_DIR / "cli" / "python-typer"
        copy_and_render_tree(cli_dir, target_dir, context)

    # 3. Dynamic Docker Compose
    generate_docker_compose(target_dir, context)

    # 4. Agent Rules (project context + stack rules per gekozen assistent)
    write_rules(target_dir, context)

    # 5. Agent Skills: basis, stack-specifiek en de gekozen optionele skills
    alle_skills = list(dict.fromkeys(BASIS_SKILLS + stack_skills(stack) + skills))
    for skill in alle_skills:
        copy_skill(skill, target_dir, context)

    # 6. Create .appcreator.json manifest
    create_manifest(
        project_dir=target_dir,
        app_naam=app_naam,
        category=category,
        stack=stack,
        skills=alle_skills,
        assistants=context["assistants"],
    )

    return target_dir
