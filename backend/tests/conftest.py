"""A narrow SDK test double keeps package tests independent from a Host checkout."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Callable


@dataclass(frozen=True)
class ModuleDefinition:
    id: str
    name: str
    version: str
    register: Callable[[object], None]


class ModuleContext:
    def include_router(self, router: object) -> None:  # pragma: no cover - protocol shape only
        raise NotImplementedError


app = ModuleType("app")
platform = ModuleType("app.platform")
modules = ModuleType("app.platform.modules")
sdk = ModuleType("app.platform.modules.sdk")
sdk.ModuleDefinition = ModuleDefinition
sdk.ModuleContext = ModuleContext
sys.modules.update(
    {"app": app, "app.platform": platform, "app.platform.modules": modules,
     "app.platform.modules.sdk": sdk}
)
