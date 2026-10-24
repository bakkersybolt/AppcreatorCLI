#!/usr/bin/env bash
# Adds Shadcn-Vue components without the CLI's unwanted side effects.
#
# Usage (from anywhere):  frontend/scripts/shadcn-add.sh <component> [<component> ...]
#
# What it does:
#   1. backs up package.json, package-lock.json and the Tailwind css (from components.json);
#   2. runs `shadcn-vue add` and answers "n" to every overwrite question;
#   3. restores the backed-up files (runs `npm ci` only if the lockfile had changed),
#      replaces `from 'cn'` with `from '@/lib/utils'` in src/components/ui/,
#      formats the new files with Prettier, and reports new files and dependencies the new components would need.
#
# Exit code 0: components added, nothing else to do.
# Exit code 2: a new component imports a package that is not in package.json;
#              add it deliberately with `npm install <name>`.
# Override the CLI version with SHADCN_VUE_VERSION=<version>.
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <component> [<component> ...]" >&2
  exit 1
fi

SHADCN_VUE_VERSION="${SHADCN_VUE_VERSION:-2.8.2}"
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FRONTEND_DIR"

CSS_PATH="$(node -p "require('./components.json').tailwind.css")"
UI_DIR="src/components/ui"
PROTECTED=(package.json package-lock.json "$CSS_PATH")

BACKUP_DIR="$(mktemp -d)"
trap 'rm -rf "$BACKUP_DIR"' EXIT

for file in "${PROTECTED[@]}"; do
  mkdir -p "$BACKUP_DIR/$(dirname "$file")"
  cp "$file" "$BACKUP_DIR/$file"
done
find src -type f | sort > "$BACKUP_DIR/files-before.txt"

restore() {
  for file in "${PROTECTED[@]}"; do
    if ! cmp -s "$BACKUP_DIR/$file" "$file"; then
      echo "Restored: $file"
      if [[ "$file" == "$CSS_PATH" ]]; then
        echo "  (the CLI changed it; start of the diff below, apply what you really need by hand)"
        diff -u "$BACKUP_DIR/$file" "$file" | head -40 | sed 's/^/    /' || true
      fi
      cp "$BACKUP_DIR/$file" "$file"
      if [[ "$file" == "package-lock.json" ]]; then
        LOCK_CHANGED=1
      fi
    fi
  done
}

LOCK_CHANGED=0
echo "==> npx shadcn-vue@$SHADCN_VUE_VERSION add $*"
set +e
yes n | npx --yes "shadcn-vue@$SHADCN_VUE_VERSION" add "$@"
CLI_STATUS=${PIPESTATUS[1]} # PIPESTATUS[0] is `yes`, killed by SIGPIPE
set -e

# Detect dependencies the CLI tried to add, before restoring package.json.
ADDED_BY_CLI="$(node -e '
  const [before, after] = process.argv.slice(1).map((f) => require(f));
  const names = (p) => Object.keys({ ...p.dependencies, ...p.devDependencies });
  const old = new Set(names(before));
  console.log(names(after).filter((n) => !old.has(n) && n !== "cn").join(" "));
' "$BACKUP_DIR/package.json" "$FRONTEND_DIR/package.json")"

echo
echo "==> Cleaning up"
restore
if [[ "$LOCK_CHANGED" -eq 1 ]]; then
  echo "package-lock.json had changed: running npm ci to match node_modules again"
  npm ci --no-audit --no-fund
fi

# The CLI sometimes writes `import { cn } from 'cn'`.
FIXED_CN="$(grep -rlE "from ['\"]cn['\"]" "$UI_DIR" || true)"
if [[ -n "$FIXED_CN" ]]; then
  while IFS= read -r file; do
    sed -i.bak -E "s#from (['\"])cn(['\"])#from \1@/lib/utils\2#g" "$file"
    rm -f "$file.bak"
    echo "Fixed cn import: $file"
  done <<< "$FIXED_CN"
fi

find src -type f | sort > "$BACKUP_DIR/files-after.txt"
NEW_FILES="$(comm -13 "$BACKUP_DIR/files-before.txt" "$BACKUP_DIR/files-after.txt")"

# The CLI does not follow the project's Prettier settings; format the new files so `npm run lint` passes.
if [[ -n "$NEW_FILES" ]]; then
  # shellcheck disable=SC2086 # word splitting is intended: one argument per file
  npx --no-install prettier --write --log-level warn $NEW_FILES || echo "Warning: prettier failed; run npm run format"
fi

echo
if [[ -n "$NEW_FILES" ]]; then
  echo "New files:"
  echo "$NEW_FILES" | sed 's/^/  /'
  OUTSIDE_UI="$(echo "$NEW_FILES" | grep -v "^$UI_DIR/" || true)"
  if [[ -n "$OUTSIDE_UI" ]]; then
    echo "Warning: new files outside $UI_DIR/, check whether you want them:"
    echo "$OUTSIDE_UI" | sed 's/^/  /'
  fi
else
  echo "No new files (component already present, or the CLI failed)."
fi

CHANGED_EXISTING=""
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  CHANGED_EXISTING="$(git diff --name-only --relative -- src | grep -vxF -f <(printf '%s\n' "${PROTECTED[@]}") || true)"
else
  echo "(No git repository: cannot list changed existing files; check src/ yourself.)"
fi
if [[ -n "$CHANGED_EXISTING" ]]; then
  echo "Changed existing files (check with git diff):"
  echo "$CHANGED_EXISTING" | sed 's/^/  /'
fi

# Packages imported by the new files that package.json does not have.
MISSING_DEPS=""
if [[ -n "$NEW_FILES" ]]; then
  # shellcheck disable=SC2086 # word splitting is intended: one argument per file
  MISSING_DEPS="$(node -e '
    const fs = require("fs");
    const pkg = require(process.argv[1]);
    const known = new Set(Object.keys({ ...pkg.dependencies, ...pkg.devDependencies }));
    const missing = new Set();
    for (const file of process.argv.slice(2)) {
      const source = fs.readFileSync(file, "utf8");
      for (const m of source.matchAll(/(?:from|import)\s*["\x27]([^"\x27]+)["\x27]/g)) {
        const spec = m[1];
        if (spec.startsWith(".") || spec.startsWith("@/") || spec === "vue") continue;
        const name = spec.startsWith("@") ? spec.split("/").slice(0, 2).join("/") : spec.split("/")[0];
        if (!known.has(name)) missing.add(name);
      }
    }
    console.log([...missing].join(" "));
  ' "$FRONTEND_DIR/package.json" $NEW_FILES)"
fi
for dep in $ADDED_BY_CLI; do
  [[ " $MISSING_DEPS " == *" $dep "* ]] || MISSING_DEPS="${MISSING_DEPS:+$MISSING_DEPS }$dep"
done

echo
if [[ -n "$MISSING_DEPS" ]]; then
  echo "Dependencies needed but not in package.json: $MISSING_DEPS"
  echo "package.json was restored on purpose. If you really want these, add them deliberately:"
  echo "  cd frontend && npm install $MISSING_DEPS"
  echo "Otherwise remove the new component files again."
  exit 2
fi

if [[ "$CLI_STATUS" -ne 0 ]]; then
  echo "shadcn-vue add exited with code $CLI_STATUS; see its output above." >&2
  exit "$CLI_STATUS"
fi

echo "Done. No new dependencies needed. Check with: npm run lint && npm run build"
