# Android APK

## First Moves

1. `file` and `unzip -l` to confirm APK structure and compression.
2. `aapt2 dump badging` or parse `AndroidManifest.xml` for package name, permissions, activities, services, receivers, and SDK versions.
3. `apktool d` to decompile resources and smali. Note obfuscation level.
4. `jadx` or `cfr` to recover Java/Kotlin source. Grep for entry points: `onCreate`, `onReceive`, `onStartCommand`.
5. `strings` + `grep` across the APK for URLs, API endpoints, hardcoded keys, format strings.
6. List native libraries (`lib/`). Run `readelf -d` and `nm -D` on each `.so`.

## Key Tools

`apktool`, `jadx`, `cfr`, `dex2jar`, `frida`, `adb`, `drozer`, `objection`

## Expected Artifacts

Decompiled source tree, manifest analysis, string dumps, native lib symbol tables.

## Escalation Triggers

- Obfuscated class/method names everywhere → try `frida` runtime hooking to trace calls
- Certificate pinning blocking traffic inspection → `objection` or `frida` to bypass
- Native crypto in `.so` files → switch to firmware/binary playbook for those libraries
