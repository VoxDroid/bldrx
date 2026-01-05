from pathlib import Path


def test_project_outline_exists():
    assert Path("PROJECT_OUTLINE.md").exists(), "PROJECT_OUTLINE.md is missing"
