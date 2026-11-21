#!/usr/bin/env python3
"""Portable compaction-proof recency anchor hook for Antigravity, Gemini CLI, and Claude Code."""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import urllib.parse

CANDIDATE_FILES = ("AGENTS.md", "GEMINI.md", "CLAUDE.md")
URI_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]+:")


def _safe_resolve(raw_path: str) -> pathlib.Path | None:
    text = raw_path.strip()
    if not text:
        return None
    if URI_SCHEME_RE.match(text):
        parsed = urllib.parse.urlparse(text)
        if parsed.scheme.lower() != "file" or parsed.netloc.lower() not in ("", "localhost"):
            return None
        text = urllib.parse.unquote(parsed.path)
        if not text:
            return None
    try:
        return pathlib.Path(text).resolve()
    except (OSError, RuntimeError, ValueError):
        try:
            return pathlib.Path(os.path.abspath(text))
        except Exception:
            return None


def _safe_process_cwd() -> pathlib.Path | None:
    try:
        cwd = pathlib.Path.cwd().resolve()
    except (OSError, RuntimeError, ValueError):
        return None
    return cwd.parent if cwd.name in (".agents", ".claude") else cwd


def resolve_candidate_dirs(payload: dict) -> list[pathlib.Path]:
    candidates: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    explicit_scope_provided = False

    def add(path: pathlib.Path | None) -> None:
        if path is not None and path not in seen:
            seen.add(path)
            candidates.append(path)

    raw_cwd = payload.get("cwd")
    if isinstance(raw_cwd, str) and raw_cwd.strip():
        explicit_scope_provided = True
        add(_safe_resolve(raw_cwd))

    ws_paths = payload.get("workspacePaths")
    if isinstance(ws_paths, list):
        for entry in reversed(ws_paths):
            if isinstance(entry, str) and entry.strip():
                explicit_scope_provided = True
                add(_safe_resolve(entry))

    if not candidates and not explicit_scope_provided:
        add(_safe_process_cwd())

    return candidates


def resolve_hook_root() -> tuple[pathlib.Path | None, bool]:
    try:
        script_path = pathlib.Path(os.path.abspath(__file__))
    except Exception:
        return None, False
    parent = script_path.parent
    if parent.name in (".agents", ".claude"):
        try:
            return parent.parent.resolve(), True
        except (OSError, RuntimeError, ValueError):
            return parent.parent, True
    if parent.name == "hooks":
        try:
            return parent.parent.resolve(), False
        except (OSError, RuntimeError, ValueError):
            return parent.parent, False
    return None, False


def _read_candidate(path: pathlib.Path) -> str | None:
    try:
        if not path.is_file():
            return None
        text = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None
    return text or None


def is_constitution_text(text: str) -> bool:
    fence_char: str | None = None
    fence_len = 0
    for raw_line in text.splitlines():
        indent = 4 if raw_line.startswith("\t") else len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.lstrip(" ")
        if fence_char is None:
            if indent >= 4:
                continue
            m = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                continue
            if stripped.startswith("#"):
                low = stripped.lower()
                if "autonomous engineering constitution" in low or "mandatory 5-step" in low:
                    return True
        else:
            if indent <= 3 and re.match(rf"^{re.escape(fence_char)}{{{fence_len},}}\s*$", stripped):
                fence_char = None
                fence_len = 0
            continue
    return False


def has_substantive_rules(text: str) -> bool:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        while line.startswith(">"):
            line = line[1:].strip()
        if not line or line.startswith("#") or line.startswith("@"):
            continue
        if re.fullmatch(r"[-*_]{3,}", line):
            continue
        if line.startswith("<!--") and line.endswith("-->"):
            continue
        if re.match(r"^[-*+]\s+@", line):
            continue
        return True
    return False


def find_constitution(
    start_dir: pathlib.Path,
    hook_root: pathlib.Path | None,
    enforce_hook_boundary: bool,
) -> tuple[pathlib.Path, str] | None:
    chain = (start_dir, *start_dir.parents)
    if enforce_hook_boundary and hook_root is not None:
        if hook_root not in chain:
            return None
        scoped_chain = chain[: chain.index(hook_root) + 1]
    else:
        scoped_chain = chain

    # Pass 1: Nearest ancestor containing the actual constitution heading
    for directory in scoped_chain:
        for fname in CANDIDATE_FILES:
            candidate = directory / fname
            text = _read_candidate(candidate)
            if text is not None and is_constitution_text(text):
                return candidate, text

    # Pass 2: Custom/translated constitution at hook root when inside that workspace
    if hook_root is not None and hook_root in scoped_chain:
        for fname in CANDIDATE_FILES:
            candidate = hook_root / fname
            text = _read_candidate(candidate)
            if text is not None and has_substantive_rules(text):
                return candidate, text

    # Pass 3: Generic nearest readable rule file fallback within workspace boundary
    for directory in scoped_chain:
        for fname in CANDIDATE_FILES:
            candidate = directory / fname
            text = _read_candidate(candidate)
            if text is not None and has_substantive_rules(text):
                return candidate, text

    return None


def main() -> None:
    payload_in: dict = {}
    if not sys.stdin.isatty():
        try:
            raw_in = sys.stdin.read().strip()
            if raw_in:
                parsed = json.loads(raw_in)
                if isinstance(parsed, dict):
                    payload_in = parsed
        except Exception:
            pass

    hook_root, enforce_hook_boundary = resolve_hook_root()
    found: tuple[pathlib.Path, str] | None = None
    for candidate_dir in resolve_candidate_dirs(payload_in):
        found = find_constitution(candidate_dir, hook_root, enforce_hook_boundary)
        if found is not None:
            break

    if found is None:
        sys.exit(0)

    _, constitution = found
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
