import shutil
import time
from threading import Thread

from bldrx.engine import Engine


def test_concurrent_install_waits(tmp_path, monkeypatch):
    src = tmp_path / "src"
    # create a nested dir so copytree is used and can be slowed
    (src / "sub").mkdir(parents=True, exist_ok=True)
    (src / "sub" / "file.txt").write_text("hello")
    user_templates = tmp_path / "user_templates"
    engine = Engine(user_templates_root=user_templates)

    orig_copytree = shutil.copytree

    def slow_copytree(a, b, *args, **kwargs):
        time.sleep(1.0)
        return orig_copytree(a, b, *args, **kwargs)

    monkeypatch.setattr(shutil, "copytree", slow_copytree)

    def installer():
        engine.install_user_template(
            src, name="concurrent", force=True, wrap=False, lock_timeout=5
        )

    t = Thread(target=installer)
    t.start()
    time.sleep(0.2)

    start = time.time()
    # this should wait for the first install to finish (because lock is held) then succeed
    engine.install_user_template(
        src, name="concurrent", force=True, wrap=False, lock_timeout=5
    )
    elapsed = time.time() - start
    assert elapsed >= 0.8
    t.join()


def test_concurrent_install_timeout(tmp_path, monkeypatch):
    src = tmp_path / "src"
    # create a nested dir so copytree is used and can be slowed
    (src / "sub").mkdir(parents=True, exist_ok=True)
    (src / "sub" / "file.txt").write_text("hello")
    user_templates = tmp_path / "user_templates"
    engine = Engine(user_templates_root=user_templates)

    orig_copytree = shutil.copytree

    def slow_copytree(a, b, *args, **kwargs):
        time.sleep(2.0)
        return orig_copytree(a, b, *args, **kwargs)

    monkeypatch.setattr(shutil, "copytree", slow_copytree)

    def installer():
        engine.install_user_template(
            src, name="concurrent", force=True, wrap=False, lock_timeout=5
        )

    t = Thread(target=installer)
    t.start()
    time.sleep(0.2)

    import pytest

    # this should timeout quickly and raise
    with pytest.raises(RuntimeError):
        engine.install_user_template(
            src, name="concurrent", force=True, wrap=False, lock_timeout=0.1
        )
    t.join()
