from pathlib import Path

import yaml


def test_root_manifest_identifies_packages() -> None:
    manifest = yaml.safe_load((Path(__file__).parents[2] / "module.yaml").read_text())
    assert manifest["id"] == "search"
    assert manifest["version"] == "0.1.0"
    assert manifest["backend"]["package"] == "ocp-module-search"
    assert manifest["frontend"]["package"] == "@open-city-planner/search"
