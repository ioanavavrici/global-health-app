import ast
from pathlib import Path

FORBIDDEN_PREFIXES = ("fastapi", "app.controllers", "app.dependencies")


def imported_modules(path: Path) -> set[str]:
    """Names of the modules imported by one Python file."""
    modules = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _layer_files() -> list[Path]:
    files = [Path("app/domain.py")]
    files.extend(sorted(Path("app/repositories").rglob("*.py")))
    files.extend(sorted(Path("app/services").rglob("*.py")))
    return files


def test_lower_layers_do_not_import_presentation_or_fastapi() -> None:
    violations: list[str] = []
    for path in _layer_files():
        for mod in sorted(imported_modules(path)):
            if any(
                mod == prefix or mod.startswith(f"{prefix}.")
                for prefix in FORBIDDEN_PREFIXES
            ):
                violations.append(f"{path}: imports {mod}")
    assert not violations, "Forbidden layer dependencies found:\n" + "\n".join(violations)
