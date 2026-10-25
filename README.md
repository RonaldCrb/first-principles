# First Principles: Deterministic Harnesses for Autonomous Engineering

> *"For a successful technology, reality must take precedence over public relations, for nature cannot be fooled."* — Richard Feynman

## Why This Exists

Out-of-the-box LLMs optimize for plausible completion and conversational agreement ("sycophancy"), not architectural integrity. Left unconstrained in production repositories, autonomous coding agents exhibit five predictable failure modes:

1. **Premature Emission:** Writing code on token one before tracing live callers, schemas, or execution environments.
2. **Sycophantic Execution:** Faithfully implementing a flawed or lower-leverage user premise instead of falsifying it first.
3. **The Patch-in-Place Trap:** Adding defensive `if/else` glue and adapters around dead or duplicated state instead of deleting the obsolete layer.
4. **Green-Test Theater:** Writing circular unit-test mocks that return `200 OK` while live network or container contracts fail in production.
5. **Context Entropy:** Bloating system prompts and responses with ceremonial markdown, causing multi-turn recency decay where Turn-1 invariants are forgotten by Turn 5.

This repository solves those failure modes by separating **human engineering philosophy** from **machine-executable cognitive bytecode**.

---

## Architecture: Treatise vs. Machine Bytecode

Following Dijkstra and Wirth's separation of concerns, this repository splits context by consumer:

| Artifact | Target Consumer | Purpose |
| :--- | :--- | :--- |
| **[`FIRST_PRINCIPLES.md`](FIRST_PRINCIPLES.md)** | **Humans** | The foundational treatise deriving 11 engineering laws from Tesla, Brooks, Gall, Hoare, Feynman, Dijkstra, Wirth, Pike, Lamport, Popper, Hamming, Musk, and Shannon. |
| **[`AGENTS.md`](AGENTS.md)** | **Autonomous Agents** | A dense, 15-line operational sequence ("machine bytecode") autoloaded into `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` that enforces strict pre-execution falsification and invariant continuity on every turn. |
| **[`evals/`](evals/run_eval.py)** | **Verification Harness** | Single-turn and multi-turn `/tmp` sandbox benchmark comparing unguided Baseline agents against Constitution-governed agents across multi-file engineering scenarios (`claude`, `codex`, `gemini`, `agy`). |

---

## How It Works: The Mandatory 5-Step Sequence

Every agent turn is bound to a strict cognitive state machine defined in [`AGENTS.md`](AGENTS.md):

```
[1. Observe System Reality] ──► [2. Simulate & Define Invariants] ──► [3. Delete First]
                                                                              │
[5. Top-Down Execution & Empirical Proof] ◄── [4. Falsification / Counter-Proposal Gate]
```

1. **Order Matters:** Placing the *Falsification Gate* (Step 4) after *System Observation* (Step 1), *Mental Simulation* (Step 2), and *Delete First* (Step 3) prevents cold-start agents from hallucinating counter-proposals in a vacuum before reading callers.
2. **Hard Counter-Proposal Gate:** If the user's premise is flawed or lower-leverage, the agent is forbidden from writing code and must halt with a **Counter-Proposal** (`Fatal Flaw`, `Superior Path`, `Go/No-Go`).
3. **Post-Gate Invariant Continuity:** Clearing Step 4 does not grant license for local patch myopia. During Step 5, user framing, running subagents, downstream callers, and existing tests are treated as fallible hypotheses—obsolete methods and orphaned tests are deleted rather than shimmed.
4. **Shannon Signal-to-Noise:** Responses are written in plain, natural human English—banning technobabble, filler, and ceremonial markdown to preserve attention across long conversations.

---

## Installation (Universal Cross-Harness Autoloading)

Symlink [`AGENTS.md`](AGENTS.md) into your workspace root so Claude Code, Cursor, Gemini / Antigravity, and Codex autoload the same operational bytecode:

```bash
ln -sf /path/to/first-principles/AGENTS.md ~/Workspace/AGENTS.md
ln -sf /path/to/first-principles/AGENTS.md ~/Workspace/CLAUDE.md
ln -sf /path/to/first-principles/AGENTS.md ~/Workspace/GEMINI.md
```

### Model Thinking Budget (`Medium` Effort Required)

Because [`AGENTS.md`](AGENTS.md) bans thinking out loud (*"Lead with the answer"*), the model must execute Steps 1–4 silently inside its internal `<thought>` block before emitting its first visible word:

- **Do not use `Low` effort (`5%`):** Starves the internal `<thought>` block to `0 tokens`, forcing the model to guess on Token 1 without checking callers or invariants first.
- **Avoid `High` effort (`100%`) as a default:** Multiplies token burn across every intermediate file read and causes the model to over-complicate simple tasks.
- **Use `Medium` effort (`20%`) from Turn 1:** Gives the model enough silent thinking room to run Steps 1–4 before speaking at 1/5th the token cost of `High`. Avoid flipping the effort setting mid-conversation, as changing the system header wipes the prompt cache.

---

## Empirical Sandbox Evals (`evals/`)

[`evals/run_eval.py`](evals/run_eval.py) tests whether an agent actually inspects connected files, deletes dead code, and holds its ground under user pressure—grading **both** the mutated files on disk inside disposable `/tmp` workspaces and the agent's response across single-turn and multi-turn (`--continue`) conversations:

```bash
# Instant replay of recorded live traces (zero cost / CI)
python3 evals/run_eval.py

# Run live against your installed agent CLI (auto-detects claude, codex, gemini, or agy)
python3 evals/run_eval.py --live --effort medium
```
