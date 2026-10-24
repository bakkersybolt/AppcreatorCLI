"""The Vue 3 frontend template: Tailwind v4, reka-ui, design tokens, shared form and test helpers."""

import json
import os
import re

import pytest

from appcreator.core.generator import assemble_project

STACK = {"backend": "fastapi", "frontend": "vue3", "database": "sqlite", "entiteiten": []}

KEY_FILES = [
    "package.json",
    "components.json",
    "vite.config.ts",
    "vitest.config.ts",
    "env.d.ts",
    "tsconfig.app.json",
    "tsconfig.vitest.json",
    "scripts/shadcn-add.sh",
    "src/App.vue",
    "src/app.json",
    "src/config.ts",
    "src/main.ts",
    "src/assets/index.css",
    "src/assets/brand/tokens.css",
    "src/router/index.ts",
    "src/router/routes.ts",
    "src/views/HomeView.vue",
    "src/views/__tests__/HomeView.spec.ts",
    "src/composables/useApiError.ts",
    "src/composables/useFormFeedback.ts",
    "src/composables/__tests__/useApiError.spec.ts",
    "src/composables/__tests__/useFormFeedback.spec.ts",
    "src/components/common/FormAlert.vue",
    "src/lib/utils.ts",
    "src/lib/zod-nl.ts",
    "src/test/setup.ts",
    "src/test/api.ts",
    "src/test/helpers.ts",
    "src/components/ui/button/index.ts",
    "src/components/ui/alert/index.ts",
    "src/components/ui/sonner/index.ts",
    "src/components/ui/form/index.ts",
    "src/components/ui/input/index.ts",
    "src/components/ui/label/index.ts",
]


@pytest.fixture
def frontend(tmp_path):
    target = tmp_path / "Web App"
    assemble_project("Web App", "fullstack", STACK, [], target, assistants=["claude"])
    return target / "frontend"


def test_key_files_exist(frontend):
    missing = [f for f in KEY_FILES if not (frontend / f).is_file()]
    assert missing == []


def test_tailwind_v4_without_old_config(frontend):
    assert not (frontend / "tailwind.config.js").exists()
    assert not (frontend / "postcss.config.js").exists()
    assert "tailwindcss()" in (frontend / "vite.config.ts").read_text()
    css = (frontend / "src" / "assets" / "index.css").read_text()
    assert "@import 'tailwindcss';" in css
    assert "@import 'tw-animate-css';" in css
    assert "@import './brand/tokens.css';" in css
    assert "@theme inline" in css
    assert "--primary: var(--brand-primary);" in css
    tokens = (frontend / "src" / "assets" / "brand" / "tokens.css").read_text()
    assert "design-system" in tokens
    assert "--brand-primary:" in tokens


def test_package_json_stack(frontend):
    package = json.loads((frontend / "package.json").read_text())
    deps = {**package["dependencies"], **package["devDependencies"]}
    for name in ("@tailwindcss/vite", "tailwindcss", "tw-animate-css", "reka-ui", "vue-sonner", "@fontsource-variable/inter"):
        assert name in deps, name
    for name in ("radix-vue", "autoprefixer", "postcss"):
        assert name not in deps, name
    assert package["scripts"]["build"] == "vue-tsc --build && vite build"
    assert "vue-tsc --noEmit -p tsconfig.vitest.json" in package["scripts"]["lint"]
    assert "prettier --check src/" in package["scripts"]["lint"]


def test_components_json_uses_tailwind_v4(frontend):
    components = json.loads((frontend / "components.json").read_text())
    assert components["tailwind"]["config"] == ""
    assert components["tailwind"]["css"] == "src/assets/index.css"
    assert components["tailwind"]["baseColor"] == "neutral"
    assert components["aliases"]["composables"] == "@/composables"


def test_shadcn_add_script_is_executable(frontend):
    script = frontend / "scripts" / "shadcn-add.sh"
    assert os.access(script, os.X_OK)
    assert 'SHADCN_VUE_VERSION="${SHADCN_VUE_VERSION:-' in script.read_text()


def test_toaster_and_app_name(frontend):
    assert "<Toaster" in (frontend / "src" / "App.vue").read_text()
    assert json.loads((frontend / "src" / "app.json").read_text()) == {"name": "Web App", "assistants": "Claude Code"}


def test_no_template_syntax_or_other_app_left(frontend):
    for path in frontend.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text()
        assert "{%" not in text, path
        assert not re.search(r"dwaze|druiven|bordeaux|wijn", text, re.IGNORECASE), path


def test_skills_describe_the_frontend_helpers(tmp_path):
    target = tmp_path / "Web"
    assemble_project("Web", "fullstack", STACK, ["test-engineer"], target, assistants=["claude"])
    skills = target / ".claude" / "skills"
    vue = (skills / "vue-shadcn" / "SKILL.md").read_text()
    tests = (skills / "test-engineer" / "SKILL.md").read_text()
    assert "frontend/scripts/shadcn-add.sh" in vue
    assert "### Vaste regel voor formulieren" in vue
    assert "## Valkuilen" in vue
    assert "mockedApi()" in tests
    assert "### Gedeelde testhulpen" in tests
    assert "settle()" in tests
    for text in (vue, tests):
        assert "{%" not in text and "{{" not in text
        assert not re.search(r"playwright|contract-samples|ProfileView|formulieren\.md|make_evening", text, re.I)
