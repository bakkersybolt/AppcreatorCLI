"""AI assistant targets (Google Antigravity, Claude Code) and the rules written for them."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Assistant:
    key: str
    naam: str
    skills_dir: str
    rules_dir: str
    context_file: str
    open_cmd: str


ASSISTANTS: Dict[str, Assistant] = {
    "antigravity": Assistant(
        key="antigravity",
        naam="Google Antigravity",
        skills_dir=".agents/skills",
        rules_dir=".agents/rules",
        context_file=".agents/rules/project-context.md",
        open_cmd="antigravity .",
    ),
    "claude": Assistant(
        key="claude",
        naam="Claude Code",
        skills_dir=".claude/skills",
        rules_dir=".claude/rules",
        context_file="CLAUDE.md",
        open_cmd="claude",
    ),
}

DEFAULT_ASSISTANTS = ["antigravity"]

PROJECT_CONTEXT_SOURCE = "project-context.md.jinja"
PROJECT_CONTEXT_DESCRIPTION = (
    "Globale projectmetadata, commando's en omgevingsdetails. Geldt voor de gehele repository."
)


@dataclass(frozen=True)
class Rule:
    name: str
    stack_key: str
    stack_value: str
    globs: List[str]
    description: str


RULES: List[Rule] = [
    Rule(
        name="backend-rules",
        stack_key="backend",
        stack_value="fastapi",
        globs=["backend/**/*"],
        description="Architectuur- en codeerstandaarden voor de Python / FastAPI backend.",
    ),
    Rule(
        name="frontend-rules",
        stack_key="frontend",
        stack_value="vue3",
        globs=["frontend/**/*"],
        description="Architectuur- en componentenstandaarden voor de Vue 3 frontend met Shadcn-Vue.",
    ),
    Rule(
        name="design-rules",
        stack_key="frontend",
        stack_value="vue3",
        globs=["frontend/src/**/*.vue"],
        description="Stijlregels voor de schermen: tokens, bouwstenen, verboden kleuren en de controle op 390 en 1280 px.",
    ),
    Rule(
        name="esp32-rules",
        stack_key="hardware",
        stack_value="esp32",
        globs=["{src,include,lib}/**/*.{cpp,h,hpp}", "platformio.ini"],
        description="Standaarden voor ESP32 PlatformIO C++ firmware.",
    ),
    Rule(
        name="cli-rules",
        stack_key="cli",
        stack_value="python-typer",
        globs=["{src,tests}/**/*.py", "pyproject.toml"],
        description="Standaarden voor Python CLI tools met Typer en Rich.",
    ),
]


def normalize_assistants(assistants: Optional[List[str]]) -> List[str]:
    """Returns the known assistant keys in a fixed order, defaulting to Antigravity."""
    gekozen = [key for key in ASSISTANTS if key in (assistants or [])]
    return gekozen or list(DEFAULT_ASSISTANTS)


def join_namen(namen: List[str]) -> str:
    """Joins names as Dutch prose: 'A', 'A en B', 'A, B en C'."""
    if len(namen) <= 1:
        return "".join(namen)
    return ", ".join(namen[:-1]) + " en " + namen[-1]


def project_assistant_context(assistants: List[str]) -> Dict[str, Any]:
    """Context shared by all templates of a project: which assistants it is generated for."""
    gekozen = [ASSISTANTS[key] for key in normalize_assistants(assistants)]
    return {
        "assistants": [a.key for a in gekozen],
        "assistant_namen": join_namen([a.naam for a in gekozen]),
        "context_files": [a.context_file for a in gekozen],
        "skills_dirs": [a.skills_dir for a in gekozen],
    }


def assistant_context(key: str) -> Dict[str, Any]:
    """Context for files written for one specific assistant (its rules and skills)."""
    assistant = ASSISTANTS[key]
    return {
        "assistant": assistant.key,
        "assistant_naam": assistant.naam,
        "context_file": assistant.context_file,
        "rules_dir": assistant.rules_dir,
        "skills_dir": assistant.skills_dir,
    }


def rule_frontmatter(key: str, description: str, globs: Optional[List[str]] = None) -> str:
    """Returns the frontmatter an assistant expects for a rule; globs=None means always active."""
    if key == "claude":
        if not globs:
            return ""
        paths = "\n".join(f'  - "{glob}"' for glob in globs)
        return f"---\npaths:\n{paths}\n---\n\n"

    if not globs:
        return f'---\ntrigger: always_on\ndescription: "{description}"\n---\n\n'
    return f'---\ntrigger: glob\nglobs: "{", ".join(globs)}"\ndescription: "{description}"\n---\n\n'
