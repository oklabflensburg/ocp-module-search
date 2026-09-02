# ocp-module-search

Installable Search module for the Open City Planner. It will eventually own the
Search and Intelligent Search functionality removed from the Slim Host.

> **Status: bootstrap / pre-functional.** Version 0.1.0 proves packaging,
> discovery, and lifecycle integration. It does not implement production search.

## Surfaces

- `ocp-module-search`: Python package with an SDK `ModuleDefinition` and a small
  `/api/v1/search/module-info` installation-readiness endpoint.
- `@open-city-planner/search`: frontend package exposing only the neutral
  `search.bootstrap` discovery capability. There is deliberately no Search UI.
- `search-0.1.0.ocp`: reproducible bundle containing both packages and the manifest.

There are no database models, migrations, domain SQL, notification extensions,
or private Host imports.

## Development

```bash
cd backend
uv sync --frozen --extra dev
uv run ruff check src tests
uv run pytest
uv build --wheel

cd ../frontend
pnpm install --frozen-lockfile
pnpm typecheck
pnpm test
pnpm build

cd ..
scripts/build-bundle
scripts/host-contract-test
```

## Follow-up

Characterize the historical Host Search implementation before functional migration.
Provider contracts and Intelligent Search will be designed in later issues from
real consumer requirements, rather than being invented as a generic mega-API.
