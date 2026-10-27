#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_WORKSPACE="${1:-$(pwd)}"
TARGET_WORKSPACE="$(cd "$TARGET_WORKSPACE" && pwd)"

chmod +x "$REPO_DIR/hooks/inject_constitution.py" "$REPO_DIR/evals/run_eval.py"

mkdir -p "$TARGET_WORKSPACE/.agents"

if [ "$TARGET_WORKSPACE" = "$REPO_DIR" ]; then
  # Installed directly inside the cloned first-principles repository
  ln -sf "AGENTS.md" "$TARGET_WORKSPACE/CLAUDE.md"
  ln -sf "AGENTS.md" "$TARGET_WORKSPACE/GEMINI.md"
  ln -sf "../hooks/inject_constitution.py" "$TARGET_WORKSPACE/.agents/inject_constitution.py"
elif [[ "$REPO_DIR" == "$TARGET_WORKSPACE/"* ]]; then
  # first-principles lives as a subdirectory inside TARGET_WORKSPACE (e.g., multi-repo workspace)
  REL_REPO="${REPO_DIR#$TARGET_WORKSPACE/}"
  for fname in AGENTS.md CLAUDE.md GEMINI.md; do
    ln -sf "$REL_REPO/AGENTS.md" "$TARGET_WORKSPACE/$fname"
  done
  ln -sf "../$REL_REPO/hooks/inject_constitution.py" "$TARGET_WORKSPACE/.agents/inject_constitution.py"
else
  # Installed from an external clone (e.g., /tmp/first-principles) into a standalone project
  cp "$REPO_DIR/AGENTS.md" "$TARGET_WORKSPACE/AGENTS.md"
  cp "$REPO_DIR/FIRST_PRINCIPLES.md" "$TARGET_WORKSPACE/FIRST_PRINCIPLES.md"
  ln -sf "AGENTS.md" "$TARGET_WORKSPACE/CLAUDE.md"
  ln -sf "AGENTS.md" "$TARGET_WORKSPACE/GEMINI.md"
  cp "$REPO_DIR/hooks/inject_constitution.py" "$TARGET_WORKSPACE/.agents/inject_constitution.py"
  chmod +x "$TARGET_WORKSPACE/.agents/inject_constitution.py"
fi

# Merge Antigravity / Gemini hook into .agents/hooks.json without clobbering existing hooks
python3 - "$TARGET_WORKSPACE/.agents/hooks.json" <<'PY'
import json, pathlib, sys

hooks_path = pathlib.Path(sys.argv[1])
data = {}
if hooks_path.exists():
    try:
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
    except Exception:
        data = {}

data["constitution-recency-anchor"] = {
    "enabled": True,
    "PreInvocation": [
        {
            "type": "command",
            "command": "[ -f .agents/inject_constitution.py ] && python3 .agents/inject_constitution.py || python3 ./inject_constitution.py",
            "timeout": 5,
        }
    ],
}
hooks_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY

echo "Installed First Principles into: $TARGET_WORKSPACE"
echo "  - Rules configured: AGENTS.md, CLAUDE.md, GEMINI.md (portable relative links/files)"
echo "  - Recency hook configured: .agents/hooks.json -> .agents/inject_constitution.py"
echo "  - Next: Set your model thinking budget / effort to Medium (20%)."
