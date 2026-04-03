# Anti-Patterns

Mistakes that waste time. Check this list before starting an experiment.

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| **Brute-force without evidence** | Trying every tool/option blindly burns time and produces noise. | Form a hypothesis first. Choose the tool that tests it. |
| **Skipping recon** | Jumping into dynamic analysis or crypto without understanding the target. | Always run recon first. `file`, `strings`, `binwalk`, `xxd` are nearly free. |
| **Ignoring error messages** | Error strings are breadcrumbs the developer left for you. | Grep for error text in decompiled source — it leads directly to the relevant code. |
| **Analyzing the wrong layer** | Spending hours on binary analysis when the answer is in the network traffic. | Check which layer your question actually lives in before committing. |
| **Repeating failed approaches** | Retrying the same tool with the same input expecting different results. | Check `attempts.md` and `knowledge-base/disproved.md` before starting. |
| **Over-investing in one path** | Spending days on a single blocked path while ignoring ready alternatives. | Time-box experiments (15-30 min). Switch paths when blocked. |
| **Modifying source artifacts** | Accidentally patching or overwriting original files. | Always work on copies in `derived/`. Keep `artifacts/` read-only. |
| **Trusting decompiler output literally** | Decompilers produce approximations, not exact source. Variable names and types may be wrong. | Verify critical decompiler claims against actual binary behavior (dynamic analysis). |
