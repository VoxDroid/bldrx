import tempfile
from pathlib import Path
from bldrx.engine import Engine


def test_apply_python_cli(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / 'bldrx' / 'templates')
    dest = tmp_path / 'proj'
    metadata = {'project_name': 'proj', 'author_name': 'Test', 'email': 't@example.com'}
    results = list(engine.apply_template('python-cli', dest, metadata, force=True))
    # expecting README, LICENSE, src_main
    created = [r for r in results if r[1] in ('rendered','copied')]
    assert any('README.md' in r[0] for r in created)
    assert any('LICENSE' in r[0] for r in created)
    assert any('src_main.py' in r[0] or 'src_main' in r[0] for r in created)
    # content check
    readme = dest / 'README.md'
    assert 'proj' in readme.read_text()


def test_remove_python_cli(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / 'bldrx' / 'templates')
    dest = tmp_path / 'proj'
    metadata = {'project_name': 'proj', 'author_name': 'T', 'email': 't@example.com'}
    # create files first
    list(engine.apply_template('python-cli', dest, metadata, force=True))
    readme = dest / 'README.md'
    assert readme.exists()
    # removing without force should report skipped (safety)
    results = list(engine.remove_template('python-cli', dest, force=False))
    assert any(r[1] in ('skipped', 'missing') for r in results)
    # removing with force should remove files
    results2 = list(engine.remove_template('python-cli', dest, force=True))
    assert any(r[1] == 'removed' for r in results2)
    assert not readme.exists()


def test_apply_dry_run(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / 'bldrx' / 'templates')
    dest = tmp_path / 'proj'
    metadata = {'project_name': 'proj', 'author_name': 'T', 'email': 't@example.com'}
    results = list(engine.apply_template('python-cli', dest, metadata, force=False, dry_run=True))
    # Should report would-render or would-copy actions and not create files
    assert any(r[1] in ('would-render','would-copy') for r in results)
    assert not (dest / 'README.md').exists()


def test_apply_force_behavior(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / 'bldrx' / 'templates')
    dest = tmp_path / 'proj'
    metadata = {'project_name': 'proj', 'author_name': 'T', 'email': 't@example.com'}
    # create files first
    list(engine.apply_template('python-cli', dest, metadata, force=True))
    readme = dest / 'README.md'
    assert readme.exists()
    # modify to simulate local changes
    readme.write_text('original', encoding='utf-8')
    results = list(engine.apply_template('python-cli', dest, metadata, force=False))
    assert any(r[1] == 'skipped' for r in results)
    # with force True, template should be re-rendered
    results2 = list(engine.apply_template('python-cli', dest, metadata, force=True))
    assert any(r[1] == 'rendered' for r in results2)


def test_remove_template_dry_run(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / 'bldrx' / 'templates')
    dest = tmp_path / 'proj'
    metadata = {'project_name': 'proj', 'author_name': 'T', 'email': 't@example.com'}
    list(engine.apply_template('python-cli', dest, metadata, force=True))
    readme = dest / 'README.md'
    assert readme.exists()
    results = list(engine.remove_template('python-cli', dest, force=True, dry_run=True))
    assert any(r[1] == 'would-remove' for r in results)
    assert readme.exists()
