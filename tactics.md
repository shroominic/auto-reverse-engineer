# Tactics

This is the reverse-engineering tactics reference for an autonomous RE project. Consult this when seeding initial investigation paths, when stuck, or when choosing between approaches. It encodes domain knowledge so you spend time on experiments, not on figuring out what to try.

## How to Use This File

- **At project start**: Read the playbook for your target type. Seed `paths.md` with the first-move sequence.
- **When choosing a path**: Use the analysis layer ladder to pick the right approach depth.
- **When stuck**: Check the pattern library for techniques you haven't tried.
- **Before any experiment**: Scan the anti-patterns to avoid wasted effort.

---

## Target-Type Playbooks

Each playbook lists a first-move sequence (do these in order before branching), key tools, and what artifacts to expect.

### Android APK

**First moves:**
1. `file` and `unzip -l` to confirm APK structure and compression.
2. `aapt2 dump badging` or parse `AndroidManifest.xml` for package name, permissions, activities, services, receivers, and SDK versions.
3. `apktool d` to decompile resources and smali. Note obfuscation level.
4. `jadx` or `cfr` to recover Java/Kotlin source. Grep for entry points: `onCreate`, `onReceive`, `onStartCommand`.
5. `strings` + `grep` across the APK for URLs, API endpoints, hardcoded keys, format strings.
6. List native libraries (`lib/`). Run `readelf -d` and `nm -D` on each `.so`.

**Key tools:** `apktool`, `jadx`, `cfr`, `dex2jar`, `frida`, `adb`, `drozer`, `objection`

**Expected artifacts:** Decompiled source tree, manifest analysis, string dumps, native lib symbol tables.

**Escalation triggers:**
- Obfuscated class/method names everywhere → try `frida` runtime hooking to trace calls
- Certificate pinning blocking traffic inspection → `objection` or `frida` to bypass
- Native crypto in `.so` files → switch to firmware/binary playbook for those libraries

### BLE / IoT Device

**First moves:**
1. Scan for device advertisements: `hcitool lescan` or `bluetoothctl`.
2. Connect and enumerate GATT services/characteristics: `gatttool` or `bluetoothctl`.
3. Record characteristic UUIDs, properties (read/write/notify), and initial values.
4. Capture BLE traffic with a sniffer (`nRF Sniffer`, `Ubertooth`, `btlejack`) or HCI logs.
5. Correlate app actions with BLE writes/notifications. Map command→response pairs.
6. Look for standard profiles (Heart Rate, Glucose, etc.) vs. vendor-specific UUIDs.

**Key tools:** `gatttool`, `bluetoothctl`, `hcidump`, `Wireshark` (BLE dissector), `nRF Connect`, `btlejack`, `Ubertooth`, `frida` (for companion app)

**Expected artifacts:** GATT service map, characteristic value dumps, pcap captures, command-response correlation table.

**Escalation triggers:**
- Encrypted BLE payloads → inspect companion app for key exchange logic
- Bonding/pairing required → capture pairing from app, look for static keys
- Vendor-specific protocol → treat as unknown protocol (see Network Protocol playbook)

### Firmware / Binary

**First moves:**
1. `file` to identify format. `binwalk` to scan for embedded filesystems, compressed sections, headers.
2. `binwalk -e` to extract. Inspect extracted filesystem structure.
3. `strings` with minimum length 8+ to find configuration, URLs, credentials, debug messages.
4. Entropy analysis: `binwalk -E`. High-entropy regions suggest encryption or compression.
5. Identify architecture: `readelf -h` or `file` on extracted ELF binaries. Note endianness.
6. Locate the main application binary. Run `nm`, `objdump -d`, or load into Ghidra/radare2.

**Key tools:** `binwalk`, `firmware-mod-kit`, `ubi_reader`, `sasquatch`, `Ghidra`, `radare2`, `IDA`, `readelf`, `objdump`, `strings`, `xxd`

**Expected artifacts:** Extracted filesystem, entropy map, string dumps, disassembly of key binaries, symbol tables.

**Escalation triggers:**
- Encrypted firmware → look for bootloader or update mechanism that holds decryption keys
- Custom RTOS (no standard filesystem) → manual carving with `dd` and entropy-guided offsets
- Anti-debug or integrity checks → static analysis first, patch only after understanding the check

### Network Protocol

**First moves:**
1. Capture traffic: `tcpdump` or `Wireshark` during normal operation.
2. Identify transport: TCP/UDP, port numbers, TLS version.
3. If TLS: attempt MITM with `mitmproxy` or `Burp Suite`. Check for certificate pinning.
4. Isolate message boundaries. Look for length prefixes, delimiters, or fixed-size headers.
5. Correlate actions to messages. Build a message table: trigger→request→response.
6. Look for patterns: magic bytes, version fields, sequence numbers, checksums.

**Key tools:** `tcpdump`, `Wireshark`, `tshark`, `mitmproxy`, `Burp Suite`, `nmap`, `netcat`, `scapy`

**Expected artifacts:** pcap files, message boundary analysis, protocol state diagram, message format documentation.

**Escalation triggers:**
- Encrypted payloads after TLS strip → application-layer encryption, inspect client binary
- Binary protocol with no obvious structure → entropy analysis per field, compare across messages
- Stateful protocol → build a state machine from observed sequences

### Web API / Service

**First moves:**
1. Map endpoints: intercept app traffic with `mitmproxy` or `Burp`. Crawl with `ffuf` or `gobuster`.
2. Identify auth mechanism: API keys, JWT, OAuth, session cookies.
3. Document request/response pairs. Note content types, status codes, error formats.
4. Test parameter boundaries: missing fields, extra fields, type mismatches, boundary values.
5. Check for undocumented endpoints: common paths (`/debug`, `/admin`, `/graphql`, `/swagger.json`).
6. Inspect client code (JS bundles, mobile app) for hardcoded endpoints and API versions.

**Key tools:** `mitmproxy`, `Burp Suite`, `curl`, `httpie`, `ffuf`, `gobuster`, `jq`, `jwt_tool`

**Expected artifacts:** Endpoint map, auth flow documentation, request/response examples, parameter schemas.

**Escalation triggers:**
- Obfuscated client JS → use browser devtools to set breakpoints on `fetch`/`XMLHttpRequest`
- GraphQL → introspection query first, then schema analysis
- Rate limiting blocking enumeration → slow down, use authenticated sessions, try different auth levels

---

## Analysis Layer Escalation

Work from cheapest to most expensive. Only escalate when the current layer cannot answer your question.

| Layer | When to Use | Typical Cost | Example Questions |
|-------|------------|--------------|-------------------|
| **1. Recon** | Always start here | Minutes | What is this file? What format? What size? |
| **2. Static analysis** | After recon identifies targets | Minutes–hours | What functions exist? What strings are present? What's the control flow? |
| **3. Dynamic analysis** | When static is insufficient | Hours | What happens at runtime? What's the actual call sequence? What data flows where? |
| **4. Network analysis** | When communication is involved | Hours | What protocol? What messages? What's encrypted? |
| **5. Crypto analysis** | When encryption is confirmed | Hours–days | What algorithm? Where are the keys? Can we recover plaintext? |
| **6. Hardware/side-channel** | Last resort, needs physical access | Days | Can we extract keys from the chip? Can we glitch past security checks? |

**Escalation criteria:** Move to the next layer when:
- You have a specific question the current layer cannot answer
- You've exhausted the useful techniques at the current layer
- Evidence from the current layer points to the next layer as the critical path

**Do not escalate when:**
- You haven't finished basic recon
- You're escalating out of frustration rather than evidence
- A cheaper technique at the current layer could still yield the answer

---

## Pattern Library

Reusable analysis patterns. Each pattern states when to apply it, what to do, and what the result tells you.

### Entropy Analysis
- **When:** You have binary data and need to distinguish encrypted, compressed, and plaintext regions.
- **Method:** `binwalk -E` or compute Shannon entropy per block. Plot across the file.
- **Interpretation:** Entropy near 1.0 (8 bits) = encrypted or compressed. Near 0.5 = code/data. Near 0 = padding/empty. Sharp transitions indicate section boundaries.

### String Cross-Referencing
- **When:** You have strings but don't know where they're used.
- **Method:** Extract strings, then `grep -r` or `xrefs` in disassembler to find code that references them.
- **Interpretation:** Error messages lead to error handlers (reveals logic). Format strings reveal data structures. URLs reveal communication endpoints. Debug strings reveal internal naming.

### Differential Analysis
- **When:** You have two versions of a binary, firmware, or protocol capture.
- **Method:** Binary diff (`radiff2`, `diaphora`, `BinDiff`) or traffic diff (compare pcaps).
- **Interpretation:** Changed functions likely relate to patched vulnerabilities or new features. Unchanged crypto routines are more likely to be standard library code.

### Protocol State Machine Reconstruction
- **When:** You're analyzing a stateful protocol.
- **Method:** Record message sequences for different operations. Identify states (idle, authenticating, streaming, etc.) and transitions (messages that cause state changes).
- **Interpretation:** The state machine reveals required message ordering, authentication gates, and which states expose the data you need.

### Symbol Recovery
- **When:** Dealing with a stripped binary.
- **Method:** (1) Check for debug symbols in separate files. (2) Match function signatures against known libraries (`FLIRT`, `rizzo`). (3) Use string references to name functions manually. (4) Compare against open-source versions of suspected libraries.
- **Interpretation:** Even partial symbol recovery dramatically accelerates understanding. Prioritize functions that handle input, crypto, and the target functionality.

### Call Graph Narrowing
- **When:** A binary is too large to analyze entirely.
- **Method:** Identify entry points relevant to your goal (e.g., the BLE callback, the API handler). Trace the call graph forward from those entry points. Ignore everything not reachable.
- **Interpretation:** Reduces the analysis surface from thousands of functions to dozens. Focus on the subgraph that processes the data you care about.

---

## Conjecture Patterns

The most powerful breakthroughs in RE come not from following playbooks, but from proposing non-obvious relationships between known facts that, if true, collapse the remaining problem. This is the difference between grinding and insight.

**When to conjecture:** After accumulating several facts in `knowledge-base/facts.md`, pause before choosing your next standard path. Ask: *is there a relationship between these facts that would make the remaining problem dramatically simpler?*

**How to conjecture:**
1. Review `knowledge-base/facts.md` for patterns you haven't explicitly connected.
2. Propose a bound, equivalence, or simplification you can't fully justify yet.
3. Identify the cheapest experiment that would confirm or disprove it.
4. Test it before continuing with standard paths.

**The test is cheap, the payoff is enormous.** A conjecture that fails costs one short experiment. A conjecture that holds can skip entire analysis layers.

### Conjecture Templates

| Type | Shape | Example | If True |
|------|-------|---------|---------|
| **Structural simplification** | "X is derived from publicly observable Y" | "The session key is derived from the device MAC address" | Skip crypto analysis entirely |
| **Behavioral equivalence** | "Custom thing X is just a wrapper around known thing Y" | "This binary protocol is protobuf with a 4-byte length prefix" | Use existing parsers instead of manual RE |
| **Invariant discovery** | "Property X always holds across all observed instances" | "The last 4 bytes are always CRC32 of the payload" | Parse messages without full format understanding |
| **Bound compression** | "The space of possibilities for X is bounded by Y" | "Distinct message types ≤ number of UI actions" | Enumerate the protocol by exercising the UI |
| **Layer collapse** | "The answer to X lives at a simpler layer than expected" | "The 'encryption' is just XOR with a static key visible in strings output" | One `strings` + `xxd` experiment replaces days of crypto analysis |

### Why This Works

Standard playbooks explore the problem space incrementally (like the Transposition Rule in self-organizing lists — steady, near-optimal, bounded regret). Conjectures are orthogonal: they propose shortcuts through the space. Most will be wrong, but the ones that hold compress the entire remaining problem into a single verification step. Always maintain both: playbook paths for steady progress, conjectures for potential breakthroughs.

---

## Anti-Patterns

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
