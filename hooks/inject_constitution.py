#!/usr/bin/env python3
"""Portable compaction-proof recency anchor hook for Antigravity, Gemini CLI, and Claude Code."""
import json
import pathlib
import sys


def resolve_start_dir(payload: dict) -> pathlib.Path:
    ws_paths = payload.get("workspacePaths")
    if isinstance(ws_paths, list) and ws_paths:
        return pathlib.Path(ws_paths[0]).resolve()
    if isinstance(payload.get("cwd"), str) and payload["cwd"]:
        return pathlib.Path(payload["cwd"]).resolve()
    cwd = pathlib.Path.cwd().resolve()
    return cwd.parent if cwd.name in (".agents", ".claude") else cwd


def find_constitution(start_dir: pathlib.Path) -> pathlib.Path | None:
    for directory in (start_dir, *start_dir.parents):
        for fname in ("AGENTS.md", "GEMINI.md", "CLAUDE.md"):
            candidate = directory / fname
            if candidate.exists():
                return candidate
    return None


def main() -> None:
    payload_in = {}
    if not sys.stdin.isatty():
        try:
            raw_in = sys.stdin.read().strip()
            if raw_in:
                payload_in = json.loads(raw_in)
        except Exception:
            pass

    start_dir = resolve_start_dir(payload_in)
    const_path = find_constitution(start_dir)
    if const_path is None:
        sys.exit(0)

    constitution = const_path.read_text(encoding="utf-8").strip()
    anchor_text = (
        "MANDATORY RECENCY ANCHOR (Enforce before emitting any tool call or response):\n"
        f"{constitution}"
    )

    if payload_in.get("hook_event_name") == "UserPromptSubmit":
        out = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": anchor_text,
            }
        }
    else:
        out = {
            "injectSteps": [
                {
                    "ephemeralMessage": anchor_text,
                }
            ]
        }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
