# Conjecture Patterns

The most powerful breakthroughs in RE come not from following playbooks, but from proposing non-obvious relationships between known facts that, if true, collapse the remaining problem.

## When to Conjecture

After accumulating several facts in `knowledge-base/facts.md`, pause before choosing your next standard path. Ask: *is there a relationship between these facts that would make the remaining problem dramatically simpler?*

## How to Conjecture

1. Review `knowledge-base/facts.md` for patterns you haven't explicitly connected.
2. Propose a bound, equivalence, or simplification you can't fully justify yet.
3. Identify the cheapest experiment that would confirm or disprove it.
4. Test it before continuing with standard paths.

**The test is cheap, the payoff is enormous.** A conjecture that fails costs one short experiment. A conjecture that holds can skip entire analysis layers.

## Conjecture Templates

| Type | Shape | Example | If True |
|------|-------|---------|---------|
| **Structural simplification** | "X is derived from publicly observable Y" | "The session key is derived from the device MAC address" | Skip crypto analysis entirely |
| **Behavioral equivalence** | "Custom thing X is just a wrapper around known thing Y" | "This binary protocol is protobuf with a 4-byte length prefix" | Use existing parsers instead of manual RE |
| **Invariant discovery** | "Property X always holds across all observed instances" | "The last 4 bytes are always CRC32 of the payload" | Parse messages without full format understanding |
| **Bound compression** | "The space of possibilities for X is bounded by Y" | "Distinct message types ≤ number of UI actions" | Enumerate the protocol by exercising the UI |
| **Layer collapse** | "The answer to X lives at a simpler layer than expected" | "The 'encryption' is just XOR with a static key visible in strings output" | One `strings` + `xxd` experiment replaces days of crypto analysis |

## Why This Works

Standard playbooks explore the problem space incrementally — steady, near-optimal, bounded regret. Conjectures are orthogonal: they propose shortcuts through the space. Most will be wrong, but the ones that hold compress the entire remaining problem into a single verification step. Always maintain both: playbook paths for steady progress, conjectures for potential breakthroughs.
