"""Composition root for the installable Search bootstrap module."""

from app.platform.modules.sdk import ModuleContext, ModuleDefinition, parse_manifest

from ocp_module_search.api.router import router

MANIFEST = parse_manifest(
    {
        "manifest_version": 1,
        "id": "search",
        "name": "Search",
        "version": "0.1.0",
        "requires": {"host": ">=0.2.0,<1.0.0", "sdk": ">=1.14.0,<2.0.0"},
        "backend": {"package": "ocp-module-search"},
        "frontend": {"package": "@open-city-planner/search"},
        "capabilities": ["search.module-info"],
    },
    origin=__name__,
)


class SearchModule:
    manifest = MANIFEST

    def register(self, context: ModuleContext) -> None:
        """Register the neutral bootstrap endpoint through the public API port."""
        context.api.include_router(router)


DEFINITION = ModuleDefinition(
    manifest=MANIFEST,
    loader=SearchModule,
    origin=__name__,
    declared_id=MANIFEST.id,
)
