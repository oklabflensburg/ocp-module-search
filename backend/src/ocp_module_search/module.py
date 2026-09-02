"""Open City Planner module definition and registration hook."""

from app.platform.modules.sdk import ModuleContext, ModuleDefinition

from ocp_module_search import __version__
from ocp_module_search.api.router import router


def register(context: ModuleContext) -> None:
    """Register the bootstrap endpoint through the public module context."""
    context.include_router(router)


module = ModuleDefinition(
    id="search",
    name="Search",
    version=__version__,
    register=register,
)
