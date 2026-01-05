from pathlib import Path


def test_build_instructions_exists():
    assert Path("BUILD_INSTRUCTIONS.md").exists(), "BUILD_INSTRUCTIONS.md is missing"
