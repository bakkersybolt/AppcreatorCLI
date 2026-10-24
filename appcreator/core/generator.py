"""Modular template assembly and Jinja2 rendering engine for AppCreator."""

import os
import re
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
from appcreator.core.design import ontwerp_context
from appcreator.core.manifest import create_manifest
from appcreator.core.ports import ProjectPorts, default_ports, write_root_env
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

    if dst_path.name.endswith(".sh") or _has_shebang(dst_path):
        dst_path.chmod(dst_path.stat().st_mode | 0o111)


def _has_shebang(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(2) == b"#!"
    except OSError:
        return False


# Conditional files: a tag like `@frontend` in a file or folder name means "only generate
# this when the flag holds"; the tag is stripped from the output name.
# Example: `HelpView@frontend.vue` -> `HelpView.vue`, only in projects with a Vue frontend.
FLAG_PATTERN = re.compile(r"@([a-z]+)")

FLAGS = {
    "frontend": lambda c: c.get("frontend") == "vue3",
    "backend": lambda c: c.get("backend") == "fastapi",
    "web": lambda c: bool(c.get("backend") or c.get("frontend")),
    "postgres": lambda c: c.get("database") == "postgres",
    "database": lambda c: c.get("database") not in (None, "none"),
    "claude": lambda c: "claude" in c.get("assistants", []),
    "hobbyserver": lambda c: bool((c.get("features") or {}).get("hobbyserver")),
}


def flags_hold(name: str, context: Dict[str, Any]) -> bool:
    """True when every @flag tag in a path part holds for this project."""
    for flag in FLAG_PATTERN.findall(name):
        if flag not in FLAGS:
            raise ValueError(f"Onbekende template-flag '@{flag}' in '{name}'")
        if not FLAGS[flag](context):
            return False
    return True


def strip_flags(path: str) -> str:
    return FLAG_PATTERN.sub("", path)


def copy_and_render_tree(src_dir: Path, dst_dir: Path, context: Dict[str, Any]):
    """Recursively copies and renders a template directory into dst_dir."""
    if not src_dir.exists():
        return

    for root, dirs, files in os.walk(src_dir):
        rel_root = Path(root).relative_to(src_dir)

        # Skip pycache, entity templates and hidden system dirs
        if any(part.startswith("__pycache__") or part.startswith("_") for part in rel_root.parts):
            continue
        if not all(flags_hold(part, context) for part in rel_root.parts):
            continue

        for file_name in files:
            # Sla entiteit-specifieke sjablonen over als er geen kern_domein is gekozen
            if not context.get("kern_domein") and "kern_domein" in file_name:
                continue
            if not flags_hold(file_name, context):
                continue

            src_file = Path(root) / file_name

            # Resolve template variables in target file path (e.g. {{ app_slug }})
            rel_file_path_str = strip_flags(str(rel_root / file_name))
            rendered_rel_path = render_string(rel_file_path_str, context)

            # Strip .jinja suffix if present
            if rendered_rel_path.endswith(".jinja"):
                rendered_rel_path = rendered_rel_path[:-6]

            target_file = dst_dir / rendered_rel_path
            render_file(src_file, target_file, context)


def write_port_env(dst_dir: Path, context: Dict[str, Any]):
    """Writes the app's ports into the root .env (read by Docker Compose, dev.sh, Vite and `appcreator dev`)."""
    if not FLAGS["web"](context):
        return
    ports = ProjectPorts(**{k: context["ports"][k] for k in ("slot", "backend", "frontend", "postgres")})
    write_root_env(dst_dir, ports, include_postgres=FLAGS["postgres"](context))


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
    ports: Optional[ProjectPorts] = None,
    features: Optional[Dict[str, Any]] = None,
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
        "ports": (ports or default_ports()).as_context(),
        "features": features or {},
        **ontwerp_context(stack.get("frontend") == "vue3"),
        **project_assistant_context(assistants),
    }


def assemble_project(
    app_naam: str,
    category: str,
    stack: Dict[str, Any],
    skills: List[str],
    target_dir: Path,
    assistants: Optional[List[str]] = None,
    ports: Optional[ProjectPorts] = None,
    features: Optional[Dict[str, Any]] = None,
) -> Path:
    """Assembles all layers and renders the project into target_dir."""
    context = build_context(app_naam, category, stack, assistants, ports, features)
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

    # 3. Ports of this app in the root .env (docker-compose.yml comes from common/)
    write_port_env(target_dir, context)

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
        ports={k: context["ports"][k] for k in ("slot", "backend", "frontend", "postgres")} if FLAGS["web"](context) else None,
        features=context["features"],
    )

    return target_dir
