import io
import json
import tarfile

from bldrx.engine import Engine


def test_fetch_remote_tar_and_install(tmp_path):
    templates = tmp_path / "remote"
    t = templates / "rem"
    t.mkdir(parents=True)
    (t / "file.txt").write_text("content\n")
    # create proper sha256 (use engine helper style)
    import hashlib

    manifest = {
        "files": {"file.txt": hashlib.sha256((t / "file.txt").read_bytes()).hexdigest()}
    }
    (t / "bldrx-manifest.json").write_text(json.dumps(manifest))

    tar_path = tmp_path / "rem.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tf:
        tf.add(t, arcname=t.name)

    engine = Engine(
        templates_root=tmp_path / "templates",
        user_templates_root=tmp_path / "user_templates",
    )
    installed = engine.fetch_remote_template(
        tar_path.as_uri(), name="remoy", force=True
    )
    assert (installed / "file.txt").exists()


def test_fetch_remote_tar_detects_traversal(tmp_path):
    templates = tmp_path / "remote"
    t = templates / "rem"
    t.mkdir(parents=True)
    (t / "file.txt").write_text("content\n")

    tar_path = tmp_path / "bad.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tf:
        tf.add(t, arcname=t.name)
        # add a malicious entry
        ti = tarfile.TarInfo("../evil.txt")
        ti.size = len(b"evil")
        tf.addfile(ti, io.BytesIO(b"evil"))

    engine = Engine(
        templates_root=tmp_path / "templates",
        user_templates_root=tmp_path / "user_templates",
    )
    import pytest

    with pytest.raises(RuntimeError):
        engine.fetch_remote_template(tar_path.as_uri(), name="bad", force=True)
