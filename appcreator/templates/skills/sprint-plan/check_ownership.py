#!/usr/bin/env python3
"""Check that a track branch only changes files from its ownership list in bouwplan.md.

Usage: check_ownership.py <bouwplan.md> <track-letter> <branch> <base>

Reads the "- Eigendom:" bullet under "### Track <letter> – ..." (any heading level, e.g. "####" under a wave) (paths in backticks, `*` globs,
`{a,b}` expansion, "(+ spec)" / "(+ specs)" adds `__tests__/<name>.spec.ts` and `<name>.spec.ts`;
any file in `__tests__/` next to an owned file is allowed as well)
and compares it with `git diff --name-only <base>...<branch>`. Exit code 1 when files fall outside.
"""

import fnmatch
import posixpath
import re
import subprocess
import sys


def expand_braces(pattern: str) -> list[str]:
    match = re.search(r"\{([^{}]*)\}", pattern)
    if not match:
        return [pattern]
    head, tail = pattern[: match.start()], pattern[match.end() :]
    result: list[str] = []
    for option in match.group(1).split(","):
        result.extend(expand_braces(head + option.strip() + tail))
    return result


def ownership_text(bouwplan: str, track: str) -> str:
    with open(bouwplan, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    # Tracks may sit at any heading level, e.g. `#### Track A` under a "### Golf 1" heading.
    header = re.compile(rf"^(#{{2,6}})\s+Track\s+{re.escape(track)}\b", re.IGNORECASE)
    start, level = next(
        ((i, len(m.group(1))) for i, line in enumerate(lines) if (m := header.match(line))), (None, 0)
    )
    if start is None:
        sys.exit(f"Track {track} not found in {bouwplan}")
    heading = re.compile(r"^(#{1,6})\s")
    collected: list[str] = []
    in_block = False
    for line in lines[start + 1 :]:
        if (m := heading.match(line)) and len(m.group(1)) <= level:
            break
        if line.startswith("- Eigendom:"):
            in_block = True
            collected.append(line)
        elif in_block and line.startswith("  ") and not line.lstrip().startswith("- "):
            collected.append(line)
        else:
            in_block = False
    if not collected:
        sys.exit(f"No '- Eigendom:' line for track {track}")
    return " ".join(collected)


def patterns(text: str) -> list[str]:
    """Bare names like `test_x.py` resolve to the directory of the previous full path.
    "(+ spec)" applies to the path just before it; "(+ specs)" to the run of paths before it
    that are only separated by ", "."""
    result: list[str] = []
    last_dir = ""
    run: list[str] = []
    previous_end = 0
    for match in re.finditer(r"`([^`]+)`(\s*\(\+\s*(specs?)\))?", text):
        if text[previous_end : match.start()].strip() not in ("", ","):
            run = []
        previous_end = match.end()
        paths = expand_braces(match.group(1))
        if "/" not in match.group(1) and last_dir:
            paths = [posixpath.join(last_dir, p) for p in paths]
        elif "/" in match.group(1):
            last_dir = posixpath.dirname(paths[0])
        result.extend(paths)
        run.extend(paths)
        if match.group(2):
            for path in run if match.group(3) == "specs" else paths:
                directory, name = posixpath.split(path)
                stem = name.rsplit(".", 1)[0]
                result.append(posixpath.join(directory, "__tests__", f"{stem}.spec.ts"))
                result.append(posixpath.join(directory, f"{stem}.spec.ts"))
            run = []
    return result


def owned(path: str, owned_patterns: list[str]) -> bool:
    if owned_test(path, owned_patterns):
        return True
    for pattern in owned_patterns:
        if pattern.startswith("…"):  # abbreviated sibling path, e.g. `…/x.md`
            if path.endswith(pattern[1:]):
                return True
        elif fnmatch.fnmatchcase(path, pattern) or fnmatch.fnmatchcase(path, relative(pattern)):
            return True
    return False


ROOTS = ("frontend/", "backend/", "docs/", ".docs/", ".todos/", ".claude/", ".github/")


def relative(pattern: str) -> str:
    """A shortened path such as `components/x/*` (without `frontend/src/`) matches as the tail of a full path."""
    return pattern if pattern.startswith(ROOTS) else f"*/{pattern}"


def owned_test(path: str, owned_patterns: list[str]) -> bool:
    """A file in `<dir>/__tests__/` is owned when the track owns a file directly in `<dir>`
    (werkafspraak: tests next to owned files belong to the track)."""
    directory = posixpath.dirname(path)
    if posixpath.basename(directory) != "__tests__":
        return False
    parent = posixpath.dirname(directory)
    return any(
        "__tests__" not in pattern
        and (
            fnmatch.fnmatchcase(parent, posixpath.dirname(pattern))
            or fnmatch.fnmatchcase(parent, relative(posixpath.dirname(pattern)))
        )
        for pattern in owned_patterns
    )


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    bouwplan, track, branch, base = sys.argv[1:]
    owned_patterns = patterns(ownership_text(bouwplan, track))
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{branch}"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    outside = [path for path in diff if not owned(path, owned_patterns)]
    print(f"Track {track}: {len(diff)} changed, {len(outside)} outside ownership")
    for path in outside:
        print(f"  OUTSIDE {path}")
    return 1 if outside else 0


if __name__ == "__main__":
    sys.exit(main())
