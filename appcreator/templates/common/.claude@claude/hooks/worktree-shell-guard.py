#!/usr/bin/env python3
"""Claude Code hook (PreToolUse, Bash) for subagents in `.claude/worktrees/`.

Blocks shell commands that the worktree guard of the environment rejects anyway, and explains what does
work. Exit code 2 = blocked; stderr goes to Claude as the reason.

Only active when the hook's `cwd` lies inside `.claude/worktrees/`, so the leader in the main folder keeps
full use of the shell. WORKTREE_GUARD_FORCE=1 applies it anywhere (for testing).

Test:
  echo '{"cwd":"/x/.claude/worktrees/a","tool_input":{"command":"cd frontend && npm test"}}' \
    | python3 .claude/hooks/worktree-shell-guard.py; echo "exit $?"
"""

from __future__ import annotations  # runs on the macOS system python3 (3.9) too

import json
import os
import re
import shlex
import subprocess
import sys

SEPARATORS = {"&&", "||", ";", "|", "&", ";;", "|&", "(", ")"}
LOOP_WORDS = {"for", "while", "until"}
# git commit options that take the next token as their value.
COMMIT_VALUE_LONG = {
    "--message",
    "--file",
    "--reuse-message",
    "--reedit-message",
    "--author",
    "--date",
    "--template",
    "--fixup",
    "--squash",
    "--cleanup",
    "--trailer",
    "--pathspec-from-file",
}
COMMIT_VALUE_SHORT = set("mFCct")


def block(reason: str, instead: str) -> None:
    print(f"GEWEIGERD door de worktree-shell-guard (.claude/hooks/): {reason}", file=sys.stderr)
    print(f"Wat wel werkt: {instead}", file=sys.stderr)
    sys.exit(2)


def tokenize(cmd: str) -> list[str] | None:
    lexer = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:  # unbalanced quotes: only the regex check for heredocs applies
        return None


def segments(tokens: list[str]) -> list[list[str]]:
    """Simple commands between separators, without leading VAR=value assignments."""
    result: list[list[str]] = []
    current: list[str] = []
    for token in [*tokens, ";"]:
        if token in SEPARATORS:
            while current and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", current[0]):
                current = current[1:]
            if current:
                result.append(current)
            current = []
        else:
            current.append(token)
    return result


def uses_git_dash_c(seg: list[str]) -> bool:
    """`git -C <dir> …`: global options come before the subcommand."""
    i = 1
    while i < len(seg) and seg[i].startswith("-"):
        if seg[i] == "-C":
            return True
        i += 2 if seg[i] == "-c" else 1
    return False


def commit_paths(args: list[str]) -> list[str]:
    paths: list[str] = []
    i, only_paths = 0, False
    while i < len(args):
        arg = args[i]
        if only_paths or not arg.startswith("-") or arg == "-":
            paths.append(arg)
        elif arg == "--":
            only_paths = True
        elif arg.startswith("--"):
            if "=" not in arg and arg in COMMIT_VALUE_LONG:
                i += 1
        else:
            for pos, ch in enumerate(arg[1:], start=1):
                if ch in COMMIT_VALUE_SHORT:
                    if pos == len(arg) - 1:
                        i += 1  # the value is the next token
                    break  # otherwise the rest of this token is the value
        i += 1
    return paths


def untracked(path: str, cwd: str) -> bool:
    if not os.path.isfile(os.path.join(cwd, path)):
        return False
    result = subprocess.run(["git", "ls-files", "--error-unmatch", "--", path], cwd=cwd, capture_output=True)
    return result.returncode != 0


def postgres_container(cwd: str) -> str:
    """Name of the app's Postgres container, read from the nearest docker-compose.yml."""
    path = os.path.abspath(cwd)
    while True:
        compose = os.path.join(path, "docker-compose.yml")
        if os.path.isfile(compose):
            with open(compose, encoding="utf-8") as f:
                match = re.search(r"container_name:\s*(\S+-postgres)\b", f.read())
            if match:
                return match.group(1)
        parent = os.path.dirname(path)
        if parent == path:
            return "<app>-postgres"
        path = parent


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    cmd = (data.get("tool_input") or {}).get("command") or ""
    cwd = data.get("cwd") or os.getcwd()
    if not cmd:
        sys.exit(0)
    if os.environ.get("WORKTREE_GUARD_FORCE") != "1" and "/.claude/worktrees/" not in cwd + "/":
        sys.exit(0)

    tokens = tokenize(cmd)
    # Heredocs (<<, <<-), not here-strings (<<<).
    if tokens is None:
        heredoc = bool(re.search(r"(^|[^<])<<-?([^<]|$)", cmd))
    else:
        heredoc = "<<" in tokens or "<<-" in tokens
    if heredoc:
        block(
            "heredocs (<<) worden in een worktree geweigerd, ook binnen een npm-commando.",
            "schrijf of wijzig het bestand met de Edit- of Write-tool.",
        )
    if tokens is None:
        sys.exit(0)

    segs = segments(tokens)
    for index, seg in enumerate(segs):
        name = seg[0]
        if name == "cd" and len(segs) > 1:
            block(
                "'cd … && …' en 'cd x; y' worden in een worktree geweigerd.",
                "draai het commando los vanuit de root van je worktree, of gebruik "
                "'npm --prefix frontend run <script>' (één testbestand: "
                "'npm --prefix frontend run test -- <bestand>').",
            )
        if name == "git" and uses_git_dash_c(seg):
            block(
                "'git -C <map>' wordt in een worktree geweigerd.",
                "draai git zonder -C vanuit de root van je worktree.",
            )
        if name in LOOP_WORDS:
            block(
                "shell-lussen (for/while/until) worden in een worktree geweigerd.",
                "één commando per bestand, of één commando met alle paden als argumenten.",
            )
        if name == "psql":
            block(
                "psql staat niet op de host.",
                f'docker exec {postgres_container(cwd)} psql -U postgres -d <database> -c "…"',
            )
        if name == "git" and len(seg) > 1 and seg[1] == "commit":
            if any(s[:2] == ["git", "add"] for s in segs[:index]):
                continue
            new = [p for p in commit_paths(seg[2:]) if untracked(p, cwd)]
            if new:
                block(
                    f"'git commit <pad>' faalt op een bestand dat git nog niet kent: {', '.join(new)}.",
                    f"eerst 'git add {' '.join(new)}', daarna 'git commit {' '.join(new)} -m …'.",
                )
    sys.exit(0)


if __name__ == "__main__":
    main()
