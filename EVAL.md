# Evaluation: is `auto-reverse-engineer` still relevant?

**Date:** 2026-09-20
**Repo state evaluated:** `cc18cfd` on `main` (last commit 2026-04-07)
**Question:** given current AI progress, is this still worth shipping — and if so, in what shape, measured how?

## Verdict

The **job** is more relevant than it was in April. The **repo as shipped is not a product**.

Autonomous reverse engineering is still unsolved. The strongest published agentic RE numbers in mid/late 2026 are well below human: SRE-Bench’s best model scores 61.4% per instance and fully solves 31.5%; CREBench’s best model recovers the flag on 59% of crypto-RE tasks versus 92% for a human expert; AgentRE-Bench v3 still fails exact reconstruction (no model recovered the true Level 23 C2 endpoint). Reveree (September 2026) localizes the failure: agents triage and map binaries, then stall at comprehension. Extra budget, persistence, and reasoning effort rescue few of those stalls. Successful runs share one behavioral signature: they **stop re-reading the binary and write a solver**.

That is exactly the loop this repo was reaching for — hypothesis, cheap experiment, record, re-rank, compound a wiki, write scripts. The idea aged well. The artifact did not.

What shipped is three markdown files and a `tmux` + `while true` wrapper around whatever coding agent the user already has. In April 2026 that was a reasonable prototype. By September 2026 the market filled the adjacent slots:

| Slot | Who owns it now | Why this repo loses |
| --- | --- | --- |
| “Talk to Ghidra” | LaurieWired/GhidraMCP (~9k stars), ReVa / `ghidra-headless-mcp` | Tool access, not a prompt, is the product |
| “RE skill for Claude/Codex” | reverse-workbench-skill, firmware-reverse-engineering, generic cyber skill packs | Distribution is Agent Skills, not a standalone prompt repo |
| “Reconstruct C from a binary” | auto-re-agent, ReVa headless | They have Ghidra, checkers, and build/test gates |
| “Did the agent understand the binary?” | SRE-Bench, AgentRE-Bench, CREBench, Reveree | They have hidden ground truth and graders |

A prompt-only framework with 9 stars, no license, no demo, no grader, and no recorded run cannot compete in those slots. People will not install this to get a slightly better `program.md`.

They **will** care if this becomes the thing those projects are not: a **long-horizon protocol-recovery lab** that takes mixed artifacts (APK + capture + optional live device), keeps evidence honest across days, and emits a **working decoder plus a cited spec**. That job is still empty. There is no public BLE/GATT/IoT protocol-recovery benchmark for agents. CTF flags and PE malware suites do not measure it. The README’s CGM example is the right *kind* of target and the wrong *public* demo.

**Ship that lab, or archive the repo.** Do not ship another markdown loop.

## What this repo actually is

`auto-reverse-engineer` is a prompt framework, not a tool. Bootstrap creates an isolated per-target workspace. The runtime prompt runs a continuous experiment loop inside it.

The durable design, not the wording, is the IP:

1. **Isolated workspace.** The framework repo stays generic. Each target gets `goal.md`, `context.md`, `progress.md`, `attempts.md` / `attempts.tsv`, `paths.md`, `inbox/`, `wiki/`, immutable `artifacts/`, and `derived/` / `scripts/` / `logs/`.
2. **Hypothesis-experiment-record.** Time-boxed attempts. Facts, hypotheses, and disproved claims are separate. Claims cite files.
3. **Path board with triggers.** Blocked work does not stop the run. Human help is queued as a trigger (`inbox/`), not as a chat interruption.
4. **Compounding wiki.** Session memory is files, not the model context window.
5. **Bias toward writing tools.** Scripts and decoders are first-class outputs.

The April history matters. The repo grew a detailed program (paths, blockers, knowledge-base rules), then repeatedly simplified. Three community PRs that pointed at the real gaps were closed unmerged:

- **PR #1** — agent-agnostic `agents.md` + a verification checklist
- **PR #2** — `tactics/` playbooks (APK, BLE, firmware, protocol, anti-patterns)
- **PR #3** — an optional “conjecture” step for layer-collapsing shortcuts

PR #2 was the highest-value of the three. The current `program.md` tells the agent *how to keep a lab notebook*. It does not tell it *what to do to a BLE stack*. Harnesses can now keep notebooks on their own. Domain procedure and a checkable output are what they still lack.

## What changed since April 2026

### The loop is now a commodity

Claude Code, Codex, Cursor, and similar harnesses internalized planning, memory, subagents, and long runs. `claude "run bootstrap.md"` plus a tmux restart loop is no longer a differentiator. It is also a worse runtime than the harnesses’ own session model.

Reveree measured this directly. On 88 picoCTF / NYU-CTF RE challenges, four prompting strategies (vanilla, ReAct, Reflexion, hypothesis ledger) were compared with the harness and tools held fixed:

- On easy picoCTF, strategy moved solve rate by **2.8 points** (0.852–0.880).
- On harder NYU-CTF, reasoning prompts helped **7–12 points**, model-dependently. Ledger tied Reflexion as Opus’s best (0.552).
- **72% of solves were solved by all four strategies.**
- The **base model dominated**. Larger, newer, or costlier models were not reliably stronger.
- Failures concentrated at comprehension. Extra budget did not fix them.

A better `program.md` will not be why people adopt this. If the prompt helps, it will show up as a small ablation on a hard, uncontaminated protocol task — not as the product.

### Tool-connected RE won the mindshare

The projects people actually clone give the agent Ghidra (or jadx, or a debugger), not a notebook format. GhidraMCP made “agent + disassembler” normal. ReVa added headless mode and context-rot control for long binaries. Headless Ghidra MCP servers expose hundreds of tools for sandboxed agents. auto-re-agent added a reverser/checker loop with build and parity gates.

This repo has **zero tool adapters**. An agent following `program.md` can call `jadx` if the user installed it. That is not a system.

### Skills ate prompt repos

The distribution format for this kind of work is now an Agent Skill / Claude plugin: `SKILL.md`, optional references, optional scripts. Firmware extraction, Ghidra-headless, APK, and generic RE skill packs already exist. A three-file GitHub repo that you paste into Claude is the 2025 packaging.

### Benchmarks arrived, and they are the wrong ones for this repo

2026 produced real agentic RE evals. They are almost all **binary comprehension / CTF / malware**:

| Bench | What it measures | Best published signal | Fit for this repo |
| --- | --- | --- | --- |
| **SRE-Bench** (Aug 2026) | Clean-room, real-scale binaries; 262 instances, 1,572 deterministic tasks | GPT-5.6-sol 61.4% / 31.5% full solve; $31.4k sweep | Use later as a *transfer* check, not the home field |
| **AgentRE-Bench** v3 (Aug 2026) | Source-free PE; evidence-grounded, hallucination-penalized | Recognition before reconstruction; exact C2 unrecovered | Good rubric for “unsupported claims” |
| **CREBench** (2026) | Crypto binary ladder: algo → key → reimplement → flag | GPT-5.4 59% flag vs human 92% | Useful crypto sub-task |
| **Reveree** (Sep 2026) | Trajectory: 8-stage schema + behavioral Markov profile | Success = pivot to solver; prompt strategy secondary | Steal the scoring idea |
| **Protocol recovery (BLE / GATT / IoT)** | Working decoder + spec from mixed artifacts | **Does not exist as a public agent bench** | **This is the opening** |

SRE-Bench’s domains include “network protocols” and “firmware”, but the unit of scoring is still binary-semantics tasks inside a bash-only mini-SWE-agent box. It does not score “here is an APK, an HCI dump, and a pairing story; emit a decoder that parses held-out traces.”

That second job is what the README already describes. Nobody has productized the eval for it.

### Existence proof, not from this repo

The Kingfisher write-up (reviving an abandoned IoT device with Claude + live BLE + a debug probe) is the demo this README implied: one agent orchestrates radio and debugger, tests hypotheses against the device, then writes a Home Assistant integration. That run was a clever one-off. This repo’s workspace + inbox + attempts ledger is the right structure to make that repeatable. It has never been shown doing so.

## What is still distinctive

Keep these. They are not commoditized.

1. **Multi-artifact, multi-day, human-in-the-loop.** Ghidra chat is one binary, one session. Real protocol recovery is an APK *and* a capture *and* a human who can press the sensor button. `paths.md` + `inbox/` + trigger conditions are still the cleanest encoding of that.
2. **The deliverable is a decoder, not a paragraph.** Reveree’s success signature is “build the solver.” This repo already wants `scripts/` and `derived/`. Lean into that until the default end state is `scripts/decode.py` plus hidden-vector tests, not `wiki/facts.md`.
3. **Evidence calibration.** AgentRE penalizes unsupported claims because models now *sound* like they reversed the thing. `facts.md` / `hypotheses.md` / `disproved.md` plus attempt TSV is the right schema if — and only if — a grader reads it.
4. **Workspace as the compounding artifact.** People will keep a `projects/<slug>/` folder the way they keep a Ghidra DB. The wiki is a byproduct of a run that produced a decoder, not the product.

What is no longer distinctive: the wiki format, the “never stop” loop, generic “be creative,” or being harness-agnostic. Every serious agent is harness-agnostic now by speaking Skills + MCP + files.

## Best releasable shape

### Positioning

**Name the job, not the method.**

> Recover an unknown protocol from mixed artifacts. Emit a working decoder and a cited spec. Keep a lab notebook so a second session, or a human, can continue.

Do not position as:

- a general autonomous reverse engineer (ReVa, GhidraMCP, auto-re-agent)
- a Claude Code skill dump (already crowded)
- a medical-device or malware product
- “better prompting for agents”

The CGM story in the README is a *private* motivation, not a launch demo. Interoperability RE of a regulated medical radio is legally and medically the wrong public artifact. Use synthetic protocols and abandoned/open devices for anything published.

### What to ship (v1 people can care about)

A small lab, not a manifesto.

```text
auto-reverse-engineer/
  skill/SKILL.md          # installable Agent Skill: when and how to run the loop
  workspace/              # templates: goal, context, attempts, paths, wiki scaffold
  program.md              # runtime loop, shortened, decoder-first
  bootstrap.md            # init only
  tactics/                # revive PR #2, one playbook per target class
  adapters/               # thin, optional: jadx, strings, btsnoop, ghidra-headless
  benches/pre/            # synthetic protocol tasks + hidden graders
  examples/toy-ble/       # one complete public run (trace + decoder + wiki)
```

Hard requirements for v1:

1. **Install as a skill.** `SKILL.md` with a trigger description. If it is not loadable by Claude Code / Codex / Cursor, it will not be used.
2. **Decoder-first success criteria.** `goal.md` templates end in “a script that parses these traces / talks this GATT service,” not “understand the protocol.”
3. **One synthetic public bench with a grader.** Unpublished framing, hidden test vectors. `are eval` prints pass/fail, spec F1, cost, wall time.
4. **One recorded run.** The wiki, attempts TSV, and decoder from that run are in `examples/`. This is the screenshot. A prompt file is not.
5. **Optional tools, required schema.** The loop must work with only `jadx`/`apktool`/`tshark`/`python`. Ghidra MCP is an accelerator, not a dependency. That is the opposite of ReVa, and it is the right split for protocol work (often the APK + capture is enough).
6. **License and safety page.** Apache-2.0 or MIT. Explicit authorized-use / no-malware-as-a-service / no-medical-advice. Without this, serious users will not touch it.

### What v1 must not include

- A new Ghidra plugin.
- A tmux babysitter as the happy path. Let the user’s harness run. Document a loop only as a fallback.
- More prompt philosophy before a number exists.
- A public CGM/Libre/Dexcom walkthrough.
- Exploit, bypass, or “pwn this device” playbooks. Interop and documentation only.

### Why this shape beats the alternatives

| Shape | Who cares | Why it dies |
| --- | --- | --- |
| Prompt pack only (current) | Almost nobody | Commoditized; Reveree says prompts are secondary |
| Ghidra agent | RE tool users | 9k-star incumbent; you will be a worse ReVa |
| Generic RE skill router | Beginners | reverse-workbench-skill already does this |
| Full product / hosted agent | Too early | No eval, no demo, hardware in the loop |
| **Protocol lab + grader + one run** | Interop hackers, IoT, researchers | Unique job + a number they can repeat |

v1 is successful if a stranger can, in one evening:

1. install the skill
2. run `benches/pre/ble-cleartext`
3. see this loop beat “just reverse this” on decoder pass rate
4. open `examples/toy-ble` and recognize the notebook they would want on a real device

Until that is true, keep the repo private or clearly experimental. Shipping markdown will not create demand.

### Revive from the closed PRs, in order

1. **`tactics/` (PR #2)** — after the grader exists, so playbooks can be ablated.
2. **`agents.md` (PR #1)** — as `SKILL.md` / `AGENTS.md`, not as a fourth manifesto.
3. **Verification (PR #1)** — only if it checks “decoder exists and tests run,” not “the wiki is tidy.”
4. **Conjecture step (PR #3)** — last. Cute, model-dependent, not the reason to clone.

## How to test and benchmark vs other methods

Do not lead with SRE-Bench or picoCTF. Those measure a different job (binary semantics / flags). Use them later as a transfer check so you can say “this harness does not *hurt* binary RE.” The home-field bench is protocol recovery.

### PRE-Bench: Protocol Recovery Evaluation

**Unit of work:** recover enough of an unpublished protocol to parse held-out traffic (and, on live tasks, to complete a documented happy-path exchange).

**Contamination rule (from SRE-Bench):** generate the protocol for the bench. Do not wrap a public CGM, a well-known IoT gadget, or a CTF challenge the models have already seen. Identity leakage is fatal in RE: once the model recognizes the device, it is not reversing.

**Artifact bundles** (give the agent a subset, score the same hidden truth):

| Bundle | What the agent gets | What this isolates |
| --- | --- | --- |
| A. App only | Companion APK or Python client | Static recovery |
| B. Capture only | HCI/`btsnoop`/PCAP + maybe GATT dump | Trace-only recovery |
| C. App + capture | Both | Correlation (the actual job) |
| D. + live | Emulated GATT server or recorded replay | Hypothesis tests against a device |
| E. Adversarial | App lies or is stale; capture is truth | Whether the notebook updates |

**Difficulty ladder** (start with three tasks; do not build 262):

1. **Cleartext framed BLE.** Length + opcode + CRC. UUIDs in the APK. Decoder should fall out of either artifact.
2. **Sessioned.** Frame + token derived from pairing material visible in the client. Needs correlation.
3. **Layered.** Custom integrity, versioned opcodes, one field only in notifications. Needs the wiki to not thrash.

Each task ships:

- `artifacts/` for the agent
- `hidden/ground_truth.json` (UUIDs, opcodes, field map, endianness, integrity)
- `hidden/vectors.bin` (traces the agent never sees)
- `hidden/grade.py` (deterministic)

The agent may write anything in its workspace. The grader only imports `scripts/decode.py` (or a declared entrypoint) and runs it on hidden vectors. No LLM-as-judge on the primary metric.

### Primary metrics

| Metric | How | Why |
| --- | --- | --- |
| **Decoder pass rate** | Hidden vectors, exact field values | The only number that means “it works” |
| **Spec F1** | Predicted UUID/opcode/field map vs `ground_truth.json` | Partial credit when the decoder is incomplete |
| **Unsupported-claim rate** | Claims in `wiki/facts.md` with no cited artifact path, or contradicted by ground truth | AgentRE’s actual contribution |
| **Time-to-first-decoder** | Wall clock to first `scripts/decode.py` that parses *public* sample traces | Operationalizes Reveree’s “pivot to solver” |
| **Stage coverage** | GATT/map → framing → fields → integrity → session → live | Stall funnel, not just pass/fail |
| **Cost** | USD, tokens, tool calls, wall clock | Frontier RE evals are expensive; this must be cheap enough to rerun |
| **Human interrupts** | `inbox/` requests issued; time blocked | Measures whether the HITL design helps or nags |
| **Contamination probe** | Model + description, no artifacts | If it scores well, the task leaked |

Do not use “quality of the wiki” as a primary metric. It will optimize for prose.

### Baselines (same model, same tools, same budget)

Hold the model and the installed tools fixed. Change only the scaffold. Otherwise you are ranking models, which Reveree already did.

| ID | Condition | What it answers |
| --- | --- | --- |
| B0 | Naive agent: “recover the protocol, write a decoder” | Is the scaffold doing anything? |
| B1 | Naive + Ghidra MCP / ReVa | Is this just missing a disassembler? |
| B2 | This repo’s loop (current `program.md`) | Honest baseline of *today* |
| B3 | v1: loop + decoder-first goal + tactics | The candidate |
| B4 | B3 minus wiki | Is the notebook load-bearing? |
| B5 | B3 minus attempts/paths | Is the bookkeeping load-bearing? |
| B6 | B3 minus tactics | Are playbooks load-bearing? |
| B7 | Human, time-capped (optional) | Calibration, not a launch gate |

Report **B3 vs B0** as the headline. If that delta is noise, do not release. Reveree’s lesson is that scaffolds often lose to the base model. This project only deserves to exist if the notebook + decoder gate changes behavior on *multi-artifact* tasks — specifically, fewer re-analysis loops and faster time-to-first-decoder.

### Suggested first experiment (cheap enough to run this month)

- 1 model family (whatever you already pay for).
- 3 PRE-Bench tasks × bundles A/B/C (9 cells).
- Conditions B0 and B3 only.
- Budget cap per cell (wall clock + dollars), declared in advance.
- 2 seeds if cost allows; otherwise say N=1 and do not overclaim.

Publish a table:

```text
task × bundle          naive pass   this pass   time-to-decoder   $
ble-cleartext / A
ble-cleartext / B
ble-cleartext / C
ble-session   / C
...
```

That table is the release. A blog post without it is not.

### Transfer checks (optional, later)

- 5–10 NYU-CTF or similar RE challenges, B0 vs B3, to show the loop does not regress flag solving.
- Do **not** claim SRE-Bench numbers unless you run their harness and their private binaries. You will not.

### What “better than other methods” is allowed to mean

Allowed:

- “On unpublished protocol-recovery tasks, this scaffold raised decoder pass rate from X to Y versus the same model with no scaffold.”
- “Time-to-first-decoder dropped, matching the solver-pivot pattern in Reveree.”
- “Unsupported factual claims in the notebook fell.”

Not allowed:

- “We beat GhidraMCP.” Different job.
- “We beat SRE-Bench.” You did not run it.
- “Agents can now RE medical devices.” That is a liability statement.

## Recommendation

**Keep the project. Change the object.**

1. Reposition as a protocol-recovery lab with a decoder-first contract.
2. Package the loop as an Agent Skill plus a workspace template.
3. Build three synthetic PRE-Bench tasks and a deterministic grader before any more prompt editing.
4. Revive `tactics/` only so it can be ablated against that grader.
5. Publish one synthetic (or abandoned-device) run, a license, and a safety page.
6. Use the CGM/OpenGlucose motivation privately if you want; do not make it the public proof.

If PRE-Bench B3 does not beat B0, the honest outcome is: the method is a good personal notebook and not a releasable system. That is still a useful result. It is not worth pretending a prompt file is a product in a year when Ghidra speaks MCP and RE benches exist.

The white space is real. The current repo is not yet the thing that occupies it.
