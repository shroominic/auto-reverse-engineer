# Tactics

Reverse-engineering domain knowledge. Consult this when seeding investigation paths, choosing between approaches, or when stuck.

## How to Use

- **At project start**: Read the playbook for your target type. Seed `paths.md` with the first-move sequence.
- **When choosing a path**: Use the escalation ladder to pick the right approach depth.
- **When stuck**: Check `patterns.md` for techniques you haven't tried. Check `conjectures.md` for shortcut-seeking.
- **Before any experiment**: Scan `anti-patterns.md` to avoid wasted effort.

## Playbooks

| Target Type | File |
|-------------|------|
| Android APK | `apk.md` |
| BLE / IoT Device | `ble.md` |
| Firmware / Binary | `firmware.md` |
| Network Protocol | `protocol.md` |
| Web API / Service | `web-api.md` |

## Analysis Layer Escalation

Work from cheapest to most expensive. Only escalate when the current layer cannot answer your question.

| Layer | When to Use | Typical Cost | Example Questions |
|-------|------------|--------------|-------------------|
| **1. Recon** | Always start here | Minutes | What is this file? What format? What size? |
| **2. Static analysis** | After recon identifies targets | Minutes-hours | What functions exist? What strings are present? What's the control flow? |
| **3. Dynamic analysis** | When static is insufficient | Hours | What happens at runtime? What's the actual call sequence? What data flows where? |
| **4. Network analysis** | When communication is involved | Hours | What protocol? What messages? What's encrypted? |
| **5. Crypto analysis** | When encryption is confirmed | Hours-days | What algorithm? Where are the keys? Can we recover plaintext? |
| **6. Hardware/side-channel** | Last resort, needs physical access | Days | Can we extract keys from the chip? Can we glitch past security checks? |

**Escalation criteria:** Move to the next layer when:
- You have a specific question the current layer cannot answer
- You've exhausted the useful techniques at the current layer
- Evidence from the current layer points to the next layer as the critical path

**Do not escalate when:**
- You haven't finished basic recon
- You're escalating out of frustration rather than evidence
- A cheaper technique at the current layer could still yield the answer
