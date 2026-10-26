from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FILES = (
    "main.py",
    "tripbudget/__init__.py",
    "tripbudget/cli.py",
    "tripbudget/errors.py",
    "tripbudget/models.py",
    "tripbudget/report.py",
    "tripbudget/storage.py",
    "tripbudget/utils.py",
    "tests/test_models.py",
    "legacy/cli.py",
    "legacy/main_simple.py",
    "legacy/models.py",
)


@pytest.mark.parametrize("relative_path", EXPECTED_FILES)
def test_project_files_follow_documented_layout(relative_path: str) -> None:
    assert (PROJECT_ROOT / relative_path).is_file()
