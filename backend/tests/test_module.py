from fastapi import FastAPI
from fastapi.testclient import TestClient

from ocp_module_search.module import module, register


class Context:
    def __init__(self) -> None:
        self.app = FastAPI()

    def include_router(self, router: object) -> None:
        self.app.include_router(router)


def test_module_definition() -> None:
    assert (module.id, module.name, module.version) == ("search", "Search", "0.1.0")


def test_registration_adds_info_endpoint() -> None:
    context = Context()
    register(context)  # type: ignore[arg-type]
    response = TestClient(context.app).get("/api/v1/search/module-info")
    assert response.status_code == 200
    assert response.json() == {"module": "search", "version": "0.1.0", "status": "ready"}
