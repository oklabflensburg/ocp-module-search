from fastapi import FastAPI
from fastapi.testclient import TestClient

from ocp_module_search.module import DEFINITION, MANIFEST, SearchModule


class Api:
    def __init__(self) -> None:
        self.app = FastAPI()

    def include_router(self, router: object, *, prefix: str = "", tags=()) -> None:
        self.app.include_router(router, prefix=prefix, tags=list(tags))


class Context:
    def __init__(self) -> None:
        self.api = Api()


def test_module_definition_uses_current_passive_shape() -> None:
    assert DEFINITION.manifest is MANIFEST
    assert DEFINITION.loader is SearchModule
    assert DEFINITION.origin == "ocp_module_search.module"
    assert DEFINITION.declared_id == "search"
    assert DEFINITION.persistence is None
    assert DEFINITION.settings is None


def test_loader_exposes_manifest() -> None:
    assert SearchModule.manifest is MANIFEST
    assert SearchModule().manifest.id == "search"


def test_registration_adds_info_endpoint_via_api_port() -> None:
    context = Context()
    SearchModule().register(context)  # type: ignore[arg-type]
    response = TestClient(context.api.app).get("/api/v1/search/module-info")
    assert response.status_code == 200
    assert response.json() == {"module": "search", "version": "0.1.0", "status": "ready"}
