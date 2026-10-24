"""In-app help and the design system (tokens, design-rules.md, design-guard.json, sandbox, skill design-system)."""

import json
import re
import subprocess
import sys

import pytest

from appcreator.core.generator import assemble_project
from appcreator.core.manifest import load_manifest

FULLSTACK = {"backend": "fastapi", "frontend": "vue3", "database": "postgres", "entiteiten": []}
BACKEND = {"backend": "fastapi", "database": "none", "entiteiten": []}

HELP_AND_DESIGN_FILES = [
    "design-guard.json",
    "src/content/help/categories.json",
    "src/content/help/aan-de-slag/welkom.md",
    "src/content/help/__tests__/docs.spec.ts",
    "src/lib/help/frontmatter.ts",
    "src/lib/help/articles.ts",
    "src/lib/help/render.ts",
    "src/views/help/HelpView.vue",
    "src/views/help/HelpArticleView.vue",
    "src/components/help/HelpButton.vue",
    "src/test/fixtures/help.ts",
    "src/test/__tests__/design-guard.spec.ts",
    "src/design/screens.ts",
    "src/design/DesignIndex.vue",
    "src/design/DesignScreen.vue",
    "src/design/screens/VoorbeeldScherm.vue",
]


@pytest.fixture(scope="module")
def fullstack(tmp_path_factory):
    target = tmp_path_factory.mktemp("web") / "Web"
    assemble_project("Web", "fullstack", FULLSTACK, [], target, assistants=["antigravity", "claude"])
    return target


def _guard_script(project):
    """The design-guard part of the Claude lint hook (the embedded Python between `<<'PY'` and `PY`)."""
    hook = (project / ".claude" / "hooks" / "lint-changed-file.sh").read_text()
    return re.search(r"<<'PY'\n(.*?)\nPY\n", hook, re.DOTALL).group(1)


def _guard(project, rel):
    """Run the hook's design guard on `frontend/<rel>`; returns its output (empty = clean)."""
    result = subprocess.run(
        [sys.executable, "-c", _guard_script(project), str(project / "frontend"), rel],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_help_and_design_files_exist_for_fullstack(fullstack):
    frontend = fullstack / "frontend"
    assert [f for f in HELP_AND_DESIGN_FILES if not (frontend / f).is_file()] == []
    package = json.loads((frontend / "package.json").read_text())
    assert "markdown-it" in package["dependencies"]
    assert "@types/markdown-it" in package["devDependencies"]


def test_no_frontend_help_or_design_for_backend_only(tmp_path):
    target = tmp_path / "Api"
    assemble_project("Api", "backend", BACKEND, [], target, assistants=["claude"])
    assert not (target / "frontend").exists()
    assert not (target / ".claude" / "rules" / "design-rules.md").exists()
    assert not (target / ".claude" / "skills" / "design-system").exists()
    assert "design-system" not in load_manifest(target)["skills"]


def test_design_rules_written_per_assistant(fullstack):
    claude = (fullstack / ".claude" / "rules" / "design-rules.md").read_text()
    assert claude.startswith('---\npaths:\n  - "frontend/src/**/*.vue"\n---\n')
    antigravity = (fullstack / ".agents" / "rules" / "design-rules.md").read_text()
    assert antigravity.startswith('---\ntrigger: glob\nglobs: "frontend/src/**/*.vue"\n')
    for text in (claude, antigravity):
        for kop in ["## Karakter", "## Kleur en typografie", "## Bouwstenen", "## Verboden", "## Controle"]:
            assert kop in text
        assert "FormAlert" in text and "390 px" in text and "1280 px" in text
        assert "{{" not in text and "{%" not in text


def test_design_guard_json_is_valid_and_compiles_in_python(fullstack):
    guard = json.loads((fullstack / "frontend" / "design-guard.json").read_text())
    assert len(guard["rules"]) >= 3
    for rule in guard["rules"]:
        re.compile(rule["pattern"])
        assert rule["message"] and rule["files"]
        assert "src/components/ui/*" in rule["allow"]


@pytest.mark.parametrize(
    "line, flagged",
    [
        ('<div class="bg-[#ff0000] p-2">', True),
        ('<div class="text-[oklch(0.5_0.2_30)]">', True),
        ('<div class="bg-card dark:bg-black">', True),
        ("  color: #fff;", True),
        ("const style = { color: '#a1b2c3' }", True),
        ('<div class="bg-primary text-primary-foreground">', False),
        ('<template #default="{ item }">', False),
        ("<template #add>", False),
        ('<a href="#inhoud">Naar de inhoud</a>', False),
        ("Tailwind would apply the `dark:` classes", False),
        ('<div class="rounded-[min(var(--radius-md),10px)]">', False),
    ],
)
def test_design_guard_patterns_in_python(fullstack, line, flagged):
    """Same examples as design-guard.spec.ts, so the patterns behave alike in Python (hook) and JavaScript (test)."""
    rules = json.loads((fullstack / "frontend" / "design-guard.json").read_text())["rules"]
    assert any(re.search(rule["pattern"], line) for rule in rules) is flagged


def test_hook_design_guard_flags_a_violating_view(fullstack):
    views = fullstack / "frontend" / "src" / "views"
    (views / "Fout.vue").write_text('<template>\n  <div class="bg-[#ff0000] dark:bg-black">x</div>\n</template>\n')
    (views / "Goed.vue").write_text('<template>\n  <div class="bg-primary">x</div>\n</template>\n')
    try:
        out = _guard(fullstack, "src/views/Fout.vue")
        assert "src/views/Fout.vue:2:" in out
        assert "dark:" in out and "bg-[#...]" in out
        assert _guard(fullstack, "src/views/Goed.vue") == ""
        # The ui components (shadcn) may use dark: variants
        assert _guard(fullstack, "src/components/ui/button/index.ts") == ""
    finally:
        (views / "Fout.vue").unlink()
        (views / "Goed.vue").unlink()


def test_template_sources_pass_the_hook_design_guard(fullstack):
    frontend = fullstack / "frontend"
    hits = [
        out
        for path in sorted((frontend / "src").rglob("*"))
        if path.is_file() and (out := _guard(fullstack, str(path.relative_to(frontend))))
    ]
    assert hits == []


def test_design_system_skill_is_installed_and_listed(fullstack):
    assert "design-system" in load_manifest(fullstack)["skills"]
    claude = (fullstack / ".claude" / "skills" / "design-system" / "SKILL.md").read_text()
    antigravity = (fullstack / ".agents" / "skills" / "design-system" / "SKILL.md").read_text()
    for text in (claude, antigravity):
        assert "## Modus 1: Uitstraling vastleggen" in text
        assert "## Modus 2: Ontwerp overnemen" in text
        assert ".docs/ontwerp/06-navigatie-en-uitstraling.md" in text
        assert ".docs/ontwerp/ontwerp-overnames.md" in text
        assert "frontend/design-guard.json" in text
        assert "shadcn-add.sh" in text and "@lucide/vue" in text
    assert ".claude/rules/design-rules.md" in claude
    assert ".agents/rules/design-rules.md" in antigravity
    assert "AskUserQuestion" in claude and "AskUserQuestion" not in antigravity
    assert "WebFetch" in claude and "WebFetch" not in antigravity


def test_other_skills_point_to_the_design_system_skill(fullstack):
    skills = fullstack / ".claude" / "skills"
    for naam in ["vue-shadcn", "brainstorm-architect", "feature-builder"]:
        assert "`design-system`" in (skills / naam / "SKILL.md").read_text(), naam
    assert "design-system" in (fullstack / "frontend" / "src" / "assets" / "brand" / "tokens.css").read_text()


def test_routes_have_help_and_dev_only_sandbox(fullstack):
    routes = (fullstack / "frontend" / "src" / "router" / "routes.ts").read_text()
    assert routes.count("help: 'aan-de-slag/welkom'") == 3
    assert "path: '/_ontwerp'" in routes and "devOnly: true" in routes
    assert "import.meta.env.DEV" in routes
    assert "help?: string" in routes and "devOnly?: boolean" in routes
    assert "<HelpButton />" in (fullstack / "frontend" / "src" / "App.vue").read_text()


def test_documentation_points_to_routes_ts(fullstack):
    skill = (fullstack / ".claude" / "skills" / "documentatie" / "SKILL.md").read_text()
    assert "frontend/src/router/routes.ts" in skill
    assert "router/index.ts" not in skill
    hulp = (fullstack / "docs" / "onderdelen" / "hulp.md").read_text()
    assert "router/routes.ts" in hulp and "router/index.ts" not in hulp
