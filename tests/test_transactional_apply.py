import os

import pytest

from bldrx.engine import Engine


def test_atomic_apply_success(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "txn"
    t.mkdir(parents=True)
    (t / "a.txt.j2").write_text("A {{ project_name }}\n")
    (t / "b.txt.j2").write_text("B {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()
    (dest / "a.txt").write_text("OLD A\n")
    (dest / "b.txt").write_text("OLD B\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    # perform atomic apply
    list(
        engine.apply_template(
            "txn", dest, {"project_name": "X"}, force=True, atomic=True, backup=True
        )
    )

    assert (dest / "a.txt").read_text().rstrip("\r\n") == "A X"
    assert (dest / "b.txt").read_text().rstrip("\r\n") == "B X"
    # backups exist
    backups = dest / ".bldrx" / "backups"
    assert backups.exists()


def test_atomic_apply_rollback_on_replace_error(tmp_path, monkeypatch):
    templates = tmp_path / "templates"
    t = templates / "txn"
    t.mkdir(parents=True)
    (t / "c.txt.j2").write_text("C {{ project_name }}\n")
    (t / "d.txt.j2").write_text("D {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()
    (dest / "c.txt").write_text("OLD C\n")
    (dest / "d.txt").write_text("OLD D\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )

    # simulate failure in os.replace when replacing d.txt
    orig_replace = os.replace

    def fake_replace(src, dst):
        if dst.endswith("d.txt"):
            raise OSError("simulated replace failure")
        return orig_replace(src, dst)

    monkeypatch.setattr("os.replace", fake_replace)

    with pytest.raises(RuntimeError):
        list(
            engine.apply_template(
                "txn", dest, {"project_name": "Y"}, force=True, atomic=True, backup=True
            )
        )

    # after rollback, original files should be intact
    assert (dest / "c.txt").read_text().rstrip("\r\n") == "OLD C"
    assert (dest / "d.txt").read_text().rstrip("\r\n") == "OLD D"
