#!/usr/bin/env python3
"""Compaction-proof recency anchor hook for Antigravity / Claude Code."""
import json
import pathlib
import sys

cwd = pathlib.Path.cwd().resolve()
if not any((p / "AGENTS.md").exists() or (p / "GEMINI.md").exists() for p in (cwd, *cwd.parents)):
    sys.exit(0)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
constitution = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8").strip()
payload = {
    "injectSteps": [
        {
            "ephemeralMessage": (
                "MANDATORY RECENCY ANCHOR (Enforce before emitting any tool call or response):\n"
                f"{constitution}"
            )
        }
    ]
}
print(json.dumps(payload))
