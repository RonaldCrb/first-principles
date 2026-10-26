#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_WORKSPACE="${1:-$(pwd)}"
TARGET_WORKSPACE="$(cd "$TARGET_WORKSPACE" && pwd)"

chmod +x "$REPO_DIR/hooks/inject_constitution.py" "$REPO_DIR/evals/run_eval.py"

for fname in AGENTS.md CLAUDE.md GEMINI.md; do
  ln -sf "$REPO_DIR/AGENTS.md" "$TARGET_WORKSPACE/$fname"
done

mkdir -p "$TARGET_WORKSPACE/.agents"
cat > "$TARGET_WORKSPACE/.agents/hooks.json" <<EOF
{
  "constitution-recency-anchor": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "python3 $REPO_DIR/hooks/inject_constitution.py",
        "timeout": 5
      }
    ]
  }
}
EOF

echo "Installed First Principles into: $TARGET_WORKSPACE"
echo "  - Symlinked AGENTS.md, CLAUDE.md, and GEMINI.md -> $REPO_DIR/AGENTS.md"
echo "  - Configured recency anchor hook -> $TARGET_WORKSPACE/.agents/hooks.json"
echo "  - Next: Ensure your model thinking budget / effort is set to Medium (20%)."
