#!/usr/bin/env bash
# PostToolUse hook: lint the file that was just edited or written.
# Python files are auto-fixed and formatted with ruff first, frontend src files with prettier first;
# only what remains is reported. Exit code 2 sends the output back to the agent so it can fix it right away.
set -u
file=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)
[ -z "$file" ] || [ ! -f "$file" ] && exit 0

# Find the repo (or worktree) root that contains the file.
root=$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null) || exit 0
rel=${file#"$root"/}

ruff_file() {
  # $1 = directory with the .venv, $2 = file relative to that directory
  [ -x "$1/.venv/bin/ruff" ] || return 0
  (cd "$1" && .venv/bin/ruff check --fix --quiet "$2" >/dev/null 2>&1; .venv/bin/ruff format --quiet "$2" >/dev/null 2>&1)
  out=$(cd "$1" && .venv/bin/ruff check "$2" 2>&1) || { echo "$out" >&2; exit 2; }
}

case "$rel" in
  backend/*.py)
    ruff_file "$root/backend" "${rel#backend/}"
    ;;
  src/*.py|tests/*.py)
    ruff_file "$root" "$rel"
    ;;
  frontend/src/*.ts|frontend/src/*.vue|frontend/e2e/*.ts)
    [ -x "$root/frontend/node_modules/.bin/eslint" ] || exit 0
    case "$rel" in
      frontend/src/*) (cd "$root/frontend" && node_modules/.bin/prettier --write --log-level silent "${rel#frontend/}" >/dev/null 2>&1) ;;
    esac
    out=$(cd "$root/frontend" && node_modules/.bin/eslint "${rel#frontend/}" 2>&1) || { echo "$out" >&2; exit 2; }
    # Design guard: the same rules as src/test/__tests__/design-guard.spec.ts, read from frontend/design-guard.json.
    if [ -f "$root/frontend/design-guard.json" ]; then
      out=$(python3 - "$root/frontend" "${rel#frontend/}" <<'PY'
import fnmatch, json, re, sys
base, rel = sys.argv[1], sys.argv[2]
rules = json.load(open(f"{base}/design-guard.json", encoding="utf-8")).get("rules", [])
text = open(f"{base}/{rel}", encoding="utf-8").read().splitlines()
hits = []
for rule in rules:
    if not any(fnmatch.fnmatch(rel, g) for g in rule.get("files", ["src/**"])):
        continue
    if any(fnmatch.fnmatch(rel, g) for g in rule.get("allow", [])):
        continue
    pattern = re.compile(rule["pattern"])
    for nr, line in enumerate(text, 1):
        if pattern.search(line):
            hits.append(f"{rel}:{nr}: {rule['message']}\n    {line.strip()}")
print("\n".join(hits))
PY
)
      [ -z "$out" ] || { printf 'design-rules.md (frontend/design-guard.json):\n%s\n' "$out" >&2; exit 2; }
    fi
    ;;
esac
exit 0
