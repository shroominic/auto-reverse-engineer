# Network Protocol

## First Moves

1. Capture traffic: `tcpdump` or `Wireshark` during normal operation.
2. Identify transport: TCP/UDP, port numbers, TLS version.
3. If TLS: attempt MITM with `mitmproxy` or `Burp Suite`. Check for certificate pinning.
4. Isolate message boundaries. Look for length prefixes, delimiters, or fixed-size headers.
5. Correlate actions to messages. Build a message table: trigger-request-response.
6. Look for patterns: magic bytes, version fields, sequence numbers, checksums.

## Key Tools

`tcpdump`, `Wireshark`, `tshark`, `mitmproxy`, `Burp Suite`, `nmap`, `netcat`, `scapy`

## Expected Artifacts

pcap files, message boundary analysis, protocol state diagram, message format documentation.

## Escalation Triggers

- Encrypted payloads after TLS strip → application-layer encryption, inspect client binary
- Binary protocol with no obvious structure → entropy analysis per field, compare across messages
- Stateful protocol → build a state machine from observed sequences
