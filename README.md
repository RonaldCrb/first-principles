![First Principles Banner](assets/banner.png)

# First Principles: Deterministic Harnesses for Autonomous Engineering

[![CI](https://github.com/RonaldCrb/first-principles/actions/workflows/ci.yml/badge.svg)](https://github.com/RonaldCrb/first-principles/actions/workflows/ci.yml)

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

1. **Universal Epistemic Fallibility & Order:** Every unverified claim—from humans, subagents, docs, tests, or prior turns—is treated as a fallible hypothesis in Step 1. Placing the *Falsification Gate* (Step 4) after *System Observation* (Step 1), *Mental Simulation* (Step 2), and *Delete First* (Step 3) prevents cold-start agents from guessing or hallucinating counter-proposals before reading callers.
2. **Hard Counter-Proposal Gate:** If the premise is flawed or lower-leverage, the agent is forbidden from writing code and must halt with a **Counter-Proposal** (`Fatal Flaw`, `Superior Path`, `Go/No-Go`).
3. **Post-Gate Invariant Continuity & Maker-Breaker Verification:** Clearing Step 4 does not grant license for local patch myopia. During Step 5, changes propagate top-down from the state owner, obsolete methods and orphaned tests are deleted rather than shimmed, and a fresh-context **Breaker** subagent (or adversarial breaker script) attacks the modified code cold to trigger unhandled exceptions or silent state corruption.
4. **Shannon Signal-to-Noise:** Responses are written in plain, everyday human English—banning technobabble, filler, and ceremonial markdown to preserve attention across long conversations.

---

## Installation (Zero-Friction Agent or Human Setup)

If you are an **autonomous coding agent** and the user gave you this repository URL (`https://github.com/RonaldCrb/first-principles`), run the installer against the user's current workspace (`$(pwd)`):

```bash
# 1. If installing into an existing project repo (self-contained, leaves no nested git clone):
git clone https://github.com/RonaldCrb/first-principles.git /tmp/first-principles
bash /tmp/first-principles/install.sh "$(pwd)"
python3 /tmp/first-principles/evals/run_eval.py
rm -rf /tmp/first-principles

# 2. Or if installing into a multi-repo parent workspace where first-principles/ stays cloned:
git clone https://github.com/RonaldCrb/first-principles.git
bash ./first-principles/install.sh "$(pwd)"
python3 ./first-principles/evals/run_eval.py
```

`install.sh` requires **zero machine-specific paths** (safe to commit or share across macOS, Linux, and containers):
1. Installs [`AGENTS.md`](AGENTS.md) and relative symlinks (`CLAUDE.md`, `GEMINI.md`) in the target workspace root so Claude Code, Cursor, Gemini / Antigravity, and Codex autoload the same 15-line operational bytecode.
2. Installs [`hooks/inject_constitution.py`](hooks/inject_constitution.py) into `.agents/inject_constitution.py` and merges relative hook entries into both `.agents/hooks.json` (`PreInvocation` for Gemini / Antigravity) and `.claude/settings.json` (`UserPromptSubmit` for Claude Code), preserving any existing hooks so the 15-line constitution stays anchored at the tail of the context window across 1,000+ step sessions and multiple compactions.

### Model Thinking Budget (`Medium` Effort Required)

Because [`AGENTS.md`](AGENTS.md) bans thinking out loud (*"Lead with the answer"*), the model must execute Steps 1–4 silently inside its internal `<thought>` block before emitting its first visible word:

- **Do not use `Low` effort (`5%`):** Starves the internal `<thought>` block to `0 tokens`, forcing the model to guess on Token 1 without checking callers or invariants first.
- **Avoid `High` effort (`100%`) as a default:** Multiplies token burn across every intermediate file read and causes the model to over-complicate simple tasks.
- **Use `Medium` effort (`20%`) from Turn 1:** Gives the model enough silent thinking room to run Steps 1–4 before speaking at 1/5th the token cost of `High`. Avoid flipping the effort setting mid-conversation, as changing the system header wipes the prompt cache.

---

## Empirical Sandbox Evals & Zero-Key CI (`evals/`)

[`evals/run_eval.py`](evals/run_eval.py) tests whether an agent actually inspects connected files, deletes dead code, and holds its ground under user pressure across 16 production scenarios—spanning backend correctness, cross-package mock-vs-producer divergence, multi-turn sycophancy resistance, adversarial Maker-Breaker attacks, and SRE/infrastructure state invariants (Kubernetes HPA ownership conflicts, PodDisruptionBudget drain deadlocks, `terminationGracePeriodSeconds` vs `SIGTERM` drain races, Terraform ALB/ECS timeout mismatches, PostgreSQL connection-pool exhaustion, and Redis `allkeys-lru` eviction on shared Celery brokers).

### Two-Tier Verification Architecture (VCR Cassettes + Live Breaker Execution)

The benchmark separates **live LLM execution** from **deterministic CI grading** so GitHub Actions requires zero API keys, costs `$0` per push, and completes in ~2 seconds:

1. **Local Live Execution & Recording (`--live --record`):**
   Running `python3 evals/run_eval.py --live --record` on a developer machine spins up isolated git repositories with realistic commit history, executes the live CLI agent (`claude`, `codex`, `gemini`, or `agy`) in both **Baseline** (no constitution) and **Constitution** (`AGENTS.md`) modes, and records the resulting disk mutations (`files`) and final responses (`output`) into [`evals/fixtures.json`](evals/fixtures.json).
2. **Deterministic CI Replay & Live Adversarial Breaker Execution ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):**
   On every push and pull request, GitHub Actions runs `python3 evals/run_eval.py` without `--live`. The harness replays the recorded agent mutations from [`evals/fixtures.json`](evals/fixtures.json), verifies every file and response invariant defined in [`evals/cases.json`](evals/cases.json), and **executes the adversarial `breaker_assertions` Python scripts live** in temporary sandboxes (attacking the agent's SQLite schemas and parsers with cross-tenant collisions, `NaN`, `-inf`, and negative inputs) alongside end-to-end portability tests for `install.sh` and `hooks/inject_constitution.py`.

```bash
# 1. Instant CI replay + live adversarial breaker execution (zero API keys / ~2s)
python3 evals/run_eval.py

# 2. Run live against your installed agent CLI (auto-detects claude, codex, gemini, or agy)
python3 evals/run_eval.py --live --effort medium

# 3. Run specific cases live and update evals/fixtures.json
python3 evals/run_eval.py --live --record --case case-13,case-14,case-15
```

---

## Real-World Production Audits (Cold Ground-Truth Benchmarks)

Beyond synthetic sandbox traps, [`AGENTS.md`](AGENTS.md) is continuously stress-tested cold against production open-source repositories—measuring whether a Constitution-governed agent independently discovers both historical audit findings and unpatched live defects that survived existing test suites and human reviews:

### 1. THORChain Rujira (`gitlab.com/thorchain/rujira`) — `86%` Single-Pass Precision (`6/7` Real Bugs vs. `0` for Baseline)
Run cold against `rujira-fin` (`v1.3.0` / commit `332a3d28`, pre-audit snapshot) with zero internet access or audit reports:
- **5 of 7 findings matched confirmed Code4rena judge-accepted findings and subsequent `fix(fin)` commits:**
  1. **`#[serde(untagged)]` Schema vs. Runtime Deserialization Trap:** Static CosmWasm schema emitted `"additionalProperties": false`, while runtime `#[serde(untagged)]` silently matched unknown `ExecuteMsg::Trade` payloads into `SwapMsg::Min { min: None, to: None }` with zero slippage protection.
  2. **`Side::Base` Maker Fee Asset Mismatch:** `order_manager.rs` accumulated maker fees in the base asset on `Side::Base` while `swap_iter.rs` credited `fees_maker` as the quote asset, breaking contract balance invariants.
  3. **Stale Oracle Pool Desync:** Fixed-price and oracle-pegged pools failed to re-sync when the oracle price remained unchanged across blocks (`fix(fin): move pools when oracle hasn't moved`).
  4. **Zero-Offer Dust Lockup in `Pool::commit`:** Truncation to `offer == 0` locked user order dust without advancing pool state.
  5. **Unbounded Iteration Gas Exhaustion:** Uncapped order/retraction vector processing in `ExecuteMsg::Order`.
- **1 of 7 findings exposed an unpatched arithmetic panic still live on `main`:**
  - **[`packages/rujira-rs/src/interfaces/fin/tick.rs#L52-62`](https://gitlab.com/thorchain/rujira/-/blob/main/packages/rujira-rs/src/interfaces/fin/tick.rs#L52-62) (`Tick::do_truncate`):** Computes `let len = int.to_string().as_str().bytes().len() as u32;` on the 18-decimal `Decimal` numerator followed by an unchecked `let decimals: u32 = len - self.0 as u32;`. For any token pair or market-maker quote (`contracts/rujira-fin/src/market_maker/iter.rs#L68-69`) where the price (or `1 / price` on `Side::Base`) has fewer numerator digits than `self.0` (`< 10^(tick - 19)`), `len - self.0 as u32` panics with `attempt to subtract with overflow`.

### 2. Tether WDK (`github.com/tetherto/wdk*`) — 5 Unpatched Cross-Package & State-Invariant Defects
Run cold across `@tetherto/wdk`, `@tetherto/wdk-utils`, `@tetherto/wdk-wallet-evm`, `@tetherto/wdk-wallet-evm-erc-4337`, and `@tetherto/wdk-wallet-evm-7702-gasless` (verified with live Node.js reproductions):
1. **Cross-Package Mock Divergence Bypassing Account-Scope Policies (`@tetherto/wdk`):**
   - **[`src/wdk.js#L291-L305`](https://github.com/tetherto/wdk/blob/main/src/wdk.js#L291-L305) & [`src/policy/policy-registry.js#L174-L186`](https://github.com/tetherto/wdk/blob/main/src/policy/policy-registry.js#L174-L186) vs. [`@tetherto/wdk-wallet-evm/src/wallet-account-evm.js#L69`](https://github.com/tetherto/wdk-wallet-evm/blob/main/src/wallet-account-evm.js#L69):** `tests/wdk-policy.test.js` passes 3,400+ lines of unit tests because its mock `buildAccount` sets `account.path = "0'/0/0"` and `account.index = 0`. Every real WDK wallet implementation sets `account.path` to the full BIP-44 path (`"m/44'/60'/0'/0/0"` on EVM, `"m/84'/0'/0'/0/0"` on BTC) and omits `.index` (`undefined`), while `wdk.getAccountByPath('ethereum', "0'/0/0")` calls `_applyPolicies(account, { blockchain })` without `index` or relative `path` normalization—silently bypassing account-scope `DENY` and spending-cap rules (distilled into [`case-16-mock-contract-divergence`](evals/cases.json#L385-L413)).
2. **Stale `governedMethodCache` Memoisation vs. Live `collectTrustedFunctions` Prototype Walk (`@tetherto/wdk`):**
   - **[`src/policy/policy-account-proxy.js#L200-L212`](https://github.com/tetherto/wdk/blob/main/src/policy/policy-account-proxy.js#L200-L212), [`#L315`](https://github.com/tetherto/wdk/blob/main/src/policy/policy-account-proxy.js#L315), [`#L405-L428`](https://github.com/tetherto/wdk/blob/main/src/policy/policy-account-proxy.js#L405-L428):** `inheritedGovernedMethods` memoises the prototype's governed method map on the first `getAccount()` wrap, whereas `collectTrustedFunctions` walks the live prototype chain on subsequent `getAccount()` wraps and unions (`trusted.add(fn)`) any method not in the stale `governedMethodCache` into the shared `accountTrustedFunctions` set—causing callables attached to the prototype after the first wrap to execute raw on the target account after a second `getAccount()` call (bypassing `wdk#121`).
3. **BIP-84 Regtest SegWit v0 (`bcrt1q...`) & Signet BOLT11 Rejection (`@tetherto/wdk-utils`):**
   - **[`src/address-validation/bitcoin.js#L153-L158`](https://github.com/tetherto/wdk-utils/blob/main/src/address-validation/bitcoin.js#L153-L158) & [`src/bolt11/index.js#L184-L195`](https://github.com/tetherto/wdk-utils/blob/main/src/bolt11/index.js#L184-L195):** `validateBech32` omits `NETWORKS.regtest.bech32` (`'bcrt'`), rejecting all standard BIP-173 / BIP-84 regtest SegWit v0 (`bcrt1q...`) addresses generated by `@tetherto/wdk-wallet-btc` and `bolt11.decode` across `validateBitcoinAddress`, `parseBip21Request`, and `bolt11.encode`, while `FORMAT_ENCODERS.fallback_address` omits `'signet'`.
4. **Per-Call `config` Ignored in `_quoteCache` Key (`@tetherto/wdk-wallet-evm-erc-4337`):**
   - **[`src/wallet-account-evm-erc-4337.js#L407-L418`](https://github.com/tetherto/wdk-wallet-evm-erc-4337/blob/main/src/wallet-account-evm-erc-4337.js#L407-L418), [`#L474`](https://github.com/tetherto/wdk-wallet-evm-erc-4337/blob/main/src/wallet-account-evm-erc-4337.js#L474):** Unlike `wdk-wallet-evm-7702-gasless`, `WalletAccountEvmErc4337._getTxKey(tx)` keys `this._quoteCache` solely by `tx`, ignoring per-call `config` overrides (`isSponsored`, `useNativeCoins`, `paymasterToken`, `paymasterAddress`, `sponsorshipPolicyId`) and reusing incompatible cached `UserOperation` quotes on subsequent `sendTransaction(tx, config)` calls.
5. **Broken Private Signer Coupling, Removed `_ownerAccount.index` Getter, and `>=` Max-Fee Off-by-One (`@tetherto/wdk-wallet-evm-erc-4337` & `@tetherto/wdk-wallet-evm-7702-gasless`):**
   - **[`wallet-account-evm-erc-4337.js#L86,L126,L508`](https://github.com/tetherto/wdk-wallet-evm-erc-4337/blob/main/src/wallet-account-evm-erc-4337.js#L508) & [`wallet-account-evm-7702-gasless.js#L117,L361`](https://github.com/tetherto/wdk-wallet-evm-7702-gasless/blob/main/src/wallet-account-evm-7702-gasless.js#L361):** `_signUserOperation` reaches into `this._ownerAccount._signer._account.signingKey` (which is `undefined` when `_ownerAccount` uses `PrivateKeySignerEvm`), both packages delegate `get index()` to `this._ownerAccount.index` (removed in `@tetherto/wdk-wallet-evm@1.0.0-beta.24`), and `7702-gasless` `transfer()` uses `prepared.fee >= transferMaxFee` instead of `>`.

