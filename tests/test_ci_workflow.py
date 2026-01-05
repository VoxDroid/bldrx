from pathlib import Path


def test_ci_workflow_exists():
    assert Path(
        ".github/workflows/ci.yml"
    ).exists(), "CI workflow file missing: .github/workflows/ci.yml"
