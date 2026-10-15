"""Skill catalog for AppCreator: which skills fit which project type."""

from typing import Any, Dict, List, Optional

BASIS_SKILLS = ["init-project", "todo-beheer"]

# (stack key, stack value, skill) - worden automatisch toegevoegd bij de bijbehorende stack
STACK_SKILLS = [
    ("backend", "fastapi", "python-fastapi"),
    ("backend", "fastapi", "brainstorm-architect"),
    ("backend", "fastapi", "feature-builder"),
    ("frontend", "vue3", "vue-shadcn"),
    ("hardware", "esp32", "esp32-development"),
]

OPTIONELE_SKILLS: List[Dict[str, Any]] = [
    {
        "name": "test-engineer",
        "desc": "Testautomatisering met Pytest / Vitest (Aanbevolen)",
        "checked": True,
        "categories": ["fullstack", "backend", "cli"],
    },
    {
        "name": "code-reviewer",
        "desc": "Review op security, types en architectuur (Aanbevolen)",
        "checked": True,
        "categories": ["fullstack", "backend", "embedded", "cli"],
    },
    {
        "name": "database-architect",
        "desc": "Schema-ontwerp & Alembic migraties",
        "checked": False,
        "categories": ["fullstack", "backend"],
        "needs_database": True,
    },
    {
        "name": "docker-devops",
        "desc": "Dockerfiles & Docker Compose",
        "checked": False,
        "categories": ["fullstack", "backend"],
    },
]


def stack_skills(stack: Dict[str, Any]) -> List[str]:
    """Returns the skills that belong to the chosen stack components."""
    return [skill for key, value, skill in STACK_SKILLS if stack.get(key) == value]


def optionele_skills_voor(category: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns the optional skills that make sense for this category and database choice."""
    heeft_database = database not in (None, "none")
    return [
        skill
        for skill in OPTIONELE_SKILLS
        if category in skill["categories"] and (heeft_database or not skill.get("needs_database"))
    ]


def skill_past_bij_project(skill_naam: str, category: str, stack: Dict[str, Any]) -> bool:
    """Checks whether a skill from the catalog is relevant for the given project."""
    if skill_naam in BASIS_SKILLS:
        return True
    for key, value, skill in STACK_SKILLS:
        if skill == skill_naam:
            return stack.get(key) == value
    return skill_naam in [s["name"] for s in optionele_skills_voor(category, stack.get("database"))]
