# Search module architecture

## Ownership boundary

The **Host owns** the runtime, public Module SDK, lifecycle and generic platform
capabilities. The **Search module will own** search interpretation, orchestration,
Search UI, result composition and Search-specific integrations.

Version 0.1.0 is only an installation bootstrap: one readiness endpoint and one
neutral, contribution-free frontend layer. It has no Search engine or persistence.

## Future provider boundary

Search will consume capabilities through the service registry and public contracts:

```text
Search module
    ↓
Service Registry / Public Contracts
    ├─ Polygon provider
    ├─ Analysis Areas provider
    ├─ Layer provider
    ├─ Statistics provider
    └─ additional modules
```

It must not import foreign module internals, read foreign ORMs, or issue cross-domain
SQL. Contracts will be introduced only after the historical behavior and actual
consumers have been characterized. Notifications remain a Slim Host capability.

## Bootstrap non-goals

- no historical Search services, DTOs, stores, or Intelligent Search UI;
- no Assistant or Analysis Areas integration;
- no database schema or migrations;
- no Host changes or private Host imports;
- no speculative provider framework.
