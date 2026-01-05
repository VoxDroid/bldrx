from pathlib import Path

import bldrx


def test_version():
    # assert package version matches pyproject.toml to avoid import path surprises
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.strip().startswith("version"):
            _, val = line.split("=", 1)
            expected = val.strip().strip('"')
            break
    else:
        expected = bldrx.__version__
    assert bldrx.__version__ == expected
