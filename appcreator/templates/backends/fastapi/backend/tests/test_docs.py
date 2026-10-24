"""Documentation checks (skill `documentatie`): the technical docs in `docs/` keep up with the code.

- every field of `Settings` is in `docs/configuratie.md`;
- every file stays within 400 words (frontmatter, tables, code blocks and HTML comments not counted);
- every relative link points to an existing file, and an `#anchor` to an existing heading;
- every file is listed in the index `docs/README.md`.

Do not loosen these checks to close a sprint.
"""

import re
from pathlib import Path

import pytest

from app.core.config import Settings

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
INDEX = DOCS_DIR / "README.md"
MAX_WORDS = 400

DOC_FILES = sorted(DOCS_DIR.rglob("*.md"))
DOC_IDS = [str(path.relative_to(DOCS_DIR)) for path in DOC_FILES]

CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(([^)\s]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def count_words(text: str) -> int:
    """Count words like the help check (`countWords` in `frontend/src/lib/help/frontmatter.ts`).

    Frontmatter, code blocks, HTML comments and table rows are not counted.
    """
    prose = HTML_COMMENT.sub(" ", CODE_BLOCK.sub(" ", FRONTMATTER.sub("", text)))
    lines = [line for line in prose.splitlines() if not line.strip().startswith("|")]
    prose = re.sub(r"[#*_>`\[\]()-]", " ", " ".join(lines))
    return sum(1 for word in prose.split() if any(char.isalnum() for char in word))


def heading_anchors(text: str) -> set[str]:
    """GitHub-style anchors of all headings: lowercase, punctuation dropped, spaces to hyphens."""
    anchors = set()
    for heading in HEADING.findall(CODE_BLOCK.sub(" ", text)):
        plain = re.sub(r"[`*_]|\[([^\]]*)\]\([^)]*\)", r"\1", heading).strip().lower()
        anchors.add(re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", plain)))
    return anchors


def relative_links(text: str) -> list[str]:
    """Links in the prose that are not external (`http:`, `mailto:`…), skipping code."""
    prose = INLINE_CODE.sub(" ", CODE_BLOCK.sub(" ", text))
    return [link for link in LINK.findall(prose) if not re.match(r"^[a-z][a-z0-9+.-]*:", link, re.IGNORECASE)]


def test_every_setting_is_documented() -> None:
    text = (DOCS_DIR / "configuratie.md").read_text(encoding="utf-8")
    missing = [name for name in Settings.model_fields if f"`{name}`" not in text]
    assert not missing, f"Add these settings to docs/configuratie.md: {missing}"


def test_there_are_docs() -> None:
    assert INDEX in DOC_FILES, "docs/README.md (de index) ontbreekt"


@pytest.mark.parametrize("path", DOC_FILES, ids=DOC_IDS)
def test_doc_is_short_enough(path: Path) -> None:
    words = count_words(path.read_text(encoding="utf-8"))
    assert words <= MAX_WORDS, (
        f"docs/{path.relative_to(DOCS_DIR)} heeft {words} woorden (max {MAX_WORDS}, frontmatter, tabellen en "
        "codeblokken niet meegeteld): kort in of splits het onderwerp"
    )


@pytest.mark.parametrize("path", DOC_FILES, ids=DOC_IDS)
def test_doc_links_work(path: Path) -> None:
    broken = []
    for link in relative_links(path.read_text(encoding="utf-8")):
        target_part, _, anchor = link.partition("#")
        target = (path.parent / target_part).resolve() if target_part else path
        if not target.exists():
            broken.append(f"{link} (bestand bestaat niet)")
        elif (
            anchor
            and target.suffix == ".md"
            and anchor not in heading_anchors(target.read_text(encoding="utf-8"))
        ):
            broken.append(f"{link} (kop #{anchor} bestaat niet)")
    assert not broken, f"docs/{path.relative_to(DOCS_DIR)} heeft {len(broken)} kapotte link(s): {broken}"


@pytest.mark.parametrize(
    "path", [p for p in DOC_FILES if p != INDEX], ids=[i for i in DOC_IDS if i != "README.md"]
)
def test_doc_is_in_index(path: Path) -> None:
    linked = {
        (INDEX.parent / link.partition("#")[0]).resolve()
        for link in relative_links(INDEX.read_text(encoding="utf-8"))
        if link.partition("#")[0]
    }
    assert path.resolve() in linked, (
        f"docs/{path.relative_to(DOCS_DIR)} staat niet in de index docs/README.md"
    )
