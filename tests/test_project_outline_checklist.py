from pathlib import Path


def test_project_outline_contains_checklist():
    text = Path("PROJECT_OUTLINE.md").read_text(encoding="utf-8")
    assert "Checklist" in text
    assert "| Feature / Area | Status | Notes |" in text
    assert "Safe merging (content-level merge)" in text
