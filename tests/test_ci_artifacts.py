from pathlib import Path


def test_ci_uploads_use_unique_names():
    text = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "pytest-logs-${{ matrix.python-version }}-${{ github.run_id }}" in text
    assert "name: bldrx-dist-${{ github.run_id }}-${{ github.ref_name }}" in text
    assert "if: startsWith(github.ref, 'refs/tags/')" in text
