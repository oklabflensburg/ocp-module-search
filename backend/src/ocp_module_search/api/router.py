"""Minimal module information endpoint; this is not a search API."""

from fastapi import APIRouter

from ocp_module_search import __version__

router = APIRouter(prefix="/api/v1/search", tags=["search-module"])


@router.get("/module-info")
def module_info() -> dict[str, str]:
    """Expose bootstrap readiness for installation contract checks."""
    return {"module": "search", "version": __version__, "status": "ready"}
