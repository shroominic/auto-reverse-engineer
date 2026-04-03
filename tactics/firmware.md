# Firmware / Binary

## First Moves

1. `file` to identify format. `binwalk` to scan for embedded filesystems, compressed sections, headers.
2. `binwalk -e` to extract. Inspect extracted filesystem structure.
3. `strings` with minimum length 8+ to find configuration, URLs, credentials, debug messages.
4. Entropy analysis: `binwalk -E`. High-entropy regions suggest encryption or compression.
5. Identify architecture: `readelf -h` or `file` on extracted ELF binaries. Note endianness.
6. Locate the main application binary. Run `nm`, `objdump -d`, or load into Ghidra/radare2.

## Key Tools

`binwalk`, `firmware-mod-kit`, `ubi_reader`, `sasquatch`, `Ghidra`, `radare2`, `IDA`, `readelf`, `objdump`, `strings`, `xxd`

## Expected Artifacts

Extracted filesystem, entropy map, string dumps, disassembly of key binaries, symbol tables.

## Escalation Triggers

- Encrypted firmware → look for bootloader or update mechanism that holds decryption keys
- Custom RTOS (no standard filesystem) → manual carving with `dd` and entropy-guided offsets
- Anti-debug or integrity checks → static analysis first, patch only after understanding the check
