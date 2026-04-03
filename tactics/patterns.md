# Analysis Patterns

Reusable analysis patterns. Each states when to apply it, what to do, and what the result tells you.

## Entropy Analysis
- **When:** You have binary data and need to distinguish encrypted, compressed, and plaintext regions.
- **Method:** `binwalk -E` or compute Shannon entropy per block. Plot across the file.
- **Interpretation:** Entropy near 1.0 (8 bits) = encrypted or compressed. Near 0.5 = code/data. Near 0 = padding/empty. Sharp transitions indicate section boundaries.

## String Cross-Referencing
- **When:** You have strings but don't know where they're used.
- **Method:** Extract strings, then `grep -r` or `xrefs` in disassembler to find code that references them.
- **Interpretation:** Error messages lead to error handlers (reveals logic). Format strings reveal data structures. URLs reveal communication endpoints. Debug strings reveal internal naming.

## Differential Analysis
- **When:** You have two versions of a binary, firmware, or protocol capture.
- **Method:** Binary diff (`radiff2`, `diaphora`, `BinDiff`) or traffic diff (compare pcaps).
- **Interpretation:** Changed functions likely relate to patched vulnerabilities or new features. Unchanged crypto routines are more likely to be standard library code.

## Protocol State Machine Reconstruction
- **When:** You're analyzing a stateful protocol.
- **Method:** Record message sequences for different operations. Identify states (idle, authenticating, streaming, etc.) and transitions (messages that cause state changes).
- **Interpretation:** The state machine reveals required message ordering, authentication gates, and which states expose the data you need.

## Symbol Recovery
- **When:** Dealing with a stripped binary.
- **Method:** (1) Check for debug symbols in separate files. (2) Match function signatures against known libraries (`FLIRT`, `rizzo`). (3) Use string references to name functions manually. (4) Compare against open-source versions of suspected libraries.
- **Interpretation:** Even partial symbol recovery dramatically accelerates understanding. Prioritize functions that handle input, crypto, and the target functionality.

## Call Graph Narrowing
- **When:** A binary is too large to analyze entirely.
- **Method:** Identify entry points relevant to your goal (e.g., the BLE callback, the API handler). Trace the call graph forward from those entry points. Ignore everything not reachable.
- **Interpretation:** Reduces the analysis surface from thousands of functions to dozens. Focus on the subgraph that processes the data you care about.
