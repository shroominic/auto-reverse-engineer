# Web API / Service

## First Moves

1. Map endpoints: intercept app traffic with `mitmproxy` or `Burp`. Crawl with `ffuf` or `gobuster`.
2. Identify auth mechanism: API keys, JWT, OAuth, session cookies.
3. Document request/response pairs. Note content types, status codes, error formats.
4. Test parameter boundaries: missing fields, extra fields, type mismatches, boundary values.
5. Check for undocumented endpoints: common paths (`/debug`, `/admin`, `/graphql`, `/swagger.json`).
6. Inspect client code (JS bundles, mobile app) for hardcoded endpoints and API versions.

## Key Tools

`mitmproxy`, `Burp Suite`, `curl`, `httpie`, `ffuf`, `gobuster`, `jq`, `jwt_tool`

## Expected Artifacts

Endpoint map, auth flow documentation, request/response examples, parameter schemas.

## Escalation Triggers

- Obfuscated client JS → use browser devtools to set breakpoints on `fetch`/`XMLHttpRequest`
- GraphQL → introspection query first, then schema analysis
- Rate limiting blocking enumeration → slow down, use authenticated sessions, try different auth levels
