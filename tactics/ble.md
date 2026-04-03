# BLE / IoT Device

## First Moves

1. Scan for device advertisements: `hcitool lescan` or `bluetoothctl`.
2. Connect and enumerate GATT services/characteristics: `gatttool` or `bluetoothctl`.
3. Record characteristic UUIDs, properties (read/write/notify), and initial values.
4. Capture BLE traffic with a sniffer (`nRF Sniffer`, `Ubertooth`, `btlejack`) or HCI logs.
5. Correlate app actions with BLE writes/notifications. Map command-response pairs.
6. Look for standard profiles (Heart Rate, Glucose, etc.) vs. vendor-specific UUIDs.

## Key Tools

`gatttool`, `bluetoothctl`, `hcidump`, `Wireshark` (BLE dissector), `nRF Connect`, `btlejack`, `Ubertooth`, `frida` (for companion app)

## Expected Artifacts

GATT service map, characteristic value dumps, pcap captures, command-response correlation table.

## Escalation Triggers

- Encrypted BLE payloads → inspect companion app for key exchange logic
- Bonding/pairing required → capture pairing from app, look for static keys
- Vendor-specific protocol → treat as unknown protocol (see `protocol.md`)
