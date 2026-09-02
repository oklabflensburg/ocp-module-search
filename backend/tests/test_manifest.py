import json
from pathlib import Path

import yaml


def test_root_manifest_identifies_packages() -> None:
    manifest = yaml.safe_load((Path(__file__).parents[2] / "module.yaml").read_text())
    frontend = json.loads((Path(__file__).parents[2] / "frontend/module.json").read_text())
    assert manifest["manifest_version"] == 1
    assert manifest["id"] == "search"
    assert manifest["version"] == "0.1.0"
    assert manifest["requires"] == {
        "host": ">=0.2.0,<1.0.0",
        "sdk": ">=1.14.0,<2.0.0",
        "modules": {},
    }
    assert manifest["backend"]["package"] == "ocp-module-search"
    assert manifest["frontend"]["package"] == "@open-city-planner/search"
    assert manifest["capabilities"] == ["search.module-info"]
    assert "persistence" not in manifest
    assert "config" not in manifest
    assert frontend["compatibility"]["sdk"] == ">=1.5.0 <2.0.0"
    assert frontend["backendModuleId"] == manifest["id"]
