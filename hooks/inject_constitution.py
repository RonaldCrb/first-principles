#!/usr/bin/env python3
"""Compaction-proof recency anchor hook for Antigravity / Claude Code."""
import json
import os
import pathlib
import sys

if os.environ.get("FP_NO_CONSTITUTION") == "1":
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
