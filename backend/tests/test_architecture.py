import ast
from pathlib import Path


def test_host_imports_use_only_public_sdk() -> None:
    root = Path(__file__).parents[1] / "src" / "ocp_module_search"
    host_imports: list[str] = []
    for source in root.rglob("*.py"):
        tree = ast.parse(source.read_text(), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app."):
                host_imports.append(node.module)
            if isinstance(node, ast.Import):
                host_imports.extend(alias.name for alias in node.names if alias.name.startswith("app."))
    assert host_imports == ["app.platform.modules.sdk"]


def test_no_domain_persistence_or_migrations() -> None:
    package = root = Path(__file__).parents[1]
    assert not (package / "migrations").exists()
    assert not any(root.glob("src/ocp_module_search/**/*model*.py"))
