# Search Dependency Matrix

This matrix summarizes the direct dependencies and target ownership derived from
the historical Host Search at
`410e9ba5dff2e3ed702d1a4ced95a5e5524cb52e`. Candidate contracts are design inputs,
not committed SDK contracts.

## Dependency matrix

| Dependency | Historical usage | Private/direct? | Target owner | Future access | Required? | Contract candidate |
| --- | --- | --- | --- | --- | --- | --- |
| FastAPI router | Two public POST routes | Host framework import | Search | Module API registrar | Required platform | Existing `context.api` |
| Async DB session | Route, interpreter and executor | Host DB import | Provider owner | Provider-owned transactions; Search only if its own persistence ever exists | Not for core Search data | Existing database port, no new Search DB contract |
| Public query security | Rate limit and PostgreSQL statement timeout | Private Host service | Host | Public query port at Search route boundary | Required platform | Existing `context.public_queries` |
| Analysis Area ORM/table | Scan names/slugs; spatial target | Private persistence/direct SQL | Analysis Areas | Provider via `context.services` | Optional | SDK `SearchProviderPort` at `analysis-areas.search@1` |
| Analysis Area legacy queries | GeoJSON, detail, bbox, area size, analytics, comparison | Private application import | Analysis Areas | Domain-owned provider or narrowly public existing service | Optional | `analysis-areas.search@1`; existing `analysis-areas.lookup@1` is partial |
| Polygon filter constants | Validate categories, status, floors, size, business structure, sources | Private foreign schema | Polygon/provider owners | Provider descriptor/result contract | Optional | Fields/descriptors in common provider DTOs |
| `user_polygons` | Area-scoped features/counts with domain filters | Direct SQL | Host Polygon capability | Host-provided Search provider | Optional | `platform.polygon-search@1` |
| `polygon_analysis_areas` | Scope polygons to selected area | Direct cross-domain join | Analysis Areas/Polygon integration | Hidden behind provider | Optional | Same Polygon provider; no join DTO |
| `polygon_osm_sources` | Deduplicate OSM linked to polygons | Direct cross-domain read | Polygon/OSM integration | Provider-owned dedup or Search resource identity policy | Optional | Provider result canonical/resource identity |
| `osm_features` | Spatially select/count nodes, ways and relations | Direct SQL | Host OSM capability | Host-provided Search provider | Optional | `platform.osm-search@1` |
| OSM canonical SQL helpers | Derive category/status/floor | Private Host import | OSM classification owner | Inside OSM provider | Optional | No SQL helper in contract |
| Statistics | Catalog string and Assistant UI only; no deterministic Search call | Indirect/UI leakage | Statistics/Assistant | None for Search parity | No | No Search contract; `statistics.query@1` remains for actual consumers |
| Assistant catalog imports | Assistant reused labels, synonyms and normalization | Reverse private dependency | Search | Assistant may consume a future public Search API | No | Separate public Search consumer API only if needed |
| Assistant Search executor reuse | Assistant tool built `SearchPlan` and called executor | Reverse private dependency | Search | Assistant calls Search service/API later | No | Search consumer contract, not Search -> Assistant |
| Assistant HTTP endpoint | Final Search store submitted every query | Direct wrong-way frontend dependency | Assistant | Remove from standalone Search UI | No | None |
| Pinia filter store | Apply `UPDATE_FILTERS` | Private Host frontend store | Host frontend capability | Public filter action/contribution | Needed for filter commands only | Host frontend prerequisite candidate |
| Pinia map store | Store map actions and select area | Private Host frontend store | Host map | Public map/selection contribution | Needed for map behavior | Host frontend prerequisite candidate |
| OSM viewport store | Toggle point/area visibility | Private Host frontend store | Host/OSM UI | Public layer/filter action | Optional | Host frontend prerequisite candidate |
| MapLibre Search source/layers | Persistent GeoJSON overlay and fit | Host implementation detail | Host map | Provider-neutral map target | Needed for map behavior | SDK/frontend `SearchMapTarget` candidate |
| Nuxt routing | Documentation link only; no resource navigation | Hard-coded allowlist | Provider/frontend router owner | Opaque/typed navigation contribution | Optional | SDK/frontend `SearchNavigationTarget` candidate |
| Raw query logs | No explicit Search logging | None | Search/Host observability | Do not log raw query; bounded outcome/timing | No | Existing logger/metrics/tracing ports |

## Historical private import inventory

| File | Import | Category | Replacement direction |
| --- | --- | --- | --- |
| `api/search.py` | `app.db.session.get_session` | Private Host | Module database/public route facilities only as needed |
| `api/search.py` | `app.services.public_query_security` | Private Host | Existing public-query port |
| `api/search.py` | Search schemas/interpreter/executor | Same Search domain | Module-owned internal imports |
| `search_catalog.py` | `app.schemas.polygon_filters` | Private Polygon/Host | Provider descriptors or public DTO constraints |
| `search_interpreter.py` | `app.modules.analysis_areas.persistence.models.AnalysisArea` | Private Analysis Areas persistence | `analysis-areas.search@1` provider |
| `search_interpreter.py` | Search schema/catalog | Same Search domain | Module-owned internal imports |
| `search_executor.py` | `analysis_areas.application.legacy_queries` | Private Analysis Areas application | Analysis Areas provider/public service |
| `search_executor.py` | `app.services.osm_canonical` | Private Host OSM | OSM provider |
| `search_executor.py` | Search schemas | Same Search domain | Module-owned internal imports |
| `schemas/search.py` | `app.schemas.polygon_filters` | Private Polygon/Host | Common primitive DTOs plus provider validation |
| All backend files | Python, Pydantic, SQLAlchemy, FastAPI | Generic framework | Allowed only where module architecture permits |

There were no public SDK imports in the historical Search files because they
predated the external module boundary.

## Target ownership matrix

| Area | Search owns | Provider/Host owns | Boundary |
| --- | --- | --- | --- |
| Query parsing | Length, normalization, locale, generic syntax | Domain aliases and constraints | Provider descriptors/request |
| Intent classification | Generic search/action decision and unsupported behavior | Whether/how a domain can satisfy it | Provider capability metadata |
| Provider discovery | Bounded orchestration and deterministic order | Registration under owner namespace | `context.services` only |
| Provider execution | Deadline, cancellation and partial-result policy | Query, auth, data access and local errors | Common `SearchProviderPort` candidate |
| Ranking | Global normalization, sort and tie-breaks | Provider-local relevance | Validated local score |
| Result normalization | Stable `SearchResult`/batch/API | Public domain projection | Common DTOs |
| Analysis Areas searching | Dispatch/merge | Names, hierarchy, geometry, detail route | `analysis-areas.search@1` candidate |
| OSM searching | Dispatch/merge | Tags, canonical classes, spatial query, OSM identity | `platform.osm-search@1` candidate |
| Polygon searching | Dispatch/merge | Visibility, filters, spatial assignment, identity | `platform.polygon-search@1` candidate |
| Navigation metadata | Transport/validate | Canonical provider resource destination | Opaque or typed navigation target |
| Map target metadata | Normalize bounds/geometry/selection | Domain geometry/resource meaning; Host renders | EPSG:4326 map target |
| Filter side effect | Search command presentation | Host applies public filter action | Frontend contribution candidate |
| Statistics | Nothing for historical Search parity | Statistics/Assistant | No dependency |
| Assistant | Nothing required | Optional downstream consumer | One-way Assistant -> Search |

## Required versus optional

| Capability/provider | Classification | Degraded behavior when absent |
| --- | --- | --- |
| Host module lifecycle, API registrar, service registry and public-query guard | Required platform | Search module cannot register safely |
| Analysis Areas Search provider | Optional module-provided | No area results or area-scoped commands; other providers remain usable if they support non-area queries |
| Polygon Search provider | Optional host-provided | No Stadtplaner polygon hits/counts |
| OSM Search provider | Optional host-provided | No OSM/POI hits/counts |
| Statistics | None for parity; optional only after a separate use case | No effect on core Search |
| Assistant | None | Search remains fully usable |

The module manifest should not declare optional providers until their service IDs,
versions and provider modules are real. This task changes no manifest or SDK.

## Contract candidates

| Contract name | Service ID | Version | Producer | Consumer | Methods / DTOs | Required? |
| --- | --- | --- | --- | --- | --- | --- |
| `SearchProviderPort` | `analysis-areas.search` | 1 | Analysis Areas | Search | `search(SearchProviderRequest) -> SearchResultBatch` | Optional |
| `SearchProviderPort` | `platform.polygon-search` | 1 | Host Polygon capability | Search | Same common method and DTOs | Optional |
| `SearchProviderPort` | `platform.osm-search` | 1 | Host OSM capability | Search | Same common method and DTOs | Optional |
| Search consumer/orchestration service, if Assistant needs in-process access | `search.query` | 1 | Search | Assistant/other modules | `search(SearchRequest) -> SearchResponse` | Optional to consumers; not needed for Search HTTP |

Candidate common DTO requirements:

- request: normalized query, locale, bounded limit, optional public spatial/filter
  context, deadline/cancellation context and authorization-safe principal scope;
- result: provider ID, kind, title/subtitle, provider-local relevance, opaque
  resource reference, optional navigation/map targets and bounded public metadata;
- batch: immutable items, truncation/total information and structured warnings;
- no SQLAlchemy session/ORM, provider callbacks, raw exception, secrets or private
  user fields.

Under the existing registry rule, service IDs belong to producers. A service ID
such as `search.provider.analysis-areas` would incorrectly claim Search ownership
for an Analysis Areas registration. Uniform contract identity likely requires a
public SDK `SearchProviderPort`; that is a prerequisite candidate, not an SDK change
in this task.

The registry currently resolves exact service ID/version pairs and does not
enumerate all `SearchProviderPort` implementations. The contract follow-up must
choose between a finite manifest-declared provider list and a minimal, explicit
provider-discovery addition. It must not create `context.search` or another bespoke
context slot.

## Migration constraints

- Do not port the five direct cross-domain table reads.
- Do not reuse private Analysis Areas application/persistence imports or OSM SQL
  helpers.
- Do not make Statistics or Assistant required.
- Do not expose the historical `data: Any` response as the new normal form.
- Preserve public-only projections and move future visibility checks into each
  provider.
- Preserve deterministic limits/tie-breaks while defining real score semantics.
- Keep raw free-text out of logs and low-cardinality metric labels.
- Preserve German behavior as a tested locale; do not claim English support without
  provider/parser fixtures.
- Keep the Slim Host free of Search interpretation, ranking and result composition.
