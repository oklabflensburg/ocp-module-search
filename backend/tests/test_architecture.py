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
    package = Path(__file__).parents[1]
    root = package
    assert not (package / "migrations").exists()
    assert not (package / "src/ocp_module_search/migrations").exists()
    assert not any(root.glob("src/ocp_module_search/**/*model*.py"))


def test_no_private_host_imports() -> None:
    package = Path(__file__).parents[1] / "src" / "ocp_module_search"
    forbidden = ("app.services", "app.models", "app.api", "app.db", "app.core", "app.integrations")
    for source in package.rglob("*.py"):
        contents = source.read_text(encoding="utf-8")
        assert not any(name in contents for name in forbidden), source
