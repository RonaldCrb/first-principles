#!/usr/bin/env python3
"""
Agentic Sandbox Benchmark for first-principles/AGENTS.md
Runs single-turn and multi-turn engineering scenarios inside isolated /tmp workspaces
across agent CLIs (claude, codex, gemini, agy) or replays recorded runs from fixtures.json.

Usage:
  python3 evals/run_eval.py                         # Replay recorded runs (instant / CI)
  python3 evals/run_eval.py --live                  # Run live via auto-detected CLI (claude/codex/gemini/agy)
  python3 evals/run_eval.py --live --runner claude  # Force a specific CLI runner
  python3 evals/run_eval.py --live --record         # Run live and update fixtures.json
  python3 evals/run_eval.py --live --case <id>      # Run only a specific case ID
"""
import argparse, json, os, pathlib, shutil, subprocess, tempfile

DIR = pathlib.Path(__file__).resolve().parent
CONSTITUTION_PATH = DIR.parent / "AGENTS.md"
CASES_PATH = DIR / "cases.json"
FIXTURES_PATH = DIR / "fixtures.json"


def detect_runner(preferred: str) -> str:
    if preferred != "auto":
        return preferred
    for cmd in ("claude", "codex", "gemini", "agy"):
        if shutil.which(cmd) or (pathlib.Path.home() / ".local" / "bin" / cmd).exists():
            return cmd
    raise RuntimeError("No supported agent CLI found (claude, codex, gemini, agy).")


def build_cli_cmd(runner: str, effort: str, model: str, prompt: str, is_continuation: bool) -> list[str]:
    if runner == "agy":
        bin_path = shutil.which("agy") or str(pathlib.Path.home() / ".local" / "bin" / "agy")
        cmd = [bin_path]
        if is_continuation:
            cmd.append("-c")
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["-p", prompt, "--effort", effort, "--dangerously-skip-permissions"])
        return cmd
    if runner == "claude":
        cmd = ["claude"]
        if is_continuation:
            cmd.append("-c")
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["-p", prompt, "--dangerously-skip-permissions"])
        return cmd
    if runner == "gemini":
        return ["gemini", "-p", prompt, "--yolo"]
    if runner == "codex":
        return ["codex", "exec", prompt, "--full-auto"]
    raise ValueError(f"Unknown runner: {runner}")


def run_cli_in_sandbox(runner: str, effort: str, model: str, with_constitution: bool, case: dict) -> dict:
    sandbox_root = pathlib.Path.home() / ".cache" / "fp_evals"
    sandbox_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="workspace_", dir=sandbox_root) as tmp:
        tmp_path = pathlib.Path(tmp)
        for fname, content in case["files"].items():
            fpath = tmp_path / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")

        if with_constitution:
            const_text = CONSTITUTION_PATH.read_text(encoding="utf-8")
            for rule_file in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
                (tmp_path / rule_file).write_text(const_text, encoding="utf-8")

        env = os.environ.copy()
        if not with_constitution:
            env["FP_NO_CONSTITUTION"] = "1"
        turns = case.get("turns") or [case["prompt"]]
        turn_outputs = []
        for idx, prompt in enumerate(turns):
            cmd = build_cli_cmd(runner, effort, model, prompt, is_continuation=(idx > 0))
            proc = subprocess.run(cmd, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=180)
            out = (proc.stdout or "").strip()
            if "MANDATORY RECENCY ANCHOR" in out:
                out = out.split("MANDATORY RECENCY ANCHOR")[0].strip()
            turn_outputs.append(out)

        final_files = {}
        for fname in case["files"]:
            fpath = tmp_path / fname
            final_files[fname] = fpath.read_text(encoding="utf-8") if fpath.exists() else "<DELETED>"

        return {
            "output": turn_outputs[-1],
            "turn_outputs": turn_outputs,
            "files": final_files,
        }


def grade(result: dict, case: dict) -> tuple[bool, str]:
    output = result["output"]
    files = result["files"]

    for fname, bad_list in case.get("forbidden_file_substrings", {}).items():
        file_content = files.get(fname, "")
        for bad in bad_list:
            if bad in file_content:
                return False, f"Modified {fname} with forbidden pattern '{bad}'"

    for fname, req_list in case.get("required_file_substrings", {}).items():
        file_content = files.get(fname, "")
        for req in req_list:
            if req not in file_content:
                return False, f"Removed required invariant '{req}' from {fname}"

    for bad_out in case.get("forbidden_output_substrings", []):
        if bad_out.lower() in output.lower():
            return False, f"Sycophantically agreed ('{bad_out}')"

    req_any = case.get("required_output_any", [])
    if req_any and not any(tok.lower() in output.lower() for tok in req_any):
        return False, f"Missed required diagnosis (expected one of {req_any})"

    breaker_assertions = case.get("breaker_assertions", [])
    if breaker_assertions:
        with tempfile.TemporaryDirectory(prefix="breaker_") as btmp:
            bpath = pathlib.Path(btmp)
            for fname, content in files.items():
                if content != "<DELETED>":
                    (bpath / fname).write_text(content, encoding="utf-8")
            for assertion in breaker_assertions:
                proc = subprocess.run(
                    ["python3", "-c", assertion],
                    cwd=bpath,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if proc.returncode != 0:
                    err = (proc.stderr or proc.stdout or "").strip().splitlines()
                    last_line = err[-1] if err else "assertion failed"
                    return False, f"Breaker test broke implementation: `{assertion}` -> {last_line}"

    return True, "PASS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run live against an agent CLI in /tmp sandboxes")
    parser.add_argument("--runner", default="auto", choices=["auto", "claude", "codex", "gemini", "agy"])
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--model", default="", help="Optional model ID override (e.g. claude-sonnet-5-5-medium)")
    parser.add_argument("--record", action="store_true", help="Save live results to fixtures.json")
    parser.add_argument("--case", default="", help="Filter to a single case ID")
    args = parser.parse_args()

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
    fixtures = json.loads(FIXTURES_PATH.read_text(encoding="utf-8")) if FIXTURES_PATH.exists() else {}
    runner = detect_runner(args.runner) if args.live else "fixture"

    for mode, with_const in [("BASELINE (No Constitution)", False), ("CONSTITUTION (AGENTS.md)", True)]:
        passed = 0
        fixtures.setdefault(mode, {})
        label = f"LIVE: {runner} ({args.model or args.effort})" if args.live else "RECORDED TRACE"
        print(f"\n=== {mode} [{label}] ===")
        for c in cases:
            if args.live:
                res = run_cli_in_sandbox(runner, args.effort, args.model, with_const, c)
                fixtures[mode][c["id"]] = res
            else:
                res = fixtures[mode][c["id"]]
            ok, reason = grade(res, c)
            passed += int(ok)
            turns_tag = f" ({len(c.get('turns', [1]))}-turn)" if "turns" in c else ""
            print(f"  [{'PASS' if ok else 'FAIL'}] {c['id']}{turns_tag}: {reason}")
        print(f"Score: {passed}/{len(cases)} ({passed / len(cases) * 100:.0f}%)")

    if args.live and args.record:
        FIXTURES_PATH.write_text(json.dumps(fixtures, indent=2) + "\n", encoding="utf-8")
        print(f"\nRecorded live traces to {FIXTURES_PATH}")


if __name__ == "__main__":
    main()
