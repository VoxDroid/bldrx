from pathlib import Path

import bldrx


def test_bldrx_imports_from_local_source():
    # ensure we imported bldrx module from repo root, not from installed site-packages
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = Path(bldrx.__file__).resolve()
    assert str(repo_root) in str(
        mod_path
    ), f"bldrx module should be loaded from repo root, got {mod_path}"
