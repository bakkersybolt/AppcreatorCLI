"""Modular template assembly and Jinja2 rendering engine for AppCreator."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import jinja2

from appcreator.core.manifest import create_manifest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"


def get_jinja_env() -> jinja2.Environment:
    """Configures a flexible Jinja2 environment."""
    return jinja2.Environment(
        undefined=jinja2.Undefined,
        keep_trailing_newline=True,
        autoescape=False,
    )


def render_string(template_str: str, context: Dict[str, Any]) -> str:
    """Renders an in-memory string with Jinja2."""
    env = get_jinja_env()
    template = env.from_string(template_str)
    return template.render(**context)


def render_file(src_path: Path, dst_path: Path, context: Dict[str, Any]):
    """Renders a file with Jinja2 if it is text/jinja, otherwise copies directly."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if binary file
    is_binary = False
    try:
        with open(src_path, "tr", encoding="utf-8") as check_f:
            check_f.read(1024)
    except (UnicodeDecodeError, Exception):
        is_binary = True

    if is_binary:
        shutil.copy2(src_path, dst_path)
        return

    try:
        content = src_path.read_text(encoding="utf-8")
        rendered = render_string(content, context)
        dst_path.write_text(rendered, encoding="utf-8")
        if dst_path.name.endswith(".sh"):
            dst_path.chmod(dst_path.stat().st_mode | 0o111)
    except Exception:
        # Fallback to direct copy if rendering fails
        shutil.copy2(src_path, dst_path)
        if dst_path.name.endswith(".sh"):
            try:
                dst_path.chmod(dst_path.stat().st_mode | 0o111)
            except Exception:
                pass


def copy_and_render_tree(src_dir: Path, dst_dir: Path, context: Dict[str, Any]):
    """Recursively copies and renders a template directory into dst_dir."""
    if not src_dir.exists():
        return

    for root, dirs, files in os.walk(src_dir):
        rel_root = Path(root).relative_to(src_dir)

        # Skip pycache and hidden system dirs
        if any(part.startswith("__pycache__") for part in rel_root.parts):
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
            "      - '5432:5432'",
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


def copy_skill(skill_name: str, dst_dir: Path, context: Dict[str, Any]):
    """Copies and renders a single skill from templates/skills into dst_dir/.agents/skills/."""
    src_skill_dir = TEMPLATES_DIR / "skills" / skill_name
    if not src_skill_dir.exists():
        return False
    target_skill_dir = dst_dir / ".agents" / "skills" / skill_name
    copy_and_render_tree(src_skill_dir, target_skill_dir, context)
    return True


def assemble_project(
    app_naam: str,
    category: str,
    stack: Dict[str, Any],
    skills: List[str],
    target_dir: Path,
) -> Path:
    """Assembles all layers and renders the project into target_dir."""
    app_slug = app_naam.lower().replace(" ", "-").replace("_", "-")
    context = {
        "app_naam": app_naam,
        "app_slug": app_slug,
        "category": category,
        "backend": stack.get("backend"),
        "frontend": stack.get("frontend"),
        "hardware": stack.get("hardware"),
        "database": stack.get("database", "none"),
        "kern_domein": stack.get("kern_domein"),
        "skills": skills,
    }

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Base / Common layer
    common_dir = TEMPLATES_DIR / "common"
    if common_dir.exists():
        copy_and_render_tree(common_dir, target_dir, context)

    # 2. Stack Layers
    if stack.get("backend") == "fastapi":
        backend_dir = TEMPLATES_DIR / "backends" / "fastapi"
        copy_and_render_tree(backend_dir, target_dir, context)

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

    # 4. Agent Rules (.agents/rules/)
    agents_rules_dir = target_dir / ".agents" / "rules"
    agents_rules_dir.mkdir(parents=True, exist_ok=True)

    rules_source_dir = TEMPLATES_DIR / "rules"
    if rules_source_dir.exists():
        # Universal project context
        context_rule = rules_source_dir / "project-context.md.jinja"
        if context_rule.exists():
            render_file(context_rule, agents_rules_dir / "project-context.md", context)

        # Stack specific rules
        if stack.get("backend") == "fastapi":
            backend_rule = rules_source_dir / "backend-rules.md"
            if backend_rule.exists():
                render_file(backend_rule, agents_rules_dir / "backend-rules.md", context)

        if stack.get("frontend") == "vue3":
            frontend_rule = rules_source_dir / "frontend-rules.md"
            if frontend_rule.exists():
                render_file(frontend_rule, agents_rules_dir / "frontend-rules.md", context)

        if stack.get("hardware") == "esp32":
            esp32_rule = rules_source_dir / "esp32-rules.md"
            if esp32_rule.exists():
                render_file(esp32_rule, agents_rules_dir / "esp32-rules.md", context)

        if stack.get("cli") == "python-typer":
            cli_rule = rules_source_dir / "cli-rules.md"
            if cli_rule.exists():
                render_file(cli_rule, agents_rules_dir / "cli-rules.md", context)

    # 5. Agent Skills (.agents/skills/)
    # Universal init-project skill
    copy_skill("init-project", target_dir, context)

    # Stack-specific skills
    if stack.get("backend") == "fastapi":
        copy_skill("python-fastapi", target_dir, context)
    if stack.get("frontend") == "vue3":
        copy_skill("vue-shadcn", target_dir, context)
    if stack.get("hardware") == "esp32":
        copy_skill("esp32-development", target_dir, context)

    # Optional chosen skills
    for skill in skills:
        copy_skill(skill, target_dir, context)

    # 6. Create .appcreator.json manifest
    create_manifest(
        project_dir=target_dir,
        app_naam=app_naam,
        category=category,
        stack=stack,
        skills=list(set(["init-project"] + skills)),
    )

    return target_dir
