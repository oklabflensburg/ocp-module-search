"""Small public-SDK stand-in for standalone unit tests.

The real SDK is exercised by scripts/host-contract-test against the pinned Host.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Any

try:
    import app.platform.modules.sdk  # noqa: F401
except ModuleNotFoundError:
    app_module = ModuleType("app")
    platform_module = ModuleType("app.platform")
    modules_module = ModuleType("app.platform.modules")
    sdk_module = ModuleType("app.platform.modules.sdk")

    @dataclass(frozen=True, slots=True)
    class Manifest:
        id: str
        name: str
        version: str
        requires: dict[str, Any]
        backend: dict[str, str] | None = None
        frontend: dict[str, str] | None = None
        capabilities: tuple[str, ...] = ()
        persistence: None = None

    def parse_manifest(data: dict[str, Any], *, origin: str | None = None) -> Manifest:
        del origin
        assert data["manifest_version"] == 1
        return Manifest(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            requires=data["requires"],
            backend=data.get("backend"),
            frontend=data.get("frontend"),
            capabilities=tuple(data.get("capabilities", ())),
        )

    @dataclass(frozen=True, slots=True)
    class ModuleDefinition:
        manifest: Manifest
        loader: type
        origin: str
        declared_id: str
        persistence: None = None
        settings: None = None

    class ModuleContext:
        pass

    sdk_module.ModuleContext = ModuleContext
    sdk_module.ModuleDefinition = ModuleDefinition
    sdk_module.parse_manifest = parse_manifest
    sys.modules.update(
        {
            "app": app_module,
            "app.platform": platform_module,
            "app.platform.modules": modules_module,
            "app.platform.modules.sdk": sdk_module,
        }
    )
