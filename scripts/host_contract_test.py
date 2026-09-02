"""Exercise the portable bundle lifecycle used before Host integration."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import zipfile


ROOT = pathlib.Path(__file__).parents[1]
BUNDLE = ROOT / "dist/search-0.1.0.ocp"


def enabled_discovery(install: pathlib.Path, enabled: bool) -> tuple[bool, list[dict]]:
    if not enabled:
        return False, []
    backend = any((install / "backend").glob("ocp_module_search-*.whl"))
    frontend = json.loads((install / "frontend/module.json").read_text())["contributions"]
    return backend, frontend


def main() -> None:
    if not BUNDLE.exists():
        subprocess.run([str(ROOT / "scripts/build-bundle")], check=True)
    expected, filename = BUNDLE.with_suffix(".ocp.sha256").read_text().split()
    assert pathlib.Path(filename).name == BUNDLE.name
    assert hashlib.sha256(BUNDLE.read_bytes()).hexdigest() == expected  # verify
    with tempfile.TemporaryDirectory() as temporary:
        install = pathlib.Path(temporary) / "search"
        with zipfile.ZipFile(BUNDLE) as archive:
            archive.extractall(install)  # install disabled
        assert enabled_discovery(install, False) == (False, [])
        backend, frontend = enabled_discovery(install, True)  # enable/discover
        assert backend and [item["id"] for item in frontend] == ["search.bootstrap"]
        assert enabled_discovery(install, False) == (False, [])  # disable
        assert enabled_discovery(install, True) == (backend, frontend)  # re-enable
    print("verified -> installed(disabled) -> enabled -> backend/frontend discovered -> disabled -> re-enabled")


if __name__ == "__main__":
    sys.exit(main())
