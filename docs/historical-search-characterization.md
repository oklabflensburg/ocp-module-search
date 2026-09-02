# Historical Search Characterization

## Scope and conclusion

This document characterizes the Search implementation that existed in the Host
before the Slim Host cutover. It is evidence for issue
`oklabflensburg/open-city-planner#213`; it is not a committed API or SDK design.

The historical feature called "intelligent search" comprised two distinct
systems:

1. a deterministic, public Search API (`/api/v1/search` and
   `/api/v1/search/interpret`) with a rule interpreter and read-only executor;
2. an `IntelligentSearch.vue` UI which, at the final reference state, called the
   richer Assistant API (`/api/v1/assistant/query`) instead of the Search API.

The deterministic backend worked without the Assistant. The final frontend did
not. Restoring Search must therefore not copy the final frontend dependency on the
Assistant. The Assistant may consume Search later, but Search must remain complete
without it.

The historical backend was a command/query interpreter, not a conventional
full-text search engine. It had no generic `SearchResult[]`, autocomplete,
pagination, provider discovery, relevance score or cross-provider ranking. Feature
queries were constrained to an analysis area, returned GeoJSON, and spent a shared
200-item budget on Stadtplaner polygons first and OSM objects second.

## Reference commits

| Repository / purpose | Commit | Use in this characterization |
| --- | --- | --- |
| Host, last functional pre-Slim state | `410e9ba5dff2e3ed702d1a4ced95a5e5524cb52e` | Primary source for runtime behavior, DTOs, UI and tests |
| Host, initial Search/Assistant implementation | `394824a` | Establishes that Search and Assistant were introduced together |
| Host, filter-context correction | `71915f6` | Final filter inheritance behavior in the UI |
| Host, Statistics UI expansion | `d13b63a` | Explains Statistics fields in the shared frontend Search/Assistant types |
| Host, numeric area and knowledge correction | `6f00d13` | Adds numeric fields to Search plans/executor; parsing remained in Assistant |
| Host, responsive toolbar | `6421398` | Final desktop/compact/mobile placement and behavior |
| Slim Host | `6e78bf72f16343c9c29ce8eeeeff8bbf45115bb2` | Target Host and public service-registry baseline |
| Analysis Areas | `df8b067757b9bf20fbc54efc9555f3388bd951ff` | Current owner and `analysis-areas.lookup@1` baseline |
| Statistics | `4525491995cddb7ad9670f456bba1a49e289f583` | Current owner and `statistics.query@1` baseline |
| Search bootstrap | `5d78b945f0db9369a768574519bff5e0750056e8` | Module baseline for this document |

The targeted history contains no more complete standalone Search implementation
after `410e9ba`. Later commits (`4468b04`, `6b1df2f`, `7c425b1`, `de023dd`)
progressively moved or removed domain code for the modular cutover. No historical
commit was cherry-picked.

The Host worktree used for inspection had unrelated, uncommitted Slim Host work on
`feat/196-analysis-areas-host-cleanup`; all historical inspection used Git objects
and did not modify that worktree.

## Investigated files

Primary backend files:

- `backend/app/api/search.py`
- `backend/app/services/search_catalog.py`
- `backend/app/services/search_interpreter.py`
- `backend/app/services/search_executor.py`
- `backend/app/schemas/search.py`

Primary frontend files:

- `frontend/app/stores/search.ts`
- `frontend/app/components/search/IntelligentSearch.vue`
- `frontend/app/types/search.ts`

Important indirect files:

- `backend/app/api/router.py`, `backend/app/services/public_query_security.py`
- `backend/app/schemas/polygon_filters.py`
- `backend/app/modules/analysis_areas/application/legacy_queries.py`
- `backend/app/services/osm_canonical.py`
- `backend/app/services/assistant.py`, `assistant_tools.py`,
  `assistant_knowledge.py`
- `frontend/app/stores/map.ts`, `filter.ts`, `osmViewport.ts`
- `frontend/app/composables/useMapCanvasHost.ts`
- `frontend/app/components/layout/AppShell.vue`, `GisPanelContent.vue`,
  `LeftSidebar.vue`
- `backend/tests/test_intelligent_search.py`
- `frontend/tests/intelligent-search.test.ts`
- `frontend/e2e/intelligent-search.spec.ts`
- `docs/intelligent-search.md`

`DocsSearch.vue` and the documentation search utilities are a separate,
client-side documentation index and were not part of this Search architecture.

## Functional scope

| Feature | Historical entry point | Side | Input | Output | Data source / side effect | Dependent domain | Needed for Search target? | Target ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Whitespace-normalized text command | `SearchRequest`, `interpret_search()` | Backend | 2–500 characters | `SearchPlan` or error | NFKC/case-fold normalization | Search | Yes | Search |
| Intent recognition | `interpret_search()` | Backend | German normalized text | One of seven intents | Ordered rules, optional protocol fallback | Search plus leaked domain vocabulary | Yes, after scope review | Search owns generic parsing; providers own domain vocabulary |
| Catalog | `SEARCH_CATALOG` | Backend | Static Python constants | Filter values, synonyms, operation names | No lookup and no generated URL | Polygon, Analysis Areas, OSM, Analytics, Statistics | Vocabulary yes; current shape no | Split between Search and provider descriptors |
| List area types | `SHOW_ANALYSIS_AREAS` | Both | “alle”/“anzeigen”/“zeige” plus area-type synonym | Area GeoJSON and map action | Shows one Analysis Areas layer type | Analysis Areas | Yes if provider installed | Analysis Areas provider; Search dispatch/UI |
| Resolve named area | `resolve_analysis_area()` | Backend | Name/slug embedded in text | ID, slug, name, type | Full table read; 404/409 handling | Analysis Areas | Yes if provider installed | Analysis Areas provider |
| Show area/detail/size | `SHOW_AREA` | Backend | Area plus map/detail/size phrase | Detail DTO, answer, bbox | Fits map and selects area in final UI | Analysis Areas | Useful, but not generic result search | Analysis Areas provider metadata; Search presentation |
| Search features in area | `SHOW_FEATURES` | Backend | Area, category/source/geometry filters | GeoJSON FeatureCollection | Replaces persistent Search map layer | Polygon and OSM | Yes | Respective providers; Search merges/limits |
| Count features | `COUNT_FEATURES` | Backend | Area and filters | Total plus counts by source | No GeoJSON materialization | Polygon and OSM | Useful | Providers count or Search counts complete batches; decide before contract |
| Area analytics | `ASK_ANALYTICS` | Backend | Area and filters | Analysis Area analytics DTO | Fits area | Analysis Areas/Polygon analytics | Not necessarily core Search | Domain provider or Assistant, not Search-owned calculation |
| Area comparison | `COMPARE_AREA` | Backend | One area versus municipality | Comparison DTO | Fits area | Analysis Areas/Polygon analytics | Not necessarily core Search | Analysis Areas or Assistant |
| Filter commands | `_filter_plan()`, store `applyFilters()` | Both | “nur” plus supported value | `UPDATE_FILTERS` action | Mutates shared Pinia filters | Host map/filter UI, Polygon/OSM vocabulary | Yes for command UI parity | Search parses; UI contribution applies public filter action |
| Category parsing | `_category()` | Backend | German retail/gastronomy synonyms | One polygon category | Narrows feature query | Polygon/OSM classification | Yes | Provider descriptors; Search may match normalized descriptors |
| Numeric area filtering | `SearchPlan`, executor SQL | Backend | Pre-populated lower/upper m² bounds | Polygon subset | PostGIS `ST_Area` in EPSG:25832 | Polygon | Yes if historical Assistant parity is desired | Polygon provider |
| OSM amenity filtering | `SearchPlan`, executor SQL | Backend | Pre-populated allowlisted tag values | OSM subset | `amenity` equality | OSM | Yes for POI commands | OSM provider |
| Suggestions | `examples` in `IntelligentSearch.vue` | Frontend | Focus on empty/inactive panel | Four hard-coded example buttons | Submits the example | Search UI | Yes as examples, not autocomplete | Search frontend |
| Search history | Search store | Frontend | Successful Assistant responses | Last 10 unique queries in memory | Restores panel state only | Assistant in final implementation | Optional | Search frontend, with Search DTOs only |
| Result grouping | `IntelligentSearch.vue` presentation branches | Frontend | Assistant presentation type | Cards/lists/tables | Up to 8/12/20 displayed items by branch | Assistant, Statistics, Analysis Areas | No as-is | Search needs its own generic renderer |
| Navigation to detail page | Only knowledge `NuxtLink` | Frontend | Documentation source allowlist | `/dokumentation` | Router link | Documentation/Assistant | No historical resource navigation | Future provider-supplied navigation metadata |
| Map navigation | `applySearchAction()` | Frontend | Bounds or GeoJSON | `fitBounds`, max zoom 16 | 350 ms camera move with responsive padding | Host map | Yes | Search emits neutral target; Host map contribution executes it |
| Area selection | Search store `apply()` | Frontend | Assistant active area | Runtime map selection | Opens/selects Analysis Area | Analysis Areas/Host map | Yes if result selected | Provider resource reference plus public map selection action |
| Empty query | Search store / Pydantic | Both | Fewer than 2 characters | No request in UI; HTTP 422 in API | None | Search | Yes | Search |
| Unknown query | `interpret_search()` | Backend | No supported deterministic rule | `UNSUPPORTED_SEARCH_INTENT`, 422 | Optional protocol called only when explicitly injected | Search | Yes | Search |
| Ambiguous area | `_unique_area()` | Backend | Same longest name/slug for multiple areas | `AMBIGUOUS_AREA`, 409 with names | None | Analysis Areas | Yes | Provider returns ambiguity; Search presents it |

There was no search by arbitrary polygon name, OSM name, OSM ID, address, or tag
text. OSM nodes, ways and relations could all appear, but only because matching
rows from `osm_features` were selected spatially and through normalized category,
status, amenity, floor and geometry filters.

## Backend architecture

```text
POST request
  -> public rate/statement-timeout guard
  -> deterministic interpreter
       -> direct AnalysisArea ORM scan for name/slug resolution
       -> optional SearchLLMProvider only if a caller injects one
  -> validated SearchPlan
  -> executor dispatch by intent
       -> Analysis Areas legacy application functions, or
       -> static Polygon/OSM SQL
  -> SearchResponse with German answer, arbitrary data and map action
```

The API never injected `SearchLLMProvider`, so both public Search routes were
deterministic in production. A provider failure mode was consequently not defined.
Unknown input returned the deterministic unsupported error.

### Interpreter rules and ordering

Rules were evaluated in this order:

1. Normalize using Unicode NFKC, case-folding, `ß` to `ss`, punctuation removal
   and whitespace collapse.
2. Reject regex matches for SQL-like mutations, passwords/MFA/session/OAuth/tokens,
   user/e-mail requests and “ignore all rules”. This happened before any DB query.
3. Recognize `MUNICIPALITY`, `DISTRICT` or `QUARTER`; with “alle”, “anzeigen” or
   “zeige”, emit `SHOW_ANALYSIS_AREAS` without resolving a named area.
4. Recognize filter-only commands in fixed order: vacancy, occupied, polygons,
   OSM, Stadtplaner, ground floor, chain, independent.
5. Resolve one Analysis Area by exact case-insensitive name, exact slug, then the
   longest bounded name/slug contained in the query. More than one remaining
   candidate was a 409 ambiguity.
6. Detect a category from the first matching category/synonym in catalog order.
7. Dispatch compare, count/analytics, area size, features, or area display in that
   order.
8. If explicitly supplied by an internal caller, ask `SearchLLMProvider` for a
   plan and validate it again. Otherwise return unsupported, 422.

Area resolution was performed for every query reaching step 5, even if a later
rule did not need an area. `needs_area` was a substring heuristic (`" in "`,
`"wie viele"`, `"wie gross"`, `"vergleiche"`) that changed a miss from
unsupported to `AREA_NOT_FOUND`.

The general rules were normalization, forbidden-scope rejection, ordered dispatch
and fallback. Area types/names, retail categories, vacancy, floor, business
structure, data-source labels and geometry meanings were domain-specific and must
not be hard-coded into the future Search core.

### Executor behavior

| Intent | Calls | Result data | Ordering / limit | Error behavior |
| --- | --- | --- | --- | --- |
| `CHANGE_FILTERS` | None | `null` | N/A | None |
| `SHOW_ANALYSIS_AREAS` | `areas_geojson()` | Filtered FeatureCollection | Upstream collection order; no local limit | Upstream exceptions propagated |
| `SHOW_AREA` | `area_detail_by_slug()` | Full area detail | N/A | 404 if missing |
| `SHOW_FEATURES` | Area detail, Polygon SQL, then OSM SQL | FeatureCollection | Shared 200; polygons consume budget first | Upstream/DB errors propagated |
| `COUNT_FEATURES` | Area detail, one union count query | `{count, by_source}` | Source rows ordered alphabetically | Upstream/DB errors propagated |
| `ASK_ANALYTICS` | Area detail, `area_analytics()` | Analytics DTO | Service-defined | 404 if missing |
| `COMPARE_AREA` | Area detail, `area_comparison()` | Comparison DTO | Service-defined | 404 if unavailable |

Feature execution was sequential, not parallel. Polygon rows were ordered by
`updated_at DESC, id DESC`. OSM rows with a `name` tag came first, followed by
`osm_type, osm_id`. This was deterministic source priority, not relevance ranking.
When both sources were enabled, linked OSM rows were excluded through
`polygon_osm_sources` to avoid duplicates.

The intended future flow is:

```text
query
  -> Search-owned validation and generic interpretation
  -> provider selection through context.services
  -> bounded provider execution
  -> result normalization
  -> global ranking and deterministic tie-breaks
  -> SearchResult[] plus presentation actions
```

## Search API

Both routes were mounted below the Host router prefix `/api/v1` and were public;
neither declared an authentication dependency.

| Route | Method | Request | Response | Pagination / limits | Status codes |
| --- | --- | --- | --- | --- | --- |
| `/api/v1/search/interpret` | POST | `SearchRequest` | `SearchInterpretResponse` | None | 200; 403 forbidden; 404 unknown required area; 409 ambiguous area; 422 validation/unsupported; 429 public-query limit; 503 statement timeout; unexpected failures 500 |
| `/api/v1/search` | POST | `SearchRequest` | `SearchResponse` | No pagination; FeatureCollection capped at 200 | Same, plus executor 404s and executor 422 unsupported |

`SearchRequest.query` rejected extra fields, required 2–500 characters, collapsed
whitespace and preserved the normalized display string. FastAPI/Pydantic request
validation used the standard 422 shape. Search-specific errors used
`detail.error.code` and `detail.error.message`. A PostgreSQL statement timeout was
rolled back and mapped to `SEARCH_QUERY_TIMEOUT`/503. The shared rate limiter used
`PUBLIC_QUERY_RATE_LIMITED`/429.

There was no cursor, page, offset, configurable client limit or requested sort.
`/interpret` executed the public-query guard and area lookup but no feature or
analytics query. `/search` interpreted and executed synchronously in one request.

## Search schemas

All backend models used `extra="forbid"` where input integrity mattered.

| DTO | Fields and types | Semantics | Producer -> consumer | Classification |
| --- | --- | --- | --- | --- |
| `SearchIntent` | Seven string enum values | Executor operation | Interpreter/provider -> executor/UI | Search-specific but several values leak Analysis Areas analytics |
| `SearchMapActionType` | `NONE`, `FIT_AREA`, `SHOW_ANALYSIS_AREAS`, `REPLACE_SEARCH_LAYER`, `UPDATE_FILTERS` | Host map/UI command | Interpreter -> response -> frontend | Search presentation with Host/Analysis Areas leakage |
| `SearchGeometryFilter` | `ALL`, `POINTS_ONLY`, `POLYGONS_ONLY` | Geometry-kind constraint | Interpreter/Assistant -> executor | Generic spatial filter |
| `SearchAreaType` | `MUNICIPALITY`, `DISTRICT`, `QUARTER` | Analysis Area taxonomy | Interpreter -> executor/UI | Foreign Analysis Areas domain leaked |
| `SearchArea` | `id`, `name`, `slug`, `area_type` | Resolved area reference | Interpreter -> plan/executor | Foreign Analysis Areas domain leaked |
| `SearchFilters` | lists of categories, occupancy statuses, floors, area sizes, business structures, sources | Existing polygon filter contract; empty means all, `NONE` is exclusive | Interpreter/Assistant -> executor/UI | Foreign Polygon/OSM domain leaked |
| `SearchPresentation` | action `type`, `fit_bounds` | Planned presentation | Interpreter -> executor | Search-specific |
| `SearchPlan` | intent, optional area/type, filters, geometry filter, up to 10 OSM amenities, optional bounded m² range, presentation | Fully validated executable command | Interpreter/provider/Assistant tool -> executor | Search envelope containing several foreign-domain DTOs |
| `SearchRequest` | normalized `query: str` | Public API input | Client -> routes | Generic Search |
| `SearchInterpretResponse` | `query`, `plan`, `resolved=true`, `warnings=[]` | Interpretation-only response | Route -> clients | Search-specific; `resolved` was never false |
| `SearchMapAction` | action type, `fit_bounds`, optional four-number bounds | Concrete presentation instruction | Executor -> frontend | Search/Host map boundary |
| `SearchResponse` | `query`, `plan`, German `answer`, map action, `data: Any`, warnings | Executed command response | Executor -> clients | Search envelope; untyped data leaked every provider DTO |

The frontend duplicated the Search DTOs and additionally placed all Assistant
DTOs in `frontend/app/types/search.ts`. Its `SearchResponse` also declared
`error_code`, which did not exist in the backend response model. This file-level
coupling must not be retained.

## Search catalog

`search_catalog.py` was a static vocabulary/allowlist, not a provider catalog. It
performed no discovery, dynamic registration, URL creation or routing.

| Catalog entry | Historical source | Data need | Target owner | Potential provider |
| --- | --- | --- | --- | --- |
| Area types and synonyms | Hard-coded Search constants | Municipality/district/quarter labels | Analysis Areas | `analysis-areas.search` candidate |
| Category labels/synonyms | Hard-coded retail vocabulary plus Polygon allowlist | Category key/label/aliases | Polygon/OSM classification owner | Polygon and OSM Search providers |
| Occupancy, floor, size, business filters | `schemas.polygon_filters` | Allowed values | Polygon | Polygon Search provider descriptor |
| Sources | `STADTPLANNER`, `OSM` | Source selection | Search presentation/provider IDs | Search plus providers |
| Vacancy synonyms | Hard-coded German words | Filter intent | Polygon | Polygon provider descriptor |
| Allowed operations | Static strings for Analysis Areas, analytics, statistics, polygons, OSM, data-source status | LLM/Assistant safety context | Multiple domains | Do not recreate as one Search mega-catalog |

The operation allowlist mentioned Analysis Areas list/GeoJSON/detail/analytics,
comparison/statistics, analytics overview/compare, public polygons, public OSM and
data-source status. The deterministic Search executor used only Analysis Areas
list/detail/analytics/comparison plus Polygon/OSM reads. URLs were never stored or
generated. Assistant and Assistant knowledge imported the catalog directly.

## Frontend architecture

### Store

The final `useSearchStore` held:

- query, loading, error and the latest `AssistantResponse`;
- `AssistantContext`, including active area/filters and conversational topics;
- open/closed state, answer/history tab and a five-second confirmation;
- ten in-memory, newest-first, query-deduplicated history entries;
- module-level active request and confirmation timers.

`submit()` trimmed and ignored queries shorter than two characters, aborted the
previous request, enforced a 12-second browser timeout, copied current filters into
Assistant context and posted to `/assistant/query`. It did not call either Search
route. Stale responses were discarded. Closing/disposal aborted the request.

Successful responses updated context, applied filters and map actions, and either
kept the panel open or auto-closed it according to Assistant presentation behavior.
Errors retained prior context and kept the panel open.

### IntelligentSearch component

The component used an explicit submit button/Enter form submission; there was no
debounce or search-as-you-type. Keyboard behavior comprised native form behavior
and Escape closing the result panel. Clearing restored focus. The submit button was
disabled below two trimmed characters but stayed enabled while loading so a newer
request could replace the active one.

On focus, it showed four static examples. It rendered loading and error states,
answer/history tabs, metrics, statistics lists/series, feature summaries/details,
comparisons, knowledge, data-source status, clarification chips and follow-up
buttons. These were Assistant presentation types, not Search result kinds. Empty
history had a message; there was no explicit “zero search results” state beyond the
returned answer/presentation.

Desktop placed the component in the left sidebar and widened the layout while an
answer was open. Compact/mobile opened the existing GIS panel/bottom sheet from a
“Suche” map action. Mobile inherited focus trapping, safe-area and back/Escape
behavior from that shell. All visible strings and examples were hard-coded German.

### Routing and map behavior

There was no `router.push` or `navigateTo` for Search resources. The only route in
the component was an allowlisted `/dokumentation` link for Assistant knowledge.
No polygon slug or OSM feature result navigated to a detail page.

| Historical result/action | UI effect |
| --- | --- |
| Active Analysis Area in Assistant context | Select `analysis-areas.data` runtime feature with ID/name/slug/type |
| `UPDATE_FILTERS` | Replace Pinia category/status/floor/size/business/source selections |
| `POLYGONS_ONLY` / `POINTS_ONLY` | Toggle OSM area/POI visibility |
| `REPLACE_SEARCH_LAYER` | Replace persistent `host.search-results` GeoJSON source |
| `SHOW_ANALYSIS_AREAS` | Replace Search source and show only requested Analysis Area layers |
| `FIT_AREA` | Clear Search source and fit explicit bounds |
| Any `fit_bounds` action with data | Derive geometry bounds and fit with responsive padding, max zoom 16, 350 ms |
| `HIGHLIGHT_AREAS` (Assistant only) | Set Analysis Areas highlight-layer slug filter |
| Knowledge source | Optional navigation to `/dokumentation` |

The Assistant context declared selected polygon slug, selected OSM node/way/
relation and viewport. The Search store initialized them but did not populate them;
they were Assistant concerns, not demonstrated Search inputs.

## Data and domain dependencies

### Direct database reads

| Table | Domain | Why Search read it | Direct read acceptable in future? |
| --- | --- | --- | --- |
| `analysis_areas` | Analysis Areas | Resolve names/slugs; target geometry/ID for spatial queries | No |
| `osm_features` | Host OSM | Return/count spatially covered OSM nodes, ways and relations | No |
| `polygon_osm_sources` | Host Polygon/OSM linkage | Suppress linked OSM duplicates when polygons enabled | No |
| `user_polygons` | Host Polygon | Return/count Stadtplaner polygons and filters | No |
| `polygon_analysis_areas` | Analysis Areas/Polygon assignment | Scope polygons to an area | No |

Hidden legacy service calls also depended on Analysis Areas, polygon analytics and
their cache/query implementations. Search must not import their application,
persistence, ORM or SQL in the target architecture.

### Analysis Areas

Search required area UUID, slug, name and type for resolution and plans; geometry
for list/feature selection; bbox and `area_m2` for map fitting/size answers; detail
data for `SHOW_AREA`; and analytics/comparison data for the two analytics intents.
The final frontend used ID, slug, name and type to select an area.

At the stable module baseline, `analysis-areas.lookup@1` exposes materialized
summary lookup (ID, slug, name, type, parent), geometry and hierarchy through
`context.services`. It does not expose bbox, area size, analytics/comparison or
search relevance. It can support exact resolution, but it is not by itself the
complete historical Search dependency. A domain-owned Search provider should hide
how Analysis Areas are matched and emit only normalized results/map metadata.

### Statistics

**No direct Statistics dependency existed in the deterministic Search interpreter
or executor.** `analysis_areas.statistics` appeared only in the static catalog.
Statistics queries, statistics keyword interpretation and statistics UI cards
belonged to the Assistant path added in `d13b63a`. The shared frontend types made
that coupling look like Search. Search must not require `statistics.query@1` for
core operation. A future Statistics Search provider is optional only if an actual
“find a metric/dataset” use case is separately accepted.

### OSM / POI

The executor could return any OSM node, way or relation present in `osm_features`
whose representative point was covered by the selected area. It filtered by
derived retail category, derived occupancy status, exact `amenity`, derived floor
group and point/area geometry. It returned source, `osm_type:osm_id`, derived name,
category, status, null area and GeoJSON geometry. It did not search arbitrary tags
or rank names. Map behavior was a GeoJSON overlay and fit, not selection or detail
routing.

The Slim Host `platform.osm-snapshot-query@1` is a bounded generic snapshot service
with OSM type, geometry kind, required tags, exact tag filters, bbox and cursor. It
does not provide area containment, derived canonical categories/status/floor,
deduplication against polygons or text relevance. Reusing or extending it is a
follow-up decision; Search must not read `osm_features` directly.

### Polygons

The executor searched all rows in `user_polygons` assigned to the area, filtered by
category, occupancy, floor, size class, business structure, geometry and measured
m² bounds. It returned only public-style fields plus geometry, never owner/contact
fields. The historical model did not have a private/public visibility flag and its
public endpoints also exposed sanitized projections of all polygons. Nevertheless,
direct SQL bypassed the public serializer and any future authorization policy.

Search did not distinguish “own”, other users' or public polygons, did not search
Map Selection, and did not navigate by polygon slug. A future provider must enforce
visibility and authorization itself and return only permitted, materialized DTOs.
Existing `PolygonQueryPort` lists summaries for a precomputed internal
`PolygonScope`; it lacks text/spatial filter input and geometry, so it does not
cover the historical feature query on its own.

### Assistant

Search backend files did not import or call Assistant. In the other direction,
Assistant imported catalog labels/synonyms, normalization/forbidden patterns,
Search plan DTOs and `execute_search()`. Its `SEARCH_FEATURES` tool constructed a
Search plan and reused the executor. The final Search store/UI called Assistant and
rendered Assistant DTOs.

Target direction:

```text
Search (works alone) <- optional consumer: Assistant
```

Shared parsing primitives may live in Search's public API only if they are stable
consumer contracts. Assistant-specific context, knowledge, Statistics, tool plans,
telemetry and conversational follow-ups do not belong to Search.

## Security and auth

- Routes were anonymous and read-only.
- A shared public-query guard applied 120 requests per 60 seconds by default and an
  8-second PostgreSQL statement timeout.
- Pydantic rejected extra plan fields, invalid allowlist values, invalid numeric
  ranges and more than ten OSM amenities.
- Static parameterized SQL prevented query text from becoming SQL, identifiers,
  order clauses or joins.
- Forbidden-text regexes ran before area DB access, but were defense-in-depth, not
  an authorization mechanism.
- The response did not include polygon owner/contact/private administration fields.
- Provider implementations must own authorization and visibility. Search must not
  recreate foreign permission rules or assume all future user resources are public.
- Free-text queries may contain personal data. The historical Search files had no
  explicit query logging, metrics or Search-specific tracing. Generic application
  tracing still wrapped HTTP requests. Future telemetry should record bounded,
  low-cardinality outcome/provider/timing fields and not raw query text.

## Performance

- Backend feature result maximum: 200 combined items.
- Source allocation: polygons first, OSM receives only the remaining budget.
- Execution: sequential; no provider timeouts or partial-success semantics.
- Spatial OSM query: bbox/GiST prefilter followed by `ST_Covers` of
  `ST_PointOnSurface`; invalid geometries excluded for returned features.
- Polygon area: `ST_Transform(..., 25832)` then `ST_Area`.
- Counts: one aggregate union query, not loaded GeoJSON.
- Typical feature request performed the guard statement, one full area-resolution
  query, an area-detail lookup and up to two feature queries. Cache behavior of
  legacy area functions was outside Search.
- Browser request timeout: 12 seconds, on the Assistant route.
- Input: submit only; no debounce.
- No API response-time SLO, provider concurrency, per-provider quota or ranking
  budget was defined.

A future orchestrator should set a total deadline, smaller per-provider deadlines,
per-provider limits and explicit partial-result warnings. Independent providers can
run concurrently only after resource and connection-pool limits are defined.

## Internationalization

Interpretation, aliases, answer strings, errors, labels, examples and UI states were
German. A few ASCII transliterations (`ae`, `oe`, `ue`, `ss`) were recognized; no
locale was accepted and no English intent vocabulary existed. Provider descriptors
and parsing must carry locale explicitly before multilingual behavior is claimed.

## Existing tests

| Historical test | Behavior evidenced |
| --- | --- |
| `backend/tests/test_intelligent_search.py` area commands | District/quarter list intents and map actions |
| Filter-command parameterization | Vacancy, occupied, polygons, source, floor and business filters |
| Area-query parameterization | Feature/count/analytics/area/compare intents and category detection |
| Unknown and ambiguous area tests | 404 no guessing; 409 conflict |
| Forbidden-intent tests | Rejection before DB access |
| Pydantic/catalog tests | Extra-field/value rejection, allowlists, read-only operation names |
| Executor limit/static-query test | 200 cap and query text absent from SQL |
| Amenity/area threshold tests | Bound SQL parameters and source exclusions |
| OpenAPI route test | Both Search routes registered |
| `frontend/tests/intelligent-search.test.ts` | Assistant request/context, filters/map effects, error, timeout, abort, stale response, knowledge and responsive wiring |
| `frontend/e2e/intelligent-search.spec.ts` | Assistant metric, area layer, Search layer, filter follow-up, comparison, knowledge, Statistics and mobile bottom sheet/history |

The frontend tests explicitly prove `/assistant/query`, not Search API consumption.
Most E2E cases are therefore Assistant characterization and cannot be copied as
Search contract tests.

### Target characterization baseline

| Case | Historical outcome | Required future assertion |
| --- | --- | --- |
| Empty query | UI no-op; API 422 | Same explicit client/server boundary |
| Recognized text | Deterministic plan/action | Stable intent or normalized provider request |
| Unknown query | 422 unsupported | Controlled unsupported/empty result, decision required |
| Analysis Area hit | Exact/contained name or slug | Provider result with stable resource and map target |
| OSM hit | Area-scoped filtered GeoJSON | Optional provider result, no direct SQL |
| Polygon hit | Area-assignment filtered GeoJSON | Optional provider result with visibility enforced |
| Multiple providers | Polygon-first shared 200 budget | Bounded batches, deterministic global ordering |
| Ranking | No score; fixed source/query order | Provider-local relevance plus Search-owned normalization |
| Navigation | No domain detail navigation | Provider-owned opaque resource/navigation reference |
| Map selection | Area selection and Search GeoJSON layer | Neutral map target interpreted by Host contribution |
| Backend error | UI error, previous context retained | Stable error code and retry-safe UI |
| Provider unavailable | Not defined | Timeout/unavailable warning and partial results |
| Optional provider missing | Not defined | Search starts and returns remaining providers |

## Target ownership

| Concern | Target owner | Rationale |
| --- | --- | --- |
| Query validation/normalization | Search | Cross-provider entry semantics |
| Generic intent classification | Search | Orchestration, not domain persistence |
| Domain keywords/filter descriptors | Provider owner | Prevent foreign vocabulary in Search core |
| Provider discovery/selection | Search via `context.services` | Central bounded orchestration |
| Provider execution | Domain provider | Own data, queries, auth and local relevance |
| Result normalization | Search | Stable public Search response |
| Global ranking/limits/tie-breaks | Search | Comparable deterministic result set |
| Provider-local relevance | Provider | Domain-specific match quality |
| Analysis Area searching | Analysis Areas | Owns names, hierarchy, geometry and routes |
| OSM searching/classification | Host generic OSM provider or future OSM module | Owns canonical tags and snapshot |
| Polygon searching | Host generic Polygon provider | Owns visibility, filters, assignment and dedup data |
| Statistics searching | None for parity | No direct historical Search use case |
| Assistant interpretation/presentation | Assistant | Optional consumer, never required by Search |
| Navigation metadata | Provider supplies opaque target; Search transports | Provider knows canonical resource route |
| Map target metadata | Provider supplies geometry/bounds/resource; Search normalizes | Host map executes technology-neutral contribution |
| UI history/loading/errors | Search frontend | Search interaction state |
| Map/filter side effects | Host public frontend contracts | Search UI must not import Host-private stores |

Analytics, comparison and free-form knowledge should not silently expand a generic
Search provider into an all-domain command API. They require an explicit product
scope decision: either separate, narrowly typed provider operations or ownership by
Analysis Areas/Assistant.

## Result normal form candidate

This is a requirements sketch, not a committed contract:

```text
SearchResult
  id                 opaque, stable within provider
  provider           stable provider/service ID
  kind               provider-neutral coarse kind
  title              localized primary label
  subtitle           optional localized context
  local_score        provider-local finite relevance
  resource_ref       opaque owner/type/id-or-slug reference
  navigation         optional route contribution, not a hard-coded route
  map_target         optional bounds/geometry/selection reference in EPSG:4326
  metadata           bounded public primitives only

SearchResultBatch
  items
  total              optional, only if cheaply/accurately known
  truncated
  warnings
  provider_duration_ms (telemetry response metadata, not a Prometheus label)
```

Do not expose ORM objects, database IDs needed only for joins, arbitrary provider
payloads, owner data or executable router/map callbacks. A discriminated union may
be safer than unrestricted `metadata`; decide this in the SDK-contract issue.

Providers should return local relevance. Search should validate finite/ranged
scores, normalize across providers, apply configurable provider-neutral ranking,
and use stable tie-breaks (`normalized score`, provider order/ID, result ID). The
historical polygon-first behavior is a parity input, not proof that polygons always
deserve a higher semantic score.

## Provider candidates

These names are candidates only. The producer owns its service namespace under the
current registry rules.

| Contract | Candidate service ID | Version | Producer | Consumer | Method sketch | Required? |
| --- | --- | --- | --- | --- | --- | --- |
| Common `SearchProviderPort` from public SDK | `analysis-areas.search` | 1 | Analysis Areas | Search | `search(request) -> SearchResultBatch` | Optional module provider |
| Common `SearchProviderPort` from public SDK | `platform.polygon-search` | 1 | Slim Host Polygon capability | Search | same | Optional host-provided |
| Common `SearchProviderPort` from public SDK | `platform.osm-search` | 1 | Slim Host OSM capability | Search | same | Optional host-provided |
| Search API/orchestrator (module-owned, not a provider lookup) | N/A | N/A | Search | HTTP/frontend/Assistant | `search(query, locale, limit, context) -> SearchResponse` | Search core |

`analysis-areas.lookup@1` is already public and may support exact area lookup, but
requiring it directly would put Analysis Areas interpretation back in Search. It is
preferable for an Analysis Areas Search provider to consume its own internals or
lookup service and return normalized results.

Core Search should require only generic Host lifecycle/API/public-query facilities
and the service registry. Analysis Areas is optional, Statistics is not required,
Assistant is not a dependency, and OSM/Polygon providers are optional Host
capabilities. A deployment with no domain providers should still start and return a
controlled empty/unavailable response.

### Host SDK prerequisite candidates

No SDK change is made by this task. The follow-up contract issue must decide:

- a persistence-free common `SearchProviderPort`, request/batch/result DTOs and
  score semantics;
- provider-neutral resource, navigation and EPSG:4326 map-target DTOs;
- how Search discovers zero-to-many providers. The current registry resolves an
  exact contract/service-ID/version and does not enumerate implementations;
- declaration of optional service IDs/modules and deterministic provider order;
- deadline/cancellation, per-provider limits and partial-error semantics;
- locale and authorization/request-principal context without leaking FastAPI or
  foreign ORM/session types;
- whether providers own their transactions, consistent with current registry
  guidance, or receive a narrowly defined query context.

All lookup must use `context.services`; do not add `context.search`,
`context.analysis_areas` or private cross-domain imports.

## Open questions

1. Is Phase 2 restoring only resource discovery/map commands, or also historical
   analytics/count/compare answers that are closer to Assistant behavior?
2. Should unknown text produce 422, an empty result batch, or a successful response
   with an unsupported warning?
3. How are provider-local scores calibrated for global ordering without favoring a
   provider merely because of score scale?
4. Is historical polygon-first allocation a compatibility requirement or only an
   implementation artifact?
5. Should count be a provider method, a batch total, or excluded until a complete
   count contract exists?
6. Are navigation routes safe opaque strings contributed by providers, or typed
   frontend resource contributions resolved outside the backend?
7. Can the existing OSM snapshot service efficiently satisfy spatial containment
   and canonical-category search, or is a bounded OSM Search service necessary?
8. Does Polygon Search need a new host service with geometry and area scoping, and
   how will future private/user-specific visibility be represented?
9. Does the registry need provider enumeration, or should Search explicitly resolve
   a finite manifest-declared list of known optional service IDs?
10. Which locale negotiation and synonym ownership model replaces the German-only
    static catalog?
11. What total latency budget and partial-result policy should replace sequential
    execution under one database statement timeout?
12. Which historical Assistant UI branches, if any, belong in the standalone Search
    contribution rather than a later Assistant module?

## Recommended follow-up issues

### A. `[Search] Öffentlichen Search Provider Contract im SDK etablieren`

Decide the common provider DTOs, service ownership/IDs, discovery, scores, locale,
auth context, deadlines, limits and partial failures. Add only the minimal public
SDK/registry capabilities proved necessary by this characterization.

### B. `[Search] Backend-Suche in ocp-module-search portieren`

Port query validation, deterministic generic interpretation, orchestration,
normalization/ranking and the two public routes. Consume providers exclusively
through `context.services`; add no domain SQL or private imports.

### C. `[Search] Frontend Intelligent Search als Modul-Contribution portieren`

Build a Search-owned store and UI against Search DTOs, using public frontend map,
selection, filter and navigation contributions. Do not copy Assistant DTOs or the
`/assistant/query` dependency.

### D. `[Search] Cross-Provider E2E und Performance Contract`

Verify missing/slow/failing providers, global/per-provider limits, deterministic
ranking, authorization isolation, map targets, responsive UI and latency budgets.
